# IndieScope: Indie Game Competitor Discovery

**Live app:** https://bana409-indiescope-syycc.streamlit.app/

For an indie game publishing manager, this dashboard turns a large Steam catalogue into a list of comparable games for a weekly pricing and positioning review. **IndieScope is a working team name; replace it before submission.**

## 1. Dataset and provenance

Source: [Steam Games Dataset by Martin Bustos / Fronkon Games](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset), collected from Steam and Steam Spy. Refer to its data card for attribution and license terms.

The user-supplied `games.csv` is 401,140,503 bytes with **125,855 records**. Each row represents a Steam app, not a sale, player or observation day. Apps may include demos, playtests and other content. Raw release dates span June 30, 1997–December 1, 2026; release dates are not collection dates. This is scraped platform data, not synthetic transactions.

The snapshot collection date and price currency were not supplied with the local file. We do not invent them. The analysis cutoff is **October 12, 2026**; it excludes future-dated titles but is not a verified snapshot timestamp. The dashboard displays prices in source units and requires live-page verification before pricing decisions.

## 2. Decision-maker and action

One indie game publishing manager responsible for an upcoming paid game reviews competitors every Monday.

**If the manager sees games matching the intended genre, release cohort and price band, with substantial player feedback and strong approval, they will shortlist 5–10 titles, inspect their store pages and discount status, and bring those comparisons to the pricing and positioning meeting.** This app supports choosing what to research, rather than deciding an optimal price or predicting success.

A plausible existing workflow is manual Steam searches and an inconsistently updated spreadsheet. It repeats work and makes comparisons harder to reproduce. This is a target-role design assumption, not a measured interview or a quantified cost-saving claim.

## 3. Why a dashboard?

The same person repeatedly compares a changing competitive set. Interactive filters let them explore follow-up questions during the meeting without requesting another report. A weekly email can announce changes but cannot replace filtering by genre, price and release cohort. A one-time market study would be more appropriate if only one question or meeting were involved; this design assumes a recurring review.

## 4. EDA and preparation

`prepare_data.py` streams the raw file and profiles shape, row widths, missing values, release dates, numeric values, genres and distributions. `eda.ipynb` contains executed Pandas and Matplotlib analysis of the resulting cohort, together with the raw-data audit. `data/audit.json` records preparation counts and provenance; `data/excluded_names.csv` makes heuristic exclusions reviewable.

The raw header has **39 columns but all 125,855 rows have 40 values**. `DiscountDLC count` incorrectly merges two headers. Splitting it into `Discount` and `DLC count` before assigning any values repairs the shift. Otherwise fields including positive reviews and genres would be assigned incorrectly. Required values, discount bounds and duplicate AppIDs are checked. Malformed required values are excluded and counted; duplicate IDs or row-width mismatches stop preparation. None were encountered in this input after header repair.

Raw EDA found **42,899 zero-review apps, 42,502 missing tag fields and 8,423 missing genre fields**. Missing tags are retained as blank, not guessed; tag filters are optional. Missing genre membership cannot establish Indie status, so those apps are outside the cohort. Zero-review games have an undefined approval rate, not a 0% rate. These findings motivate an adjustable review threshold rather than a fixed reliability claim.

Export scope:

- Exact `Indie` source genre label, not verified studio size.
- Release dates from 2020 through October 12, 2026.
- Listed price >0 and ≤40 source units: a chosen paid-game segment, not an optimal range.
- Names containing `demo`, `playtest`, `soundtrack` or `dedicated server` are excluded. This imperfect rule can omit a full game or miss an unusual demo; manually inspect the final shortlist.

Sequential exclusions: 42,971 non-Indie apps, 21,799 pre-2020 apps, one future-dated app, 9,506 outside the paid price range, and 174 name-heuristic exclusions. Export: **51,404 rows, 14,496,896 bytes (14.497 MB)**, below the course's suggested 25 MB. **9,520** exported titles have ≥50 reviews. All low-review titles remain in the export so the user can lower the threshold.

## 5. Display choices and layout

The sidebar defines the competitive set: genres (match any), tags (match all), price, release year and minimum review count. Empty genre or tag selection adds no restriction. Optional tags avoid silently excluding every missing-tag title.

The three headline numbers are:

1. **Comparable games:** size of the filtered research set, not market saturation.
2. **Median listed price:** peer pricing context with less sensitivity to extreme prices. Source prices may be discounted; the currency is unverified.
3. **Median game approval:** compute `Positive / (Positive + Negative) × 100` for each reviewed title, then take the median across games. Every game has equal weight. This differs from the aggregate fraction of positive reviews.

The two supporting charts are:

- **Price vs approval:** identify comparable titles worth investigating. Hover includes review count and release date. Above 2,000 reviewed matches, a fixed random sample of 2,000 is disclosed for readability. Metrics, distribution and downloads still use the full filtered set.
- **Review-count distribution:** reveals whether the peer set has sparse or substantial feedback. Review counts accumulate with age and are not copies sold.

The bottom table gives names, price, discount, approval, review count, release date, genre/tag, developer/publisher and direct Steam links. The manager can select up to ten games and download a shortlist. With no selection, the download contains every filtered match.

Layout: scope in the sidebar; headline overview at the top; explanatory charts in the middle; actionable research detail at the bottom. The detail table earns its space because creating a usable shortlist is the purpose of the page.

Default opening view: Strategy, 2020–2026, paid prices ≤40, ≥50 reviews. It yields **2,200 comparable games**, median price **5.750 source units**, and median approval **83.502%**. These describe only that filtered cohort and should not be generalized to all Steam games.

## 6. What we chose not to show

1. **Estimated revenue and market-share rankings.** Owner estimates are intervals, and listed prices are not realized prices. Discounts, refunds, keys and platform fees are unknown. Multiplication would create unsupported precision.
2. **Metacritic/User-score headline metrics and playtime rankings.** Coverage and zero-value meanings would first need verification. They add another scoreboard without changing the initial peer-selection decision. Approval and review volume already support that step.

We also omit a success-prediction model. Observational correlations cannot establish what changing a game's price or genre would cause.

## 7. Data limitations and handling

- One snapshot cannot measure historical price or approval changes. Release year is not a sales year; no annual-sales chart is claimed.
- ≥50 reviews is an adjustable screening assumption, not statistical proof. It omits some new/niche games; users can lower it to zero.
- Compare similar release ages: older games have had more time to accumulate feedback.
- Multi-genre/tag membership overlaps. Genres are not mutually exclusive business segments.
- The table exposes discount status; check live store pages before comparing prices.
- Indie labels and name exclusions are imperfect. Manually verify the shortlist.
- Unknown collection date prevents a freshness claim. The cutoff is explicitly distinct from snapshot time.
- The curated cohort excludes free, expensive, old and future-dated titles. It is not the complete Steam market.

## 8. Refresh, review frequency and action trigger

**Production proposal:** refresh weekly before Monday's competitor meeting. Weekly pricing and positioning decisions do not justify minute-level collection. The included Kaggle CSV is static and does not automatically update.

Store weekly snapshots for selected competitors. Proposed investigation trigger: **approval falls by at least five percentage points while at least 50 new reviews arrive since the previous snapshot**. The manager reads recent complaints and checks for a relevant patch, launch or pricing change. These thresholds are design assumptions to calibrate later; this single snapshot cannot calculate the change or fire an alert.

Stale data can mean comparing against an expired discount or overlooking recent complaints. Confirm current store pages before a pricing decision. Weekly history is a future addition; the current app supports discovery.

## Run locally

Python 3.14, as specified by the course. The compact CSV is included; the original 401 MB source is unnecessary for running the app.

```bash
uv sync
uv run streamlit run app.py
```

Regenerate compact data:

```bash
uv run python prepare_data.py /path/to/games.csv --cutoff 2026-10-12
```

Open `eda.ipynb` for the executed analysis. Its scope is the compact cohort and raw-data audit, not a claim that all original text fields were modeled.

## Deploy and submit

Create your own public GitHub repository and upload these project files. Exclude `.venv`, `.git`, caches and the original `games.csv`. Include `app.py`, `requirements.txt`, `README.md`, `eda.ipynb`, `prepare_data.py` and the `data/` folder. In Streamlit Community Cloud choose your repo, branch `main`, entry point `app.py` and Python **3.14** under Advanced settings, following the course instructions.

Verify the public app opens; change filters, test an empty selection and download a shortlist. Submit the app URL and GitHub repository URL individually on Canvas. Team discussion does not replace the individual's app/repo/README. **The app is deployed under the owner's Streamlit Cloud account; Canvas submission remains a separate step.**


### Deployment package
The 14.497 MB CSV is also stored losslessly as `data/indie_games.csv.gz` (4.012 MB); the app reads the gzip file directly. Deployed entry point in this personal course repository: `indiescope/app.py`. The EDA notebook also reads the gzip CSV directly. Part 2 of Assignment 4 uses the separate phone-trade-in notebook and course phone data.
