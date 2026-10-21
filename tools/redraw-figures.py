#!/usr/bin/env python3
"""Clean vector redrawings of reference-book figures, as SVG (website) and PDF (master).

The traced figures made by extract-figures.py keep the look of the scan. The editor's
"Source figures" panel offers only figures that have a redrawing, which this tool
writes to private-data/figures/<book>-redrawn/<figure-id>.{svg,pdf} and records in the
`redrawn` field of the figure's manifest entry.

Drawings live in tools/figures/<book>.py, one function per figure:

    @figure('colossal-p138-2', 260, 260, 'Four bugs ...')
    def amorous_bugs(c):
        c.arrow(50, 50, 210, 50) ...

A figure that the tracer merged with another, or missed, gets a new id and `page=`.
Run:
    python3 tools/redraw-figures.py                 # every redrawing
    python3 tools/redraw-figures.py colossal-p138-2 # one figure
    python3 tools/redraw-figures.py --book moscow   # one book

No external library is needed; the PDF is written directly.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / 'private-data/figures'
MANIFEST = FIGURES / 'manifest.json'
MODULES = Path(__file__).resolve().parent / 'figures'
K = 0.5523  # circle approximation by cubic Béziers
COLORS_SVG = {'black': 'black', 'dark': '#555555', 'gray': '#9a9a9a', 'light': '#dcdcdc', 'white': 'white'}
COLORS_PDF = {'black': '0 g', 'dark': '0.33 g', 'gray': '0.6 g', 'light': '0.86 g', 'white': '1 g'}


class Canvas:
    """Collects drawing primitives in a top-left origin and emits SVG and PDF."""

    def __init__(self, width, height, label):
        self.w, self.h, self.label = width, height, label
        self.ops = []
        self.transforms = []      # (angle degrees, cx, cy, sx, sy) applied to every point

    # ---- transforms ----------------------------------------------------------
    def _t(self, x, y):
        for angle, cx, cy, sx, sy in reversed(self.transforms):
            x, y = cx + (x - cx) * sx, cy + (y - cy) * sy
            a = math.radians(angle); ca, sa = math.cos(a), math.sin(a)
            x, y = cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca
        return x, y

    def _tsegs(self, segments):
        out = []
        for seg in segments:
            pts = [self._t(seg[i], seg[i + 1]) for i in range(1, len(seg), 2)]
            out.append((seg[0],) + tuple(v for pt in pts for v in pt))
        return out

    class _Transform:
        def __init__(self, canvas, item): self.canvas, self.item = canvas, item
        def __enter__(self): self.canvas.transforms.append(self.item); return self.canvas
        def __exit__(self, *_): self.canvas.transforms.pop()

    def rotated(self, angle, cx, cy):
        """with c.rotated(20, x, y): ... draws everything rotated about (x, y)."""
        return self._Transform(self, (angle, cx, cy, 1, 1))

    def scaled(self, sx, sy, cx=0, cy=0):
        return self._Transform(self, (0, cx, cy, sx, sy))

    # ---- primitives --------------------------------------------------------
    def path(self, segments, stroke=1.2, fill=None, dash=None, close=False):
        """segments: list of ('M',x,y) | ('L',x,y) | ('C',x1,y1,x2,y2,x,y)."""
        self.ops.append(('path', self._tsegs(segments) if self.transforms else segments, stroke, fill, dash, close))

    def line(self, x1, y1, x2, y2, stroke=1.2, dash=None):
        self.path([('M', x1, y1), ('L', x2, y2)], stroke, None, dash)

    def polyline(self, points, stroke=1.2, dash=None):
        self.path([('M', *points[0])] + [('L', x, y) for x, y in points[1:]], stroke, None, dash)

    def polygon(self, points, stroke=1.2, fill=None, dash=None):
        segs = [('M', *points[0])] + [('L', x, y) for x, y in points[1:]]
        self.path(segs, stroke, fill, dash, close=True)

    def rect(self, x, y, w, h, stroke=1.2, fill=None, radius=0, dash=None):
        if not radius:
            return self.polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], stroke, fill, dash)
        r, k = radius, radius * K
        segs = [('M', x + r, y), ('L', x + w - r, y), ('C', x + w - r + k, y, x + w, y + r - k, x + w, y + r),
                ('L', x + w, y + h - r), ('C', x + w, y + h - r + k, x + w - r + k, y + h, x + w - r, y + h),
                ('L', x + r, y + h), ('C', x + r - k, y + h, x, y + h - r + k, x, y + h - r),
                ('L', x, y + r), ('C', x, y + r - k, x + r - k, y, x + r, y)]
        self.path(segs, stroke, fill, dash, close=True)

    @staticmethod
    def ellipse_segments(cx, cy, rx, ry, angle=0):
        a = math.radians(angle); ca, sa = math.cos(a), math.sin(a)
        t = lambda x, y: (cx + x * ca - y * sa, cy + x * sa + y * ca)
        quads = (((rx, ry * K), (rx * K, ry), (0, ry)), ((-rx * K, ry), (-rx, ry * K), (-rx, 0)),
                 ((-rx, -ry * K), (-rx * K, -ry), (0, -ry)), ((rx * K, -ry), (rx, -ry * K), (rx, 0)))
        segs = [('M', *t(rx, 0))]
        for p1, p2, p3 in quads:
            segs.append(('C', *t(*p1), *t(*p2), *t(*p3)))
        return segs

    def ellipse(self, cx, cy, rx, ry, stroke=1.2, fill=None, angle=0, dash=None):
        self.path(self.ellipse_segments(cx, cy, rx, ry, angle), stroke, fill, dash, close=True)

    def circle(self, cx, cy, r, stroke=1.2, fill=None, dash=None):
        self.ellipse(cx, cy, r, r, stroke, fill, 0, dash)

    def arc(self, cx, cy, r, start, end, stroke=1.2, dash=None, fill=None, close=False):
        """Circular arc from angle start to end (degrees, clockwise on screen)."""
        self.path(self.arc_segments(cx, cy, r, start, end), stroke, fill, dash, close)

    @staticmethod
    def arc_segments(cx, cy, r, start, end):
        segs = []
        steps = max(1, int(abs(end - start) / 90) + 1)
        step = (end - start) / steps
        for i in range(steps):
            a0, a1 = math.radians(start + i * step), math.radians(start + (i + 1) * step)
            k = 4 / 3 * math.tan((a1 - a0) / 4)
            p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
            p3 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
            p1 = (p0[0] - k * r * math.sin(a0), p0[1] + k * r * math.cos(a0))
            p2 = (p3[0] + k * r * math.sin(a1), p3[1] - k * r * math.cos(a1))
            if not segs: segs.append(('M', *p0))
            segs.append(('C', *p1, *p2, *p3))
        return segs

    def curve(self, points, stroke=1.2, dash=None, close=False, fill=None, tension=0.3):
        """Smooth curve (Catmull-Rom as Béziers) through the points."""
        self.path(self.curve_segments(points, close, tension), stroke, fill, dash, close)

    @staticmethod
    def curve_segments(points, close=False, tension=0.3):
        pts = list(points)
        if close: pts = [pts[-1]] + pts + [pts[0], pts[1]]
        else: pts = [pts[0]] + pts + [pts[-1]]
        segs = [('M', *pts[1])]
        for i in range(1, len(pts) - 2):
            p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
            c1 = (p1[0] + (p2[0] - p0[0]) * tension, p1[1] + (p2[1] - p0[1]) * tension)
            c2 = (p2[0] - (p3[0] - p1[0]) * tension, p2[1] - (p3[1] - p1[1]) * tension)
            segs.append(('C', *c1, *c2, *p2))
        return segs

    def text(self, x, y, s, size=12, italic=False, anchor='start', rotate=0, bold=False, color='black'):
        if self.transforms:
            x, y = self._t(x, y); rotate += sum(t[0] for t in self.transforms)
        self.ops.append(('text', x, y, str(s), size, italic, anchor, rotate, bold, color))

    def arrow(self, x1, y1, x2, y2, head=7, stroke=1.2, gap=0, both=False):
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
        x1, y1 = x1 + ux * gap, y1 + uy * gap
        x2, y2 = x2 - ux * gap, y2 - uy * gap
        self.line(x1 + (ux * head * 0.8 if both else 0), y1 + (uy * head * 0.8 if both else 0), x2 - ux * head * 0.8, y2 - uy * head * 0.8, stroke)
        px, py = -uy, ux
        self.polygon([(x2, y2), (x2 - ux * head + px * head * 0.45, y2 - uy * head + py * head * 0.45),
                      (x2 - ux * head - px * head * 0.45, y2 - uy * head - py * head * 0.45)], 0, 'black')
        if both:
            self.polygon([(x1, y1), (x1 + ux * head + px * head * 0.45, y1 + uy * head + py * head * 0.45),
                          (x1 + ux * head - px * head * 0.45, y1 + uy * head - py * head * 0.45)], 0, 'black')

    def hatch(self, clip_segments, spacing=5, angle=45, stroke=0.7):
        """Parallel lines clipped to the closed path given by clip_segments."""
        xs = [v for seg in clip_segments for v in seg[1::2]]
        ys = [v for seg in clip_segments for v in seg[2::2]]
        x0, x1, y0, y1 = min(xs) - 2, max(xs) + 2, min(ys) - 2, max(ys) + 2
        a = math.radians(angle); dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        diag = math.hypot(x1 - x0, y1 - y0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        lines = []
        n = int(diag / spacing) + 1
        for i in range(-n, n + 1):
            ox, oy = cx + nx * i * spacing, cy + ny * i * spacing
            lines.append(((ox - dx * diag, oy - dy * diag), (ox + dx * diag, oy + dy * diag)))
        if self.transforms:
            clip_segments = self._tsegs(clip_segments); lines = [(self._t(*a), self._t(*b)) for a, b in lines]
        self.ops.append(('hatch', clip_segments, lines, stroke))

    def heart(self, cx, cy, s, fill='black'):
        """A playing-card heart of width s centred on (cx, cy)."""
        u = s / 2
        segs = [('M', cx, cy + u * 0.95),
                ('C', cx - u * 0.9, cy + u * 0.2, cx - u * 1.05, cy - u * 0.35, cx - u * 0.55, cy - u * 0.75),
                ('C', cx - u * 0.25, cy - u * 0.95, cx, cy - u * 0.65, cx, cy - u * 0.45),
                ('C', cx, cy - u * 0.65, cx + u * 0.25, cy - u * 0.95, cx + u * 0.55, cy - u * 0.75),
                ('C', cx + u * 1.05, cy - u * 0.35, cx + u * 0.9, cy + u * 0.2, cx, cy + u * 0.95)]
        self.path(segs, 0, fill, None, close=True)

    # ---- output --------------------------------------------------------------
    @staticmethod
    def _d(segs, close):
        return ' '.join(seg[0] + ' ' + ' '.join(f'{v:.2f}' for v in seg[1:]) for seg in segs) + (' Z' if close else '')

    def svg(self):
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}pt" height="{self.h}pt" role="img" aria-label="{self.label}">',
               f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="white"/>']
        clips = 0
        for op in self.ops:
            if op[0] == 'path':
                _, segs, stroke, fill, dash, close = op
                attrs = f'fill="{COLORS_SVG.get(fill, fill)}"' if fill else 'fill="none"'
                if stroke:
                    attrs += f' stroke="black" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"'
                if dash:
                    attrs += f' stroke-dasharray="{dash[0]} {dash[1]}"'
                out.append(f'<path d="{self._d(segs, close)}" {attrs}/>')
            elif op[0] == 'hatch':
                _, clip, lines, stroke = op
                clips += 1
                out.append(f'<clipPath id="c{clips}"><path d="{self._d(clip, True)}"/></clipPath>')
                out.append(f'<g clip-path="url(#c{clips})" stroke="black" stroke-width="{stroke}">' +
                           ''.join(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>' for a, b in lines) + '</g>')
            else:
                _, x, y, s, size, italic, anchor, rotate, bold, color = op
                attrs = f'x="{x:.2f}" y="{y:.2f}" font-family="Times,serif" font-size="{size}" fill="{COLORS_SVG.get(color, color)}"'
                if italic: attrs += ' font-style="italic"'
                if bold: attrs += ' font-weight="bold"'
                if anchor != 'start': attrs += f' text-anchor="{anchor}"'
                if rotate: attrs += f' transform="rotate({rotate} {x:.2f} {y:.2f})"'
                out.append(f'<text {attrs}>{s.replace("&", "&amp;").replace("<", "&lt;")}</text>')
        out.append('</svg>')
        return '\n'.join(out) + '\n'

    def pdf(self):
        Y = lambda y: self.h - y

        def path_ops(segs, close):
            parts = []
            for seg in segs:
                if seg[0] == 'M': parts.append(f'{seg[1]:.2f} {Y(seg[2]):.2f} m')
                elif seg[0] == 'L': parts.append(f'{seg[1]:.2f} {Y(seg[2]):.2f} l')
                else: parts.append(f'{seg[1]:.2f} {Y(seg[2]):.2f} {seg[3]:.2f} {Y(seg[4]):.2f} {seg[5]:.2f} {Y(seg[6]):.2f} c')
            if close: parts.append('h')
            return ' '.join(parts)
        cs = ['0 g 0 G 1 J 1 j']
        for op in self.ops:
            if op[0] == 'path':
                _, segs, stroke, fill, dash, close = op
                paint = ('B' if stroke else 'f') if fill else ('S' if stroke else 'n')
                setup = (f'{COLORS_PDF[fill]} ' if fill else '') + (f'{stroke} w ' if stroke else '') + (f'[{dash[0]} {dash[1]}] 0 d ' if dash else '[] 0 d ')
                cs.append('q ' + setup + path_ops(segs, close) + f' {paint} Q')
            elif op[0] == 'hatch':
                _, clip, lines, stroke = op
                cs.append(f'q {path_ops(clip, True)} W n {stroke} w [] 0 d ' +
                          ' '.join(f'{a[0]:.1f} {Y(a[1]):.1f} m {b[0]:.1f} {Y(b[1]):.1f} l S' for a, b in lines) + ' Q')
            else:
                _, x, y, s, size, italic, anchor, rotate, bold, color = op
                width = sum(0.5 if ch.isdigit() or ch == ' ' else 0.62 for ch in s) * size
                if anchor == 'middle': x -= width / 2
                elif anchor == 'end': x -= width
                font = 'F3' if bold else ('F2' if italic else 'F1')
                escaped = s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
                if rotate == 180:
                    cs.append(f'q {COLORS_PDF[color]} BT /{font} {size} Tf -1 0 0 -1 {x + width:.2f} {Y(y) + size * 0.7:.2f} Tm ({escaped}) Tj ET Q')
                elif rotate:
                    a = math.radians(-rotate); ca, sa = math.cos(a), math.sin(a)
                    cs.append(f'q {COLORS_PDF[color]} BT /{font} {size} Tf {ca:.4f} {sa:.4f} {-sa:.4f} {ca:.4f} {x:.2f} {Y(y):.2f} Tm ({escaped}) Tj ET Q')
                else:
                    cs.append(f'q {COLORS_PDF[color]} BT /{font} {size} Tf {x:.2f} {Y(y):.2f} Td ({escaped}) Tj ET Q')
        stream = '\n'.join(cs).encode('latin-1', 'replace')
        objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
                   f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.w} {self.h}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R /F3 7 0 R >> >> >>'.encode(),
                   b'<< /Length ' + str(len(stream)).encode() + b' >>\nstream\n' + stream + b'\nendstream',
                   b'<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman /Encoding /WinAnsiEncoding >>',
                   b'<< /Type /Font /Subtype /Type1 /BaseFont /Times-Italic /Encoding /WinAnsiEncoding >>',
                   b'<< /Type /Font /Subtype /Type1 /BaseFont /Times-Bold /Encoding /WinAnsiEncoding >>']
        pdf = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'); offsets = []
        for i, obj in enumerate(objects, 1):
            offsets.append(len(pdf)); pdf += f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n'
        xref = len(pdf)
        pdf += f'xref\n0 {len(objects) + 1}\n0000000000 65535 f \n'.encode() + b''.join(f'{o:010d} 00000 n \n'.encode() for o in offsets)
        pdf += f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
        return bytes(pdf)


def _text_box(op):
    _, x, y, s, size, italic, anchor, rotate, bold, color = op
    w = sum(0.5 if ch.isdigit() or ch == ' ' else 0.62 for ch in s) * size
    x0 = x if anchor == 'start' else x - w / 2 if anchor == 'middle' else x - w
    if rotate % 180 == 90:
        return x - size, y - w, x + size * 0.3, y + w
    return x0, y - size * 0.75, x0 + w, y + size * 0.25


def fit(canvas, margin=8):
    """Shrink or grow the canvas to its content plus a margin, translating everything."""
    xs, ys = [], []
    for op in canvas.ops:
        if op[0] in ('path', 'hatch'):
            half = (op[2] or 0) / 2 if op[0] == 'path' else 0
            for seg in op[1]:
                for i in range(1, len(seg), 2):
                    xs += [seg[i] - half, seg[i] + half]; ys += [seg[i + 1] - half, seg[i + 1] + half]
        else:
            x0, y0, x1, y1 = _text_box(op); xs += [x0, x1]; ys += [y0, y1]
    if not xs: return
    dx, dy = margin - min(xs), margin - min(ys)
    moved = []
    for op in canvas.ops:
        if op[0] == 'path':
            moved.append(('path', _shift(op[1], dx, dy)) + op[2:])
        elif op[0] == 'hatch':
            moved.append(('hatch', _shift(op[1], dx, dy), [((a[0] + dx, a[1] + dy), (b[0] + dx, b[1] + dy)) for a, b in op[2]], op[3]))
        else:
            moved.append(('text', op[1] + dx, op[2] + dy) + op[3:])
    canvas.ops = moved
    canvas.w = round(max(xs) - min(xs) + 2 * margin, 1); canvas.h = round(max(ys) - min(ys) + 2 * margin, 1)


def _shift(segs, dx, dy):
    return [(seg[0],) + tuple(v + (dx if i % 2 == 0 else dy) for i, v in enumerate(seg[1:])) for seg in segs]


# ---- helpers shared by the drawing modules -------------------------------------
OFFSETS = {'n': (0, -5), 's': (0, 13), 'e': (5, 4), 'w': (-5, 4), 'ne': (4, -4), 'nw': (-4, -4), 'se': (4, 12), 'sw': (-4, 12), 'c': (0, 4)}
ANCHORS = {'n': 'middle', 's': 'middle', 'e': 'start', 'w': 'end', 'ne': 'start', 'nw': 'end', 'se': 'start', 'sw': 'end', 'c': 'middle'}


def label(c, x, y, s, where='n', size=11, italic=True, bold=False):
    """Place a label beside a point: where is a compass direction."""
    dx, dy = OFFSETS[where]
    c.text(x + dx, y + dy, s, size, italic, ANCHORS[where], 0, bold)


def labels(c, points, where=None, size=11, italic=True):
    """points: name -> (x, y); where: name -> compass direction (default north)."""
    for name, (x, y) in points.items():
        label(c, x, y, name, (where or {}).get(name, 'n'), size, italic)


def dot(c, x, y, r=2):
    c.circle(x, y, r, 0, 'black')


def dots(c, points, r=2):
    for x, y in (points.values() if isinstance(points, dict) else points):
        dot(c, x, y, r)


def segment(c, p, q, stroke=1.2, dash=None):
    c.line(p[0], p[1], q[0], q[1], stroke, dash)


def segments(c, points, pairs, stroke=1.2, dash=None):
    """pairs like 'AB BC' between named points."""
    for pair in pairs.split():
        segment(c, points[pair[0]], points[pair[1]], stroke, dash)


def unit(p, q):
    n = math.hypot(q[0] - p[0], q[1] - p[1]) or 1
    return (q[0] - p[0]) / n, (q[1] - p[1]) / n


def right_angle(c, corner, a, b, size=6):
    """Small square mark at corner between the directions of a and b."""
    ux, uy = unit(corner, a); vx, vy = unit(corner, b)
    p1 = (corner[0] + ux * size, corner[1] + uy * size)
    p2 = (corner[0] + (ux + vx) * size, corner[1] + (uy + vy) * size)
    p3 = (corner[0] + vx * size, corner[1] + vy * size)
    c.polyline([p1, p2, p3], 0.8)


def tick(c, p, q, n=1, size=4, stroke=1):
    """n short marks across the middle of segment pq (equal-length marks)."""
    ux, uy = unit(p, q); mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    for i in range(n):
        o = (i - (n - 1) / 2) * 3
        cx, cy = mx + ux * o, my + uy * o
        c.line(cx - uy * size, cy + ux * size, cx + uy * size, cy - ux * size, stroke)


def midpoint(p, q, t=0.5):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def grid(c, x, y, cols, rows, cell, stroke=1.0, fill=None):
    if fill: c.rect(x, y, cols * cell, rows * cell, 0, fill)
    for i in range(cols + 1): c.line(x + i * cell, y, x + i * cell, y + rows * cell, stroke)
    for j in range(rows + 1): c.line(x, y + j * cell, x + cols * cell, y + j * cell, stroke)


def number_grid(c, x, y, cell, rows, size=None, stroke=1.0, italic=False, shade=None):
    """rows: list of lists; None leaves a cell empty, '' draws no cell at all."""
    size = size or cell * 0.5
    for j, row in enumerate(rows):
        for i, v in enumerate(row):
            if v == '': continue
            fill = shade(i, j, v) if shade else None
            c.rect(x + i * cell, y + j * cell, cell, cell, stroke, fill)
            if v is not None:
                c.text(x + i * cell + cell / 2, y + j * cell + cell / 2 + size * 0.35, v, size, italic, 'middle')


def matchstick(c, x1, y1, x2, y2, stroke=2.2, head=2.6):
    c.line(x1, y1, x2, y2, stroke)
    c.circle(x2, y2, head, 0, 'black')


def match_grid(c, x, y, cols, rows, cell, gap=2):
    """A grid of unit squares built from matchsticks."""
    for j in range(rows + 1):
        for i in range(cols):
            matchstick(c, x + i * cell + gap, y + j * cell, x + (i + 1) * cell - gap, y + j * cell)
    for i in range(cols + 1):
        for j in range(rows):
            matchstick(c, x + i * cell, y + j * cell + gap, x + i * cell, y + (j + 1) * cell - gap)


def coin(c, x, y, r=12, text=None):
    c.circle(x, y, r, 1.1)
    c.circle(x, y, r * 0.78, 0.6)
    if text is not None: c.text(x, y + r * 0.3, text, r * 0.8, False, 'middle')


def chessboard(c, x, y, cell=18, n=8, dark='gray', light_first=True):
    for j in range(n):
        for i in range(n):
            dark_cell = ((i + j) % 2 == 1) if light_first else ((i + j) % 2 == 0)
            c.rect(x + i * cell, y + j * cell, cell, cell, 0.5, dark if dark_cell else 'white')
    c.rect(x, y, n * cell, n * cell, 1.2)


def chess_piece(c, x, y, letter, black=False, r=6.5):
    """Schematic piece: a circle with the piece letter; black pieces are filled."""
    c.circle(x, y, r, 0.9, 'black' if black else 'white')
    if black:
        c.circle(x, y, r - 1.6, 0.8, 'white')
    c.text(x, y + r * 0.45, letter, r * 1.25, False, 'middle', 0, True)


def iso(ox, oy, s, angle=30):
    """Isometric projector: i right-forward, j left-forward, k up."""
    ux, uy = math.cos(math.radians(angle)) * s, math.sin(math.radians(angle)) * s
    return lambda i, j, k: (ox + (i - j) * ux, oy - (i + j) * uy - k * s)


def cabinet(ox, oy, s, depth=0.5, angle=45):
    """Cabinet projector: i right, j back (receding), k up; origin at bottom-left front."""
    dx, dy = depth * s * math.cos(math.radians(angle)), -depth * s * math.sin(math.radians(angle))
    return lambda i, j, k: (ox + i * s + j * dx, oy - k * s + j * dy)


def box(c, P, ni, nj, nk, stroke=1.2, fills=('white', 'light', 'gray'), subdivide=False, dash=None):
    """Draw a box with projector P and optional unit grid lines on the three visible faces.

    With a cabinet projector the visible side faces are j=0 (front) and i=ni (right);
    with an isometric projector they are j=nj (left front) and i=ni (right front).
    """
    front = 0 if P(0, 0, 0)[1] >= P(0, 1, 0)[1] else nj   # cabinet: j recedes upward
    c.polygon([P(0, 0, nk), P(ni, 0, nk), P(ni, nj, nk), P(0, nj, nk)], stroke, fills[1])
    c.polygon([P(ni, 0, 0), P(ni, nj, 0), P(ni, nj, nk), P(ni, 0, nk)], stroke, fills[2])
    c.polygon([P(0, front, 0), P(ni, front, 0), P(ni, front, nk), P(0, front, nk)], stroke, fills[0])
    if subdivide:
        for t in range(1, ni):
            c.line(*P(t, front, 0), *P(t, front, nk), 0.7, dash); c.line(*P(t, 0, nk), *P(t, nj, nk), 0.7, dash)
        for t in range(1, nk):
            c.line(*P(0, front, t), *P(ni, front, t), 0.7, dash); c.line(*P(ni, 0, t), *P(ni, nj, t), 0.7, dash)
        for t in range(1, nj):
            c.line(*P(ni, t, 0), *P(ni, t, nk), 0.7, dash); c.line(*P(0, t, nk), *P(ni, t, nk), 0.7, dash)


def subscript(c, x, y, base, index, size=11, italic=True):
    c.text(x, y, base, size, italic); c.text(x + size * 0.62, y + size * 0.25, index, size * 0.65, italic)


def fraction(c, x, y, num, den, size=9, whole=''):
    """A stacked fraction centred at x with its bar at y; whole part to the left."""
    w = max(len(str(num)), len(str(den))) * size * 0.55
    if whole: c.text(x - w / 2 - 2, y + size * 0.4, whole, size * 1.3, anchor='end')
    c.text(x, y - 2, num, size, anchor='middle'); c.text(x, y + size * 0.95, den, size, anchor='middle'); c.line(x - w / 2, y, x + w / 2, y, 0.6)


def lens_segments(c1, r1, c2, r2):
    """Path around the intersection of two circles."""
    d = math.hypot(c2[0] - c1[0], c2[1] - c1[1])
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d); h = math.sqrt(max(r1 * r1 - a * a, 0))
    mx, my = c1[0] + a * (c2[0] - c1[0]) / d, c1[1] + a * (c2[1] - c1[1]) / d
    p = (mx + h * (c2[1] - c1[1]) / d, my - h * (c2[0] - c1[0]) / d)
    q = (mx - h * (c2[1] - c1[1]) / d, my + h * (c2[0] - c1[0]) / d)
    ap, aq = math.degrees(math.atan2(p[1] - c1[1], p[0] - c1[0])), math.degrees(math.atan2(q[1] - c1[1], q[0] - c1[0]))
    bq, bp = math.degrees(math.atan2(q[1] - c2[1], q[0] - c2[0])), math.degrees(math.atan2(p[1] - c2[1], p[0] - c2[0]))
    if (aq - ap) % 360 > 180: ap += 360
    if (bp - bq) % 360 > 180: bq += 360
    return Canvas.arc_segments(*c1, r1, ap, aq) + Canvas.arc_segments(*c2, r2, bq, bp)[1:]


def half_plane(a, b, left, w, h):
    """The part of the rectangle (0,0,w,h) on one side of line ab, as path segments."""
    poly = [(0, 0), (w, 0), (w, h), (0, h)]
    def inside(p): return ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0) == left
    def cross(p, q):
        d1 = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]); d2 = (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])
        t = d1 / (d1 - d2); return (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % 4]
        if inside(p): out.append(p)
        if inside(p) != inside(q): out.append(cross(p, q))
    return [('M', *out[0])] + [('L', *pt) for pt in out[1:]]


def delaunay(points):
    """Bowyer-Watson triangulation; returns index triples."""
    pts = list(points)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    big = max(max(xs) - min(xs), max(ys) - min(ys)) * 20
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    pts += [(cx - big, cy - big), (cx + big, cy - big), (cx, cy + big)]
    n = len(points)
    tris = [(n, n + 1, n + 2)]
    def circum(t):
        (ax, ay), (bx, by), (cx_, cy_) = pts[t[0]], pts[t[1]], pts[t[2]]
        d = 2 * (ax * (by - cy_) + bx * (cy_ - ay) + cx_ * (ay - by)) or 1e-9
        ux = ((ax * ax + ay * ay) * (by - cy_) + (bx * bx + by * by) * (cy_ - ay) + (cx_ * cx_ + cy_ * cy_) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx_ - bx) + (bx * bx + by * by) * (ax - cx_) + (cx_ * cx_ + cy_ * cy_) * (bx - ax)) / d
        return ux, uy, math.hypot(ax - ux, ay - uy)
    for i in range(n):
        bad = [t for t in tris if math.hypot(pts[i][0] - circum(t)[0], pts[i][1] - circum(t)[1]) < circum(t)[2]]
        edges = {}
        for t in bad:
            for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                key = tuple(sorted(e)); edges[key] = edges.get(key, 0) + 1
        tris = [t for t in tris if t not in bad] + [(e[0], e[1], i) for e, k in edges.items() if k == 1]
    return [t for t in tris if max(t) < n]


def regular_polygon(cx, cy, r, n, start=-90):
    return [(cx + r * math.cos(math.radians(start + 360 * i / n)), cy + r * math.sin(math.radians(start + 360 * i / n))) for i in range(n)]


def star(c, cx, cy, r, n=5, stroke=1.2):
    pts = regular_polygon(cx, cy, r, n)
    step = n // 2
    for i in range(n):
        segment(c, pts[i], pts[(i + step) % n], stroke)


# ---- registry ----------------------------------------------------------------
REGISTRY = {}


def figure(figure_id, width, height, label, page=None, fit=True):
    """width/height are the drawing space; with fit (default) the output is cropped to the content."""
    def register(fn):
        REGISTRY[figure_id] = (width, height, label, fn, page, fit)
        return fn
    return register


__all__ = ['Canvas', 'figure', 'label', 'labels', 'dot', 'dots', 'segment', 'segments', 'right_angle', 'unit', 'tick', 'midpoint',
           'grid', 'number_grid', 'matchstick', 'match_grid', 'coin', 'chessboard', 'chess_piece', 'iso', 'cabinet', 'box',
           'regular_polygon', 'star', 'math', 'subscript', 'fraction', 'lens_segments', 'half_plane', 'delaunay']


def load_modules(book=None):
    for module in sorted(MODULES.glob('*.py')):
        if book and module.stem != book: continue
        spec = importlib.util.spec_from_file_location('figures_' + module.stem, module)
        mod = importlib.util.module_from_spec(spec)
        mod.__dict__.update({name: globals()[name] for name in __all__})
        spec.loader.exec_module(mod)


def main(args):
    book = None
    if args[:1] == ['--book']:
        book, args = args[1], args[2:]
    load_modules(book)
    manifest = json.loads(MANIFEST.read_text())
    by_id = {f['id']: f for f in manifest['figures']}
    ids = args or [i for i in REGISTRY if not book or i.startswith(book + '-')]
    for figure_id in ids:
        if figure_id not in REGISTRY:
            raise SystemExit(f'No redrawing function for {figure_id}.')
        width, height, text, draw, page, do_fit = REGISTRY[figure_id]
        source = figure_id.split('-p')[0]
        if figure_id not in by_id:
            if not page:
                raise SystemExit(f'{figure_id} is not in the figure manifest; give page= or trace its page first.')
            sibling = next((f for f in manifest['figures'] if f['source'] == source), None)
            if not sibling:
                raise SystemExit(f'No traced figure of {source} to copy the source details from.')
            index = max([f['index'] for f in manifest['figures'] if f['source'] == source and f['page'] == page] + [0]) + 1
            by_id[figure_id] = {'id': figure_id, 'source': source, 'sourceId': sibling['sourceId'], 'sourceTitle': sibling['sourceTitle'],
                                'page': page, 'index': index, 'dir': sibling['dir'], 'pdf': '', 'svg': '', 'width': 0, 'height': 0,
                                'bytes': {}, 'warnings': ['redrawn-only']}
            manifest['figures'].append(by_id[figure_id])
        canvas = Canvas(width, height, text)
        draw(canvas)
        if do_fit: fit(canvas)
        width, height = canvas.w, canvas.h
        entry = by_id[figure_id]
        out_dir = FIGURES / f'{source}-redrawn'
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f'{figure_id}.svg').write_text(canvas.svg())
        (out_dir / f'{figure_id}.pdf').write_bytes(canvas.pdf())
        entry['redrawn'] = {'dir': out_dir.name, 'pdf': f'{figure_id}.pdf', 'svg': f'{figure_id}.svg', 'width': width, 'height': height}
    manifest['figures'].sort(key=lambda f: (f['source'], f['page'], f['index']))
    manifest['count'] = len(manifest['figures'])
    MANIFEST.write_text(json.dumps(manifest, indent=1) + '\n')
    print(f'{len(ids)} drawn; {sum(1 for f in manifest["figures"] if f.get("redrawn"))} redrawn figure(s) in the manifest')


if __name__ == '__main__':
    main(sys.argv[1:])
