"""Yaglom Vol 2: redrawn figures (graphs, lattices and shaded areas; equations are not figures)."""


def axes(c, ox, oy, right, top, size=8):
    c.arrow(ox, oy, ox + right, oy, 5, 1.2); c.arrow(ox, oy, ox, oy - top, 5, 1.2)
    c.text(ox + right - 2, oy + 11, 'x', size, True); c.text(ox + 5, oy - top + 6, 'y', size, True); c.text(ox - 8, oy + 10, 'O', size, True)


@figure('yaglom-2-p15-1', 230, 220, 'Figure 2: a grid of unit squares with the x axis and y axis through O')
def grid_axes(c):
    u, x0, y0 = 28, 15, 15
    grid(c, x0, y0, 7, 5, u, 1)
    ox, oy = x0 + 2 * u, y0 + 3 * u
    c.line(x0 - 10, oy, x0 + 7 * u + 10, oy, 2); c.line(ox, y0 - 10, ox, y0 + 5 * u + 10, 2)
    c.text(ox + 4, oy + 10, 'O', 9, True); c.text(x0 + 7 * u + 4, oy - 4, 'x', 9, True); c.text(ox - 10, y0 - 2, 'y', 9, True)
    c.text(x0 + 3.5 * u, y0 + 5 * u + 24, 'Fig. 2', 9, anchor='middle', bold=True)


@figure('yaglom-2-p15-2', 310, 160, 'Figure 3: lattices with dots, (a) holding a thin parallelogram and (b) a non-convex lattice polygon')
def lattice_polygons(c):
    u = 18
    def lattice(x0, y0, cols, rows):
        grid(c, x0, y0, cols, rows, u, 0.6)
        for i in range(cols + 1):
            for j in range(rows + 1): dot(c, x0 + i * u, y0 + j * u, 1.5)
    lattice(10, 10, 5, 5); lattice(125, 10, 7, 5)
    L = lambda x0, y0, i, j: (x0 + i * u, y0 + (5 - j) * u)
    c.polygon([L(10, 10, 1, 1), L(10, 10, 3, 4), L(10, 10, 3, 5), L(10, 10, 1, 2)], 1.4)
    c.polygon([L(125, 10, 0, 3), L(125, 10, 2, 1), L(125, 10, 4, 5), L(125, 10, 5, 2), L(125, 10, 7, 1), L(125, 10, 2, 0)], 1.4)
    c.text(55, 122, 'a', 9, bold=True); c.text(188, 122, 'b', 9, bold=True); c.text(160, 140, 'Fig. 3', 9, anchor='middle', bold=True)


@figure('yaglom-2-p16-1', 170, 170, 'A circle with centre O containing a square lattice of dots; a small unit square sits at O and an arrow marks a radius')
def lattice_circle(c):
    cx, cy, R, u = 85, 85, 72, 16
    c.circle(cx, cy, R, 1.1)
    for i in range(-5, 6):
        for j in range(-5, 6):
            x, y = cx + i * u, cy + j * u
            if math.hypot(i * u, j * u) < R - 4 and (i, j) != (0, 0): dot(c, x, y, 1.6)
    c.rect(cx, cy - 7, 7, 7, 1); c.text(cx - 4, cy + 4, 'O', 9, True, 'end')
    c.arrow(cx, cy, cx + R * 0.707, cy - R * 0.707, 5, 0.9)


@figure('yaglom-2-p17-1', 160, 170, 'Figure 5: three straight lines; the half-plane beyond each line is hatched, leaving a triangle unhatched', fit=False)
def half_planes(c):
    W, H = 160, 150
    lines = [((10, 62), (155, 70), True), ((40, 5), (75, 150), False), ((132, 5), (95, 150), True)]
    for a, b, left in lines:
        segs = half_plane(a, b, left, W, H)
        c.hatch(segs, 4, 45, 0.5)
        ux, uy = unit(a, b); c.line(a[0] - ux * 200, a[1] - uy * 200, b[0] + ux * 200, b[1] + uy * 200, 1.3)
    c.rect(0, 0, W, H, 0, None)
    c.text(80, 165, 'Fig. 5', 9, anchor='middle', bold=True)


@figure('yaglom-2-p17-2', 110, 110, 'A small graph of sixteen dots joined by edges, with one pair of dots joined by two edges')
def small_graph(c):
    N = [(28, 6), (10, 16), (48, 18), (28, 22), (6, 34), (20, 34), (36, 32), (50, 36), (60, 30), (64, 42), (52, 48), (14, 46), (46, 60), (40, 66), (33, 65), (22, 68)]
    E = [(0, 1), (0, 2), (0, 3), (1, 4), (4, 5), (5, 6), (3, 6), (1, 5), (5, 11), (4, 11), (6, 7), (2, 8), (8, 9), (9, 10), (7, 10), (10, 12), (12, 13), (13, 15), (12, 14), (14, 15)]
    for i, j in E: segment(c, N[i], N[j], 1)
    c.curve([N[14], ((N[14][0] + N[15][0]) / 2, (N[14][1] + N[15][1]) / 2 + 5), N[15]], 1)
    for p in N: dot(c, *p, 1.6)


@figure('yaglom-2-p17-3', 160, 85, 'A broken line of five dots, a hexagon and a pentagon with dots at their vertices')
def dotted_shapes(c):
    line_pts = [(6, 62), (10, 42), (26, 28), (36, 20), (40, 6)]
    c.polyline(line_pts, 1.1); dots(c, line_pts, 1.6)
    hexa = regular_polygon(78, 40, 22, 6, -60); c.polygon(hexa, 1.1); dots(c, hexa, 1.6)
    penta = regular_polygon(130, 44, 20, 5, -100); c.polygon(penta, 1.1); dots(c, penta, 1.6)


def sperner(c, vertices, interior, labels_, shaded, caption_text, size=7):
    pts = vertices + interior
    tris = delaunay(pts)
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            if a < b or (b, a) not in []: segment(c, pts[a], pts[b], 0.9)
    if shaded is not None:
        best = min(tris, key=lambda t: sum(math.hypot(pts[i][0] - shaded[0], pts[i][1] - shaded[1]) for i in t))
        segs = [('M', *pts[best[0]]), ('L', *pts[best[1]]), ('L', *pts[best[2]])]
        c.hatch(segs, 2.5, 45, 0.5); c.path(segs, 0.9, close=True)
    c.polygon(vertices, 1.5)
    for p, lab in zip(pts, labels_):
        c.text(p[0] + 2, p[1] - 3, lab, size, bold=True)
    c.text((vertices[0][0] + vertices[2][0]) / 2, vertices[0][1] + 18, caption_text, 9, anchor='middle', bold=True)


@figure('yaglom-2-p18-1', 260, 150, 'Figure 7: a large triangle with vertices labelled 1, 2 and 3, subdivided into small triangles whose vertices carry labels 1, 2 or 3; one small triangle labelled 1, 2, 3 is hatched')
def sperner_7(c):
    V = [(12, 128), (120, 8), (248, 128)]
    I = [(80, 56), (62, 80), (95, 85), (118, 60), (140, 68), (120, 92), (110, 128), (162, 128), (180, 82), (160, 100), (200, 70), (195, 120), (215, 100), (150, 42)]
    L = ['1', '2', '3'] + ['2', '2', '1', '2', '3', '1', '1', '3', '1', '3', '3', '3', '3', '3']
    sperner(c, V, I, L, (112, 80), 'Fig. 7')


@figure('yaglom-2-p19-1', 240, 190, 'Figure 8: a large triangle with vertices 1, 2, 3, subdivided into small triangles with labelled vertices')
def sperner_8(c):
    V = [(10, 170), (105, 10), (230, 170)]
    I = [(80, 68), (100, 62), (125, 45), (65, 95), (95, 110), (85, 140), (120, 170), (150, 125), (160, 170), (175, 95), (130, 95), (145, 60)]
    L = ['1', '1', '3'] + ['2', '3', '3', '3', '1', '2', '3', '2', '1', '1', '2', '3']
    sperner(c, V, I, L, None, 'Fig. 8')


@figure('yaglom-2-p19-2', 110, 125, 'Figure 9: a square map divided into regions numbered 1 to 6 by irregular boundaries, with one narrow region hatched')
def region_map(c):
    c.rect(5, 5, 100, 100, 1.6)
    c.polyline([(5, 42), (28, 55), (44, 30), (58, 5)], 1.2); c.polyline([(28, 55), (18, 105)], 1.2)
    c.polyline([(44, 30), (70, 40), (78, 20), (90, 5)], 1.2); c.polyline([(70, 40), (105, 48)], 1.2)
    c.polyline([(70, 40), (62, 70), (78, 105)], 1.2); c.polyline([(62, 70), (40, 80), (36, 105)], 1.2)
    quad = [('M', 44, 50), ('L', 58, 46), ('L', 60, 90), ('L', 48, 95)]
    c.hatch(quad, 2.5, 60, 0.5); c.path(quad, 1, close=True)
    for x, y, n in ((36, 40, '1'), (20, 92, '2'), (62, 100, '3'), (70, 60, '4'), (82, 36, '5'), (70, 18, '6')): c.text(x, y, n, 9)
    c.text(55, 120, 'Fig. 9', 9, anchor='middle', bold=True)


@figure('yaglom-2-p28-1', 150, 160, 'Figure 14: a board of numbered cells in a staircase shape, chequered black and white, with the top-right torn away: rows read 4 5; 3 2 1; 2 3 0 1; 1 0 3 2 5; 0 1 2 3 4')
def grundy_board(c):
    rows = [['4', '5'], ['3', '2', '1'], ['2', '3', '0', '1'], ['1', '0', '3', '2', '5'], ['0', '1', '2', '3', '4']]
    u, x0, y0 = 24, 10, 10
    for j, row in enumerate(rows):
        for i, v in enumerate(row):
            black = (i + j) % 2 == 1
            c.rect(x0 + i * u, y0 + j * u, u, u, 1, 'black' if black else 'white')
            c.text(x0 + i * u + u / 2, y0 + j * u + u * 0.68, v, 12, anchor='middle', color='white' if black else 'black')
    c.line(x0, y0, x0, y0 + 5 * u + 4, 1.6); c.line(x0 - 2, y0 + 5 * u + 4, x0 + 5 * u + 10, y0 + 5 * u + 4, 1.6)
    c.curve([(x0, y0), (x0 + 2 * u, y0 + 2), (x0 + 3 * u, y0 + u), (x0 + 4 * u, y0 + 2 * u), (x0 + 5 * u, y0 + 3 * u), (x0 + 5 * u + 10, y0 + 5 * u + 4)], 1.4)
    c.text(x0 + 2.5 * u, y0 + 5 * u + 22, 'Fig. 14', 9, anchor='middle', bold=True)


@figure('yaglom-2-p29-1', 190, 100, 'Figure 15: a board of 3 rows and 8 columns with hatched counters in the third column of the lower two rows and the seventh column of the top row')
def counters_board(c):
    u, x0, y0 = 20, 10, 10
    grid(c, x0, y0, 8, 3, u, 1.4)
    for i, j in ((6, 0), (4, 1), (4, 2)):
        cx, cy = x0 + i * u + u / 2, y0 + j * u + u / 2
        c.hatch(c.ellipse_segments(cx, cy, 6, 6), 2.5, 45, 0.6); c.circle(cx, cy, 6, 1.2)
    c.text(x0 + 4 * u, y0 + 3 * u + 18, 'Fig. 15', 9, anchor='middle', bold=True)


@figure('yaglom-2-p30-1', 180, 150, 'Figure 16: the graph of a function on the interval from A to B, rising to a maximum M above P and dipping below the axis, with the axes through O')
def function_graph(c):
    ox, oy = 18, 108
    axes(c, ox, oy, 150, 95, 9)
    A, P, B = 42, 85, 130
    curve = [(A, 72), (48, 68), (60, 82), (70, 78), (78, 48), (P, 42), (92, 58), (100, 112), (106, 116), (114, 100), (122, 62), (B, 48)]
    c.curve(curve, 1.6, tension=0.3)
    c.line(A, oy, A, 72, 1.2); c.line(P, oy, P, 42, 1.2); c.line(B, oy, B, 48, 1.2)
    for x, lab in ((A, 'A'), (P, 'P'), (B, 'B')): c.text(x, oy + 12, lab, 9, True, 'middle')
    c.text(P, 36, 'M', 9, True, 'middle'); c.text(90, 140, 'Fig. 16', 9, anchor='middle', bold=True)


@figure('yaglom-2-p36-1', 140, 200, 'The parabola y = x squared with the area under it from 0 to a hatched, and a brace marking a below the axis')
def parabola_area(c):
    ox, oy = 36, 172; a = 108; k = 152 / 72 ** 2
    f = lambda x: oy - k * (x - ox) ** 2
    region = [('M', ox, oy)] + [('L', x, f(x)) for x in range(ox + 2, a + 1, 2)] + [('L', a, oy)]
    c.hatch(region, 3.5, 45, 0.5); c.path(region, 0, close=True)
    c.polyline([(x, f(x)) for x in range(22, 114, 2)], 1.4)
    axes(c, ox, oy, 100, 160, 9); c.line(a, oy, a, f(a), 1)
    c.text(84, 100, 'y = x', 8, True, rotate=-62); c.text(96, 82, '2', 5, True, rotate=-62)
    c.polyline([(ox, oy + 10), (ox, oy + 16), (a, oy + 16), (a, oy + 10)], 0.8); c.text((ox + a) / 2, oy + 27, 'a', 9, True, 'middle')


def hyperbola(c, ox, oy, C, x_from, x_to, stroke=1.4):
    pts = [(x, oy - C / (x - ox)) for x in range(x_from, x_to + 1, 2)]
    c.polyline(pts, stroke)


def shade_under(c, ox, oy, C, x1, x2, spacing=3.5, angle=45):
    region = [('M', x1, oy)] + [('L', x, oy - C / (x - ox)) for x in range(x1, x2 + 1, 2)] + [('L', x2, oy)]
    c.hatch(region, spacing, angle, 0.5); c.path(region, 0, close=True); c.line(x1, oy, x1, oy - C / (x1 - ox), 1); c.line(x2, oy, x2, oy - C / (x2 - ox), 1)


@figure('yaglom-2-p39-1', 270, 220, 'Figure 23: the hyperbola y = 1/x with two hatched areas S1 between a1 and b1 and S2 between a2 and b2')
def hyperbola_two_areas(c):
    ox, oy, C = 18, 190, 730
    shade_under(c, ox, oy, C, 28, 53); shade_under(c, ox, oy, C, 66, 145)
    hyperbola(c, ox, oy, C, 24, 200); axes(c, ox, oy, 200, 150, 9)
    for x, lab in ((28, 'a1'), (53, 'b1'), (66, 'a2'), (145, 'b2')): subscript(c, x - 4, oy + 12, lab[0], lab[1], 8)
    subscript(c, 32, 150, 'S', '1', 10); subscript(c, 100, 178, 'S', '2', 10)
    c.text(60, 110, 'y =', 9, True); fraction(c, 80, 108, '1', 'x', 8)
    c.text(120, 212, 'Fig. 23', 9, anchor='middle', bold=True)


@figure('yaglom-2-p39-2', 220, 160, 'Figure 24: the hyperbola y = 1/x with the area between a and b under the curve hatched')
def hyperbola_one_area(c):
    ox, oy, C = 10, 120, 868
    shade_under(c, ox, oy, C, 72, 138); hyperbola(c, ox, oy, C, 18, 200); axes(c, ox, oy, 200, 112, 9)
    c.text(72, oy + 12, 'a', 9, True, 'middle'); c.text(138, oy + 12, 'b', 9, True, 'middle')
    c.text(44, 80, 'y =', 9, True); fraction(c, 66, 78, '1', 'x', 8)
    c.text(100, 150, 'Fig. 24', 9, anchor='middle', bold=True)


@figure('yaglom-2-p40-1', 320, 160, 'Figure 25: two graphs of y = 1/x; in (a) the area F(z) from 1 to z is hatched, in (b) the area minus F(z) from z to 1')
def hyperbola_fz(c):
    for k, (z, lab, letter) in enumerate(((100, 'F(z)', 'a'), (34, '-F(z)', 'b'))):
        ox, oy, C = 14 + k * 160, 110, 520
        one = ox + 24
        x1, x2 = (one, z + k * 160) if k == 0 else (z + 160, one)
        shade_under(c, ox, oy, C, min(x1, x2), max(x1, x2)); hyperbola(c, ox, oy, C, ox + 8, ox + 135); axes(c, ox, oy, 140, 100, 8)
        c.text(one, oy + 10, '1', 7, True, 'middle'); c.text(z + k * 160, oy + 10, 'z', 7, True, 'middle')
        c.text((x1 + x2) / 2, oy - 6, lab, 7, True, 'middle', color='white' if k else 'black'); c.rect((x1 + x2) / 2 - 12, oy - 13, 24, 9, 0, 'white'); c.text((x1 + x2) / 2, oy - 6, lab, 7, True, 'middle')
        c.text(ox + 40, 60, 'y =', 8, True); fraction(c, ox + 58, 58, '1', 'x', 7)
        c.text(ox + 70, oy + 24, letter, 8, bold=True)


@figure('yaglom-2-p42-1', 320, 200, 'Figure 26: (a) the exponential curve y = a to the x with the area from 0 to b hatched; (b) the logarithm curve y = log a of x with the area from 1 to b hatched')
def exp_log_areas(c):
    ox, oy = 20, 150
    f = lambda x: oy - 12 * math.exp((x - ox) / 28)
    region = [('M', ox, oy)] + [('L', x, f(x)) for x in range(ox, ox + 81, 2)] + [('L', ox + 80, oy)]
    c.hatch(region, 3.5, 45, 0.5); c.path(region, 0, close=True); c.line(ox + 80, oy, ox + 80, f(ox + 80), 1)
    c.polyline([(x, f(x)) for x in range(ox - 14, ox + 92, 2)], 1.4); axes(c, ox, oy, 110, 140, 8)
    c.text(ox - 4, oy - 12 + 3, '1', 7, True, 'end'); c.text(ox + 40, 70, 'y = a', 8, True); c.text(ox + 62, 66, 'x', 5, True)
    c.polyline([(ox, oy + 10), (ox, oy + 16), (ox + 80, oy + 16), (ox + 80, oy + 10)], 0.8); c.text(ox + 40, oy + 27, 'b', 8, True, 'middle'); c.text(ox + 40, oy + 42, 'a.', 8, bold=True)
    ox2, oy2 = 180, 130
    g = lambda x: oy2 - 28 * math.log((x - ox2) / 14)
    region = [('M', ox2 + 14, oy2)] + [('L', x, g(x)) for x in range(ox2 + 14, ox2 + 121, 2)] + [('L', ox2 + 120, oy2)]
    c.hatch(region, 3.5, 45, 0.5); c.path(region, 0, close=True); c.line(ox2 + 120, oy2, ox2 + 120, g(ox2 + 120), 1)
    c.polyline([(x, g(x)) for x in range(ox2 + 6, ox2 + 136, 2)], 1.4); axes(c, ox2, oy2, 140, 90, 8)
    c.text(ox2 + 14, oy2 + 10, '1', 7, True, 'middle'); c.text(ox2 + 50, 80, 'y = log  x', 8, True); c.text(ox2 + 74, 84, 'a', 5, True)
    c.polyline([(ox2, oy2 + 14), (ox2, oy2 + 20), (ox2 + 120, oy2 + 20), (ox2 + 120, oy2 + 14)], 0.8); c.text(ox2 + 60, oy2 + 31, 'b', 8, True, 'middle'); c.text(ox2 + 60, oy2 + 46, 'b.', 8, bold=True)
    c.text(160, 195, 'Fig. 26', 9, anchor='middle', bold=True)


@figure('yaglom-2-p43-1', 220, 140, 'Figure 27: the curve y = log a of x over x, crossing the axis at 1, rising to a maximum and decaying; the area from 1 to b is hatched and arrows mark 1 and b')
def log_over_x(c):
    ox, oy = 16, 86
    f = lambda x: oy - 60 * math.log((x - ox) / 22) / ((x - ox) / 22)
    region = [('M', ox + 22, oy)] + [('L', x, f(x)) for x in range(ox + 22, ox + 149, 2)] + [('L', ox + 148, oy)]
    c.hatch(region, 3, 45, 0.5); c.path(region, 0, close=True); c.line(ox + 148, oy, ox + 148, f(ox + 148), 1)
    c.polyline([(x, f(x)) for x in range(ox + 16, ox + 186, 2)], 1.4); axes(c, ox, oy, 200, 76, 8)
    c.arrow(ox, oy - 20, ox + 22, oy - 20, 4, 0.8, both=True); c.text(ox + 11, oy - 23, '1', 7, True, 'middle')
    c.arrow(ox, oy + 22, ox + 148, oy + 22, 4, 0.8, both=True); c.rect(ox + 68, oy + 16, 12, 10, 0, 'white'); c.text(ox + 74, oy + 25, 'b', 8, True, 'middle')
    c.line(ox + 148, oy + 14, ox + 148, oy + 30, 0.8)
    c.text(ox + 60, 22, 'y =', 8, True); fraction(c, ox + 92, 20, 'log  x', 'x', 7); c.text(ox + 92, 16, 'a', 4, True)
    c.text(110, 130, 'Fig. 27', 9, anchor='middle', bold=True)
