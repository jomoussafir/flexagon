#!/usr/bin/env python3
"""Trace the figures of scanned reference books into vector PDF and SVG files.

The reference library contains one 600 dpi scan per page and no vector objects, so a
figure becomes a vector only by tracing it. This tool locates each drawing on a page
(body text is separated from graphics by component size and line structure), crops it
from the original bitmap, traces it with potrace and writes:

    private-data/figures/<book>/<book>-p<page>-<n>.pdf   vector master (LaTeX, iPhone)
    private-data/figures/<book>/<book>-p<page>-<n>.svg   same drawing for the website
    private-data/figures/review/<book>-p<page>.png       detected boxes, for checking
    private-data/figures/manifest.json                   library index read by the plugin

The website offers only figures that also have a clean redrawing; see redraw-figures.py.

Usage:
    python3 tools/extract-figures.py --source colossal --pages 24-32,138
    python3 tools/extract-figures.py --source colossal --problems   # pages cited by problems
    python3 tools/extract-figures.py --all --problems

Requires poppler (pdfimages), potrace, Pillow, numpy and scipy. Re-running a page
replaces that page's figures in the manifest; other pages are kept.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw
    from scipy import ndimage
except ImportError as error:  # pragma: no cover - environment check
    raise SystemExit(f'Missing Python package ({error.name}). Install Pillow, numpy and scipy for this interpreter.')

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / 'private-data/references'
OUTPUT = ROOT / 'private-data/figures'
ANALYSIS_DPI = 100              # figure detection works on a reduced image
SLUGS = {
    'The Colossal Book of Short Puzzles and Problems': 'colossal',
    'The Moscow Puzzles': 'moscow',
    'The Stanford Mathematics Problem Book': 'stanford',
    'Challenging Problems In Geometry': 'geometry',
    'Challenging Problems In Algebra': 'algebra',
    'Yaglom Vol 1': 'yaglom-1',
    'Yaglom Vol 2': 'yaglom-2',
}
MAX_FILE = 2 * 1024 * 1024      # upload limit of the website


def slug_for(source: dict) -> str:
    if source['title'] in SLUGS:
        return SLUGS[source['title']]
    if re.fullmatch(r'[a-z]+-\d{4}', source['id']):
        return source['id']
    return re.sub(r'[^a-z0-9]+', '-', source['id'].lower()).strip('-')


def load_library() -> dict[str, dict]:
    manifest = json.loads((REFERENCES / 'manifest.json').read_text())
    library = {}
    for source in manifest:
        source['slug'] = slug_for(source)
        library[source['slug']] = source
    return library


def cited_pages(source_id: str) -> set[int]:
    bundle = ROOT / 'private-data/legacy-export/import.json'
    if not bundle.is_file():
        raise SystemExit('private-data/legacy-export/import.json is needed for --problems.')
    pages = set()
    for problem in json.loads(bundle.read_text())['problems']:
        for occurrence in problem.get('occurrences', []):
            if occurrence.get('source_id') == source_id and occurrence.get('pdf_page'):
                pages.add(int(occurrence['pdf_page']))
    return pages


def parse_pages(text: str) -> set[int]:
    pages = set()
    for part in text.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            start, end = part.split('-', 1)
            pages.update(range(int(start), int(end) + 1))
        else:
            pages.add(int(part))
    return pages


def page_bitmap(source: dict, page: int, workdir: Path):
    """Return the page scan as a boolean ink array and its resolution in dpi."""
    for part in source['parts']:
        if part['start'] <= page <= part['end']:
            break
    else:
        raise SystemExit(f'Page {page} is outside {source["title"]}.')
    in_file = page - part['start'] + 1
    prefix = workdir / f'page-{page}'
    subprocess.run(['pdfimages', '-png', '-f', str(in_file), '-l', str(in_file), str(REFERENCES / part['file']), str(prefix)],
                   check=True, capture_output=True)
    listing = subprocess.run(['pdfimages', '-list', '-f', str(in_file), '-l', str(in_file), str(REFERENCES / part['file'])],
                             check=True, capture_output=True, text=True).stdout.splitlines()[2:]
    # Books are scanned at 300 or 600 dpi; take the resolution of the largest image.
    dpi = 600
    best = 0
    for row in listing:
        cols = row.split()
        if len(cols) > 13 and cols[2] == 'image' and cols[3].isdigit() and int(cols[3]) * int(cols[4]) > best:
            best = int(cols[3]) * int(cols[4]); dpi = int(cols[12])
    images = sorted(workdir.glob(f'page-{page}-*.png'))
    if not images:
        raise SystemExit(f'No scanned image found on page {page} of {source["title"]}.')
    # Scanned books store one full-page image; use the largest when several exist.
    image = Image.open(max(images, key=lambda f: f.stat().st_size)).convert('L')
    if image.width < 1000:
        raise SystemExit(f'Page {page} of {source["title"]} is not a full-page scan.')
    ink = np.asarray(image) < 128
    for file in images:
        file.unlink()
    return ink, dpi


def reduce_any(ink: np.ndarray, factor: int) -> np.ndarray:
    h, w = ink.shape
    h -= h % factor
    w -= w % factor
    return ink[:h, :w].reshape(h // factor, factor, w // factor, factor).any(axis=(1, 3))


class Box:
    __slots__ = ('x0', 'y0', 'x1', 'y1')

    def __init__(self, x0, y0, x1, y1):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1

    @property
    def w(self):
        return self.x1 - self.x0

    @property
    def h(self):
        return self.y1 - self.y0

    def expand(self, dx, dy=None):
        dy = dx if dy is None else dy
        return Box(self.x0 - dx, self.y0 - dy, self.x1 + dx, self.y1 + dy)

    def intersects(self, other) -> bool:
        return self.x0 < other.x1 and other.x0 < self.x1 and self.y0 < other.y1 and other.y0 < self.y1

    def union(self, other):
        return Box(min(self.x0, other.x0), min(self.y0, other.y0), max(self.x1, other.x1), max(self.y1, other.y1))

    def contains(self, other) -> bool:
        return self.x0 <= other.x0 and self.y0 <= other.y0 and self.x1 >= other.x1 and self.y1 >= other.y1


def detect_figures(small: np.ndarray):
    """Find figure boxes on the 100 dpi ink image.

    Returns (boxes, labels, members, text_runs, text_height) where members[i] is the
    set of component labels that belong to figure i.
    """
    labels, count = ndimage.label(small, structure=np.ones((3, 3), dtype=int))
    if count == 0:
        return [], labels, [], [], 10
    objects = ndimage.find_objects(labels)
    areas = ndimage.sum(small, labels, index=np.arange(1, count + 1))
    page_h, page_w = small.shape
    comps = {}
    for index, (sl, area) in enumerate(zip(objects, areas), start=1):
        if sl is None:
            continue
        box = Box(sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)
        comps[index] = (box, int(area))
    # Typical glyph height: the most common height among small components.
    heights = [box.h for box, area in comps.values() if 3 <= box.h <= 30 and area >= 4]
    text_h = int(np.median(heights)) if heights else 10
    text_h = max(5, min(text_h, 16))
    glyph, graphic, noise = {}, {}, set()
    for index, (box, area) in comps.items():
        if area < 2:
            noise.add(index)
        elif (box.w > 0.9 * page_w or box.h > 0.9 * page_h):
            noise.add(index)          # scanner border or page frame
        elif box.h <= 2.2 * text_h and not (box.h <= 3 and box.w >= 3 * text_h):
            glyph[index] = box        # letters, or whole words fused at 100 dpi
        else:
            graphic[index] = box      # taller than a text line, or a horizontal rule
    # Group glyphs into lines: vertical overlap and a small horizontal gap.
    order = sorted(glyph, key=lambda i: (glyph[i].x0, glyph[i].y0))
    parent = {i: i for i in order}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    gap = 0.8 * text_h
    by_row = sorted(order, key=lambda i: glyph[i].y0)
    for a_pos, a in enumerate(by_row):
        ba = glyph[a]
        for b in by_row[a_pos + 1:]:
            bb = glyph[b]
            if bb.y0 > ba.y1:
                break
            overlap = min(ba.y1, bb.y1) - max(ba.y0, bb.y0)
            if overlap < 0.4 * min(ba.h, bb.h):
                continue
            if bb.x0 - ba.x1 <= gap and ba.x0 - bb.x1 <= gap:
                parent[find(a)] = find(b)
    runs = {}
    for i in order:
        runs.setdefault(find(i), []).append(i)
    run_boxes = []
    for members in runs.values():
        box = glyph[members[0]]
        for i in members[1:]:
            box = box.union(glyph[i])
        run_boxes.append((box, members))
    # The left margin of the text column: where most long lines start.
    starts = [box.x0 for box, members in run_boxes if len(members) >= 4 or box.w >= 0.25 * page_w]
    margin = int(np.median(starts)) if starts else 0
    text_runs, label_runs = [], []
    for box, members in run_boxes:
        # A line of prose has several words and starts at the margin or one indent in.
        # A short line flush with the margin is a caption such as "Figure 1.6"; labels
        # and small parts inside a drawing are indented, so they can join a figure.
        at_margin = box.x0 - margin <= 3 * text_h
        prose = ((len(members) >= 4 or box.w >= 0.25 * page_w) and at_margin) or box.w >= 0.6 * page_w
        caption = len(members) >= 2 and box.w > 4 * text_h and abs(box.x0 - margin) <= 1.5 * text_h
        if prose or caption:
            text_runs.append((box, members))
        else:
            label_runs.append((box, members))
    # Seeds: graphics wide and tall enough to be a drawing. Rules, fraction bars and
    # tall brackets are only parts: they join a drawing but never start one, so
    # displayed equations, tables and underlined headings are not figures.
    area_seeds = {i: box for i, box in graphic.items() if box.w >= 2 * text_h and box.h >= 2 * text_h}
    # Long lines (arrows, axes, long segments) may also start a drawing; short ones are parts.
    line_seeds = {i: box for i, box in graphic.items() if i not in area_seeds and max(box.w, box.h) >= 6 * text_h}
    seeds = area_seeds | line_seeds
    label_runs += [(box, [i]) for i, box in graphic.items() if i not in seeds]
    figures = [(box, {i}) for i, box in seeds.items()]
    merge_gap = int(1.5 * text_h)
    far_gap = int(4 * text_h)        # stacked parts of one figure
    side_gap = int(6 * text_h)       # parts placed side by side

    def text_between(a: Box, b: Box) -> bool:
        gap_box = Box(min(a.x0, b.x0), min(a.y0, b.y0), max(a.x1, b.x1), max(a.y1, b.y1))
        if a.x1 <= b.x0 or b.x1 <= a.x0:      # side by side
            gap_box.x0, gap_box.x1 = min(a.x1, b.x1), max(a.x0, b.x0)
        else:                                  # stacked
            gap_box.y0, gap_box.y1 = min(a.y1, b.y1), max(a.y0, b.y0)
        return any(run.intersects(gap_box) for run, _ in text_runs)

    def should_merge(a: Box, b: Box) -> bool:
        if a.expand(merge_gap).intersects(b):
            return True
        dx = max(a.x0 - b.x1, b.x0 - a.x1, 0)
        dy = max(a.y0 - b.y1, b.y0 - a.y1, 0)
        x_overlap = min(a.x1, b.x1) - max(a.x0, b.x0)
        y_overlap = min(a.y1, b.y1) - max(a.y0, b.y0)
        if dy <= far_gap and x_overlap >= 0.3 * min(a.w, b.w) and not text_between(a, b):
            return True
        if dx <= side_gap and y_overlap >= 0.3 * min(a.h, b.h) and not text_between(a, b):
            return True
        return False

    changed = True
    while changed:
        changed = False
        merged = []
        while figures:
            box, members = figures.pop()
            i = 0
            while i < len(merged):
                other, other_members = merged[i]
                if should_merge(box, other):
                    box, members = box.union(other), members | other_members
                    merged.pop(i)
                    changed = True
                else:
                    i += 1
            merged.append((box, members))
        figures = merged
        # Labels near a drawing belong to it (A, B, 1, 8 ...), never body text.
        for index, (box, members) in enumerate(figures):
            for run, run_members in label_runs:
                if run_members[0] in members:
                    continue
                if box.expand(merge_gap).intersects(run):
                    figures[index] = (box.union(run), members | set(run_members))
                    box, members = figures[index]
                    changed = True
    results = []
    text_members = {i for _, run_members in text_runs for i in run_members}
    for box, members in figures:
        # Drawings made of lines only (no solid shape) must be clearly two-dimensional,
        # which excludes a lone rule with a label or a heading between two rules.
        minimum = (3 if any(i in area_seeds for i in members) else 4) * text_h
        if box.w < minimum or box.h < minimum:
            continue
        # Everything inside the box belongs to the drawing (halftone dots, small marks),
        # except prose that crosses its edge, which is cut out and reported.
        inside = {i for i, (cb, _) in comps.items() if box.contains(cb)}
        warnings = []
        for run, run_members in text_runs:
            if run.intersects(box) and not box.contains(run):
                inside -= set(run_members)
                if 'text-overlap' not in warnings:
                    warnings.append('text-overlap')
        members = members | inside
        # A box whose ink is mostly lines of prose is a table or a text block.
        ink = sum(comps[i][1] for i in members)
        prose_ink = sum(comps[i][1] for i in members if i in text_members)
        if ink and prose_ink / ink > 0.6:
            continue
        results.append((box, members, warnings))
    results.sort(key=lambda item: (item[0].y0, item[0].x0))
    return results, labels, text_runs, text_h


def trace(crop: np.ndarray, pdf: Path, svg: Path, dpi: int) -> tuple[float, float]:
    """Trace a boolean crop with potrace; return the size in points."""
    h, w = crop.shape
    with tempfile.NamedTemporaryFile(suffix='.pbm', delete=False) as handle:
        bits = np.packbits(crop, axis=1)
        handle.write(f'P4\n{w} {h}\n'.encode() + bits.tobytes())
        pbm = handle.name
    try:
        speckle = max(2, round(12 * (dpi / 600) ** 2))   # ignore dust smaller than ~0.04 mm²
        common = ['potrace', '-r', str(dpi), '-t', str(speckle), '-a', '1', '-O', '0.2', '-M', '0', pbm]
        subprocess.run(common + ['-b', 'pdf', '-o', str(pdf)], check=True, capture_output=True)
        subprocess.run(common + ['-b', 'svg', '-o', str(svg)], check=True, capture_output=True)
    finally:
        Path(pbm).unlink(missing_ok=True)
    text = svg.read_text()
    # The website accepts plain SVG without declarations, DOCTYPE or metadata.
    text = re.sub(r'<\?xml[^>]*\?>\s*|<!DOCTYPE[^>]*>\s*|<metadata>.*?</metadata>\s*', '', text, flags=re.S)
    svg.write_text(text.strip() + '\n')
    return w * 72 / dpi, h * 72 / dpi


def process_page(source: dict, page: int, workdir: Path, review_dir: Path) -> list[dict]:
    ink, dpi = page_bitmap(source, page, workdir)
    reduce = max(1, round(dpi / ANALYSIS_DPI))
    small = reduce_any(ink, reduce)
    figures, labels, text_runs, text_h = detect_figures(small)
    slug = source['slug']
    out_dir = OUTPUT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob(f'{slug}-p{page}-*'):
        old.unlink()
    pad = int(0.8 * text_h)
    entries = []
    review = Image.fromarray(np.where(small, 0, 255).astype(np.uint8)).convert('RGB')
    draw = ImageDraw.Draw(review)
    for run, _ in text_runs:
        draw.rectangle([run.x0, run.y0, run.x1 - 1, run.y1 - 1], outline=(190, 190, 255))
    for n, (box, members, warnings) in enumerate(figures, start=1):
        x0, y0 = max(box.x0 - pad, 0), max(box.y0 - pad, 0)
        x1, y1 = min(box.x1 + pad, small.shape[1]), min(box.y1 + pad, small.shape[0])
        mask = np.isin(labels[y0:y1, x0:x1], list(members))
        crop = ink[y0 * reduce:y1 * reduce, x0 * reduce:x1 * reduce] & np.kron(mask, np.ones((reduce, reduce), dtype=bool))
        figure_id = f'{slug}-p{page}-{n}'
        pdf, svg = out_dir / f'{figure_id}.pdf', out_dir / f'{figure_id}.svg'
        width, height = trace(crop, pdf, svg, dpi)
        draw.rectangle([x0, y0, x1 - 1, y1 - 1], outline=(220, 40, 40), width=2)
        draw.text((x0 + 3, y0 + 2), str(n), fill=(220, 40, 40))
        entry = {'id': figure_id, 'source': slug, 'sourceId': source['id'], 'sourceTitle': source['title'], 'page': page,
                 'index': n, 'dir': slug, 'pdf': pdf.name, 'svg': svg.name, 'width': round(width, 1), 'height': round(height, 1),
                 'bytes': {'pdf': pdf.stat().st_size, 'svg': svg.stat().st_size}, 'warnings': warnings}
        if max(entry['bytes'].values()) > MAX_FILE:
            entry['warnings'].append('oversized')
        entries.append(entry)
    review_dir.mkdir(parents=True, exist_ok=True)
    review.save(review_dir / f'{slug}-p{page}.png')
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--source', action='append', default=[], help='book slug or reference id (repeatable)')
    parser.add_argument('--all', action='store_true', help='every scanned book in the reference manifest')
    parser.add_argument('--pages', default='', help='page list such as 24-32,138 (PDF page numbers of the book)')
    parser.add_argument('--problems', action='store_true', help='pages cited by imported problems')
    args = parser.parse_args()
    for tool in ('pdfimages', 'potrace'):
        if not shutil.which(tool):
            raise SystemExit(f'{tool} is not installed (brew install poppler potrace).')
    library = load_library()
    by_id = {source['id']: source for source in library.values()}
    if args.all:
        selected = [s for s in library.values() if s['id'] in {'local-2ef4179b3388', 'local-cf02a5b5653e', 'local-077c5a30ffe6', 'book-geometry', 'book-algebra', 'local-7cf7eb6f2799', 'local-b2f0ddb6120f'}]
    else:
        selected = []
        for key in args.source:
            source = library.get(key) or by_id.get(key)
            if not source:
                raise SystemExit(f'Unknown source {key}. Known: {", ".join(sorted(library))}')
            selected.append(source)
    if not selected:
        parser.error('choose --source <book> or --all')
    if not args.pages and not args.problems:
        parser.error('choose --pages or --problems')
    manifest_file = OUTPUT / 'manifest.json'
    manifest = {'format': 'lpdj-figures-v1', 'figures': []}
    if manifest_file.is_file():
        manifest = json.loads(manifest_file.read_text())
    workdir = Path(tempfile.mkdtemp(prefix='lpdj-figures-'))
    try:
        for source in selected:
            pages = parse_pages(args.pages) if args.pages else set()
            if args.problems:
                pages |= cited_pages(source['id'])
            pages = sorted(p for p in pages if 1 <= p <= source['pages'])
            print(f'{source["title"]}: {len(pages)} page(s)')
            for page in pages:
                entries = process_page(source, page, workdir, OUTPUT / 'review')
                previous = {f['id']: f for f in manifest['figures'] if f['source'] == source['slug'] and f['page'] == page}
                manifest['figures'] = [f for f in manifest['figures'] if not (f['source'] == source['slug'] and f['page'] == page)]
                for entry in entries:   # a redrawing (tools/redraw-figures.py) survives re-tracing
                    if previous.get(entry['id'], {}).get('redrawn'): entry['redrawn'] = previous[entry['id']]['redrawn']
                new_ids = {entry['id'] for entry in entries}
                for old in previous.values():   # redrawings whose traced box disappeared are kept
                    if old.get('redrawn') and old['id'] not in new_ids:
                        old['warnings'] = sorted(set(old.get('warnings', [])) | {'redrawn-only'}); entries.append(old)
                manifest['figures'].extend(entries)
                flags = ', '.join(f'{e["index"]}:{"/".join(e["warnings"])}' for e in entries if e['warnings'])
                print(f'  page {page}: {len(entries)} figure(s)' + (f' — check {flags}' if flags else ''))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    manifest['figures'].sort(key=lambda f: (f['source'], f['page'], f['index']))
    manifest['generated'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    manifest['count'] = len(manifest['figures'])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, indent=1) + '\n')
    print(f'{manifest["count"]} figure(s) in {manifest_file.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
