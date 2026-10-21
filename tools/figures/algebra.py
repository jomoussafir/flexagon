"""Challenging Problems in Algebra: redrawn figures (tables and diagrams; equations are not figures)."""


@figure('algebra-p25-1', 70, 140, 'A two-column table headed I and II: 19 and 23, 9 and 46, 4 and 92, 2 and 184, 1 and 368, with the total 437 below a rule')
def peasant_multiplication(c):
    c.text(20, 14, 'I', 11, anchor='middle'); c.text(48, 14, 'II', 11, anchor='middle')
    c.line(5, 19, 68, 19, 1.3); c.line(33, 10, 33, 128, 1.3)
    for k, (a, b) in enumerate(((19, 23), (9, 46), (4, 92), (2, 184), (1, 368))):
        c.text(26, 38 + k * 18, a, 11, anchor='end'); c.text(38, 38 + k * 18, b, 11)
    c.line(33, 112, 68, 112, 1.1); c.text(38, 128, '437', 11)


@figure('algebra-p33-1', 320, 170, 'Five small tables (a) to (e) of n and f(n) with fractional entries, and a challenge table with n = 1 1/2, 1, 1/2 and f(n) = 0, -1, -2')
def function_tables(c):
    tables = [('a', [('1/2', '1/2'), ('1/3', '2/3'), ('3/5', '2/5')]), ('b', [('1/2', '3/2'), ('1/3', '4/3'), ('2/5', '7/5')]), ('c', [('1/2', '0'), ('1/3', '1/3'), ('1/4', '1/2')]),
              ('d', [('2 3/4', '3 1/2'), ('2 1/4', '3'), ('1', '1 3/4')]), ('e', [('2 3/4', '2'), ('2 1/4', '1 1/2'), ('1', '1/4')])]

    def value(x, y, s):
        if '/' in s:
            whole, frac = (s.split(' ') if ' ' in s else ('', s)); num, den = frac.split('/')
            fraction(c, x + (4 if whole else 0), y - 3, num, den, 7, whole)
        else: c.text(x, y + 1, s, 9, anchor='middle')
    for k, (lab, rows) in enumerate(tables):
        x = 12 + k * 62
        c.text(x - 6, 14, f'({lab})', 8); c.text(x + 10, 14, 'n', 8, True, 'middle'); c.text(x + 34, 14, 'f(n)', 8, True, 'middle')
        c.line(x + 2, 18, x + 50, 18, 0.8); c.line(x + 22, 8, x + 22, 72, 0.8)
        for j, (n, fn) in enumerate(rows):
            value(x + 10, 34 + j * 17, n); value(x + 36, 34 + j * 17, fn)
    c.text(10, 96, 'Challenge', 9, bold=True); c.text(60, 96, 'Now try a slightly harder table.', 9)
    x0 = 100
    c.text(x0 + 10, 118, 'n', 8, True, 'middle'); c.text(x0 + 10, 136, 'f(n)', 8, True, 'middle')
    c.line(x0 + 22, 108, x0 + 22, 142, 0.8); c.line(x0, 125, x0 + 150, 125, 0.8)
    for j, (n, fn) in enumerate((('1 1/2', '0'), ('1', '-1'), ('1/2', '-2'))):
        value(x0 + 45 + j * 42, 118, n); c.text(x0 + 45 + j * 42, 139, fn, 9, anchor='middle')
        if j: c.line(x0 + 24 + j * 42, 108, x0 + 24 + j * 42, 142, 0.6)


@figure('algebra-p34-1', 140, 150, 'Problem 6-7: a 10 by 10 grid with axes, points at (0,1), (0,2), (0,3), (1,3), (1,2) labelled A, and (1,0), (2,0), (3,0)')
def lattice_points(c):
    u, x0, y0 = 13, 5, 5
    grid(c, x0, y0, 10, 10, u, 0.8)
    ox, oy = x0 + 2 * u, y0 + 8 * u
    c.arrow(ox, oy, ox, y0 + 2 * u - 4, 5, 1.6); c.arrow(ox, oy, x0 + 8 * u + 4, oy, 5, 1.6)
    c.text(ox - 6, y0 + 2 * u + 4, 'y', 8, True); c.text(x0 + 8 * u + 6, oy + 3, 'x', 8, True); c.text(ox - 5, oy + 9, '0', 7, bold=True)
    for i, j in ((0, 1), (0, 2), (0, 3), (1, 3), (1, 2), (1, 0), (2, 0), (3, 0)):
        x, y = ox + i * u, oy - j * u
        c.polygon([(x, y - 3), (x + 3, y), (x, y + 3), (x - 3, y)], 0, 'black')
    for n in (1, 2, 3): c.text(ox - 5, oy - n * u + 3, n, 7, anchor='end', bold=True); c.text(ox + n * u, oy + 10, n, 7, anchor='middle', bold=True)
    c.text(ox + u + 4, oy - 2 * u + 3, 'A', 8, bold=True)
    c.text(x0 + 5 * u, y0 + 10 * u + 14, '6-7', 9, anchor='middle', bold=True)


@figure('algebra-p60-1', 150, 130, 'Figure 16-8: from A a drop of 3, a run of 15 marked N B, a lower parallel marked S B, then a drop of 5 to B')
def path_figure(c):
    A, B = (18, 12), (110, 118)
    dot(c, *A, 2.4); dot(c, *B, 2.4); c.text(A[0] - 6, A[1] - 2, 'A', 9, True, 'end'); c.text(B[0] - 7, B[1] + 3, 'B', 9, True, 'end')
    c.line(A[0], A[1], A[0], 40, 1.5); c.text(A[0] - 6, 30, '3', 8, True, 'end'); right_angle(c, (A[0], 40), A, (40, 40), 5)
    c.line(A[0], 40, 110, 40, 1.5); c.text(65, 36, '15', 8, True, 'middle'); c.text(88, 36, 'N B', 8, True)
    c.line(44, 36, 44, 44, 1); c.polyline([(44, 44), (44, 52)], 1); c.line(44, 52, 44, 56, 1); c.text(44, 52, '1', 6, anchor='middle')
    c.line(18, 58, 110, 58, 1.5); c.text(88, 68, 'S B', 8, True); right_angle(c, (110, 58), (90, 58), (110, 80), 5)
    c.line(110, 58, 110, 118, 1.5); c.text(116, 90, '5', 8, True)
    c.text(125, 124, '16-8', 8, bold=True)


@figure('algebra-p71-1', 150, 120, 'Problem 19-10: six points P1 to P6 with every pair joined, a complete graph')
def complete_graph(c):
    pts6 = {1: (118, 52), 2: (92, 28), 3: (42, 16), 4: (16, 68), 5: (36, 108), 6: (100, 96)}
    for i in pts6:
        for j in pts6:
            if i < j: segment(c, pts6[i], pts6[j], 1.1)
    for i, p in pts6.items():
        dot(c, *p, 2.4)
        dx, dy = {1: (6, 2), 2: (4, -4), 3: (-4, -6), 4: (-16, 2), 5: (-12, 12), 6: (6, 10)}[i]
        subscript(c, p[0] + dx, p[1] + dy, 'P', i, 9)
    c.text(135, 112, '19-10', 8, bold=True)


@figure('algebra-p74-1', 230, 150, 'Problem 20-13: a triangular table with columns C1, C2, C3 and rows R1: 1; R2: 2, 3; R3: 4, 5, 6; continuing with dots')
def triangular_table(c):
    c.line(10, 24, 220, 24, 1); c.line(48, 8, 48, 140, 1)
    for k in range(3): subscript(c, 60 + k * 26, 18, 'C', k + 1, 8)
    for k in range(3): dot(c, 150 + k * 20, 15, 1.8)
    rows = [[1], [2, 3], [4, 5, 6]]
    for j, row in enumerate(rows):
        subscript(c, 20, 44 + j * 20, 'R', j + 1, 8)
        for k, v in enumerate(row): c.text(66 + k * 26, 44 + j * 20, v, 9, anchor='middle')
    for j in range(3):
        for k in range(4 + j): dot(c, 66 + k * 26 - (0 if k < 4 else 8 * (k - 3)), 100 + j * 15, 1.8)
        dot(c, 24, 100 + j * 15, 1.8)
    c.text(205, 140, '20-13', 8, bold=True)
