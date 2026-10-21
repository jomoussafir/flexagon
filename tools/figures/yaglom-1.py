"""Yaglom Vol 1: redrawn figures."""


@figure('yaglom-1-p15-1', 130, 100, 'Figure 1: two overlapping circles A and B, both hatched, their common part cross-hatched')
def venn(c):
    A, rA, B, rB = (52, 46), 40, (100, 48), 28
    c.hatch(c.ellipse_segments(*A, rA, rA), 4, 45, 0.6); c.hatch(c.ellipse_segments(*B, rB, rB), 4, 45, 0.6)
    c.hatch(lens_segments(A, rA, B, rB), 4, -45, 0.6)
    c.circle(*A, rA, 1.6); c.circle(*B, rB, 1.6)
    c.text(A[0] - rA - 8, A[1] + 4, 'A', 11, True, 'end'); c.text(B[0] + rB + 4, B[1] + 4, 'B', 11, True)
    c.text(76, 92, 'Fig. 1', 9, anchor='middle', bold=True)


@figure('yaglom-1-p21-1', 125, 90, 'A hatched kidney-shaped region S with points A on the left and B on the right')
def kidney(c):
    pts = [(10, 24), (28, 12), (48, 22), (62, 40), (78, 32), (96, 10), (112, 14), (114, 30), (100, 50), (78, 62), (56, 66), (36, 62), (16, 48), (8, 36)]
    segs = c.curve_segments(pts, True, 0.3)
    c.hatch(segs, 3.5, 45, 0.6); c.path(segs, 1.6, close=True)
    dot(c, 22, 30, 1.6); c.text(26, 28, 'A', 9, True); dot(c, 100, 22, 1.6); c.text(104, 20, 'B', 9, True); c.text(50, 82, 'S', 10, True)


@figure('yaglom-1-p23-1', 190, 85, 'Two hexagons each cut into triangles: one by diagonals from a single vertex, the other by three diagonals in a zigzag')
def triangulations(c):
    L = [(8, 40), (34, 10), (60, 6), (78, 11), (88, 56), (60, 76)]
    c.polygon(L, 1.3)
    for p in L[:-1]:
        if p not in (L[0],): pass
    for p in (L[0], L[1], L[2], L[3]): segment(c, L[5], p, 1.1)
    R = [(104, 36), (128, 9), (150, 7), (180, 38), (150, 76), (100, 62)]
    c.polygon(R, 1.3)
    segment(c, R[0], R[2], 1.1); segment(c, R[0], R[3], 1.1); segment(c, R[5], R[3], 1.1)


@figure('yaglom-1-p27-1', 175, 90, 'A lattice of 10 by 4 unit squares with a dot at every node, from (0,0) at the bottom left to (m,n) at the top right')
def lattice_rectangle(c):
    u, x0, y0 = 14, 12, 18
    grid(c, x0, y0, 10, 4, u, 1)
    for i in range(11):
        for j in range(5): dot(c, x0 + i * u, y0 + j * u, 1.7)
    c.text(x0 - 6, y0 + 4 * u + 12, '(0,0)', 8, True); c.text(x0 + 10 * u + 2, y0 - 6, '(m,n)', 8, True, 'end')


@figure('yaglom-1-p28-1', 130, 100, 'Figure 7: a V-shaped lattice of squares standing on the vertex A, with arrows L up-left and R up-right')
def v_lattice(c):
    d = 9; A = (65, 70)
    node = lambda i, j: (A[0] + (i - j) * d, A[1] - (i + j) * d)
    for i in range(7):
        for j in range(7 - i):
            p = node(i, j)
            if i + 1 <= 6 - j: segment(c, p, node(i + 1, j), 1)
            if j + 1 <= 6 - i: segment(c, p, node(i, j + 1), 1)
            dot(c, *p, 1.3)
    c.arrow(A[0] - 22, A[1] - 2, A[0] - 32, A[1] - 16, 4, 0.8); c.text(A[0] - 36, A[1] + 2, 'L', 8, True)
    c.arrow(A[0] + 22, A[1] - 2, A[0] + 32, A[1] - 16, 4, 0.8); c.text(A[0] + 32, A[1] + 2, 'R', 8, True)
    c.text(A[0], A[1] + 12, 'A', 9, True, 'middle'); c.text(A[0] - 10, A[1] + 26, 'Fig. 7', 9, anchor='middle', bold=True)


@figure('yaglom-1-p39-1', 180, 70, 'Figure 8: a segment AB with points M, O and N at the quarter points; braces mark L/2 from A to O above and L/4 from M to O below')
def segment_braces(c):
    A, B = (12, 36), (168, 36); L = B[0] - A[0]
    c.line(*A, *B, 1.6)
    for t, lab in ((0, 'A'), (0.25, 'M'), (0.5, 'O'), (0.75, 'N'), (1, 'B')):
        x = A[0] + t * L; c.line(x, 32, x, 40, 1.2); c.text(x, 52, lab, 9, True, 'middle')
    c.polyline([(A[0], 26), (A[0], 22), (A[0] + L / 2, 22), (A[0] + L / 2, 26)], 0.8); c.text(A[0] + L / 4, 18, 'L/2', 8, True, 'middle')
    c.polyline([(A[0] + L / 4, 44), (A[0] + L / 4, 48), (A[0] + L / 2, 48), (A[0] + L / 2, 44)], 0.8); c.text(A[0] + 3 * L / 8, 60, 'L/4', 8, True, 'middle')
    c.text(130, 66, 'Fig. 8', 9, anchor='middle', bold=True)
