"""The Moscow Puzzles: redrawn figures.

Illustrations (people, animals, scenery, objects drawn for decoration) are not redrawn;
only diagrams that carry the mathematics of a problem are.
"""


def star_polygon(c, cx, cy, r, n, step, stroke=1.2, start=-90):
    pts = regular_polygon(cx, cy, r, n, start)
    for i in range(n): segment(c, pts[i], pts[(i + step) % n], stroke)
    return pts


def circle_grid(c, x0, y0, cols, rows, d, r, fill=None, numbers=None, size=8):
    k = 0
    for j in range(rows):
        for i in range(cols):
            cx, cy = x0 + i * d, y0 + j * d
            c.circle(cx, cy, r, 1.1, fill)
            if numbers: c.text(cx, cy + size * 0.35, numbers[k], size, anchor='middle', color='white' if fill == 'black' else 'black'); k += 1


def match_square(c, x, y, n, cell, inner=0):
    """A square of n matches per side; inner > 0 adds a centred small square of inner matches per side."""
    match_grid_outline(c, x, y, n, cell)
    if inner:
        off = (n - inner) * cell / 2
        match_grid_outline(c, x + off, y + off, inner, cell)


def match_grid_outline(c, x, y, n, cell, gap=2):
    for k in range(n):
        matchstick(c, x + k * cell + gap, y, x + (k + 1) * cell - gap, y); matchstick(c, x + (k + 1) * cell - gap, y + n * cell, x + k * cell + gap, y + n * cell)
        matchstick(c, x, y + (k + 1) * cell - gap, x, y + k * cell + gap); matchstick(c, x + n * cell, y + k * cell + gap, x + n * cell, y + (k + 1) * cell - gap)


def pips(c, x, y, s, n, r=None):
    """Pips of a die face n drawn in the square (x, y, s, s)."""
    r = r or s * 0.09
    pos = {1: [(.5, .5)], 2: [(.25, .25), (.75, .75)], 3: [(.25, .25), (.5, .5), (.75, .75)], 4: [(.25, .25), (.75, .25), (.25, .75), (.75, .75)],
           5: [(.25, .25), (.75, .25), (.5, .5), (.25, .75), (.75, .75)], 6: [(.25, .2), (.75, .2), (.25, .5), (.75, .5), (.25, .8), (.75, .8)]}[n]
    for px, py in pos: dot(c, x + px * s, y + py * s, r)


def die(c, x, y, s, front, right, top):
    P = cabinet(x, y + s, s, 0.45, 40)
    c.polygon([P(0, 0, 1), P(1, 0, 1), P(1, 1, 1), P(0, 1, 1)], 1.1, 'white'); c.polygon([P(1, 0, 0), P(1, 1, 0), P(1, 1, 1), P(1, 0, 1)], 1.1, 'light'); c.rect(x, y, s, s, 1.1, 'white')
    pips(c, x, y, s, front)
    with c.scaled(1, 1, 0, 0):
        pass
    # right face pips, sheared
    for px, py in [(p[0] * s, p[1] * s) for p in {1: [(.5, .5)], 2: [(.25, .25), (.75, .75)], 3: [(.25, .25), (.5, .5), (.75, .75)], 4: [(.25, .25), (.75, .25), (.25, .75), (.75, .75)], 5: [(.25, .25), (.75, .25), (.5, .5), (.25, .75), (.75, .75)], 6: [(.25, .2), (.75, .2), (.25, .5), (.75, .5), (.25, .8), (.75, .8)]}[right]]:
        q = P(1, px / s, 1 - py / s); c.ellipse(q[0], q[1], s * 0.05, s * 0.08, 0, 'black')
    for px, py in [(p[0] * s, p[1] * s) for p in {1: [(.5, .5)], 2: [(.25, .25), (.75, .75)], 3: [(.25, .25), (.5, .5), (.75, .75)], 4: [(.25, .25), (.75, .25), (.25, .75), (.75, .75)], 5: [(.25, .25), (.75, .25), (.5, .5), (.25, .75), (.75, .75)], 6: [(.25, .2), (.75, .2), (.25, .5), (.75, .5), (.25, .8), (.75, .8)]}[top]]:
        q = P(px / s, 1 - py / s, 1); c.ellipse(q[0], q[1], s * 0.08, s * 0.045, 0, 'black')


def polyhedron(c, cx, cy, size, kind, ax=22, ay=-30):
    phi = (1 + 5 ** 0.5) / 2
    if kind == 'tetra': V = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    elif kind == 'octa': V = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    elif kind == 'icosa': V = [p for s1 in (1, -1) for s2 in (1, -1) for p in ((0, s1, s2 * phi), (s1, s2 * phi, 0), (s2 * phi, 0, s1))]
    else:
        V = [(a, b, d) for a in (1, -1) for b in (1, -1) for d in (1, -1)]
        V += [p for s1 in (1, -1) for s2 in (1, -1) for p in ((0, s1 / phi, s2 * phi), (s1 / phi, s2 * phi, 0), (s2 * phi, 0, s1 / phi))]
    dmin = min(math.dist(V[i], V[j]) for i in range(len(V)) for j in range(i + 1, len(V)))
    edges = [(i, j) for i in range(len(V)) for j in range(i + 1, len(V)) if abs(math.dist(V[i], V[j]) - dmin) < 1e-6]
    rx, ry = math.radians(ax), math.radians(ay)
    def proj(p):
        x, y, z = p
        y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
        x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
        return (cx + x * size, cy - y * size, z)
    pts = [proj(p) for p in V]
    scale = max(max(abs(p[0] - cx), abs(p[1] - cy)) for p in pts) / size
    for i, j in edges:
        mid_z = (pts[i][2] + pts[j][2]) / 2
        c.line(pts[i][0], pts[i][1], pts[j][0], pts[j][1], 1.2 if mid_z > -0.15 * scale else 0.9, None if mid_z > -0.15 * scale else (3, 2))


# ---- sheet 1 ---------------------------------------------------------------

@figure('moscow-p12-2', 120, 115, 'A regular pentagon with all five diagonals drawn, forming a pentagram inside')
def pentagon_diagonals(c):
    c.polygon(regular_polygon(60, 60, 50, 5), 1.4); star(c, 60, 60, 50, 5, 1.2)


@figure('moscow-p15-1', 270, 50, 'A long slotted bar holding seven counters, four black on the left and three white on the right, with an arrow above and a notch in the middle')
def sliding_bar(c):
    c.rect(10, 18, 250, 20, 1.3, radius=3); c.line(30, 18, 30, 38, 1); c.line(240, 18, 240, 38, 1)
    c.arc(135, 18, 7, 180, 360, 1.3)
    for k in range(4): dot(c, 68 + k * 18, 28, 5)
    for k in range(3): c.circle(160 + k * 18, 28, 5, 1.2, 'white')
    c.arrow(70, 8, 125, 8, 4, 0.9)


@figure('moscow-p16-1', 260, 75, 'Five pieces of chain, each of three interlocked links, numbered 1 to 15')
def chain_pieces(c):
    n = 1
    for row, xs in ((0, (12, 95, 178)), (1, (55, 140))):
        for x0 in xs:
            for k in range(3):
                cx, cy = x0 + 14 + k * 20, 16 + row * 34
                c.ellipse(cx, cy, 13, 7, 1.3, 'white'); c.ellipse(cx, cy, 8, 3.5, 1, 'white')
                c.text(cx, cy + 17, n, 6, True, 'middle'); n += 1


@figure('moscow-p16-2', 290, 75, 'The Roman equation VI minus IV equals IX laid out with matches')
def roman_matches(c):
    def V(x): matchstick(c, x, 15, x + 14, 58); matchstick(c, x + 28, 15, x + 14, 58)
    def I(x): matchstick(c, x, 15, x, 58)
    def X(x): matchstick(c, x, 15, x + 26, 58); matchstick(c, x + 26, 15, x, 58)
    V(12); I(50); matchstick(c, 62, 37, 92, 37); I(104); V(118); matchstick(c, 158, 30, 188, 30); matchstick(c, 158, 44, 188, 44); I(204); X(222)


@figure('moscow-p18-1', 130, 130, 'A 4 by 4 array of coins')
def coin_square(c):
    circle_grid(c, 20, 20, 4, 4, 30, 12)
    for j in range(4):
        for i in range(4): c.circle(20 + i * 30, 20 + j * 30, 9, 0.6)


@figure('moscow-p18-2', 110, 90, 'A magic triangle: a triangle with its vertices numbered 1, 2 and 3', page=18)
def magic_triangle(c):
    pts = [(55, 10), (10, 80), (100, 80)]
    c.polygon(pts, 1.3)
    c.text(55, 6, '2', 9, True, 'middle'); c.text(4, 86, '1', 9, True); c.text(104, 86, '3', 9, True)


@figure('moscow-p19-1', 330, 240, 'Five diagrams (a) to (e) of twelve numbered points on a circle joined in different patterns: a twelve-pointed star, a plain ring, a star in a circle, four triangles and a twelve-pointed star')
def twelve_point_diagrams(c):
    def numbered(cx, cy, r):
        for k in range(12):
            a = math.radians(-90 + k * 30); c.text(cx + (r + 9) * math.cos(a), cy + (r + 9) * math.sin(a) + 3, 12 if k == 0 else k, 6, True, 'middle')
    for (cx, cy, lab, kind) in ((50, 60, '(a)', 'star5'), (160, 60, '(b)', 'ring'), (270, 60, '(c)', 'star5c'), (105, 170, '(d)', 'tri'), (215, 170, '(e)', 'star5')):
        r = 32
        if kind == 'ring': c.circle(cx, cy, r, 1); dots(c, regular_polygon(cx, cy, r, 12), 1.4)
        elif kind == 'tri':
            for s in range(4): c.polygon(regular_polygon(cx, cy, r, 3, -90 + s * 30), 1)
        else:
            if kind == 'star5c': c.circle(cx, cy, r, 0.8)
            star_polygon(c, cx, cy, r, 12, 5, 1)
        numbered(cx, cy, r); c.text(cx, cy + r + 24, lab, 7, True, 'middle')


@figure('moscow-p21-1', 120, 145, 'A pocket watch showing about twenty past nine, with a small seconds dial')
def pocket_watch(c):
    cx, cy, r = 60, 80, 50
    c.circle(cx, cy, r, 1.5); c.circle(cx, cy, r - 4, 0.7); c.rect(cx - 6, cy - r - 12, 12, 8, 1.1, radius=2); c.circle(cx, cy - r - 18, 6, 1.1)
    for k in range(12):
        a = math.radians(-90 + k * 30); c.text(cx + 36 * math.cos(a), cy + 36 * math.sin(a) + 3, 12 if k == 0 else k, 8, anchor='middle')
    c.circle(cx, cy + 22, 9, 0.8)
    c.line(cx, cy, cx - 28 * math.cos(math.radians(30)), cy - 28 * math.sin(math.radians(30)), 2.2)
    c.line(cx, cy, cx + 38 * math.cos(math.radians(-150 + 180)), cy + 38 * math.sin(math.radians(30)), 1.4)
    dot(c, cx, cy, 2.2)


@figure('moscow-p21-2', 150, 150, 'A clock face with Roman numerals I to XII, the numbers 13 to 24 inside, and the two hands near XII')
def roman_clock(c):
    cx, cy, r = 75, 75, 65
    c.circle(cx, cy, r, 1.6); c.circle(cx, cy, r - 5, 0.7)
    numerals = ['XII', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']
    for k in range(12):
        a = math.radians(-90 + k * 30)
        c.text(cx + 50 * math.cos(a), cy + 50 * math.sin(a) + 3, numerals[k], 7, anchor='middle')
        c.text(cx + 32 * math.cos(a), cy + 32 * math.sin(a) + 2, 24 if k == 0 else 12 + k, 5.5, True, 'middle')
    c.line(cx, cy, cx + 30 * math.cos(math.radians(-80)), cy + 30 * math.sin(math.radians(-80)), 2.2)
    c.line(cx, cy, cx + 44 * math.cos(math.radians(-95)), cy + 44 * math.sin(math.radians(-95)), 1.4); dot(c, cx, cy, 2)


@figure('moscow-p22-1', 200, 200, 'Nine coins in a 3 by 3 square; dashed lines A B, C D and E F pass through the top-left coin')
def nine_coins_lines(c):
    circle_grid(c, 60, 60, 3, 3, 45, 12)
    for j in range(3):
        for i in range(3): c.circle(60 + i * 45, 60 + j * 45, 8, 0.6)
    c.line(12, 60, 195, 60, 1, (4, 3)); c.text(6, 63, 'A', 8, True, 'end'); c.text(198, 63, 'B', 8, True)
    c.line(60, 8, 60, 195, 1, (4, 3)); c.text(60, 6, 'C', 8, True, 'middle'); c.text(60, 199, 'D', 8, True, 'middle')
    c.line(40, 20, 150, 185, 1, (4, 3)); c.text(36, 18, 'E', 8, True, 'end'); c.text(154, 190, 'F', 8, True)


@figure('moscow-p23-1', 200, 250, 'Sixteen squares arranged as an outer ring of twelve and an inner ring of four, joined by lines along the rings')
def square_rings(c):
    outer = [(20, 20), (100, 20), (180, 20), (180, 100), (180, 180), (180, 230), (100, 230), (20, 230), (20, 180), (20, 100)]
    outer = [(20, 20), (100, 20), (180, 20), (180, 125), (180, 230), (100, 230), (20, 230), (20, 125)]
    inner = [(70, 70), (130, 70), (130, 180), (70, 180), (100, 125)]
    inner = [(70, 75), (130, 75), (130, 175), (70, 175)]
    for k in range(8): segment(c, outer[k], outer[(k + 1) % 8], 1)
    for k in range(4): segment(c, inner[k], inner[(k + 1) % 4], 1)
    for k in range(4): segment(c, outer[k * 2], inner[k], 1)
    for p in outer: c.rect(p[0] - 11, p[1] - 11, 22, 22, 1.2, 'white')
    for p in inner: c.rect(p[0] - 10, p[1] - 10, 20, 20, 1.2, 'white')
    c.rect(90, 115, 20, 20, 1.2, 'white')


@figure('moscow-p24-1', 160, 160, 'A wheel of twenty coins round a rim, each joined by a spoke to a central coin')
def coin_wheel(c):
    cx, cy, R = 80, 80, 62
    for k in range(20):
        a = math.radians(k * 18); x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        c.line(cx, cy, x, y, 0.9); c.circle(x, y, 8, 1.1, 'white')
    c.circle(cx, cy, 8, 1.1, 'white')


# ---- sheet 2 ---------------------------------------------------------------

@figure('moscow-p26-1', 150, 170, 'Two bracketed columns of boxed digits: 1, 2, 7, 9 adding to 19 and 3, 4, 5, 8 adding to 20')
def boxed_sums(c):
    for x0, digits, total in ((25, (1, 2, 7, 9), '19'), (95, (3, 4, 5, 8), '20')):
        c.text(x0 - 14, 72, '+', 12)
        c.polyline([(x0 + 2, 12), (x0 - 3, 14), (x0 - 3, 70), (x0 - 7, 72), (x0 - 3, 74), (x0 - 3, 130), (x0 + 2, 132)], 0.9)
        for k, d in enumerate(digits):
            c.rect(x0 + 6, 10 + k * 30, 22, 22, 1.1); c.text(x0 + 17, 26 + k * 30, d, 10, anchor='middle')
        c.line(x0 - 6, 142, x0 + 40, 142, 1); c.text(x0 + 17, 154, total, 8, True, 'middle')


@figure('moscow-p29-1', 150, 150, 'A square field ABCD divided into sixteen plots in four rows; a dashed route winds round the plots')
def field_plots(c):
    c.rect(10, 10, 130, 130, 1.4)
    labels(c, {'A': (10, 140), 'B': (140, 140), 'C': (140, 10), 'D': (10, 10)}, {'A': 'sw', 'B': 'se', 'C': 'ne', 'D': 'nw'}, 8)
    for j in range(4):
        for i in range(4): c.rect(22 + i * 31, 22 + j * 31, 18, 18, 1, 'light')
    c.polyline([(16, 134), (16, 46), (52, 46), (52, 78), (83, 78), (83, 46), (118, 46), (118, 110), (62, 110), (62, 134), (134, 134)], 1, (3, 2))


@figure('moscow-p30-1', 160, 160, 'A circle cut into ten equal sectors by five diameters, numbered 1 to 10 round the edge; one diameter is drawn heavier')
def ten_sectors(c):
    cx, cy, r = 80, 80, 62
    c.circle(cx, cy, r, 1.3)
    for k in range(5):
        a = math.radians(k * 36 - 72); c.line(cx - r * math.cos(a), cy - r * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a), 2.2 if k == 0 else 1)
    for k in range(10):
        a = math.radians(-72 + k * 36); c.text(cx + (r + 9) * math.cos(a), cy + (r + 9) * math.sin(a) + 3, k + 1, 8, True, 'middle')


@figure('moscow-p31-1', 290, 140, 'The twelve pentominoes, each drawn as five hatched unit squares')
def pentominoes(c):
    shapes = {'F': [(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)], 'I': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)], 'L': [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)],
              'N': [(1, 0), (1, 1), (0, 2), (1, 2), (0, 3)], 'P': [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)], 'T': [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],
              'U': [(0, 0), (2, 0), (0, 1), (1, 1), (2, 1)], 'V': [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)], 'W': [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)],
              'X': [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)], 'Y': [(1, 0), (0, 1), (1, 1), (1, 2), (1, 3)], 'Z': [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)]}
    u = 9
    places = [(10, 10), (60, 10), (90, 10), (125, 10), (160, 10), (200, 10), (245, 10), (10, 70), (55, 70), (100, 70), (140, 70), (190, 70)]
    for (name, cells), (x0, y0) in zip(shapes.items(), places):
        for i, j in cells:
            segs = [('M', x0 + i * u, y0 + j * u), ('L', x0 + (i + 1) * u, y0 + j * u), ('L', x0 + (i + 1) * u, y0 + (j + 1) * u), ('L', x0 + i * u, y0 + (j + 1) * u)]
            c.hatch(segs, 2.5, 45, 0.4); c.path(segs, 1, close=True)


@figure('moscow-p32-1', 210, 340, 'Ten matches in a row numbered 1 to 10, then successive rows in which pairs of matches have been crossed: 1 over 4, 3 over 7, 9 over 5, 6 over 2, 10 over 8')
def crossing_matches(c):
    rows = [[], [(1, 4)], [(1, 4), (3, 7)], [(1, 4), (3, 7), (9, 5)], [(1, 4), (3, 7), (9, 5), (6, 2)], [(1, 4), (3, 7), (9, 5), (6, 2), (10, 8)]]
    for r, crosses in enumerate(rows):
        y = 12 + r * 55; moved = {a for a, b in crosses}
        for n in range(1, 11):
            x = 12 + (n - 1) * 20
            if n in moved: continue
            matchstick(c, x, y + 36, x, y, 1.8, 2)
            c.text(x, y + 46, n, 6, True, 'middle')
        for a, b in crosses:
            x = 12 + (b - 1) * 20; matchstick(c, x - 8, y + 36, x + 8, y, 1.8, 2); c.text(x - 7, y + 46, a, 6, True, 'middle')


@figure('moscow-p37-1', 90, 100, 'A fraction made of matches: I over VII')
def match_fraction(c):
    matchstick(c, 45, 40, 45, 8); matchstick(c, 12, 50, 78, 50)
    matchstick(c, 20, 62, 30, 94); matchstick(c, 40, 62, 30, 94); matchstick(c, 52, 62, 52, 94); matchstick(c, 64, 62, 64, 94)


@figure('moscow-p44-1', 160, 160, 'Eight matches laid like the spokes of a wheel, heads outward, not meeting at the centre')
def match_spokes(c):
    cx, cy = 80, 80
    for k in range(8):
        a = math.radians(k * 45 + 20); matchstick(c, cx + 14 * math.cos(a), cy + 14 * math.sin(a), cx + 62 * math.cos(a), cy + 62 * math.sin(a))


@figure('moscow-p45-1', 120, 45, 'A row of seven cells numbered 1 to 7: three white counters, an empty cell, then three black counters')
def seven_cells(c):
    for k in range(7):
        c.rect(8 + k * 15, 8, 15, 15, 1.1)
        if k < 3: c.circle(15.5 + k * 15, 15.5, 5, 1, 'white')
        elif k > 3: dot(c, 15.5 + k * 15, 15.5, 5)
        c.text(15.5 + k * 15, 34, k + 1, 7, True, 'middle')


@figure('moscow-p47-1', 110, 110, 'A 3 by 3 square of cells: 1 9 1 over 9 40 9 over 1 9 1, the centre cell framed')
def forty_square(c):
    number_grid(c, 10, 10, 30, [[1, 9, 1], [9, 40, 9], [1, 9, 1]], 11, 0.8, True)
    c.rect(40, 40, 30, 30, 1.6)


@figure('moscow-p48-1', 110, 110, 'A square with the digit 3 in each of its eight border cells and nothing in the centre')
def threes_square(c):
    c.rect(8, 8, 94, 94, 1.1)
    for j in range(3):
        for i in range(3):
            if (i, j) != (1, 1): c.text(24 + i * 31, 30 + j * 31, '3', 11, True, 'middle')


# ---- sheet 3 ---------------------------------------------------------------

@figure('moscow-p49-2', 140, 135, 'A pentagram with dots at its five points and five inner crossings')
def pentagram_dots(c):
    pts = star_polygon(c, 70, 72, 60, 5, 2, 1.3)
    dots(c, pts, 2.4)
    inner = regular_polygon(70, 72, 60 * 0.382, 5, 90); dots(c, inner, 2.4)


@figure('moscow-p50-1', 150, 125, 'A triangle with dashed lines dividing it into a lattice, and dots at the ten lattice points')
def triangle_lattice(c):
    A, B, C = (75, 10), (12, 118), (138, 118)
    c.polygon([A, B, C], 1.4)
    pts = []
    for j in range(4):
        for i in range(j + 1):
            t = j / 3; L = midpoint(A, B, t); R = midpoint(A, C, t)
            pts.append(midpoint(L, R, i / j if j else 0))
    for j in range(1, 3):
        segment(c, midpoint(A, B, j / 3), midpoint(A, C, j / 3), 0.8, (3, 2))
        segment(c, midpoint(A, B, j / 3), midpoint(B, C, j / 3), 0.8, (3, 2)); segment(c, midpoint(A, C, j / 3), midpoint(C, B, j / 3), 0.8, (3, 2))
    dots(c, pts, 2.4)


@figure('moscow-p50-2', 140, 160, 'A hexagram with dots at its six points, six inner crossings and centre')
def hexagram_dots(c):
    cx, cy, r = 70, 80, 64
    t1 = regular_polygon(cx, cy, r, 3, -90); t2 = regular_polygon(cx, cy, r, 3, 90)
    c.polygon(t1, 1.3); c.polygon(t2, 1.3)
    dots(c, t1 + t2, 2.4); dots(c, regular_polygon(cx, cy, r / 3 ** 0.5, 6, -60), 2.4); dot(c, cx, cy, 2.4)


@figure('moscow-p55-1', 115, 115, 'Two overlapping 3 by 3 boards: white counters on the upper-left board, black counters on the lower-right board')
def two_boards(c):
    grid(c, 8, 8, 3, 3, 20, 1.1); grid(c, 48, 48, 3, 3, 20, 1.1)
    for j in range(3):
        for i in range(3):
            if (i, j) != (2, 2): c.circle(18 + i * 20, 18 + j * 20, 7, 1, 'white'); c.circle(18 + i * 20, 18 + j * 20, 4, 0.6)
            if (i, j) != (0, 0): dot(c, 58 + i * 20, 58 + j * 20, 7)


@figure('moscow-p56-1', 170, 170, 'A cross-shaped solitaire board of thirty-three numbered holes')
def solitaire_board(c):
    n = 1; u = 22
    for j in range(7):
        for i in range(7):
            if (i < 2 or i > 4) and (j < 2 or j > 4): continue
            c.circle(23 + i * u, 23 + j * u, 9, 1.1); c.text(23 + i * u, 23 + j * u + 3, n, 7, True, 'middle'); n += 1
    pts = [(0, 2), (2, 2), (2, 0), (5, 0), (5, 2), (7, 2), (7, 5), (5, 5), (5, 7), (2, 7), (2, 5), (0, 5)]
    c.polygon([(12 + a * u, 12 + b * u) for a, b in pts], 1.4)


@figure('moscow-p57-1', 190, 110, 'Seven coins packed in a hexagon, the outer six numbered 1 to 6 around a centre coin, and six coins in a ring')
def coin_hexagon(c):
    r, d = 13, 27
    c.circle(50, 55, r, 1.1)
    for k in range(6):
        a = math.radians(k * 60 - 150); x, y = 50 + d * math.cos(a), 55 + d * math.sin(a)
        c.circle(x, y, r, 1.1); c.text(50 + (d + 18) * math.cos(a), 55 + (d + 18) * math.sin(a) + 3, k + 1, 7, True, 'middle')
    c.text(50, 100, '(a)', 7, True, 'middle')
    for k in range(6):
        a = math.radians(k * 60 - 90); c.circle(145 + d * math.cos(a), 55 + d * math.sin(a), r, 1.1)
    c.text(145, 100, '(b)', 7, True, 'middle')


# ---- sheet 4 (match puzzles) ---------------------------------------------------

@figure('moscow-p62-1', 190, 105, 'Arrangement (f): four match squares joined corner to corner in a zigzag')
def match_zigzag(c):
    u = 30
    for (x, y) in ((10, 10), (40, 40), (70, 10), (100, 40)):
        match_grid_outline(c, x, y, 1, u)
    c.text(150, 88, '(f)', 8, True)


@figure('moscow-p62-2', 270, 110, 'Arrangements (g) and (h): three 2 by 2 match grids in a cluster, and two 3 by 3 match grids')
def match_clusters(c):
    u = 12
    for (x, y) in ((40, 8), (10, 44), (70, 44)): match_grid(c, x, y, 2, 2, u, 1.5)
    c.text(14, 30, '(g)', 8, True)
    for (x, y) in ((190, 8), (220, 48)): match_grid(c, x, y, 3, 3, u * 0.9, 1.5)
    c.text(176, 92, '(h)', 8, True)


@figure('moscow-p62-3', 100, 100, 'A 2 by 2 grid of matches')
def match_2x2(c): match_grid(c, 10, 10, 2, 2, 40, 2)


@figure('moscow-p63-1', 130, 130, 'A 3 by 3 grid of matches')
def match_3x3(c): match_grid(c, 10, 10, 3, 3, 36, 2)


@figure('moscow-p63-2', 175, 175, 'A rectangular spiral of matches')
def match_spiral(c):
    pts = [(165, 10), (165, 165), (10, 165), (10, 10), (130, 10), (130, 130), (45, 130), (45, 45), (95, 45), (95, 95), (75, 95), (75, 75)]
    for k in range(len(pts) - 1):
        p, q = pts[k], pts[k + 1]; n = max(1, round(math.dist(p, q) / 30))
        for s in range(n):
            a = midpoint(p, q, s / n); b = midpoint(p, q, (s + 1) / n); ux, uy = unit(a, b)
            matchstick(c, a[0] + ux * 2, a[1] + uy * 2, b[0] - ux * 2, b[1] - uy * 2)


@figure('moscow-p64-1', 130, 130, 'A square of matches, three to a side, with a small square of four matches at its centre')
def match_square_inner(c): match_square(c, 10, 10, 3, 36, 1)


@figure('moscow-p64-2', 70, 70, 'A small 2 by 2 grid of matches')
def match_2x2_small(c): match_grid(c, 6, 6, 2, 2, 28, 1.5)


@figure('moscow-p64-3', 110, 80, 'A house of matches: a roof of two matches over three side-by-side cells')
def match_house(c):
    match_grid(c, 10, 34, 3, 1, 30, 2)
    matchstick(c, 12, 32, 55, 8); matchstick(c, 98, 32, 57, 8)


@figure('moscow-p65-1', 145, 145, 'A 4 by 4 grid of matches')
def match_4x4(c): match_grid(c, 10, 10, 4, 4, 31, 2)


@figure('moscow-p65-2', 170, 140, 'A 4 by 3 grid of matches')
def match_4x3(c): match_grid(c, 10, 10, 4, 3, 36, 2)


@figure('moscow-p66-1', 190, 60, 'An arrow made of matches: a shaft with chevrons for the fletching and a chevron head')
def match_arrow(c):
    for k in range(7):
        x = 10 + k * 13; matchstick(c, x, 8, x + 12, 28, 1.8, 2); matchstick(c, x, 50, x + 12, 30, 1.8, 2)
    matchstick(c, 108, 29, 140, 29, 1.8, 2); matchstick(c, 146, 10, 172, 29, 1.8, 2); matchstick(c, 146, 48, 172, 29, 1.8, 2)


@figure('moscow-p66-2', 145, 145, 'A square of matches, four to a side, with a small square of four matches at its centre')
def match_square_inner_4(c): match_square(c, 10, 10, 4, 30, 1)


@figure('moscow-p67-1', 145, 145, 'A square of matches, four to a side')
def match_square_4(c): match_square(c, 10, 10, 4, 30)


@figure('moscow-p67-2', 175, 175, 'A square of matches, five to a side, with a small square of four matches at its centre')
def match_square_inner_5(c): match_square(c, 10, 10, 5, 30, 1)


@figure('moscow-p68-1', 270, 50, 'Two cells made of seven matches, and a row of six cells made of nineteen matches')
def match_rows(c):
    match_grid(c, 8, 8, 2, 1, 28, 2); match_grid(c, 90, 8, 6, 1, 28, 2)


@figure('moscow-p69-2', 300, 200, 'Five shapes to be cut: (a) a hatched house of square and triangle, (b) a triangle cut into four and a trapezoid, (c) a dotted rectangle with a notch, (d) a hatched hexagon, (e) a square with a dashed diagonal and a trapezoid')
def cutting_shapes(c):
    house = [('M', 10, 60), ('L', 10, 110), ('L', 90, 110), ('L', 90, 60), ('L', 70, 60), ('L', 50, 10), ('L', 30, 60)]
    c.hatch(house, 3, 45, 0.5); c.path(house, 1.2, close=True); c.text(50, 124, '(a)', 7, True, 'middle')
    T = [(140, 10), (110, 60), (170, 60)]; c.polygon(T, 1.1)
    c.polygon([midpoint(T[0], T[1]), midpoint(T[1], T[2]), midpoint(T[0], T[2])], 1)
    c.polygon([(110, 78), (170, 78), (158, 100), (122, 100)], 1.1); c.text(140, 115, '(b)', 7, True, 'middle')
    c.polyline([(200, 10), (290, 10), (290, 50), (265, 50), (265, 70), (200, 70), (200, 10)], 1.1)
    for j in range(5):
        for i in range(8):
            if i < 6 or j < 4: dot(c, 206 + i * 11.5, 16 + j * 12, 1)
    c.text(245, 84, '(c)', 7, True, 'middle')
    hexa = regular_polygon(50, 160, 36, 6, 0); segs = [('M', *hexa[0])] + [('L', *p) for p in hexa[1:]]
    c.hatch(segs, 3, 45, 0.5); c.path(segs, 1.2, close=True); c.text(50, 198, '(d)', 7, True, 'middle')
    c.polygon([(110, 130), (175, 130), (175, 190), (110, 190)], 1.1); c.line(110, 190, 175, 130, 0.8, (3, 2))
    c.polygon([(200, 130), (260, 130), (290, 190), (200, 190)], 1.1); c.text(245, 198, '(e)', 7, True, 'middle')


@figure('moscow-p70-3', 90, 80, 'A Greek cross outline with nine dots inside and a small square at each arm')
def cross_dots(c):
    a = 16; bx, by = 45, 40
    pts = [(bx - a / 2, by - 1.5 * a), (bx + a / 2, by - 1.5 * a), (bx + a / 2, by - a / 2), (bx + 1.5 * a, by - a / 2), (bx + 1.5 * a, by + a / 2),
           (bx + a / 2, by + a / 2), (bx + a / 2, by + 1.5 * a), (bx - a / 2, by + 1.5 * a), (bx - a / 2, by + a / 2), (bx - 1.5 * a, by + a / 2),
           (bx - 1.5 * a, by - a / 2), (bx - a / 2, by - a / 2)]
    c.polygon(pts, 1.2)
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if abs(i) + abs(j) < 2: dot(c, bx + i * a * 0.75, by + j * a * 0.75, 1.5)
    for i in (-1, 1): dot(c, bx + i * a * 0.75, by, 1.5); dot(c, bx, by + i * a * 0.75, 1.5)
    for dx, dy in ((0, -1.25), (0, 1.25), (-1.25, 0), (1.25, 0)): c.rect(bx + dx * a - 2.5, by + dy * a - 2.5, 5, 5, 0.8)


# ---- sheet 5 (cutting and shapes) ------------------------------------------------

@figure('moscow-p72-2', 140, 115, 'A hatched board: a rectangle with a step cut from its top right and a tab at its left')
def stepped_board(c):
    segs = [('M', 20, 25), ('L', 100, 25), ('L', 100, 10), ('L', 125, 10), ('L', 125, 105), ('L', 20, 105), ('L', 20, 85), ('L', 10, 85), ('L', 10, 40), ('L', 20, 40)]
    c.hatch(segs, 3, 0, 0.5); c.path(segs, 1.3, close=True)


@figure('moscow-p72-3', 90, 80, 'A square ABCD with a smaller square FEDC standing on its top-left corner; the common edge is dashed')
def square_on_square(c):
    A, B = (12, 70), (62, 70); C, D = (62, 40), (37, 40); E, F = (37, 10), (12, 10)
    c.polygon([A, B, C, D, E, F], 1.2); c.line(12, 40, 37, 40, 0.9, (3, 2)); c.line(37, 40, 37, 70, 0.9, (3, 2))
    labels(c, {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F}, {'A': 'sw', 'B': 'se', 'C': 'e', 'D': 'ne', 'E': 'ne', 'F': 'nw'}, 8)


@figure('moscow-p73-1', 90, 80, 'A horseshoe with six nail holes')
def horseshoe(c):
    outer = c.arc_segments(45, 42, 34, 150, 390); inner = c.arc_segments(45, 42, 20, 390, 150)
    segs = outer + [('L', *inner[0][1:])] + inner[1:] + [('L', *outer[0][1:])]
    c.path(segs, 1.4, close=True)
    for a in (160, 200, 240, 300, 340, 20):
        r = math.radians(a); dot(c, 45 + 27 * math.cos(r), 42 + 27 * math.sin(r), 1.6)


@figure('moscow-p73-2', 120, 150, 'A vase shape: a round body with a flaring neck; dashed cutting lines and asterisks mark the pieces')
def vase(c):
    body = c.arc_segments(60, 100, 42, 215, 325 + 180)
    neck = [('L', 86, 40), ('C', 95, 25, 100, 15, 108, 10), ('L', 95, 8), ('C', 85, 20, 60, 28, 60, 28), ('C', 60, 28, 35, 20, 25, 8), ('L', 12, 10), ('C', 20, 15, 25, 25, 34, 40)]
    c.path(body + neck, 1.4, close=True)
    c.line(60, 2, 60, 150, 0.8, (3, 3)); c.line(5, 70, 60, 40, 0.8, (3, 3)); c.line(115, 70, 60, 40, 0.8, (3, 3))
    for x, y in ((60, 6), (8, 66), (112, 66), (60, 146)): star(c, x, y, 4, 5, 0.7)


@figure('moscow-p73-3', 150, 115, 'A hatched shape with two notches cut from its top edge, like a castle wall')
def notched_board(c):
    segs = [('M', 10, 10), ('L', 40, 10), ('L', 48, 40), ('L', 60, 40), ('L', 60, 12), ('L', 90, 12), ('L', 90, 40), ('L', 102, 40), ('L', 110, 10), ('L', 140, 10), ('L', 140, 105), ('L', 10, 105)]
    c.hatch(segs, 3, 0, 0.5); c.path(segs, 1.3, close=True)


@figure('moscow-p74-1', 100, 100, 'A regular octagon with an octagonal hole, the ring between them hatched')
def octagon_ring(c):
    outer = regular_polygon(50, 50, 44, 8, 22.5); inner = regular_polygon(50, 50, 20, 8, 22.5)
    segs = [('M', *outer[0])] + [('L', *p) for p in outer[1:]]
    c.hatch(segs, 3, 0, 0.5); c.path(segs, 1.3, close=True)
    hole = [('M', *inner[0])] + [('L', *p) for p in inner[1:]]; c.path(hole, 1.3, 'white', close=True)


@figure('moscow-p74-2', 260, 210, 'A parallelogram-shaped cake tiled with roses, with sides marked 10, 2, 5, 4 along the top and left and 4, 5, 2, 10 along the right and bottom')
def rose_cake(c):
    P = [(40, 20), (220, 20), (180, 180), (0, 180)]
    c.polygon(P, 1.4)
    for j in range(5):
        for i in range(5):
            x = 40 + i * 36 + 18 - j * 10; y = 20 + j * 32 + 16
            c.circle(x, y, 11, 0.9); c.circle(x, y, 6, 0.6); c.circle(x, y, 2, 0.5)
    c.text(140, 10, '10', 8, True, 'middle'); c.text(230, 10, '2', 8, True, 'middle'); c.text(242, 60, '4', 8, True); c.text(242, 140, '5', 8, True)
    c.text(28, 60, '5', 8, True, 'end'); c.text(8, 140, '4', 8, True, 'end'); c.text(10, 200, '2', 8, True, 'middle'); c.text(100, 200, '10', 8, True, 'middle')
    c.line(40, 6, 220, 6, 0.6); c.line(224, 6, 236, 6, 0.6)


@figure('moscow-p75-1', 240, 110, 'A carpet 12 by 9 seen in perspective with a long narrow hole of 8 by 1 in the middle')
def carpet_hole(c):
    P = cabinet(30, 95, 1, 1, 30)
    outer = [P(0, 0, 0), P(180, 0, 0), P(180, 100, 0), P(0, 100, 0)]
    c.polygon(outer, 1.3)
    hole = [P(45, 40, 0), P(135, 40, 0), P(135, 55, 0), P(45, 55, 0)]
    c.polygon(hole, 1.1, 'light')
    c.text(P(90, 100, 0)[0], P(90, 100, 0)[1] - 6, '12', 8, True, 'middle'); c.text(P(0, 50, 0)[0] - 10, P(0, 50, 0)[1], '9', 8, True)
    c.text(P(90, 47, 0)[0], P(90, 47, 0)[1] + 3, '8', 7, True, 'middle'); c.text(P(140, 47, 0)[0] + 4, P(140, 47, 0)[1] + 3, '1', 7, True)


@figure('moscow-p75-3', 190, 100, 'A chessboard with a dotted outline, and a smaller chessboard beside it')
def two_chessboards(c):
    chessboard(c, 10, 10, 10, 8, 'black'); c.rect(6, 6, 88, 88, 0.6, dash=(2, 2))
    chessboard(c, 120, 20, 8, 8, 'black')


@figure('moscow-p77-1', 120, 120, 'A circle with a square grid drawn inside it')
def round_table(c):
    c.circle(60, 60, 55, 1.4)
    for k in range(-4, 5):
        x = 60 + k * 13; h = math.sqrt(max(55 * 55 - (k * 13) ** 2, 0))
        c.line(x, 60 - h, x, 60 + h, 0.8); c.line(60 - h, x, 60 + h, x, 0.8)


@figure('moscow-p77-2', 180, 150, 'A right triangle with a square on each side: C on the hypotenuse, B on the longer leg, A on the shorter leg')
def pythagoras_squares(c):
    O, X, Y = (80, 120), (80, 95), (120, 120)
    a, b = 25, 40
    c.polygon([O, X, Y], 1.3)
    c.rect(O[0] - a, O[1], a, a, 1.2); c.text(O[0] - a / 2, O[1] + a / 2 + 4, 'A', 8, True, 'middle')
    c.rect(O[0], O[1], b, b, 1.2); c.text(O[0] + b / 2, O[1] + b / 2 + 4, 'B', 8, True, 'middle')
    ux, uy = unit(X, Y); n = math.hypot(b, a); px, py = uy, -ux
    sq = [X, Y, (Y[0] + px * n, Y[1] + py * n), (X[0] + px * n, X[1] + py * n)]
    c.polygon(sq, 1.2); cx = sum(p[0] for p in sq) / 4; cy = sum(p[1] for p in sq) / 4; c.text(cx, cy + 4, 'C', 8, True, 'middle')
    c.text(O[0] + 6, O[1] - 6, 'c', 6, True)


@figure('moscow-p77-3', 240, 150, '(a) a square FQEP with points A, B, C, D and dashed lines; (b) a pentagonal house shape')
def square_and_house(c):
    F, E = (20, 125), (120, 125); Q = (20, 70); A, B = (25, 20), (50, 12); Cc = (55, 32); D = (112, 40); P = (135, 35)
    c.polygon([F, E, D, Cc, A], 1.1)
    c.line(*A, *B, 1.1); c.line(*B, *Cc, 1.1); c.line(*Q, *P, 0.9, (3, 2)); c.line(*F, *Q, 1.1); c.line(*Q, *A, 1.1); c.line(*B, *P, 0.9, (3, 2)); c.line(*P, *E, 0.9, (3, 2))
    labels(c, {'A': A, 'B': B, 'C': Cc, 'D': D, 'E': E, 'F': F, 'P': P, 'Q': Q}, {'A': 'w', 'B': 'n', 'C': 'e', 'D': 'n', 'E': 'se', 'F': 'sw', 'P': 'e', 'Q': 'w'}, 7)
    c.text(70, 140, '(a)', 7, True, 'middle')
    c.polygon([(160, 50), (190, 20), (215, 40), (230, 30), (230, 125), (160, 125)], 1.2); c.text(195, 140, '(b)', 7, True, 'middle')


@figure('moscow-p78-1', 140, 125, 'A regular hexagon')
def hexagon(c): c.polygon(regular_polygon(70, 62, 58, 6, 0), 1.4)


# ---- sheet 6 ---------------------------------------------------------------

@figure('moscow-p81-1', 210, 150, 'Four pulleys A, B, C, D at the corners of a square, joined by one belt that crosses between them')
def four_pulleys(c):
    P = {'A': (40, 40), 'B': (170, 40), 'C': (170, 115), 'D': (40, 115)}
    for p in P.values(): c.circle(*p, 22, 1.3); c.circle(*p, 6, 1)
    for a, b, s in (('A', 'C', 1), ('B', 'D', 1), ('A', 'B', -1), ('C', 'D', 1), ('A', 'D', -1), ('B', 'C', 1)):
        p, q = P[a], P[b]; ux, uy = unit(p, q); c.line(p[0] - uy * 22 * s, p[1] + ux * 22 * s, q[0] - uy * 22 * s, q[1] + ux * 22 * s, 1.1)
    labels(c, P, {'A': 'nw', 'B': 'ne', 'C': 'se', 'D': 'sw'}, 8)


@figure('moscow-p81-2', 110, 100, 'Three pulleys at the corners of a triangle with a belt round them')
def three_pulleys(c):
    P = [(55, 18), (15, 82), (95, 82)]
    for p in P: c.circle(*p, 9, 1.3); c.circle(*p, 3, 1)
    for i in range(3):
        p, q = P[i], P[(i + 1) % 3]; ux, uy = unit(p, q); c.line(p[0] - uy * 9, p[1] + ux * 9, q[0] - uy * 9, q[1] + ux * 9, 1.4)


@figure('moscow-p85-1', 300, 110, 'A cube with hidden edges dashed, a pentagram shaded inside a pentagon, and a hexagram shaded inside a hexagon')
def cube_star_hexagram(c):
    P = cabinet(15, 90, 55, 0.5, 40)
    c.polygon([P(0, 0, 0), P(1, 0, 0), P(1, 0, 1), P(0, 0, 1)], 1.2); c.polygon([P(0, 0, 1), P(1, 0, 1), P(1, 1, 1), P(0, 1, 1)], 1.2); c.polygon([P(1, 0, 0), P(1, 1, 0), P(1, 1, 1), P(1, 0, 1)], 1.2)
    c.line(*P(0, 1, 0), *P(0, 1, 1), 0.9, (3, 2)); c.line(*P(0, 1, 0), *P(1, 1, 0), 0.9, (3, 2)); c.line(*P(0, 1, 0), *P(0, 0, 0), 0.9, (3, 2))
    pent = regular_polygon(150, 55, 42, 5); c.polygon(pent, 1.2)
    stars = regular_polygon(150, 55, 42, 5); inner = regular_polygon(150, 55, 42 * 0.382, 5, 90)
    starpts = []
    for k in range(5): starpts += [stars[k], inner[k]]
    segs = [('M', *starpts[0])] + [('L', *p) for p in starpts[1:]]; c.hatch(segs, 3, 45, 0.5); c.path(segs, 1.1, close=True)
    hexa = regular_polygon(250, 55, 44, 6, -90); c.polygon(hexa, 1.2)
    t1 = regular_polygon(250, 55, 44, 3, -90); t2 = regular_polygon(250, 55, 44, 3, 90)
    for t in (t1, t2):
        segs = [('M', *t[0]), ('L', *t[1]), ('L', *t[2])]; c.hatch(segs, 3, 45, 0.5); c.path(segs, 1.1, close=True)


@figure('moscow-p85-2', 240, 110, 'A circle beside a set square with a hole, and a pencil')
def circle_set_square(c):
    c.circle(50, 55, 42, 1.6)
    c.polygon([(110, 85), (225, 85), (110, 20)], 1.3); c.polygon([(125, 72), (160, 72), (125, 50)], 1)
    c.line(150, 60, 230, 92, 1.4); c.line(226, 90, 232, 96, 1.4)


@figure('moscow-p86-3', 240, 100, 'A wooden beam 8 by 8 by 27 with its dimensions marked')
def beam(c):
    P = cabinet(20, 85, 1, 0.5, 35)
    c.polygon([P(0, 0, 0), P(180, 0, 0), P(180, 0, 45), P(0, 0, 45)], 1.2); c.polygon([P(0, 0, 45), P(180, 0, 45), P(180, 45, 45), P(0, 45, 45)], 1.2); c.polygon([P(180, 0, 0), P(180, 45, 0), P(180, 45, 45), P(180, 0, 45)], 1.2, 'light')
    c.arrow(P(0, 0, 55)[0], P(0, 0, 55)[1], P(180, 0, 55)[0], P(180, 0, 55)[1], 4, 0.8, both=True); c.text(P(90, 0, 55)[0], P(90, 0, 55)[1] - 4, '27', 8, True, 'middle')
    c.arrow(P(-8, 0, 0)[0], P(-8, 0, 0)[1], P(-8, 0, 45)[0], P(-8, 0, 45)[1], 4, 0.8, both=True); c.text(P(-14, 0, 22)[0], P(-14, 0, 22)[1] + 3, '8', 8, True, 'end')
    c.arrow(P(0, 55, 45)[0], P(0, 55, 45)[1], P(0, 55, 45)[0], P(0, 55, 45)[1] - 1, 0, 0)
    c.text(P(0, 30, 45)[0] - 6, P(0, 30, 45)[1] - 4, '8', 8, True, 'end')


@figure('moscow-p87-2', 270, 120, 'Squares of 1, 4 and 9 hatched cells and triangles of 1, 4, 9 and 16 hatched cells')
def square_triangle_numbers(c):
    x = 10
    for n in (1, 2, 3):
        for j in range(n):
            for i in range(n):
                segs = [('M', x + i * 12, 10 + j * 12), ('L', x + i * 12 + 12, 10 + j * 12), ('L', x + i * 12 + 12, 22 + j * 12), ('L', x + i * 12, 22 + j * 12)]
                c.hatch(segs, 2.5, 45, 0.4); c.path(segs, 0.9, close=True)
        x += n * 12 + 14
    x = 10; s = 14; h = s * 0.866
    for n in (1, 2, 3, 4):
        base = 110
        for j in range(n):
            for i in range(j + 1):
                ax = x + (i + (n - 1 - j) / 2) * s; ay = base - (n - 1 - j) * h
                tri = [('M', ax, ay), ('L', ax + s, ay), ('L', ax + s / 2, ay - h)]
                c.hatch(tri, 2.5, 45, 0.4); c.path(tri, 0.9, close=True)
                if i < j:
                    inv = [('M', ax + s / 2, ay - h), ('L', ax + s, ay), ('L', ax + s * 1.5, ay - h)]
                    c.path(inv, 0.9, 'white', close=True)
        x += n * s + 16


@figure('moscow-p87-3', 160, 60, 'Three shapes (a), (b), (c): two L-trominoes in different orientations and a trapezoid of three triangles')
def three_small_shapes(c):
    u = 14
    for i, j in ((0, 0), (1, 0), (0, 1)): c.rect(10 + i * u, 8 + j * u, u, u, 1)
    c.text(24, 50, '(a)', 7, True, 'middle')
    for i, j in ((0, 0), (0, 1), (1, 1)): c.rect(60 + i * u, 8 + j * u, u, u, 1)
    c.text(74, 50, '(b)', 7, True, 'middle')
    h = u * 0.866
    c.polygon([(110, 8 + h), (110 + 2 * u, 8 + h), (110 + 1.5 * u, 8), (110 + u / 2, 8)], 1); c.line(110 + u / 2, 8, 110 + u, 8 + h, 1); c.line(110 + u, 8 + h, 110 + 1.5 * u, 8, 1)
    c.text(124, 50, '(c)', 7, True, 'middle')


@figure('moscow-p89-2', 250, 180, 'A triangular lattice with a large triangle drawn on it; at a point P inside, three segments meet at 120 degree angles')
def lattice_triangle_120(c):
    s = 18; h = s * 0.866
    for j in range(9):
        y = 10 + j * h; off = (j % 2) * s / 2
        for i in range(14):
            x = 10 + i * s + off
            if x + s < 245: c.line(x, y, x + s, y, 0.5)
            if j < 8:
                if x + s / 2 < 245: c.line(x, y, x + s / 2, y + h, 0.5)
                if x - s / 2 > 5: c.line(x, y, x - s / 2, y + h, 0.5)
    T = [(100, 10 + h), (46, 10 + 7 * h), (154 + s, 10 + 7 * h)]; c.polygon(T, 1.6)
    Pp = (100 + s / 2, 10 + 5 * h)
    for a in (-90, 30, 150):
        r = math.radians(a); c.line(Pp[0], Pp[1], Pp[0] + 2 * s * math.cos(r), Pp[1] + 2 * s * math.sin(r), 1.6)
    c.circle(*Pp, 4, 1, 'white'); c.text(Pp[0] - 8, Pp[1] + 14, 'P', 8, True)
    c.text(Pp[0] - 22, Pp[1] - 12, '120°', 6, True); c.text(Pp[0] + 8, Pp[1] - 12, '120°', 6, True); c.text(Pp[0] - 18, Pp[1] + 20, '120°', 6, True)


# ---- sheet 7 ---------------------------------------------------------------

@figure('moscow-p98-2', 230, 125, 'A die showing 1, 2 and 3, and the cross-shaped net of a die with all six faces of pips')
def die_and_net(c):
    die(c, 10, 40, 36, 1, 2, 3)
    u = 30; x0, y0 = 110, 5
    layout = {(1, 0): 6, (0, 1): 2, (1, 1): 1, (2, 1): 5, (3, 1): 3, (1, 2): 4}
    for (i, j), n in layout.items():
        c.rect(x0 + i * u, y0 + j * u, u, u, 1.1); pips(c, x0 + i * u, y0 + j * u, u, n)


@figure('moscow-p99-1', 290, 290, 'The four polyhedra (a) tetrahedron, (b) octahedron, (c) dodecahedron and (d) icosahedron, hidden edges dashed')
def polyhedra(c):
    polyhedron(c, 70, 70, 42, 'tetra', 15, 25); c.text(20, 130, '(a)', 7, True)
    polyhedron(c, 210, 70, 52, 'octa', 20, 30); c.text(255, 130, '(b)', 7, True)
    polyhedron(c, 70, 210, 36, 'dodeca', 15, 20); c.text(15, 270, '(c)', 7, True)
    polyhedron(c, 210, 210, 36, 'icosa', 20, 25); c.text(260, 270, '(d)', 7, True)


@figure('moscow-p100-1', 90, 140, 'Three dice stacked in a column')
def stacked_dice(c):
    die(c, 10, 90, 36, 3, 2, 5); die(c, 10, 54, 36, 6, 4, 1); die(c, 10, 18, 36, 2, 3, 1)


@figure('moscow-p100-2', 220, 70, 'Three dice side by side showing different faces')
def three_dice(c):
    die(c, 10, 20, 36, 1, 3, 2); die(c, 80, 20, 36, 2, 6, 4); die(c, 150, 20, 36, 3, 2, 1)


@figure('moscow-p103-1', 180, 110, 'A line AB cut into parts marked 14, 10, 4, 12 by four slanting lines; small circles mark where the slanting lines cross')
def crossing_lines_ab(c):
    c.line(10, 90, 170, 90, 1.2); c.text(6, 93, 'A', 8, True, 'end'); c.text(174, 93, 'B', 8, True)
    xs = [30, 70, 105, 135, 165]
    for k in range(5):
        c.line(xs[k], 90, xs[k] - 18 + (k % 2) * 36, 15, 1)
    for x, lab in ((50, '14'), (87, '10'), (120, '4'), (150, '12')): c.text(x, 102, lab, 7, True, 'middle')
    for x, y in ((48, 60), (88, 48), (118, 55), (150, 42)): c.circle(x, y, 3.5, 1, 'white')


@figure('moscow-p103-2', 300, 95, 'Two triangles on a base AB labelled with sums: (a) sides 8+5 and 9+3+4, inside 6+1+7, base marks 13 and 16; (b) sides 2+8 and 9+3, inside 6+1+7, base marks 10, 4, 12, 14')
def sum_triangles(c):
    for x0, (s1, s2, inner, base, lab) in ((10, ('8+5', '9+3+4', '6+1+7', ['13', '16'], '(a)')), (160, ('2+8', '9+3', '6+1+7', ['10', '4', '12', '14'], '(b)'))):
        A, B, T = (x0, 70), (x0 + 125, 70), (x0 + 55, 15)
        c.line(*A, *B, 1.1); c.line(*A, *T, 0.9, (3, 2)); c.line(*T, *B, 0.9, (3, 2)); c.line(*T, (x0 + 85), 70, 0.9, (3, 2))
        c.text(x0 - 4, 73, 'A', 7, True, 'end'); c.text(x0 + 129, 73, 'B', 7, True)
        c.text(x0 + 18, 40, s1, 6, True, 'middle'); c.text(x0 + 98, 38, s2, 6, True, 'middle'); c.text(x0 + 66, 55, inner, 6, True, 'middle')
        for k, b in enumerate(base): c.text(x0 + 15 + k * (110 / max(len(base) - 1, 1)), 82, b, 6, True, 'middle')
        c.text(x0 + 62, 94, lab, 7, True, 'middle')


@figure('moscow-p110-1', 150, 150, 'Four equal circles, three round a central one, each touching its neighbours')
def four_wheels(c):
    r = 30
    c.circle(75, 75, r, 1.3)
    for a in (-90, 30, 150):
        t = math.radians(a); c.circle(75 + 2 * r * math.cos(t), 75 + 2 * r * math.sin(t), r, 1.3)
        dot(c, 75 + r * math.cos(t), 75 + r * math.sin(t), 2)


@figure('moscow-p116-1', 160, 80, 'A balance: a beam on a central pivot with a pan at each end, the arms marked a and b')
def balance(c):
    c.line(15, 30, 145, 30, 1.6); c.polygon([(80, 30), (74, 44), (86, 44)], 1.2); c.line(80, 8, 80, 30, 1); c.arrow(80, 30, 80, 10, 4, 0.8)
    for x in (30, 130):
        c.polygon([(x - 18, 36), (x + 18, 36), (x + 14, 46), (x - 14, 46)], 1.2); c.line(x, 30, x, 36, 1)
    c.arrow(18, 58, 78, 58, 4, 0.8, both=True); c.text(48, 70, 'a', 8, True, 'middle')
    c.arrow(82, 58, 142, 58, 4, 0.8, both=True); c.text(112, 70, 'b', 8, True, 'middle')


def share_segment(c, left, right, width=180):
    c.line(10, 30, 10 + width, 30, 1.4); c.line(10, 22, 10, 38, 1); c.line(10 + width, 22, 10 + width, 38, 1)
    split = 10 + width * 0.6; c.line(split, 22, split, 38, 1)
    c.arrow(12, 16, split - 2, 16, 4, 0.8, both=True); c.arrow(split + 2, 16, 8 + width, 16, 4, 0.8, both=True)
    c.rect((10 + split) / 2 - 14, 8, 28, 12, 0, 'white'); c.text((10 + split) / 2, 19, left, 8, True, 'middle')
    c.rect((split + 10 + width) / 2 - 14, 8, 28, 12, 0, 'white'); c.text((split + 10 + width) / 2, 19, right, 8, True, 'middle')
    c.text((10 + split) / 2, 48, 'me', 8, True, 'middle'); c.text((split + 10 + width) / 2, 48, 'you', 8, True, 'middle')


@figure('moscow-p117-1', 200, 55, 'A segment divided into a part 2x marked me and a part x marked you')
def share_2x(c): share_segment(c, '2x', 'x')


@figure('moscow-p117-2', 200, 55, 'A segment divided into 2 1/4 x marked me and 1 1/4 x marked you')
def share_9x(c): share_segment(c, '2 1/4 x', '1 1/4 x')


@figure('moscow-p118-1', 200, 55, 'A segment divided into 25/64 x marked me and 11/64 x marked you')
def share_64(c): share_segment(c, '25/64 x', '11/64 x')


# ---- sheet 8 ---------------------------------------------------------------

@figure('moscow-p120-1', 170, 170, 'A target of eight concentric rings scoring 1, 2, 3, 5, 10, 20, 25 and 50 from the outside in, with several hits marked')
def target(c):
    cx, cy = 85, 85
    for k, v in enumerate((1, 2, 3, 5, 10, 20, 25, 50)):
        r = 78 - k * 9.5; c.circle(cx, cy, r, 1); c.text(cx, cy - r + 7, v, 6, anchor='middle')
    for x, y in ((40, 60), (120, 48), (100, 120), (60, 130), (130, 100), (75, 70), (92, 98), (118, 70)): dot(c, x, y, 2)


@figure('moscow-p124-2', 90, 90, 'A multiplication skeleton: a three-digit number with middle digit 2 times a three-digit number; the partial products show an 8, and the result shows 9 and 2')
def multiplication_skeleton(c):
    rows = [('* * *', 70), ('* 2 *', 70), None, ('* * * *', 76), ('* 8 *', 58), None, ('* * 9 * 2 *', 82)]
    y = 14
    for row in rows:
        if row is None: c.line(8, y - 8, 84, y - 8, 0.8); continue
        text, x = row; c.text(x, y, text, 8, anchor='end'); y += 13


@figure('moscow-p124-3', 95, 90, 'A multiplication skeleton in letters: ABC times BAC gives three partial products ending in stars, A and B, and a seven-star result')
def letter_skeleton(c):
    rows = [('A B C', 72), ('B A C', 72), None, ('* * *', 72), ('* * A', 60), ('* * B', 48), None, ('* * * * * * *', 84)]
    y = 12
    for row in rows:
        if row is None: c.line(6, y - 8, 90, y - 8, 0.8); continue
        text, x = row; c.text(x, y, text, 8, anchor='end'); y += 12


@figure('moscow-p128-1', 130, 140, 'An isosceles triangle ABC with apex B and the median BD to the base; equal sides and equal halves of the base are marked')
def isosceles_median(c):
    A, B, C, D = (12, 120), (65, 12), (118, 120), (65, 120)
    c.polygon([A, B, C], 1.4); c.line(*B, *D, 1.2)
    tick(c, A, B); tick(c, B, C); tick(c, A, D, 2); tick(c, D, C, 2)
    labels(c, {'A': A, 'B': B, 'C': C, 'D': D}, {'A': 'sw', 'B': 'n', 'C': 'se', 'D': 's'}, 8)


@figure('moscow-p134-1', 260, 110, 'A tray of twelve cups in two rows of six, each holding four cherries, labelled f to a above and A to F below')
def cherry_tray(c):
    c.rect(10, 20, 240, 70, 1.4, radius=6)
    for j in range(2):
        for i in range(6):
            cx, cy = 30 + i * 40, 38 + j * 36
            c.circle(cx, cy, 14, 1.1)
            for k in range(4):
                a = math.radians(k * 90 + 45); c.circle(cx + 6 * math.cos(a), cy + 6 * math.sin(a), 3, 0.8)
    for i, lab in enumerate('fedcba'): c.text(30 + i * 40, 14, lab, 8, True, 'middle')
    for i, lab in enumerate('ABCDEF'): c.text(30 + i * 40, 104, lab, 8, True, 'middle')


def letter_rows(c, top, r1, r2, bottom):
    for i, ch in enumerate(top): c.text(14 + i * 12, 12, ch, 8, True, 'middle')
    c.line(8, 16, 80, 16, 0.8)
    for i, ch in enumerate(r1): c.text(14 + i * 12, 28, ch, 8, anchor='middle')
    for i, ch in enumerate(r2): c.text(14 + i * 12, 40, ch, 8, anchor='middle')
    c.line(8, 45, 80, 45, 0.8); c.arrow(3, 34, 8, 34, 3, 0.7); c.arrow(86, 34, 81, 34, 3, 0.7)
    for i, ch in enumerate(bottom): c.text(14 + i * 12, 57, ch, 8, True, 'middle')


@figure('moscow-p134-2', 95, 65, 'Columns f e d c b a over the digits 4 4 4 0 5 5 and 5 5 5 5 6 0, with the result row A B C D E F')
def cherry_rows_1(c): letter_rows(c, 'fedcba', '444055', '555560', 'ABCDEF')


@figure('moscow-p134-3', 95, 65, 'Columns f e d c b a over the digits 2 1 2 3 1 2 and 0 0 0 0 0 6, with the result row A B C D E F')
def cherry_rows_2(c): letter_rows(c, 'fedcba', '212312', '000006', 'ABCDEF')


# ---- sheet 9 (magic figures) ------------------------------------------------------

@figure('moscow-p153-2', 140, 150, 'A hexagram with a circle at each of its six points and six crossings, twelve circles in all')
def magic_hexagram(c):
    cx, cy, r = 70, 78, 60
    t1 = regular_polygon(cx, cy, r, 3, -90); t2 = regular_polygon(cx, cy, r, 3, 90)
    c.polygon(t1, 1.1); c.polygon(t2, 1.1)
    for p in t1 + t2 + regular_polygon(cx, cy, r / 3 ** 0.5, 6, -60): c.circle(*p, 7, 1.1, 'white')


@figure('moscow-p154-1', 140, 140, 'A square with a diamond inscribed through the midpoints of its sides; circles sit at the four corners, the four midpoints and the midpoints of the diamond sides')
def square_diamond_circles(c):
    s, x0 = 110, 15
    corners = [(x0, x0), (x0 + s, x0), (x0 + s, x0 + s), (x0, x0 + s)]
    mids = [midpoint(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    c.polygon(corners, 1.1); c.polygon(mids, 1.1)
    inner = [midpoint(mids[i], mids[(i + 1) % 4]) for i in range(4)]
    for p in corners + mids + inner: c.circle(*p, 7, 1.1, 'white')


@figure('moscow-p154-2', 160, 160, 'A pentagram inside a ring of five arcs, with circles at the five points and five crossings; the inner pentagon is dashed')
def magic_pentagram(c):
    cx, cy, r = 80, 82, 58
    outer = regular_polygon(cx, cy, r, 5); inner = regular_polygon(cx, cy, r * 0.382, 5, 90)
    for i in range(5):
        segment(c, outer[i], inner[(i + 2) % 5], 1.1); segment(c, outer[i], inner[(i + 3) % 5], 1.1)
    c.polygon(inner, 0.8, dash=(3, 2))
    for i in range(5):
        a0 = -90 + i * 72 - 36; a1 = -90 + i * 72 + 36
        p0 = (cx + r * 0.62 * math.cos(math.radians(a0)), cy + r * 0.62 * math.sin(math.radians(a0)))
        p1 = (cx + r * 0.62 * math.cos(math.radians(a1)), cy + r * 0.62 * math.sin(math.radians(a1)))
        m = (cx + r * 1.08 * math.cos(math.radians(-90 + i * 72)), cy + r * 1.08 * math.sin(math.radians(-90 + i * 72)))
        c.curve([p0, m, p1], 1)
    for p in outer + inner: c.circle(*p, 6.5, 1.1, 'white')


@figure('moscow-p155-1', 150, 135, 'Nineteen circles in a hexagonal pattern, joined by lines through the centre along the six directions')
def magic_hexagon(c):
    cx, cy, d = 75, 68, 26
    pts = [(cx, cy)]
    for k in range(6):
        a = math.radians(k * 60); pts.append((cx + d * math.cos(a), cy + d * math.sin(a)))
    for k in range(6):
        a = math.radians(k * 60); pts.append((cx + 2 * d * math.cos(a), cy + 2 * d * math.sin(a)))
        b = math.radians(k * 60 + 30); pts.append((cx + d * 3 ** 0.5 * math.cos(b), cy + d * 3 ** 0.5 * math.sin(b)))
    for k in range(3):
        a = math.radians(k * 60); c.line(cx - 2 * d * math.cos(a), cy - 2 * d * math.sin(a), cx + 2 * d * math.cos(a), cy + 2 * d * math.sin(a), 1)
    hexa = regular_polygon(cx, cy, 2 * d, 6, 0); c.polygon(hexa, 1)
    for p in pts: c.circle(*p, 6.5, 1.1, 'white')


@figure('moscow-p156-1', 120, 60, 'A rectangle of three squares cut by four parallel slanting lines')
def slanted_strip(c):
    c.rect(10, 10, 100, 36, 1.2)
    for k in range(4): c.line(10 + k * 25, 46, 10 + k * 25 + 25, 10, 1)


@figure('moscow-p161-1', 150, 150, 'A chessboard with the dark squares hatched')
def hatched_chessboard(c):
    u = 16
    for j in range(8):
        for i in range(8):
            if (i + j) % 2 == 1:
                segs = [('M', 10 + i * u, 10 + j * u), ('L', 10 + (i + 1) * u, 10 + j * u), ('L', 10 + (i + 1) * u, 10 + (j + 1) * u), ('L', 10 + i * u, 10 + (j + 1) * u)]
                c.hatch(segs, 2.5, 45, 0.4)
    grid(c, 10, 10, 8, 8, u, 0.6); c.rect(10, 10, 8 * u, 8 * u, 1.4)


@figure('moscow-p161-2', 135, 135, 'The fifteen puzzle: a tray of round tiles numbered 1 to 15 with the last cell empty')
def fifteen_puzzle(c):
    c.rect(6, 6, 123, 123, 1.6, radius=6)
    for n in range(15):
        i, j = n % 4, n // 4; x, y = 20 + i * 29, 20 + j * 29
        c.rect(x - 13, y - 13, 26, 26, 0.8); c.circle(x, y, 11, 1.1); c.text(x, y + 3.5, n + 1, 9, anchor='middle', bold=True)


@figure('moscow-p161-3', 100, 100, 'A 4 by 4 tray reading 1 2 3 4, 5 6 7 8, 9 10 11 12, 13 15 14 and a gap')
def fifteen_swapped(c):
    number_grid(c, 8, 8, 21, [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 15, 14, '']], 8, 1, True); c.rect(8, 8, 84, 84, 1.5)


@figure('moscow-p162-1', 100, 100, 'A 4 by 4 tray reading 1 2 3 4, 5 6 7 8, 8 7 6 5, 4 3 2 1')
def mirrored_tray(c):
    number_grid(c, 8, 8, 21, [[1, 2, 3, 4], [5, 6, 7, 8], [8, 7, 6, 5], [4, 3, 2, 1]], 8, 1, True); c.rect(8, 8, 84, 84, 1.5)


@figure('moscow-p163-1', 110, 110, 'A 4 by 4 square of two-digit numbers: 96 11 89 68, 88 69 91 16, 61 86 18 99, 19 98 66 81')
def rotatable_square(c):
    number_grid(c, 8, 8, 23, [[96, 11, 89, 68], [88, 69, 91, 16], [61, 86, 18, 99], [19, 98, 66, 81]], 8, 1, True); c.rect(8, 8, 92, 92, 1.5)


@figure('moscow-p163-2', 90, 100, 'The Lo Shu magic square 4 9 2, 3 5 7, 8 1 6 with its magic sum S = 15')
def lo_shu(c):
    number_grid(c, 10, 8, 22, [[4, 9, 2], [3, 5, 7], [8, 1, 6]], 9, 1, True); c.rect(10, 8, 66, 66, 1.5)
    c.text(43, 90, 'S = 15', 8, True, 'middle')


@figure('moscow-p163-3', 80, 80, 'A 3 by 3 square of the symbols a1 to a9')
def symbolic_square(c):
    for j in range(3):
        for i in range(3):
            c.rect(8 + i * 22, 8 + j * 22, 22, 22, 1); subscript(c, 13 + i * 22, 23 + j * 22, 'a', 3 * j + i + 1, 8)
    c.rect(8, 8, 66, 66, 1.4)


@figure('moscow-p166-1', 120, 120, 'A 4 by 4 grid labelled A, B, C and A1, B1, C1 at the sides and a, b, c and a1, b1, c1 top and bottom, with dashed diagonals')
def labelled_grid(c):
    u = 20; x0, y0 = 25, 25
    grid(c, x0, y0, 4, 4, u, 1)
    for k in range(4):
        c.line(x0, y0 + k * u, x0 + (4 - k) * u, y0 + 4 * u, 0.7, (2, 2)); c.line(x0 + k * u, y0, x0 + 4 * u, y0 + (4 - k) * u, 0.7, (2, 2))
    for k, lab in enumerate('ABC'): c.text(x0 - 5, y0 + (k + 1) * u + 3, lab, 7, True, 'end'); subscript(c, x0 + 4 * u + 4, y0 + (k + 1) * u + 3, lab, '1', 7)
    for k, lab in enumerate('abc'): c.text(x0 + (k + 1) * u, y0 - 4, lab, 7, True, 'middle'); subscript(c, x0 + (k + 1) * u - 4, y0 + 4 * u + 12, lab, '1', 7)


# ---- sheet 10 (number patterns) ----------------------------------------------------

@figure('moscow-p168-1', 170, 75, 'Two products: 12,345,679 times 7 is 86,419,753, times 9 is 777,777,777; and 12,345,679 times 8 is 98,765,432, times 9 is 888,888,888')
def repdigits(c):
    for x, (a, b) in ((70, ('7', '86,419,753')), (160, ('8', '98,765,432'))):
        c.text(x, 14, '12,345,679', 8, anchor='end'); c.text(x, 26, a, 8, anchor='end'); c.line(x - 50, 30, x + 2, 30, 0.7)
        c.text(x, 40, b, 8, anchor='end'); c.text(x, 52, '9', 8, anchor='end'); c.line(x - 50, 56, x + 2, 56, 0.7)
        c.text(x, 66, ','.join([a * 3] * 3), 8, anchor='end')


@figure('moscow-p168-2', 190, 140, 'A triangular table: row k lists 1 and the numbers 1 + k j for j up to 6, from 1 3 5 7 9 11 13 down to 1 9 17 25 33 41 49, with stepped brackets')
def stepped_table(c):
    c.text(10, 12, 'A', 8, True)
    for k in range(1, 8):
        y = 14 + k * 16
        for j in range(7): c.text(26 + j * 24, y + 4, 1 + k * j, 7, anchor='middle')
        if k < 7: c.polyline([(14, y + 8), (14 + (k) * 24, y + 8), (14 + k * 24, y + 16)], 0.7)
    c.line(14, 24, 14, 30, 0.7)


@figure('moscow-p170-1', 180, 95, 'The cyclic number 142857: its multiples 1 to 6 listed with a brace, and a dial with the digits 1, 4, 2, 8, 5, 7 round it and arrows')
def cyclic_number(c):
    rows = ['1 = 142,857;', '2 = 285,714;', '3 = 428,571;', '4 = 571,428;', '5 = 714,285;', '6 = 857,142.']
    for k, row in enumerate(rows): c.text(16, 16 + k * 12, row, 7)
    c.polyline([(10, 8), (7, 10), (7, 44), (4, 46), (7, 48), (7, 82), (10, 84)], 0.7)
    cx, cy, r = 140, 45, 30
    c.circle(cx, cy, r, 1.3)
    for k, d in enumerate((1, 4, 2, 8, 5, 7)):
        a = math.radians(-90 + k * 60); c.text(cx + (r - 9) * math.cos(a), cy + (r - 9) * math.sin(a) + 3, d, 8, True, 'middle')
    c.arrow(cx, cy, cx, cy - 15, 4, 0.9); c.arc(cx, cy, 8, 200, 340, 0.9)


@figure('moscow-p171-1', 170, 170, 'Two concentric rings of 24 cells, the outer numbered 1 to 24 and the inner numbered 1 to 24 in a different order, with spokes to the centre')
def number_rings(c):
    cx, cy = 85, 85
    c.circle(cx, cy, 78, 1.1); c.circle(cx, cy, 60, 1.1); c.circle(cx, cy, 42, 1.1)
    inner = [1, 10, 5, 9, 4, 8, 3, 7, 2, 6, 12, 11, 24, 15, 20, 16, 21, 17, 22, 18, 23, 19, 13, 14]
    for k in range(24):
        a = math.radians(k * 15 - 90)
        c.line(cx + 42 * math.cos(a), cy + 42 * math.sin(a), cx + 78 * math.cos(a), cy + 78 * math.sin(a), 0.7)
        c.line(cx, cy, cx + 42 * math.cos(a), cy + 42 * math.sin(a), 0.4)
        b = math.radians(k * 15 - 90 + 7.5)
        c.text(cx + 69 * math.cos(b), cy + 69 * math.sin(b) + 2.5, k + 1, 6, True, 'middle'); c.text(cx + 51 * math.cos(b), cy + 51 * math.sin(b) + 2.5, inner[k], 6, True, 'middle')


@figure('moscow-p181-1', 50, 60, 'A 3 by 3 grid labelled (b)')
def small_grid_b(c):
    grid(c, 8, 6, 3, 3, 11, 1); c.text(24, 52, '(b)', 7, True, 'middle')


@figure('moscow-p187-1', 270, 100, 'Two rectangles with dimension arrows: a square of side x + y with a diagonal cut, and a rectangle of sides x and x + y with a slanting line')
def rectangle_dimensions(c):
    x0, y0, s = 15, 20, 70
    c.rect(x0, y0, s, s, 1.2); c.line(x0 + s * 0.42, y0, x0 + s * 0.42, y0 + s, 1); c.line(x0, y0 + s * 0.42, x0 + s * 0.42, y0, 1); c.line(x0, y0 + s, x0 + s * 0.42, y0 + s * 0.42, 1)
    c.arrow(x0, y0 - 8, x0 + s * 0.42, y0 - 8, 3, 0.7, both=True); c.text(x0 + s * 0.21, y0 - 11, 'y', 7, True, 'middle')
    c.arrow(x0 + s * 0.42, y0 - 8, x0 + s, y0 - 8, 3, 0.7, both=True); c.text(x0 + s * 0.71, y0 - 11, 'x', 7, True, 'middle')
    c.arrow(x0 + s + 8, y0, x0 + s + 8, y0 + s * 0.42, 3, 0.7, both=True); c.text(x0 + s + 13, y0 + s * 0.21 + 3, 'y', 7, True)
    c.arrow(x0 + s + 8, y0 + s * 0.42, x0 + s + 8, y0 + s, 3, 0.7, both=True); c.text(x0 + s + 13, y0 + s * 0.71 + 3, 'x', 7, True)
    x1, w, h = 140, 110, 45
    c.rect(x1, y0 + 25, w, h, 1.2); c.line(x1, y0 + 25 + h, x1 + w, y0 + 25, 1); c.line(x1 + 42, y0 + 25, x1 + 42, y0 + 25 + h, 1)
    c.arrow(x1, y0 + 17, x1 + 42, y0 + 17, 3, 0.7, both=True); c.text(x1 + 21, y0 + 14, 'x', 7, True, 'middle')
    c.arrow(x1 + 42, y0 + 17, x1 + w, y0 + 17, 3, 0.7, both=True); c.text(x1 + 76, y0 + 14, 'x + y', 7, True, 'middle')
    c.arrow(x1 + w + 8, y0 + 25, x1 + w + 8, y0 + 25 + h, 3, 0.7, both=True); c.text(x1 + w + 13, y0 + 50, 'x', 7, True)


@figure('moscow-p187-2', 200, 175, 'The 64 equals 65 paradox: an 8 by 8 square cut into pieces A, B, C, D, and the same pieces rearranged into a 5 by 13 rectangle')
def sixty_four_sixty_five(c):
    u = 10
    x0, y0 = 10, 40
    L = lambda a, b, p, q: c.line(x0 + a * u, y0 + b * u, x0 + p * u, y0 + q * u, 1.4)
    grid(c, x0, y0, 8, 8, u, 0.4, None); c.rect(x0, y0, 8 * u, 8 * u, 1.2)
    L(0, 3, 8, 3); L(0, 3, 8, 0); L(5, 3, 3, 8)       # two 8 by 3 triangles above, two trapezoids below
    for x, y, lab in ((x0 + 15, y0 + 15, 'A'), (x0 + 58, y0 + 25, 'C'), (x0 + 12, y0 + 60, 'B'), (x0 + 58, y0 + 62, 'D')): c.text(x, y, lab, 8, True)
    x1, y1 = 100, 70
    M = lambda a, b, p, q: c.line(x1 + a * u, y1 + b * u, x1 + p * u, y1 + q * u, 1.4)
    grid(c, x1, y1, 13, 5, u, 0.4, None); c.rect(x1, y1, 13 * u, 5 * u, 1.2)
    M(0, 5, 5, 3); M(5, 3, 5, 0); M(5, 3, 13, 0); M(0, 5, 8, 2); M(8, 2, 8, 5)
    for x, y, lab in ((x1 + 12, y1 + 20, 'B'), (x1 + 62, y1 + 15, 'A'), (x1 + 22, y1 + 44, 'C'), (x1 + 96, y1 + 36, 'D')): c.text(x, y, lab, 8, True)
