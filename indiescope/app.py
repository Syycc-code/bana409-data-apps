from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='IndieScope · Competitor discovery', page_icon='🎮', layout='wide')

@st.cache_data
def load_data():
    df = pd.read_csv(ROOT / 'data/indie_games.csv.gz')
    df['Release date'] = pd.to_datetime(df['Release date'])
    df['Genres'] = df['Genres'].fillna('')
    df['Tags'] = df['Tags'].fillna('')
    return df, json.loads((ROOT / 'data/audit.json').read_text())

df, audit = load_data()
st.title('IndieScope — Indie Game Competitor Discovery')
st.caption('Team: IndieScope · For indie publishing managers: shortlist comparable games for weekly pricing and positioning reviews.')
st.caption(f"Data: Steam / Steam Spy via Kaggle, release dates 2020–{audit['analysis_cutoff']}. Static snapshot; collection date not supplied. Intended production refresh: weekly.")
st.info('Use this page to choose games for deeper research. Prices use source units; currency is unverified. Reviews indicate feedback volume, not sales or revenue.')

genre_options = sorted({g.strip() for value in df['Genres'] for g in value.split(',') if g.strip() and g.strip() != 'Indie'})
tag_counts = pd.Series([t.strip() for value in df['Tags'] for t in value.split(',') if t.strip()]).value_counts()
with st.sidebar:
    st.header('Your competitive set')
    st.caption('Base scope: Indie, released from 2020, paid titles priced ≤40. Other segments are outside this dashboard.')
    chosen = st.multiselect('Genres (match any)', genre_options, default=['Strategy'] if 'Strategy' in genre_options else [])
    tags = st.multiselect('Tags (match all)', sorted(tag_counts[tag_counts >= 10].index.tolist()))
    prices = st.slider('Listed price range (source units)', 0.0, 40.0, (0.0, 40.0), step=1.0)
    years = st.slider('Release year range', 2020, int(df['Release date'].dt.year.max()), (2020, int(df['Release date'].dt.year.max())))
    min_reviews = st.selectbox('Minimum review count', [0, 10, 50, 100, 500, 1000], index=2)
    st.caption('50 reviews is an adjustable screening rule. It excludes some new and niche games; it is not proof that a rating is reliable.')

mask = df['Price'].between(*prices) & df['Release date'].dt.year.between(*years) & df['Review count'].ge(min_reviews)
if chosen:
    mask &= df['Genres'].map(lambda x: bool(set(chosen) & {v.strip() for v in x.split(',')}))
if tags:
    mask &= df['Tags'].map(lambda x: set(tags).issubset({v.strip() for v in x.split(',')}))
filtered = df.loc[mask].copy()
st.subheader('Your shortlisted market')
if filtered.empty:
    st.warning('No games match these filters. Broaden the genre, price or release-year range, or lower the review threshold.')
    st.stop()
cols = st.columns(3)
cols[0].metric('Comparable games', f'{len(filtered):,}')
cols[1].metric('Median listed price', f"{filtered['Price'].median():.3f}")
rate = filtered['Positive rate'].median()
cols[2].metric('Median game approval', f'{rate:.3f}%' if pd.notna(rate) else 'No reviews')
st.caption('Approval is the median of per-game positive-review percentages. Each game has equal weight. Titles without reviews have no approval score.')

left, right = st.columns([1.5, 1])
with left:
    st.subheader('Price and player approval')
    scored = filtered.dropna(subset=['Positive rate'])
    points = scored.sample(2000, random_state=42) if len(scored) > 2000 else scored
    if points.empty:
        st.caption('There are no reviewed games in this selection.')
    else:
        fig = px.scatter(points, x='Price', y='Positive rate', color='Review count',
                         color_continuous_scale='Teal', hover_name='Name',
                         hover_data={'Review count': ':,', 'Release date': '|%Y-%m-%d', 'Price': ':.3f', 'Positive rate': ':.3f'},
                         labels={'Price': 'Listed price (source units)', 'Positive rate': 'Positive reviews (%)'})
        fig.update_layout(height=400, margin=dict(l=5, r=5, t=10, b=10))
        st.plotly_chart(fig, width='stretch')
        if len(scored) > 2000: st.caption(f'Displaying a fixed random sample of 2,000 of {len(scored):,} reviewed games. Metrics, distribution and downloads use every match.')
    st.caption('Compare similarly aged releases. A high approval percentage with few reviews is a prompt to investigate, not an automatic recommendation.')
with right:
    st.subheader('How much feedback do they have?')
    bins = pd.cut(filtered['Review count'], [-1, 0, 49, 499, 4999, float('inf')], labels=['0', '1–49', '50–499', '500–4,999', '5,000+'])
    dist = bins.value_counts(sort=False).rename_axis('Reviews per game').reset_index(name='Games')
    fig = px.bar(dist, x='Reviews per game', y='Games', color_discrete_sequence=['#169c8c'])
    fig.update_layout(height=400, margin=dict(l=5, r=5, t=10, b=10))
    st.plotly_chart(fig, width='stretch')
    st.caption('Review counts accumulate over time and vary across audiences. They do not measure units sold.')

st.subheader('Choose 5–10 games for the next review')
st.caption('Sort the table, open comparable titles on Steam, and save a research list. Current source prices may include discounts; compare discount status before using a price as a benchmark.')
sort_by = st.selectbox('Initial table order', ['Review count', 'Positive rate', 'Price', 'Release date'])
table_cols = ['Name', 'Price', 'Discount', 'Positive rate', 'Review count', 'Release date', 'Genres', 'Tags', 'Developers', 'Publishers', 'Steam URL']
ordered = filtered.sort_values([sort_by, 'AppID'], ascending=[False, True], na_position='last')
st.dataframe(ordered[table_cols], hide_index=True, width='stretch',
             column_config={'Steam URL': st.column_config.LinkColumn('Steam page', display_text='Open'),
                            'Price': st.column_config.NumberColumn(format='%.3f'),
                            'Discount': st.column_config.NumberColumn('Discount (%)', format='%.0f'),
                            'Positive rate': st.column_config.NumberColumn('Approval (%)', format='%.3f'),
                            'Release date': st.column_config.DateColumn(format='YYYY-MM-DD')})
options = ordered['AppID'].tolist()
names = dict(zip(ordered['AppID'], ordered['Name']))
selected = st.multiselect('Research shortlist (choose up to 10)', options, format_func=lambda x: names[x], max_selections=10)
export = ordered.loc[ordered['AppID'].isin(selected), ['AppID'] + table_cols] if selected else ordered[['AppID'] + table_cols]
export = export.copy(); export['Release date'] = export['Release date'].dt.strftime('%Y-%m-%d')
st.download_button('Download shortlist' if selected else 'Download all filtered games', export.to_csv(index=False).encode('utf-8-sig'), 'steam_competitors.csv', 'text/csv')

with st.expander('Coverage, limitations and refresh decisions'):
    st.write('This is a curated peer set, not the entire Steam market. It excludes pre-2020, free, >40-unit, future-dated and some demo/playtest/server/soundtrack titles. Name exclusions are imperfect; manually review the shortlist.')
    st.write('Indie is a source genre label, not a verified studio-size definition. Missing tags limit tag-based discovery. Zero reviews means no score, not negative reception. Multi-genre games can belong to several groups.')
    st.write('Production proposal: refresh weekly before the Monday competitor review. Investigate a shortlisted game if its approval drops by 5 percentage points while it receives at least 50 new reviews since the prior snapshot. This is a proposed rule requiring historical snapshots; this static dataset cannot detect that change.')
    st.write('Stale prices or ratings can distort the comparison. Confirm each shortlisted game’s live store page before making a pricing decision. No revenue or causal success predictions are made.')
    st.caption('Source: ' + audit['source'])
