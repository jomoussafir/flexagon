#!/usr/bin/env python3
"""Export only community catalogue content from the local WordPress SQLite DB.

No users, passwords, sessions, options, progress, or mail queues are exported.
Metadata is carried verbatim and decoded by WordPress during import, preserving
PHP serialization byte lengths and all LaTeX backslashes.
"""
import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_META = {'_lpdj_draft', '_lpdj_published', '_lpdj_legacy',
                '_lpdj_legacy_history', '_lpdj_legacy_id'}
TYPES = {'lpdj_problem', 'lpdj_asset', 'lpdj_history'}
FIELDS = ('ID', 'post_type', 'post_status', 'post_parent', 'post_author',
          'post_title', 'post_content', 'post_date', 'post_date_gmt',
          'post_modified', 'post_modified_gmt')

def export(root, output):
    base = root / '.local/wordpress/wp-content/database'
    candidates = []
    for path in base.rglob('*'):
        if path.is_file():
            with path.open('rb') as source:
                if source.read(16) == b'SQLite format 3\x00':
                    candidates.append(path)
    if len(candidates) != 1:
        raise ValueError('Expected exactly one local WordPress database')
    db = sqlite3.connect(candidates[0].as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    db.execute('BEGIN')  # Consistent read snapshot while the local site keeps running.
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%posts'")]
    if len(tables) != 1 or not re.fullmatch(r'[A-Za-z0-9_]+posts', tables[0]):
        raise ValueError('Could not identify WordPress tables safely')
    prefix = tables[0][:-5]
    records = []
    counts = collections.Counter()
    publications = []
    rows = db.execute(f"SELECT {','.join(FIELDS)} FROM {prefix}posts WHERE post_type IN ('lpdj_problem','lpdj_asset','lpdj_history') ORDER BY ID").fetchall()
    ids = {row['ID'] for row in rows}
    for row in rows:
        record = dict(row)
        if record['post_status'] != 'private':
            raise ValueError(f"Unexpected status for record {record['ID']}")
        if record['post_parent'] and record['post_parent'] not in ids:
            raise ValueError(f"Missing parent for record {record['ID']}")
        metadata = {}
        for meta in db.execute(f'SELECT meta_key,meta_value FROM {prefix}postmeta WHERE post_id=? ORDER BY meta_id', (record['ID'],)):
            key, value = meta
            if key not in ALLOWED_META:
                continue
            if key in metadata:
                raise ValueError(f'Duplicate metadata: {record["ID"]} / {key}')
            metadata[key] = value
        if record['post_type'] == 'lpdj_problem' and '_lpdj_draft' not in metadata:
            raise ValueError(f'Missing draft: {record["ID"]}')
        record['meta'] = metadata
        records.append(record)
        counts[record['post_type']] += 1
        if '_lpdj_published' in metadata:
            publications.append({'id':record['ID'], 'title':record['post_title']})
    author_ids = sorted({row['post_author'] for row in rows})
    authors = []
    for author_id in author_ids:
        user = db.execute(f'SELECT ID,display_name FROM {prefix}users WHERE ID=?', (author_id,)).fetchone()
        if not user:
            raise ValueError(f'Missing author: {author_id}')
        authors.append(dict(user))
    db.rollback()
    db.close()
    references = []
    for path in sorted((root/'private-data/references').iterdir()):
        if path.name == 'manifest.json' or path.suffix.lower() == '.pdf':
            references.append({'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    bundle = {'format':'lpdj-wordpress-catalogue-v1',
              'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'authors':authors, 'counts':dict(counts), 'published':publications,
              'records':records, 'references':references}
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(bundle, ensure_ascii=False, separators=(',',':')).encode('utf8')
    with output.open('wb') as target:
        target.write(payload)
    output.chmod(0o600)
    audit = {'format':bundle['format'], 'created_at':bundle['created_at'],
             'counts':dict(counts), 'published':publications,
             'authors':authors, 'reference_files':len(references),
             'reference_bytes':sum(item['bytes'] for item in references),
             'bundle_bytes':len(payload), 'sha256':hashlib.sha256(payload).hexdigest()}
    report = output.with_suffix('.audit.json')
    report.write_text(json.dumps(audit, ensure_ascii=False, indent=2)+'\n')
    report.chmod(0o600)
    print(json.dumps(audit, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    options = parser.parse_args()
    export(options.root, options.output or options.root/'private-data/ovh-transfer/catalogue.json')
