"""Stream the user-supplied CSV, repair its header, and export a small cohort."""
import argparse
import csv
import json
import gzip
from collections import Counter
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = ['AppID', 'Name', 'Release date', 'Price', 'Discount', 'Positive',
          'Negative', 'Genres', 'Tags', 'Developers', 'Publishers']

def prepare(source, cutoff):
    counts, missing, genres = Counter(), Counter(), Counter()
    price_bins, review_bins = Counter(), Counter()
    ids, rows, excluded = set(), [], []
    dates = []
    with open(source, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)
        repaired = 'DiscountDLC count' in header
        if repaired:
            i = header.index('DiscountDLC count')
            header[i:i+1] = ['Discount', 'DLC count']
        if not set(FIELDS).issubset(header):
            raise ValueError('Missing required fields')
        for values in reader:
            counts['raw_rows'] += 1
            if len(values) != len(header):
                raise ValueError(f'Wrong row width at record {counts["raw_rows"]}')
            d = dict(zip(header, values))
            for key in header:
                if not d[key].strip(): missing[key] += 1
            genres.update(x.strip() for x in d['Genres'].split(',') if x.strip())
            if d['AppID'] in ids:
                counts['duplicate_appid'] += 1
                raise ValueError('Duplicate AppID; resolve before export')
            ids.add(d['AppID'])
            try:
                dt = datetime.strptime(d['Release date'], '%b %d, %Y').date()
                p, pos, neg = float(d['Price']), int(d['Positive']), int(d['Negative'])
                discount = float(d['Discount'] or 0)
                assert p >= 0 and pos >= 0 and neg >= 0 and 0 <= discount <= 100
            except (ValueError, AssertionError):
                counts['invalid_required_values'] += 1
                continue
            dates.append(dt.isoformat())
            price_bins['free' if p == 0 else '0–10' if p <= 10 else '10–20' if p <= 20 else '20–40' if p <= 40 else '>40'] += 1
            total = pos + neg
            review_bins['0' if total == 0 else '1–49' if total < 50 else '50–499' if total < 500 else '500+'] += 1
            counts['future_dates'] += dt > cutoff
            counts['zero_price'] += p == 0
            counts['zero_reviews'] += total == 0
            reason = None
            if 'Indie' not in [x.strip() for x in d['Genres'].split(',')]: reason = 'not_indie'
            elif dt.year < 2020: reason = 'before_2020'
            elif dt > cutoff: reason = 'after_cutoff'
            elif not 0 < p <= 40: reason = 'outside_paid_price_range'
            elif any(word in d['Name'].lower() for word in ['playtest', 'demo', 'soundtrack', 'dedicated server']):
                reason = 'name_exclusion_heuristic'
                excluded.append({'AppID': d['AppID'], 'Name': d['Name'], 'reason': reason})
            if reason:
                counts[reason] += 1
                continue
            out = {key: d[key] for key in FIELDS}
            out.update({'Release date': dt.isoformat(), 'Price': p, 'Discount': discount,
                        'Positive': pos, 'Negative': neg,
                        'Review count': total,
                        'Positive rate': round(100 * pos / total, 6) if total else '',
                        'Steam URL': 'https://store.steampowered.com/app/' + d['AppID'] + '/'})
            rows.append(out)
            counts['exported_reviews_50plus'] += total >= 50
    data_dir = ROOT / 'data'
    data_dir.mkdir(exist_ok=True)
    target = data_dir / 'indie_games.csv'
    with target.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS + ['Review count', 'Positive rate', 'Steam URL'])
        writer.writeheader(); writer.writerows(rows)
    with (data_dir / 'excluded_names.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['AppID', 'Name', 'reason'])
        writer.writeheader(); writer.writerows(excluded)
    target.with_suffix('.csv.gz').write_bytes(gzip.compress(target.read_bytes(), mtime=0))
    audit = {'source': 'https://www.kaggle.com/datasets/fronkongames/steam-games-dataset',
             'source_file': 'games.csv', 'source_bytes': Path(source).stat().st_size,
             'analysis_cutoff': cutoff.isoformat(), 'snapshot_collection_date': 'not supplied',
             'header_repaired': repaired, 'original_column_count': len(header) - int(repaired),
             'corrected_column_count': len(header), 'counts': dict(counts),
             'missing_raw': dict(missing), 'top_genres_raw': genres.most_common(12),
             'raw_price_bins': dict(price_bins), 'raw_review_bins': dict(review_bins),
             'raw_release_date_range': [min(dates), max(dates)], 'export_rows': len(rows),
             'export_bytes': target.stat().st_size,
             'currency': 'not verified; prices displayed in source units',
             'scope': 'Indie genre; 2020 onward through cutoff; 0 < listed price <= 40; name exclusions',
             'team_name': 'IndieScope (working team name; replace with actual team)'}
    (data_dir / 'audit.json').write_text(json.dumps(audit, indent=2, ensure_ascii=False))
    print(json.dumps(audit, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('--cutoff', default='2026-10-12')
    args = parser.parse_args()
    prepare(args.source, date.fromisoformat(args.cutoff))
