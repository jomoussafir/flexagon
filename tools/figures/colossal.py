"""The Colossal Book of Short Puzzles and Problems: redrawn figures.

Each function draws one book figure with the helpers injected by tools/redraw-figures.py
(Canvas methods, label/labels, dot, segment, right_angle, tick, grid, number_grid,
matchstick, match_grid, coin, chessboard, chess_piece, iso, cabinet, box, star, math).
"""

# ---- The Colossal Book of Short Puzzles and Problems ---------------------------

@figure('colossal-p25-1', 236, 282, 'Nine playing cards of hearts in a 3 by 3 magic square: 10, J, 6; 5, 9, K; Q, 7, 8')
def cards(c):
    ranks = [['10', 'J', '6'], ['5', '9', 'K'], ['Q', '7', '8']]
    pips = {'5': [(0, 0), (1, 0), (.5, .5), (0, 1), (1, 1)], '6': [(0, 0), (1, 0), (0, .5), (1, .5), (0, 1), (1, 1)],
            '7': [(0, 0), (1, 0), (0, .5), (1, .5), (0, 1), (1, 1), (.5, .25)], '8': [(0, 0), (1, 0), (0, .5), (1, .5), (0, 1), (1, 1), (.5, .25), (.5, .75)],
            '9': [(0, 0), (1, 0), (0, 1 / 3), (1, 1 / 3), (0, 2 / 3), (1, 2 / 3), (0, 1), (1, 1), (.5, .5)],
            '10': [(0, 0), (1, 0), (0, 1 / 3), (1, 1 / 3), (0, 2 / 3), (1, 2 / 3), (0, 1), (1, 1), (.5, 1 / 6), (.5, 5 / 6)]}
    w, h, gap = 60, 76, 15
    for row in range(3):
        for col in range(3):
            x, y = 8 + col * (w + gap), 8 + row * (h + gap)
            rank = ranks[row][col]
            c.rect(x, y, w, h, 1, None, radius=5)
            c.text(x + 4, y + 11, rank, 9); c.heart(x + 7, y + 17, 6)
            c.text(x + w - 4, y + h - 11, rank, 9, rotate=180); c.heart(x + w - 7, y + h - 17, 6)
            if rank in pips:
                for px, py in pips[rank]:
                    c.heart(x + 18 + px * (w - 36), y + 20 + py * (h - 40), 9)
            else:
                c.rect(x + 14, y + 16, w - 28, h - 32, 0.8)
                c.text(x + w / 2, y + h / 2 + 7, rank, 20, anchor='middle'); c.heart(x + w / 2, y + h / 2 + 16, 8)


@figure('colossal-p25-2', 220, 150, 'A desk calendar: two cubes showing the digits 2 and 5 on a stand labelled APRIL')
def cube_calendar(c):
    dx, dy = 18, -12          # oblique depth
    s = 46
    # Stand: a shallow box with the month on its front face.
    c.polygon([(20, 100), (200, 100), (200, 128), (20, 128)], 1.2)
    c.polygon([(20, 100), (20 + dx, 100 + dy), (200 + dx, 100 + dy), (200, 100)], 1.2, 'gray')
    c.polygon([(200, 100), (200 + dx, 100 + dy), (200 + dx, 128 + dy), (200, 128)], 1.2, 'gray')
    c.rect(70, 106, 80, 16, 0.8, radius=3); c.text(110, 118, 'APRIL', 10, anchor='middle')
    for x, digit in ((50, '2'), (118, '5')):
        y = 100 - s
        c.polygon([(x, y), (x + s, y), (x + s, y + s), (x, y + s)], 1.2)
        c.polygon([(x, y), (x + dx, y + dy), (x + s + dx, y + dy), (x + s, y)], 1.2)
        c.polygon([(x + s, y), (x + s + dx, y + dy), (x + s + dx, y + s + dy), (x + s, y + s)], 1.2, 'gray')
        c.text(x + s / 2, y + s / 2 + 10, digit, 28, anchor='middle')


@figure('colossal-p26-1', 230, 200, 'An 8 by 8 chessboard with two diagonally opposite corner squares cut off; the two removed squares lie beside it')
def mutilated_chessboard(c):
    cell, x0, y0 = 20, 40, 20
    for r in range(8):
        for col in range(8):
            if (r, col) in ((0, 0), (7, 7)): continue
            dark = (r + col) % 2 == 0
            c.rect(x0 + col * cell, y0 + r * cell, cell, cell, 0.8, 'gray' if dark else None)
    for cx, cy, angle in ((22, 14, -20), (218, 188, 25)):
        a = math.radians(angle); ca, sa = math.cos(a), math.sin(a)
        pts = [(cx + (px * ca - py * sa), cy + (px * sa + py * ca)) for px, py in ((-9, -9), (9, -9), (9, 9), (-9, 9))]
        c.polygon(pts, 1, 'gray')


@figure('colossal-p26-2', 200, 230, 'A 3 by 3 by 3 cube made of 27 small cubes, drawn with a square front face and receding top and side faces')
def termite_cube(c):
    n, s = 3, 38
    dx, dy = 0.5 * s * math.cos(math.radians(45)), -0.5 * s * math.sin(math.radians(45))
    ox, oy = 22, 212                                   # bottom-left corner of the front face
    P = lambda i, j, k: (ox + i * s + j * dx, oy - k * s + j * dy)   # i right, j back, k up
    c.polygon([P(0, 0, n), P(n, 0, n), P(n, n, n), P(0, n, n)], 1.4, 'light')
    c.polygon([P(n, 0, 0), P(n, n, 0), P(n, n, n), P(n, 0, n)], 1.4, 'gray')
    c.polygon([P(0, 0, 0), P(n, 0, 0), P(n, 0, n), P(0, 0, n)], 1.4, 'white')
    for t in (1, 2):
        c.line(*P(t, 0, 0), *P(t, 0, n), 0.8); c.line(*P(0, 0, t), *P(n, 0, t), 0.8)
        c.line(*P(t, 0, n), *P(t, n, n), 0.8); c.line(*P(0, t, n), *P(n, t, n), 0.8)
        c.line(*P(n, t, 0), *P(n, t, n), 0.8); c.line(*P(n, 0, t), *P(n, n, t), 0.8)


@figure('colossal-p27-1', 300, 330, 'Eight circles A to H joined by lines: A above B, C, D; E, F, G below them; H at the bottom')
def eight_circles(c):
    r = 26
    pos = {'A': (150, 40), 'B': (62, 125), 'C': (150, 125), 'D': (238, 125), 'E': (62, 205), 'F': (150, 205), 'G': (238, 205), 'H': (150, 290)}
    edges = ['AB', 'AC', 'AD', 'BC', 'CD', 'BE', 'CF', 'DG', 'BF', 'CE', 'CG', 'DF', 'EF', 'FG', 'EH', 'FH', 'GH']
    for p, q in edges:
        (x1, y1), (x2, y2) = pos[p], pos[q]
        n = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / n, (y2 - y1) / n
        c.line(x1 + ux * r, y1 + uy * r, x2 - ux * r, y2 - uy * r, 1.2)
    for name, (x, y) in pos.items():
        c.circle(x, y, r, 1.4, 'white')
        c.text(x - r + 2, y - r - 2, name, 12, italic=True)


@figure('colossal-p28-1', 300, 190, 'Two sheets of eight numbered squares: 1 8 7 4 over 2 3 6 5, and 1 8 2 7 over 4 5 3 6; a folded packet shows square 1 on top')
def folded_sheet(c):
    def grid(x0, y0, rows):
        cell = 30
        for r, row in enumerate(rows):
            for k, n in enumerate(row):
                c.rect(x0 + k * cell, y0 + r * cell, cell, cell, 1.2)
                c.text(x0 + k * cell + cell / 2, y0 + r * cell + cell / 2 + 6, n, 16, anchor='middle')
    grid(20, 10, [[1, 8, 7, 4], [2, 3, 6, 5]])
    grid(20, 110, [[1, 8, 2, 7], [4, 5, 3, 6]])
    # The folded packet: square 1 on top of a small stack.
    for k in (3, 2, 1):
        c.rect(200 + k * 3, 25 - k * 3, 36, 36, 1, 'white')
    c.rect(200, 25, 36, 36, 1.2, 'white'); c.text(218, 50, '1', 16, anchor='middle')


@figure('colossal-p29-1', 360, 70, 'A row of ten empty cells numbered 0 to 9 above')
def ten_cells(c):
    for k in range(10):
        c.text(20 + k * 32 + 16, 16, k, 11, anchor='middle')
        c.rect(20 + k * 32, 24, 32, 36, 1.2)


@figure('colossal-p32-1', 160, 150, 'Ten coins in a bowling-pin triangle: one, two, three and four per row')
def pennies(c):
    r, d = 15, 34
    for row in range(4):
        for k in range(row + 1):
            x = 80 + (k - row / 2) * d
            y = 24 + row * d * math.sin(math.radians(60))
            c.circle(x, y, r, 1.2)


@figure('colossal-p138-1', 260, 260, 'A dashed unit square with four right isosceles triangles attached pinwheel-fashion; legs are 1 and hypotenuses are the square root of 2')
def pinwheel(c):
    u, x0, y0 = 70, 95, 95
    TL, TR, BR, BL = (x0, y0), (x0 + u, y0), (x0 + u, y0 + u), (x0, y0 + u)
    c.polygon([TL, TR, BR, BL], 1.2, dash=(4, 3))
    c.polygon([TL, TR, (x0 + u, y0 - u)], 1.4)        # top: leg up from TR
    c.polygon([TR, BR, (x0 + 2 * u, y0 + u)], 1.4)    # right: leg right from BR
    c.polygon([BR, BL, (x0, y0 + 2 * u)], 1.4)        # bottom: leg down from BL
    c.polygon([BL, TL, (x0 - u, y0)], 1.4)            # left: leg left from TL
    def root2(x, y):   # a drawn radical sign, since the PDF base fonts have no √
        c.line(x - 9, y - 4, x - 6, y + 1, 1.1); c.line(x - 6, y + 1, x - 2, y - 11, 1.1); c.line(x - 2, y - 11, x + 7, y - 11, 1.1)
        c.text(x + 2.5, y, '2', 12, italic=True, anchor='middle')
    for x, y, s in ((x0 + u / 2, y0 - 4, 1), (x0 + u / 2, y0 + u + 13, 1), (x0 + u + 12, y0 + u / 2 + 4, 1), (x0 - 8, y0 + u / 2 + 4, 1),
                    (x0 + u + 10, y0 - u / 2 + 4, 1), (x0 + 1.5 * u, y0 + u + 14, 1), (x0 - 8, y0 + 1.5 * u + 4, 1), (x0 - u / 2, y0 - 5, 1)):
        c.text(x, y, s, 12, italic=True, anchor='middle')
    for x, y in ((x0 + u / 2 - 14, y0 - u / 2 - 2), (x0 + 1.5 * u + 16, y0 + u / 2 + 4), (x0 + u / 2 + 14, y0 + 1.5 * u + 10), (x0 - u / 2 - 16, y0 + u / 2 + 4)):
        root2(x, y)


@figure('colossal-p138-2', 260, 260, 'Four bugs A, B, C, D at the corners of a square of side 10, each crawling toward the next: A toward B, B toward C, C toward D, D toward A')
def amorous_bugs(c):
    A, B, C, D = (50, 50), (210, 50), (210, 210), (50, 210)

    def bug(cx, cy, angle):
        a = math.radians(angle); ca, sa = math.cos(a), math.sin(a)
        r = lambda x, y: (cx + x * ca - y * sa, cy + x * sa + y * ca)
        c.ellipse(cx, cy, 6.5, 4, 0, 'black', angle)
        c.circle(*r(7.5, 0), 2.4, 0, 'black')
        for x in (-3.5, 0.5, 4.5):
            for side in (1, -1):
                c.line(*r(x, side * 3.2), *r(x - 2.5, side * 7.5), 1)
        for side in (1, -1):
            c.line(*r(9.5, side * 1.2), *r(13, side * 3.5), 0.8)
    for p, q in ((A, B), (B, C), (C, D), (D, A)):
        c.arrow(*p, *q, gap=14)
    bug(*A, 0); bug(*B, 90); bug(*C, 180); bug(*D, 270)
    c.text(A[0] - 14, A[1] - 12, 'A', 12, True); c.text(B[0] + 4, B[1] - 12, 'B', 12, True)
    c.text(C[0] + 4, C[1] + 20, 'C', 12, True); c.text(D[0] - 14, D[1] + 20, 'D', 12, True)
    for x, y in ((130, 42), (224, 134), (130, 228), (30, 134)):
        c.text(x, y, '10', 11, anchor='middle')


@figure('colossal-p139-1', 300, 110, 'Three equal squares in a row; lines from the lower-left corner of each square to the upper-right corner of the last; the angles with the base are A, B and C')
def three_squares(c):
    s, x0, y0 = 80, 20, 15
    for k in range(3):
        c.rect(x0 + k * s, y0, s, s, 1.3)
    for k in range(3):
        c.line(x0 + k * s, y0 + s, x0 + 3 * s, y0, 1.3)
    for k, name in enumerate('ABC'):
        c.text(x0 + k * s + 12, y0 + s - 4, name, 12, italic=True)


@figure('colossal-p139-2', 300, 300, 'Three circles of equal radius with centres X, Y, Z meeting at a common point O; their other intersections are A, B, C')
def intersecting_circles(c):
    r, O = 70, (150, 150)
    centre = lambda deg: (O[0] + r * math.cos(math.radians(deg)), O[1] + r * math.sin(math.radians(deg)))
    X, Y, Z = centre(210), centre(330), centre(90)
    other = lambda P, Q: (P[0] + Q[0] - O[0], P[1] + Q[1] - O[1])
    A, B, C = other(X, Y), other(Y, Z), other(Z, X)
    for P in (X, Y, Z):
        c.circle(*P, r, 1.2)
    for P, name, dx, dy in ((X, 'X', -14, 4), (Y, 'Y', 8, 4), (Z, 'Z', 8, 4), (O, 'O', -14, -4), (A, 'A', 6, -5), (B, 'B', 6, 12), (C, 'C', -16, 12)):
        c.circle(*P, 1.8, 0, 'black')
        c.text(P[0] + dx, P[1] + dy, name, 12, italic=True)


# ---- suit symbols for card figures ---------------------------------------------
def spade(c, cx, cy, s):
    with c.scaled(1, -1, cx, cy):
        c.heart(cx, cy + s * 0.08, s)
    c.polygon([(cx - s * 0.18, cy + s * 0.55), (cx + s * 0.18, cy + s * 0.55), (cx, cy + s * 0.1)], 0, 'black')


def club(c, cx, cy, s):
    r = s * 0.27
    for dx, dy in ((0, -0.26), (-0.27, 0.12), (0.27, 0.12)):
        c.circle(cx + dx * s, cy + dy * s, r, 0, 'black')
    c.polygon([(cx - s * 0.14, cy + s * 0.55), (cx + s * 0.14, cy + s * 0.55), (cx, cy + s * 0.05)], 0, 'black')


def diamond(c, cx, cy, s):
    c.polygon([(cx, cy - s * 0.52), (cx + s * 0.38, cy), (cx, cy + s * 0.52), (cx - s * 0.38, cy)], 0, 'black')


def suit(c, kind, cx, cy, s):
    {'h': c.heart, 's': lambda x, y, z: spade(c, x, y, z), 'c': lambda x, y, z: club(c, x, y, z), 'd': lambda x, y, z: diamond(c, x, y, z)}[kind](cx, cy, s)


def card_fan(c, cx, cy, cards, w=44, h=64, spread=14):
    """cards: list of (rank, suit letter); fanned about a pivot below the cards."""
    n = len(cards)
    for k, (rank, kind) in enumerate(cards):
        angle = (k - (n - 1) / 2) * spread
        with c.rotated(angle, cx, cy + h * 1.6):
            x, y = cx - w / 2, cy - h / 2
            c.rect(x, y, w, h, 1, 'white', radius=4)
            c.text(x + 4, y + 11, rank, 9, bold=True)
            suit(c, kind, x + 8, y + 19, 7)
            if rank in ('K', 'Q', 'J'):
                c.rect(x + 11, y + 15, w - 22, h - 30, 0.7)
                c.text(x + w / 2, y + h / 2 + 5, rank, 15, anchor='middle')
            else:
                suit(c, kind, x + w / 2 + 2, y + h / 2, 14)


@figure('colossal-p64-1', 300, 100, 'Two fans of five playing cards: 6, 5, 4, 3, 2 of alternating spades and hearts; a king and four aces')
def card_fans(c):
    card_fan(c, 72, 48, [('6', 's'), ('5', 'h'), ('4', 's'), ('3', 'h'), ('2', 's')])
    card_fan(c, 222, 48, [('K', 's'), ('A', 'h'), ('A', 'c'), ('A', 'd'), ('A', 's')])


@figure('colossal-p83-1', 120, 100, 'Three matches: two leaning together in a V and one standing upright')
def three_matches(c):
    matchstick(c, 50, 85, 22, 15); matchstick(c, 58, 85, 86, 15); matchstick(c, 102, 85, 102, 15)


@figure('colossal-p129-2', 200, 200, 'A square with two lines from its upper-right corner, one to the left side and one to the bottom side')
def square_two_lines(c):
    c.rect(20, 20, 160, 160, 1.4)
    c.line(180, 20, 20, 20 + 160 * 0.63, 1.3); c.line(180, 20, 20 + 160 * 0.36, 180, 1.3)


@figure('colossal-p129-3', 220, 200, 'A regular hexagon circumscribed about a circle, with a smaller regular hexagon inscribed in the circle')
def hexagon_circle_hexagon(c):
    cx, cy, r = 110, 100, 72
    c.polygon(regular_polygon(cx, cy, r / math.cos(math.radians(30)), 6, 0), 1.6)
    c.circle(cx, cy, r, 1.1)
    c.polygon(regular_polygon(cx, cy, r, 6, -60), 1.6)


@figure('colossal-p130-2', 150, 240, 'A stadium of width 2 overlapped by a circle of diameter 2 at its middle; the parts of the stadium outside the circle are shaded')
def stadium_circle(c):
    u, cx, cy = 40, 65, 120
    stadium = c.arc_segments(cx, cy - 1.4 * u, u, 180, 360) + [('L', cx + u, cy + 1.4 * u)] + c.arc_segments(cx, cy + 1.4 * u, u, 0, 180)[1:] + [('L', cx - u, cy - 1.4 * u)]
    # Shade the stadium, then cover the circle.
    c.path(stadium, 1.3, 'light', close=True)
    c.hatch(stadium, 4, 45, 0.5)
    c.circle(cx, cy, u, 1.4, 'white')
    c.text(cx + u + 12, cy + 4, '2', 11, bold=True); c.line(cx + u + 5, cy - u, cx + u + 5, cy + u, 0.8)
    c.line(cx - u, cy + 2.6 * u, cx + u, cy + 2.6 * u, 0.8); c.text(cx, cy + 2.6 * u + 13, '2', 11, bold=True, anchor='middle')


@figure('colossal-p131-1', 260, 150, 'A circle with two tangents from an external point C touching at Y and X; a third tangent at P meets them at A and B; the lengths from A to C and from B to C are 10')
def tangents_from_point(c):
    cx, cy, r = 70, 75, 42
    C = (245, 75)
    d = C[0] - cx; ang = math.degrees(math.asin(r / d))
    Y = (cx + r * math.sin(math.radians(ang)), cy - r * math.cos(math.radians(ang)))
    X = (cx + r * math.sin(math.radians(ang)), cy + r * math.cos(math.radians(ang)))
    c.circle(cx, cy, r, 1.3)
    for T in (Y, X):
        ux, uy = unit(C, T); c.line(C[0], C[1], T[0] + ux * 40, T[1] + uy * 40, 1.3)
    # Tangent at P (angle 20 degrees on the right of the circle).
    t = math.radians(-20); P = (cx + r * math.cos(t), cy + r * math.sin(t))
    tx, ty = -math.sin(t), math.cos(t)
    A = (P[0] - tx * 30, P[1] - ty * 30); B = (P[0] + tx * 52, P[1] + ty * 52)
    c.line(*A, *B, 1.3)
    dot(c, *P, 1.8)
    labels(c, {'Y': Y, 'X': X, 'A': A, 'B': B, 'P': P, 'C': C}, {'Y': 'nw', 'X': 'sw', 'A': 'ne', 'B': 'se', 'P': 'w', 'C': 'e'}, 10, False)
    for p, q, lab in ((A, C, '10'), (B, C, '10')):
        ux, uy = unit(p, q); nx, ny = -uy, ux
        if q is C and p is A: nx, ny = -nx, -ny
        off = 9
        c.line(p[0] + nx * off, p[1] + ny * off, q[0] + nx * off, q[1] + ny * off, 0.6)
        m = midpoint(p, q); c.text(m[0] + nx * 18, m[1] + ny * 18 + 4, lab, 10, bold=True, anchor='middle')


@figure('colossal-p131-2', 340, 240, 'A square whose four quadrants are striped with nested right angles in different orientations, and a Greek cross outline beside it')
def striped_square(c):
    s, x0, y0, n = 100, 10, 20, 7
    for qx, qy, corner in ((0, 0, 'tl'), (1, 0, 'tr'), (0, 1, 'bl'), (1, 1, 'br')):
        X, Y = x0 + qx * s, y0 + qy * s
        c.rect(X, Y, s, s, 1.2)
        for k in range(1, n + 1):
            d = k * s / (n + 1)
            if corner == 'tl': c.polyline([(X, Y + d), (X + d, Y + d), (X + d, Y)], 0.9)
            elif corner == 'tr': c.polyline([(X + s - d, Y), (X + s - d, Y + d), (X + s, Y + d)], 0.9)
            elif corner == 'bl': c.polyline([(X, Y + s - d), (X + d, Y + s - d), (X + d, Y + s)], 0.9)
            else: c.polyline([(X + s - d, Y + s), (X + s - d, Y + s - d), (X + s, Y + s - d)], 0.9)
    a, bx, by = 20, 285, 100
    c.polygon([(bx - a / 2, by - 1.5 * a), (bx + a / 2, by - 1.5 * a), (bx + a / 2, by - a / 2), (bx + 1.5 * a, by - a / 2), (bx + 1.5 * a, by + a / 2),
               (bx + a / 2, by + a / 2), (bx + a / 2, by + 1.5 * a), (bx - a / 2, by + 1.5 * a), (bx - a / 2, by + a / 2), (bx - 1.5 * a, by + a / 2),
               (bx - 1.5 * a, by - a / 2), (bx - a / 2, by - a / 2)], 1)


@figure('colossal-p132-1', 200, 180, 'A quarter circle of radius 10 centred at D with an inscribed rectangle ABCD, A on the vertical radius, B on the arc and C on the horizontal radius; the diagonal AC is drawn and DC and the rest of the radius are 5 each')
def quarter_circle_rectangle(c):
    D = (30, 150); R = 140
    c.line(D[0], D[1], D[0], D[1] - R - 8, 1.2); c.line(D[0], D[1], D[0] + R + 25, D[1], 1.2)
    c.arc(D[0], D[1], R, -90, 0, 1.3)
    C = (D[0] + R / 2, D[1]); B = (C[0], D[1] - math.sqrt(R * R - (R / 2) ** 2)); A = (D[0], B[1])
    c.polygon([A, B, C, D], 1.5); c.line(*A, *C, 1.5)
    labels(c, {'A': A, 'B': B, 'C': C, 'D': D}, {'A': 'w', 'B': 'ne', 'C': 's', 'D': 'sw'}, 11, False)
    c.text((D[0] + C[0]) / 2, D[1] + 14, '5', 10, True, 'middle'); c.text(C[0] + R / 4, D[1] + 14, '5', 10, True, 'middle')


@figure('colossal-p132-2', 160, 160, 'A circle divided by an S-shaped curve of two semicircles into a dark region and a light region of equal area')
def yin_yang(c):
    cx, cy, r = 80, 80, 65
    with c.rotated(-45, cx, cy):
        dark = [('M', cx, cy - r)] + c.arc_segments(cx, cy, r, -90, 90)[1:] + c.arc_segments(cx, cy + r / 2, r / 2, 90, -90)[1:] + c.arc_segments(cx, cy - r / 2, r / 2, 90, 270)[1:]
        c.path(dark, 0, 'black', close=True)
        c.circle(cx, cy, r, 1.2)


@figure('colossal-p135-1', 230, 200, 'A 3-inch square with a corner of a 4-inch square at its centre D; the overlap of the squares is shaded; the sides of the small square are cut at B, 1 inch from A and 2 inches from C')
def overlapping_squares(c):
    u = 30; x0, y0 = 20, 30
    A, C = (x0 + 3 * u, y0), (x0 + 3 * u, y0 + 3 * u)
    D = (x0 + 1.5 * u, y0 + 1.5 * u)
    B = (x0 + 3 * u, y0 + u); E = (x0 + 2 * u, y0 + 3 * u)
    c.rect(x0, y0, 3 * u, 3 * u, 1.3)
    c.polygon([D, B, C, E], 0.8, 'gray')
    ang = math.degrees(math.atan2(B[1] - D[1], B[0] - D[0]))
    with c.rotated(ang, *D):
        c.rect(D[0], D[1], 4 * u, 4 * u, 1.3)
    labels(c, {'A': A, 'B': B, 'C': C, 'D': D}, {'A': 'ne', 'B': 'e', 'C': 'se', 'D': 'w'}, 10, False)
    c.text(x0 - 6, y0 + 1.5 * u + 4, '3″', 9, anchor='end'); c.text(A[0] + 6, y0 + u / 2 + 3, '1″', 9); c.text(C[0] + 6, y0 + 2 * u + 3, '2″', 9)
    far = (D[0] + 4 * u * math.cos(math.radians(ang + 45)) * math.sqrt(2) / 2 * 2, D[1])
    c.text(x0 + 3 * u + 4 * u * 0.95, y0 + 1.1 * u, '4″', 9)


@figure('colossal-p135-2', 200, 190, 'Three equal circles, each passing near the centres of the other two, with their three inner intersection points marked')
def three_circles(c):
    r = 52; cx, cy = 100, 92
    centres = [(cx - r / 2, cy - r * 0.42), (cx + r / 2, cy - r * 0.42), (cx, cy + r * 0.45)]
    for p in centres: c.circle(*p, r, 1.2)
    # Inner pairwise intersections.
    for i, j in ((0, 1), (1, 2), (2, 0)):
        (x1, y1), (x2, y2) = centres[i], centres[j]
        d = math.hypot(x2 - x1, y2 - y1); a = d / 2; h = math.sqrt(r * r - a * a)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        for sgn in (1, -1):
            px, py = mx + sgn * h * (y2 - y1) / d, my - sgn * h * (x2 - x1) / d
            third = centres[3 - i - j]
            if math.hypot(px - third[0], py - third[1]) < r: dot(c, px, py, 2.4)


@figure('colossal-p137-1', 300, 190, 'Ten coins in a triangle with the top coin moved, and ten coins in a ring with one coin moved; arrows show the moves')
def penny_moves(c):
    r, d = 13, 28
    for row in range(4):
        for k in range(row + 1):
            coin(c, 60 + (k - row / 2) * d, 60 + row * d * 0.87, r)
    coin(c, 60, 24, r); c.arrow(78, 20, 100, 40, 6, 1)
    for k in range(9):
        a = math.radians(-90 + k * 40 + 20)
        coin(c, 215 + 48 * math.cos(a), 95 + 48 * math.sin(a), r)
    coin(c, 180, 36, r); c.arrow(196, 28, 222, 24, 6, 1)


@figure('colossal-p142-1', 200, 200, 'A regular octahedron built from twelve matches, seen with a horizontal square in the middle')
def match_octahedron(c):
    T, Bt = (100, 12), (100, 188)
    L, R, F, Kp = (14, 92), (186, 108), (118, 128), (82, 72)
    for p, q in ((L, R), (R, F), (F, Kp), (Kp, L)):
        segment(c, p, q, 7)
    for p in (L, R, F, Kp):
        c.line(T[0], T[1], p[0], p[1], 3.5); c.line(Bt[0], Bt[1], p[0], p[1], 3.5)
    c.line(L[0], L[1], F[0], F[1], 7); c.line(Kp[0], Kp[1], R[0], R[1], 7)
    for p in (T, Bt, L, R, F, Kp): dot(c, *p, 3.2)


@figure('colossal-p162-1', 280, 170, 'A 6 by 6 by 6 cube of unit cubes beside a 4 by 2 by 1 block')
def cube_and_block(c):
    P = iso(80, 160, 14)
    box(c, P, 6, 6, 6, 1.2, ('white', 'white', 'white'), subdivide=True)
    for k, t in ((P(3, -0.8, 0)[0], P(3, -0.8, 0)[1]), ):
        pass
    c.text(P(3, 0, 0)[0] + 4, P(3, 0, 0)[1] + 16, '6', 11, bold=True, anchor='middle')
    c.text(P(6, 3, 0)[0] + 10, P(6, 3, 0)[1] + 14, '6', 11, bold=True, anchor='middle')
    c.text(P(0, 0, 3)[0] - 12, P(0, 0, 3)[1] + 4, '6', 11, bold=True, anchor='middle')
    Q = iso(205, 158, 14)
    box(c, Q, 4, 2, 1, 1.2, ('white', 'white', 'white'), subdivide=True)
    c.text(Q(2, 0, 0)[0] + 2, Q(2, 0, 0)[1] + 16, '4', 11, bold=True, anchor='middle')
    c.text(Q(4, 1, 0)[0] + 10, Q(4, 1, 0)[1] + 13, '2', 11, bold=True, anchor='middle')
    c.text(Q(4, 2, 0.5)[0] + 9, Q(4, 2, 0.5)[1] + 4, '1', 11, bold=True)


@figure('colossal-p163-1', 200, 180, 'A cube with dashed lines dividing each visible face into nine squares, a 3 by 3 by 3 block')
def dashed_cube(c):
    P = cabinet(25, 165, 38, 0.6, 40)
    n = 3
    c.polygon([P(0, 0, n), P(n, 0, n), P(n, n, n), P(0, n, n)], 1.4)
    c.polygon([P(n, 0, 0), P(n, n, 0), P(n, n, n), P(n, 0, n)], 1.4)
    c.polygon([P(0, 0, 0), P(n, 0, 0), P(n, 0, n), P(0, 0, n)], 1.4)
    for t in (1, 2):
        c.line(*P(t, 0, 0), *P(t, 0, n), 1, (4, 3)); c.line(*P(0, 0, t), *P(n, 0, t), 1, (4, 3))
        c.line(*P(t, 0, n), *P(t, n, n), 1, (4, 3)); c.line(*P(0, t, n), *P(n, t, n), 1, (4, 3))
        c.line(*P(n, t, 0), *P(n, t, n), 1, (4, 3)); c.line(*P(n, 0, t), *P(n, n, t), 1, (4, 3))


@figure('colossal-p163-2', 220, 300, 'A board with a square, a round and a triangular hole, and a single plug that fits all three: a solid with a circular base rising to a straight ridge')
def plug_board(c):
    x, y, w, h, dx, dy = 20, 20, 60, 270, 10, -7
    c.polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], 1.3, 'white')
    c.polygon([(x, y), (x + dx, y + dy), (x + w + dx, y + dy), (x + w, y)], 1.3, 'light')
    c.polygon([(x + w, y), (x + w + dx, y + dy), (x + w + dx, y + h + dy), (x + w, y + h)], 1.3, 'gray')
    s = 34
    c.rect(x + 13, y + 30, s, s, 1.2); c.rect(x + 16, y + 33, s, s, 0.7)
    c.circle(x + 30, y + 120, 17, 1.2); c.circle(x + 32, y + 122, 17, 0.7)
    c.polygon([(x + 30, y + 185), (x + 13, y + 219), (x + 47, y + 219)], 1.2); c.polygon([(x + 32, y + 191), (x + 19, y + 216), (x + 45, y + 216)], 0.7)
    # The plug: base ellipse, two side lines to a ridge on top.
    bx, by = 150, 170
    c.ellipse(bx, by, 36, 12, 1.2)
    ridge = ((bx + 10, by - 75), (bx + 34, by - 60))
    c.line(bx - 36, by, ridge[0][0], ridge[0][1], 1.2); c.line(bx + 36, by, ridge[1][0], ridge[1][1], 1.2)
    c.line(*ridge[0], *ridge[1], 1.3)
    for k in range(1, 12):
        t = k / 12; a = math.radians(180 + 180 * t)
        px, py = bx + 36 * math.cos(a), by + 12 * math.sin(a)
        c.line(px, py, ridge[0][0] + (ridge[1][0] - ridge[0][0]) * t, ridge[0][1] + (ridge[1][1] - ridge[0][1]) * t, 0.5)
    c.ellipse(bx, by, 36, 12, 0.8, dash=(3, 3))


@figure('colossal-p165-1', 240, 230, 'Three solids with hidden edges dashed: a triangular pyramid, a square pyramid and a triangular prism')
def three_solids(c):
    # Tetrahedron.
    A, B, C, D = (60, 10), (12, 90), (118, 72), (50, 112)
    c.polyline([B, A, C], 1.3); c.line(*A, *D, 1.3); c.line(*B, *D, 1.3); c.line(*C, *D, 1.3); c.line(*B, *C, 1, (4, 3))
    # Square pyramid.
    T, P1, P2, P3, P4 = (182, 28), (140, 118), (190, 132), (232, 122), (200, 100)
    c.polygon([T, P1, P2, P3], 1.3); c.line(*T, *P4, 1, (4, 3)); c.line(*P1, *P4, 1, (4, 3)); c.line(*P3, *P4, 1, (4, 3))
    # Triangular prism.
    E, F, G = (70, 120), (122, 122), (98, 140)
    H, I, J = (44, 200), (108, 212), (88, 228)
    c.polygon([E, F, G], 1.3); c.line(*E, *H, 1.3); c.line(*F, *I, 1.3); c.line(*G, *J, 1.3)
    c.line(*H, *J, 1.3); c.line(*J, *I, 1.3); c.line(*H, *I, 1, (4, 3))


@figure('colossal-p166-1', 200, 200, 'Two equal cylinders crossing at right angles, one vertical and one horizontal')
def crossed_cylinders(c):
    cx, cy, r = 100, 100, 30
    c.ellipse(cx, 22, r, 9, 1.2)
    c.line(cx - r, 22, cx - r, 70, 1.2); c.line(cx + r, 22, cx + r, 70, 1.2)
    c.line(cx - r, 130, cx - r, 178, 1.2); c.line(cx + r, 130, cx + r, 178, 1.2)
    with c.scaled(1, 0.3, cx, 178):
        c.arc(cx, 178, r, 0, 180, 1.2)
    # Horizontal cylinder: right end visible, left end dashed.
    c.line(cx + r, 70, 182, 70, 1.2); c.line(cx + r, 130, 182, 130, 1.2); c.ellipse(182, 100, 9, 30, 1.2)
    c.line(18, 70, cx - r, 70, 1.2, (4, 3)); c.line(18, 130, cx - r, 130, 1.2, (4, 3))
    c.path(c.ellipse_segments(18, 100, 9, 30), 1, None, (4, 3), close=True)


@figure('colossal-p187-1', 300, 100, 'Three squares: one holding a bent strip with a dashed corner, one as a triangle with an inner trapezoid and dashed apex, and one plain')
def three_square_dissections(c):
    s = 80
    c.rect(10, 10, s, s, 1.2)
    c.polyline([(10, 10), (10 + s * 0.45, 10), (10 + s * 0.45, 10 + s * 0.25), (10 + s * 0.75, 10 + s * 0.25), (10 + s * 0.75, 10 + s * 0.5), (10 + s * 0.45, 10 + s * 0.5), (10 + s * 0.45, 10 + s * 0.9)], 1.2)
    c.line(10 + s * 0.2, 10 + s * 0.25, 10 + s * 0.2, 10 + s * 0.9, 1.2); c.line(10 + s * 0.2, 10 + s * 0.25, 10 + s * 0.45, 10 + s * 0.25, 1.2)
    c.line(10 + s * 0.45, 10, 10 + s, 10, 1, (4, 3)); c.line(10 + s, 10, 10 + s, 10 + s * 0.4, 1, (4, 3))
    x0 = 110
    c.polygon([(x0, 90), (x0 + 110, 90), (x0 + 55, 10)], 1.2)
    c.line(x0 + 22, 58, x0 + 55, 10, 1, (4, 3)); c.line(x0 + 88, 58, x0 + 55, 10, 1, (4, 3))
    c.polygon([(x0 + 22, 58), (x0 + 88, 58), (x0 + 74, 90), (x0 + 36, 90)], 1.2)
    c.rect(235, 10, s, s, 1.2)


@figure('colossal-p188-1', 250, 120, 'An isosceles trapezoid divided into four congruent smaller trapezoids')
def trapezoid_dissection(c):
    k = 0.5
    T = lambda x, y: (10 + (x - 20) * k, 5 + (y - 560) * k)
    big = [T(20, 770), T(500, 770), T(380, 560), T(140, 560)]
    c.polygon(big, 1.3)
    c.polyline([T(140, 560), T(195, 660), T(315, 660), T(380, 560)], 1.2)
    c.line(*T(195, 660), *T(140, 770), 1.2); c.line(*T(315, 660), *T(375, 770), 1.2)


@figure('colossal-p37-1', 350, 200, 'Ten arrangements of numbered coins in triangles: two of three coins, four of six coins and four of ten coins')
def numbered_coin_triangles(c):
    r, d = 11, 23

    def triangle(cx, top, rows):
        for j, row in enumerate(rows):
            for k, n in enumerate(row):
                coin(c, cx + (k - (len(row) - 1) / 2) * d, top + j * d * 0.87, r, n)

    def inverted(cx, top, rows):
        for j, row in enumerate(rows):
            for k, n in enumerate(row):
                coin(c, cx + (k - (len(row) - 1) / 2) * d, top + j * d * 0.87, r, n)
    inverted(150, 14, [[3, 2], [1]]); inverted(210, 14, [[3, 1], [2]])
    for cx, rows in ((50, [[6, 2, 5], [4, 3], [1]]), (120, [[2, 6, 5], [4, 1], [3]]), (190, [[6, 1, 4], [5, 3], [2]]), (260, [[1, 6, 4], [5, 2], [3]])):
        triangle(cx, 62, rows)
    for cx, rows in ((50, [[6, 1, 10, 8], [5, 9, 2], [4, 7], [3]]), (135, [[6, 10, 1, 8], [4, 9, 7], [5, 2], [3]]),
                     (220, [[8, 3, 10, 9], [5, 7, 1], [2, 6], [4]]), (305, [[8, 10, 3, 9], [2, 7, 6], [5, 1], [4]])):
        triangle(cx, 128, rows)


@figure('colossal-p84-1', 260, 270, 'A staircase path numbering the lattice points 1 to 59, rising in steps of six beside a vertical and a horizontal boundary')
def staircase_path(c):
    u = 10.5; ox, oy = 18, 250
    pos = {1: (0, 0), 2: (1, -1), 3: (2, -2), 4: (3, -2), 5: (3, -3), 6: (3, -4)}
    for k in range(9):
        col, row = 4 + 2 * k, -4 - 2 * k
        for n, (dc, dr) in zip(range(7 + 6 * k, 13 + 6 * k), ((0, 0), (0, -1), (0, -2), (1, -2), (1, -1), (2, -1))):
            if n <= 59: pos[n] = (col + dc, row + dr)
    P = lambda n: (ox + pos[n][0] * u, oy + pos[n][1] * u)
    for n in range(1, 59):
        p, q = P(n), P(n + 1)
        ux, uy = unit(p, q)
        c.line(p[0] + ux * 4.5, p[1] + uy * 4.5, q[0] - ux * 4.5, q[1] - uy * 4.5, 0.8)
    for n in range(1, 60):
        x, y = P(n); c.text(x, y + 2.5, n, 6.5, False, 'middle', 0, True)
    c.line(ox - 10, oy + 8, ox + 23 * u, oy + 8, 1.2); c.line(ox + 23 * u, oy + 8, ox + 23 * u, 8, 1.2)
    x59, y59 = P(59); c.polyline([(x59, y59 - 6), (x59, y59 - 16), (x59 + 8, y59 - 20), (x59 + 12, y59 - 12)], 0.8)


@figure('colossal-p129-1', 150, 120, 'Nine matches forming three separate small triangles arranged as a larger triangle, one above two')
def nine_match_triangles(c):
    def tri(cx, top, s=46):
        h = s * 0.87
        matchstick(c, cx - s / 2 + 4, top + h, cx - 3, top + 5)
        matchstick(c, cx + 3, top + 5, cx + s / 2 - 4, top + h)
        matchstick(c, cx + s / 2 - 5, top + h + 3, cx - s / 2 + 5, top + h + 3)
    tri(75, 8); tri(45, 62); tri(105, 62)


@figure('colossal-p130-1', 200, 120, 'Sixteen matches forming five unit squares: three in a row below, two above the right end')
def five_match_squares(c):
    u, x0, y0 = 42, 15, 58
    squares = [(0, 0), (1, 0), (2, 0), (2, -1), (3, -1)]
    edges = set()
    for i, j in squares:
        edges |= {((i, j), (i + 1, j)), ((i, j + 1), (i + 1, j + 1)), ((i, j), (i, j + 1)), ((i + 1, j), (i + 1, j + 1))}
    for (a, b) in sorted(edges):
        p = (x0 + a[0] * u, y0 + a[1] * u); q = (x0 + b[0] * u, y0 + b[1] * u)
        ux, uy = unit(p, q)
        matchstick(c, p[0] + ux * 3, p[1] + uy * 3, q[0] - ux * 3, q[1] - uy * 3)


@figure('colossal-p134-1', 300, 150, 'Twelve matches forming a square, three to a side, and twelve matches forming a Greek cross')
def match_square_and_cross(c):
    u = 40
    for k in range(3):
        matchstick(c, 15 + k * u + 3, 15, 15 + (k + 1) * u - 3, 15); matchstick(c, 15 + k * u + 3, 15 + 3 * u, 15 + (k + 1) * u - 3, 15 + 3 * u)
        matchstick(c, 15, 15 + k * u + 3, 15, 15 + (k + 1) * u - 3); matchstick(c, 15 + 3 * u, 15 + k * u + 3, 15 + 3 * u, 15 + (k + 1) * u - 3)
    a, bx, by = 40, 225, 75
    pts = [(bx - a / 2, by - 1.5 * a), (bx + a / 2, by - 1.5 * a), (bx + a / 2, by - a / 2), (bx + 1.5 * a, by - a / 2), (bx + 1.5 * a, by + a / 2),
           (bx + a / 2, by + a / 2), (bx + a / 2, by + 1.5 * a), (bx - a / 2, by + 1.5 * a), (bx - a / 2, by + a / 2), (bx - 1.5 * a, by + a / 2),
           (bx - 1.5 * a, by - a / 2), (bx - a / 2, by - a / 2)]
    for k in range(12):
        p, q = pts[k], pts[(k + 1) % 12]; ux, uy = unit(p, q)
        matchstick(c, p[0] + ux * 3, p[1] + uy * 3, q[0] - ux * 3, q[1] - uy * 3)


@figure('colossal-p140-1', 282, 265, 'Three circles of decreasing size fitted among several straight lines that meet on a sloping base line')
def circles_among_lines(c):
    k = 0.36
    T = lambda x, y: ((x - 790) * k, (y - 15) * k)
    for p, q in (((800, 712), (1540, 470)), ((970, 655), (1100, 20)), ((970, 655), (1375, 95)), ((1265, 560), (1275, 75)),
                 ((1335, 535), (1000, 125)), ((1335, 535), (955, 300)), ((1335, 535), (910, 460))):
        c.line(*T(*p), *T(*q), 1)
    for (x, y, r) in ((1170, 200, 105), (1065, 435, 55), (1250, 500, 18)):
        c.circle(*T(x, y), r * k, 1.1)
    for p in ((970, 655), (1265, 560), (1335, 535)): dot(c, *T(*p), 1.6)


@figure('colossal-p189-2', 200, 160, 'An 11 by 9 grid of squares with a horizontal slot of seven cells missing from its middle row')
def grid_with_slot(c):
    cell, x0, y0 = 16, 12, 8
    for j in range(9):
        for i in range(11):
            if j == 4 and 2 <= i <= 8: continue
            c.rect(x0 + i * cell, y0 + j * cell, cell, cell, 0.9)


@figure('colossal-p190-1', 240, 170, 'A 20 by 13 grid of squares partitioned by heavier lines into pieces, with some cells shaded')
def partitioned_grid(c):
    cell, x0, y0 = 11, 10, 10
    for j in range(13):
        for i in range(20):
            shade = 'light' if (j == 12 and i < 8) or (i == 19 and j < 8) or (j == 8 and 8 <= i < 12) else None
            c.rect(x0 + i * cell, y0 + j * cell, cell, cell, 0.5, shade)
    L = lambda a, b, p, q: c.line(x0 + a * cell, y0 + b * cell, x0 + p * cell, y0 + q * cell, 1.8)
    c.rect(x0, y0, 20 * cell, 13 * cell, 1.8)
    L(5, 0, 5, 7); L(10, 0, 10, 8); L(14, 0, 14, 8); L(8, 8, 20, 8); L(8, 8, 8, 13); L(19, 0, 19, 8); L(8, 9, 12, 9); L(12, 8, 12, 9)


@figure('colossal-p190-2', 220, 140, 'A long triangle cut by three zigzag lines into four regions numbered 1 to 4')
def triangle_four_regions(c):
    k = 0.45
    T = lambda x, y: ((x - 1060) * k, (y - 10) * k)
    A, B, R = T(1070, 20), T(1160, 295), T(1540, 295)
    c.polygon([A, B, R], 1.5)
    P1, P2, P3 = T(1290, 155), T(1350, 295), T(1415, 225)
    c.polyline([B, P1, P2, P3], 1.4)
    for (x, y), n in ((T(1180, 165), '1'), (T(1275, 240), '2'), (T(1355, 240), '3'), (T(1420, 275), '4')):
        c.text(x, y, n, 12, anchor='middle')


@figure('colossal-p191-1', 250, 150, 'A brick wall of staggered 3 by 1 bricks, four bricks wide, continuing to the right and downward')
def brick_wall(c):
    w, h, x0, y0 = 50, 20, 20, 30
    for j in range(5):
        off = (w / 2) if j % 2 else 0
        x = x0 - (w / 2 if j % 2 else 0)
        while x < x0 + 4 * w:
            left, right = max(x, x0), min(x + w, x0 + 4 * w)
            c.rect(left, y0 + j * h, right - left, h, 1)
            x += w
    c.line(x0, y0, x0, y0 + 7 * h, 1.2); c.line(x0, y0, x0 + 4 * w + 30, y0, 1.2)
    for k in range(4):
        c.polyline([(x0 + k * w + 2, y0 - 6), (x0 + k * w + 2, y0 - 11), (x0 + (k + 1) * w - 2, y0 - 11), (x0 + (k + 1) * w - 2, y0 - 6)], 0.8)
        c.text(x0 + (k + 0.5) * w, y0 - 14, '3', 10, anchor='middle', bold=True)
    for k in range(3): dot(c, x0 + 4 * w + 12 + k * 7, y0 + 2.5 * h, 1.6); dot(c, x0 + 2 * w, y0 + 5.5 * h + k * 7, 1.6)


@figure('colossal-p192-2', 230, 110, 'A triangle with a smaller triangle inside joined corner to corner, and a rectangular spiral enclosing a shaded square')
def triangle_and_spiral(c):
    A, B, C = (65, 8), (10, 100), (120, 100)
    a, b, cc = (65, 50), (45, 82), (85, 82)
    c.polygon([A, B, C], 1.4); c.polygon([a, b, cc], 1.2)
    c.line(*A, *a, 1.2); c.line(*B, *b, 1.2); c.line(*C, *cc, 1.2)
    x = 140
    c.polyline([(x, 100), (x, 12), (x + 85, 12), (x + 85, 100), (x + 20, 100), (x + 20, 30), (x + 70, 30), (x + 70, 85), (x + 35, 85)], 1.3)
    c.rect(x + 35, 45, 30, 30, 0.8, 'gray')


@figure('colossal-p195-1', 290, 110, 'A rectangle tiled by interlocking pieces, and a rectangle containing three separate small squares')
def tiling_and_squares(c):
    x0, y0, u = 10, 10, 15
    c.rect(x0, y0, 9 * u, 6 * u, 1.3)
    L = lambda pts: c.polyline([(x0 + a * u, y0 + b * u) for a, b in pts], 1)
    L([(0, 2), (2, 2), (2, 1), (4, 1), (4, 3), (6, 3), (6, 1), (8, 1), (8, 3), (9, 3)])
    L([(1, 6), (1, 4), (3, 4), (3, 5), (5, 5), (5, 3)]); L([(5, 5), (7, 5), (7, 4), (9, 4)]); L([(2, 2), (2, 4)]); L([(6, 3), (6, 6)])
    x1 = 165
    c.rect(x1, y0, 115, 6 * u, 1.3)
    for cx, cy in ((x1 + 20, y0 + 70), (x1 + 55, y0 + 45), (x1 + 95, y0 + 18)):
        c.rect(cx - 7, cy - 7, 14, 14, 1)


@figure('colossal-p196-1', 300, 270, 'Four rings of unit squares with jagged outer edges enclosing areas of 28, 61, 90 and 127')
def jagged_rings(c):
    def ring(x, y, w, h, n, u=8):
        c.rect(x, y, w, h, 1.2)
        c.rect(x - u, y - u, w + 2 * u, h + 2 * u, 1.2)
        for k in range(0, int(w / u), 3):
            c.rect(x + k * u, y - 2 * u, u, u, 1); c.rect(x + k * u + u, y + h + u, u, u, 1)
        for k in range(0, int(h / u), 3):
            c.rect(x - 2 * u, y + k * u + u, u, u, 1); c.rect(x + w + u, y + k * u, u, u, 1)
        c.text(x + w / 2, y + h / 2 + 4, n, 11, anchor='middle', bold=True)
    ring(30, 30, 72, 48, '28'); ring(170, 25, 72, 72, '61'); ring(30, 150, 96, 96, '90'); ring(175, 140, 104, 104, '127')
    for (x, y), t in (((12, 18), 'a'), ((150, 12), 'b'), ((12, 135), 'c'), ((155, 125), 'd')):
        c.text(x, y, t, 11, True, bold=True)


@figure('colossal-p198-1', 150, 400, 'Three squares in which lines from the top corners meet at a point near the bottom, forming successively finer folds marked 8, 10 and 11')
def folding_squares(c):
    s = 120
    for k, (n, depth) in enumerate(((8, 0.96), (10, 0.82), (11, 0.9))):
        x, y = 15, 10 + k * 135
        c.rect(x, y, s, s, 1.2)
        B = (x + s / 2 + 8, y + depth * s)
        c.line(x, y, *B, 1); c.line(x + s, y, *B, 1)
        if k == 0:
            c.line(x + s / 2, y, x + s / 2 - 8, y + s, 1); c.line(x, y + s, x + s / 2 + 8, y + s * 0.96, 1); c.line(x + s, y + s, x + s / 2 + 8, y + s * 0.96, 1)
        else:
            c.line(x, y + s, *B, 1); c.line(x + s, y + s, *B, 1)
            f = 0.12 if k == 1 else 0.07
            for t in (-2, -1, 1, 2):
                c.line(B[0], B[1], x + s / 2 + 8 + t * f * s, y + s, 0.7)
            c.line(B[0] - 2 * f * s, y + s - f * s * 0.6, B[0] + 2 * f * s, y + s - f * s * 0.6, 0.7)
            label(c, *B, 'B', 'ne', 8, False); label(c, x, y + s, 'A', 'sw', 8, False); label(c, x + s, y + s, 'C', 'se', 8, False)
            if k == 2: label(c, x + s / 2 + 8, y + s, 'D', 's', 8, False)
        c.text(x - 4, y + s / 2 + 3, n, 9, anchor='end', bold=True)


@figure('colossal-p210-1', 230, 140, 'Two long rectangular beams, one lying across the other, drawn in perspective with hidden edges dashed')
def crossed_beams(c):
    P = iso(60, 125, 22)
    # Lower beam along j, upper beam along i, resting on it.
    def beam(P, i0, i1, j0, j1, k0, k1, stroke=1.2):
        c.polygon([P(i0, j0, k1), P(i1, j0, k1), P(i1, j1, k1), P(i0, j1, k1)], stroke)
        c.polygon([P(i1, j0, k0), P(i1, j1, k0), P(i1, j1, k1), P(i1, j0, k1)], stroke)
        c.polygon([P(i0, j1, k0), P(i1, j1, k0), P(i1, j1, k1), P(i0, j1, k1)], stroke)
        c.line(*P(i0, j0, k0), *P(i0, j0, k1), 0.8, (3, 3)); c.line(*P(i0, j0, k0), *P(i1, j0, k0), 0.8, (3, 3)); c.line(*P(i0, j0, k0), *P(i0, j1, k0), 0.8, (3, 3))
    beam(P, 2, 3, -1, 6, 0, 1); beam(P, -1, 6, 2, 3, 1, 2)


@figure('colossal-p210-2', 150, 120, 'Interlocking zigzag outlines of hexagonal cells, drawn as three nested chevron paths')
def zigzag_outlines(c):
    def zig(x, y, n, dx=12, dy=8):
        pts = [(x, y)]
        for k in range(n):
            pts.append((x + (k + 0.5) * dx, y - dy if k % 2 == 0 else y + dy)); pts.append((x + (k + 1) * dx, y))
        return pts
    c.polyline([(8, 60)] + zig(14, 40, 8) + [(118, 60), (118, 90)] + list(reversed(zig(14, 100, 8))) + [(8, 90), (8, 60)], 1.2)
    c.polyline([(40, 62)] + zig(40, 56, 5) + [(100, 70), (100, 84)] + list(reversed(zig(40, 84, 5))) + [(40, 62)], 1.2)
    c.polyline([(30, 20)] + zig(36, 14, 6) + [(110, 20)], 1.2)


@figure('colossal-p219-1', 260, 160, 'A closed curve that crosses itself many times, with every crossing marked by a small circle')
def tangled_curve(c):
    pts = []
    for k in range(240):
        t = 2 * math.pi * k / 240
        pts.append((130 + 100 * math.cos(3 * t) * math.cos(t) + 25 * math.sin(7 * t), 80 + 60 * math.sin(2 * t) + 15 * math.cos(5 * t)))
    c.curve(pts, 1.1, close=True, tension=0.25)
    # Mark the self-intersections of the polyline approximation.
    n = len(pts); marks = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        for j in range(i + 2, n):
            if (j + 1) % n == i: continue
            p, q = pts[j], pts[(j + 1) % n]
            d = (b[0] - a[0]) * (q[1] - p[1]) - (b[1] - a[1]) * (q[0] - p[0])
            if abs(d) < 1e-9: continue
            s = ((p[0] - a[0]) * (q[1] - p[1]) - (p[1] - a[1]) * (q[0] - p[0])) / d
            u = ((p[0] - a[0]) * (b[1] - a[1]) - (p[1] - a[1]) * (b[0] - a[0])) / d
            if 0 <= s < 1 and 0 <= u < 1: marks.append((a[0] + s * (b[0] - a[0]), a[1] + s * (b[1] - a[1])))
    for x, y in marks: c.circle(x, y, 2.6, 0.9, 'white')


@figure('colossal-p219-2', 110, 120, 'Six matches arranged like a hexagon: one upright on top, a horizontal in the middle, and two pairs leaning outward above and below')
def six_matches(c):
    k = 0.4
    T = lambda x, y: ((x - 1050) * k, (y - 10) * k)
    for p, q in (((1175, 130), (1175, 30)), ((1150, 100), (1070, 170)), ((1210, 100), (1290, 170)), ((1240, 150), (1120, 150)), ((1110, 170), (1170, 280)), ((1240, 170), (1180, 280))):
        matchstick(c, *T(*p), *T(*q))


@figure('colossal-p220-1', 160, 160, 'A square frame holding two pairs of linked rings, each a horizontal ring threaded by a vertical ring')
def linked_rings(c):
    c.rect(8, 8, 144, 144, 1.4); c.rect(12, 12, 136, 136, 0.7)
    for cx in (50, 110):
        c.ellipse(cx, 70, 24, 10, 1.2); c.ellipse(cx - 4, 92, 7, 26, 1.2)
        c.ellipse(cx, 70, 24, 10, 1.2, 'white'); c.path(c.ellipse_segments(cx - 4, 92, 7, 26)[:3], 1.2)


@figure('colossal-p220-2', 160, 160, 'Three equal circles in a trefoil, each meeting the other two; their outer intersections are A, B and C')
def trefoil_circles(c):
    r = 44; cx, cy = 80, 85
    cs = [(cx, cy - 36), (cx - 32, cy + 20), (cx + 32, cy + 20)]
    for p in cs: c.circle(*p, r, 1.3)
    def meet(P, Q, sign):
        d = math.hypot(Q[0] - P[0], Q[1] - P[1]); h = math.sqrt(r * r - (d / 2) ** 2)
        mx, my = (P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2
        return (mx + sign * h * (Q[1] - P[1]) / d, my - sign * h * (Q[0] - P[0]) / d)
    A = meet(cs[0], cs[1], 1); B = meet(cs[0], cs[2], -1); C = meet(cs[1], cs[2], -1)
    labels(c, {'A': A, 'B': B, 'C': C}, {'A': 'w', 'B': 'e', 'C': 's'}, 11, False)


def rope(c, pts, width=5, stroke=1.1, close=False):
    """A rope drawn as two parallel curves."""
    c.curve(pts, stroke, close=close)
    out = []
    for i, (x, y) in enumerate(pts):
        p = pts[max(i - 1, 0)]; q = pts[min(i + 1, len(pts) - 1)]
        ux, uy = unit(p, q); out.append((x - uy * width, y + ux * width))
    c.curve(out, stroke, close=close)


@figure('colossal-p221-1', 230, 110, 'Two rope ends A and B drawn together toward the right, and the resulting loop')
def rope_figure_1(c):
    rope(c, [(10, 30), (60, 38), (110, 46), (150, 52)], 4); label(c, 60, 32, 'A', 'n', 11, False)
    rope(c, [(10, 95), (50, 78), (100, 62), (150, 56)], 4); label(c, 60, 88, 'B', 's', 11, False)
    rope(c, [(165, 52), (190, 38), (215, 42), (220, 58), (200, 72), (170, 66)], 4)
    c.text(8, 14, '1.', 11, bold=True)


@figure('colossal-p221-2', 190, 120, 'A loop of rope whose two ends A and B lead off to the upper right')
def rope_figure_2(c):
    rope(c, [(170, 24), (120, 36), (60, 50), (20, 70), (30, 98), (80, 96), (130, 76), (170, 48)], 4)
    label(c, 174, 18, 'A', 'e', 11, False); label(c, 174, 50, 'B', 'e', 11, False)


@figure('colossal-p221-3', 250, 160, 'A rope through the ring of a key at P, running from B on the left past a loop at Q to the end A')
def rope_figure_3(c):
    rope(c, [(10, 70), (50, 66), (80, 62), (110, 70), (150, 78), (185, 60), (215, 40), (245, 30)], 4)
    c.ellipse(72, 60, 14, 10, 1.2); c.ellipse(72, 60, 9, 6, 0.8)
    c.rect(68, 70, 8, 70, 1.1); c.polyline([(76, 125), (88, 125), (88, 132), (80, 132), (80, 138), (76, 138)], 1)
    c.ellipse(190, 44, 22, 16, 1.1); c.ellipse(190, 44, 18, 12, 1.1)
    label(c, 8, 60, 'B', 'n', 11, False); label(c, 72, 44, 'P', 'n', 11, False); label(c, 200, 70, 'Q', 's', 11, False); label(c, 240, 20, 'A', 'n', 11, False)
    c.text(8, 16, '3.', 11, bold=True)


@figure('colossal-p224-1', 160, 100, 'A rectangle divided into five rooms, three above and two below, with a continuous line that crosses walls')
def five_rooms(c):
    x, y, w, h = 20, 15, 120, 60
    c.rect(x, y, w, h, 1.3)
    c.line(x + w / 3, y, x + w / 3, y + h / 2, 1.3); c.line(x + 2 * w / 3, y, x + 2 * w / 3, y + h / 2, 1.3)
    c.line(x, y + h / 2, x + w, y + h / 2, 1.3); c.line(x + w / 2, y + h / 2, x + w / 2, y + h, 1.3)
    c.curve([(8, 30), (30, 8), (55, 28), (70, 8), (95, 24), (118, 8), (150, 30), (130, 55), (150, 84), (110, 90), (90, 58), (70, 88), (40, 92), (10, 70), (35, 50), (8, 30)], 1.6, close=False, tension=0.3)


@figure('colossal-p225-1', 200, 190, 'A hatched band bent into an open ring seen in perspective, and three small diagrams of folding a hatched strip at a corner')
def band_ring(c):
    cx, cy = 100, 50
    c.ellipse(cx, cy, 90, 26, 1.2); c.ellipse(cx, cy, 80, 19, 1.2)
    c.hatch(c.ellipse_segments(cx, cy, 90, 26), 4, 60, 0.5)
    c.ellipse(cx, cy, 80, 19, 0, 'white')
    c.rect(cx - 16, cy + 24, 32, 12, 0, 'white')
    c.line(cx - 90, cy, cx - 90, cy + 16, 1.2); c.line(cx + 90, cy, cx + 90, cy + 16, 1.2)
    c.arc(cx, cy + 16, 90, 10, 80, 1.2); c.arc(cx, cy + 16, 90, 100, 170, 1.2)
    for k, (x, y) in enumerate(((10, 110), (80, 110), (150, 110))):
        strip = [('M', x, y), ('L', x + 22, y), ('L', x + 22, y + 40), ('L', x, y + 40)]
        c.path(strip, 1, close=True); c.hatch(strip, 3.5, 45, 0.5)
        if k == 0:
            c.polygon([(x, y + 40), (x + 22, y + 40), (x + 62, y + 62), (x + 40, y + 62)], 1); c.line(x + 22, y + 40, x + 22, y + 62, 0.8, (3, 2))
        elif k == 1:
            tri = [('M', x, y + 40), ('L', x + 22, y + 40), ('L', x + 22, y + 62)]; c.path(tri, 1, close=True); c.hatch(tri, 3.5, 45, 0.5)
            c.polygon([(x + 22, y + 40), (x + 44, y + 40), (x + 22, y + 62)], 1); c.arrow(x + 50, y + 50, x + 30, y + 50, 5, 1); c.arrow(x - 12, y + 48, x + 4, y + 48, 5, 1)
        else:
            c.polygon([(x, y + 40), (x + 22, y + 40), (x + 22, y + 62), (x, y + 62)], 1); c.line(x, y + 62, x + 22, y + 40, 2)
            c.text(x + 13, y + 58, 'A', 8, bold=True); c.arrow(x - 14, y + 44, x + 2, y + 52, 5, 1)


@figure('colossal-p225-2', 270, 100, "A square with dashed diagonals and a rectangle, both labelled A and A' on the sides and B and B' at bottom and top")
def square_and_rectangle(c):
    c.rect(20, 15, 70, 70, 1.2); c.line(20, 15, 90, 85, 0.8, (3, 3)); c.line(90, 15, 20, 85, 0.8, (3, 3))
    labels(c, {"B'": (55, 15), 'B': (55, 85), 'A': (20, 50), "A'": (90, 50)}, {"B'": 'n', 'B': 's', 'A': 'w', "A'": 'e'}, 9, False)
    c.rect(120, 15, 135, 70, 1.2)
    labels(c, {"B'": (187, 15), 'B': (187, 85), 'A': (120, 50), "A'": (255, 50)}, {"B'": 'n', 'B': 's', 'A': 'w', "A'": 'e'}, 9, False)


def tromino_tiling(w, h, holes):
    """Deterministic tiling of a w by h board (minus holes) with 1 by 3 bricks."""
    board = [[(x, y) in holes for x in range(w)] for y in range(h)]
    bricks = []

    def solve():
        for y in range(h):
            for x in range(w):
                if not board[y][x]:
                    for dx, dy in ((1, 0), (0, 1)):
                        cells = [(x + i * dx, y + i * dy) for i in range(3)]
                        if all(cx < w and cy < h and not board[cy][cx] for cx, cy in cells):
                            for cx, cy in cells: board[cy][cx] = True
                            bricks.append((x, y, 1 + 2 * dx, 1 + 2 * dy))
                            if solve(): return True
                            bricks.pop()
                            for cx, cy in cells: board[cy][cx] = False
                    return False
        return True
    solve()
    return bricks


@figure('colossal-p192-1', 300, 180, 'Three rectangles, 4 by 7, 5 by 8 and 4 by 8, tiled with 1 by 3 bricks; the cells left over are shaded')
def tromino_rectangles(c):
    u = 15
    for x0, (w, h, holes, title) in zip((15, 110, 215), ((4, 7, {(3, 6)}, '(3k + 1)(3k + 1)'), (5, 8, {(4, 7)}, '(3k + 2)(3k + 2)'), (4, 8, {(2, 7), (3, 7)}, '(3k + 1)(3k + 2)'))):
        y0 = 160 - h * u
        for hx, hy in holes: c.rect(x0 + hx * u, y0 + hy * u, u, u, 0.8, 'gray')
        for bx, by, bw, bh in tromino_tiling(w, h, holes):
            c.rect(x0 + bx * u, y0 + by * u, bw * u, bh * u, 1)
        c.rect(x0, y0, w * u, h * u, 1.4)
        c.text(x0 + w * u / 2, y0 - 6, title, 7.5, True, 'middle')
        c.text(x0 - 6, y0 + h * u / 2 + 3, h, 9, anchor='end', bold=True); c.text(x0 + w * u / 2, y0 + h * u + 11, w, 9, anchor='middle', bold=True)


@figure('colossal-p194-1', 350, 170, 'Polygons with 3 to 10 sides built from unit squares and equilateral triangles, each drawn with its pieces')
def polyform_polygons(c):
    s = 24; t = s * 0.866

    def tri_on(p, q, outward=1):
        """Apex of the equilateral triangle on segment pq (outward = +1 to the right of p->q)."""
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        ux, uy = unit(p, q)
        return (mx - uy * t * outward, my + ux * t * outward)

    def square(x, y): return [(x, y), (x + s, y), (x + s, y + s), (x, y + s)]

    def draw(pieces, outline, lab, lx, ly):
        for piece in pieces: c.polygon(piece, 0.9)
        c.polygon(outline, 1.5)
        c.text(lx, ly, lab, 10, anchor='middle', bold=True)
    # 3, 4
    A = [(10, 60), (10 + s, 60), (10 + s / 2, 60 - t)]; draw([], A, '3', 10 + s / 2, 74)
    draw([], square(50, 36), '4', 50 + s / 2, 74)
    # 5: house
    sq = square(95, 40); E = tri_on(sq[3], sq[0], -1)
    draw([sq], [sq[0], sq[1], sq[2], sq[3], E], '5', 95 + s / 2, 78)
    # 6: square with triangles left and right
    sq = square(145, 36); L = tri_on(sq[0], sq[3], -1); R = tri_on(sq[2], sq[1], -1)
    draw([sq], [sq[0], sq[1], R, sq[2], sq[3], L], '6', 145 + s / 2, 74)
    # 7: house with triangles on both roof sides
    sq = square(235, 44); E = tri_on(sq[3], sq[0], -1); F = tri_on(E, sq[0], 1); G = tri_on(sq[3], E, 1)
    draw([sq, [sq[3], sq[0], E]], [sq[0], sq[1], sq[2], sq[3], G, E, F], '7', 235 + s / 2, 82)
    # 8: square with a triangle on every side
    sq = square(40, 112); tris = [tri_on(sq[i], sq[(i + 1) % 4], -1) for i in range(4)]
    out = []
    for i in range(4): out += [sq[i], tris[i]]
    draw([sq], out, '8', 40 + s / 2, 160)
    # 9: as 8 plus a triangle on one triangle edge
    sq = square(135, 112); tris = [tri_on(sq[i], sq[(i + 1) % 4], -1) for i in range(4)]
    extra = tri_on(tris[0], sq[1], -1)
    out = [sq[0], tris[0], extra, sq[1], tris[1], sq[2], tris[2], sq[3], tris[3]]
    draw([sq, [sq[0], sq[1], tris[0]]], out, '9', 135 + s / 2, 160)
    # 10: as 9 plus one more triangle on the opposite side
    sq = square(240, 112); tris = [tri_on(sq[i], sq[(i + 1) % 4], -1) for i in range(4)]
    e1 = tri_on(tris[0], sq[1], -1); e2 = tri_on(tris[2], sq[3], -1)
    out = [sq[0], tris[0], e1, sq[1], tris[1], sq[2], tris[2], e2, sq[3], tris[3]]
    draw([sq, [sq[0], sq[1], tris[0]], [sq[2], sq[3], tris[2]]], out, '10', 240 + s / 2, 160)


@figure('colossal-p196-2', 200, 150, 'Figures drawn with 3, 4, 5 and 6 straight lines: a triangle, a bow tie and a bisected triangle, a pentagram, and a pentagram-like figure with six lines')
def line_count_figures(c):
    c.polygon([(8, 40), (48, 40), (28, 6)], 1.2); c.text(28, 52, '3', 10, anchor='middle', bold=True)
    c.line(66, 6, 66, 40, 1.2); c.line(110, 6, 110, 40, 1.2); c.line(66, 6, 110, 40, 1.2); c.line(66, 40, 110, 6, 1.2)
    c.polygon([(122, 40), (166, 40), (144, 6)], 1.2); c.line(144, 6, 144, 40, 1.2); c.text(118, 52, '4', 10, anchor='middle', bold=True)
    star(c, 50, 100, 42, 5, 1.2); c.text(50, 146, '5', 10, anchor='middle', bold=True)
    pts = regular_polygon(145, 100, 42, 5)
    for i, j in ((0, 2), (0, 3), (1, 4), (2, 4)): segment(c, pts[i], pts[j], 1.2)
    inner = midpoint(pts[1], pts[3], 0.62)
    segment(c, pts[1], (inner[0], inner[1] + 6), 1.2); segment(c, (inner[0], inner[1] + 6), pts[3], 1.2)
    c.text(145, 146, '6', 10, anchor='middle', bold=True)


@figure('colossal-p227-1', 150, 240, 'Five ways of joining five points by five straight lines: a pentagram and four figures with points along a top edge and a lower apex')
def five_point_figures(c):
    k = 0.4
    T = lambda x, y: ((x - 790) * k, (y - 815) * k)
    def fig(points, lines):
        P = [T(*p) for p in points]
        for i, j in lines: segment(c, P[i], P[j], 1.1)
        for p in P: dot(c, *p, 1.6)
    fig([(905, 828), (808, 895), (1003, 895), (848, 1018), (963, 1018)], [(0, 3), (0, 4), (1, 2), (1, 4), (2, 3)])
    fig([(1040, 828), (1085, 828), (1185, 828), (1235, 828), (1135, 1030)], [(0, 3), (0, 4), (3, 4), (1, 4), (2, 4)])
    fig([(808, 1090), (1003, 1090), (915, 1290), (990, 1135), (820, 1135)], [(0, 2), (1, 2), (0, 3), (1, 4), (3, 4)])
    fig([(1040, 1090), (1235, 1090), (1090, 1290), (1190, 1290), (1138, 1090)], [(0, 1), (0, 3), (1, 2), (4, 2), (4, 3)])
    fig([(930, 1355), (1130, 1355), (1030, 1550), (1100, 1430), (960, 1430)], [(0, 2), (1, 2), (0, 3), (1, 4), (3, 4)])


@figure('colossal-p228-1', 130, 125, 'Three equal circles touching, one above two, the lower right one filled black')
def three_coins_one_black(c):
    r = 28
    c.circle(65, 32, r, 1.2); c.circle(37, 82, r, 1.2); c.circle(93, 82, r, 1.2, 'black')


@figure('colossal-p229-1', 120, 285, 'Three polyomino enclosures with shaded cells: an L-shaped nest, a ring around a shaded rectangle, and interlocking L pieces')
def enclosures_a(c):
    u = 8
    L = lambda pts, s=1.1: c.polyline([(x * u, y * u) for x, y in pts], s)
    L([(1, 3), (1, 14), (5, 14), (5, 6), (9, 6), (9, 3), (3, 3), (3, 12), (7, 12), (7, 8), (11, 8), (11, 1), (13, 1), (13, 10)])
    c.rect(5 * u, 8 * u, 2 * u, 2 * u, 0, 'gray')
    c.rect(1 * u, 16 * u, 12 * u, 12 * u, 1.1); c.rect(3 * u, 18 * u, 8 * u, 8 * u, 1.1); c.rect(4 * u, 19 * u, 6 * u, 4 * u, 0, 'light'); c.rect(9 * u, 24 * u, 2 * u, 2 * u, 0, 'black')
    L([(6, 30), (6, 35), (2, 35), (2, 34)]); L([(4, 30), (10, 30), (10, 34), (13, 34), (13, 31)])
    L([(1, 35), (9, 35), (9, 31), (5, 31)]); c.rect(5 * u, 32 * u, 2 * u, 2 * u, 0, 'gray'); c.rect(7 * u, 32 * u, 2 * u, 2 * u, 0, 'black')


@figure('colossal-p229-2', 120, 200, 'Two polyomino enclosures with shaded cells: a wide ring with an inset shaded block, and a cross-shaped enclosure')
def enclosures_b(c):
    u = 8
    c.polyline([(1 * u, 1 * u), (1 * u, 11 * u), (11 * u, 11 * u), (11 * u, 4 * u), (5 * u, 4 * u), (5 * u, 9 * u), (9 * u, 9 * u), (9 * u, 6 * u), (3 * u, 6 * u), (3 * u, 1 * u), (1 * u, 1 * u)], 1.1)
    c.rect(5 * u, 7 * u, 3 * u, 2 * u, 0, 'gray')
    pts = [(4, 14), (8, 14), (8, 16), (12, 16), (12, 19), (14, 19), (14, 21), (12, 21), (12, 24), (8, 24), (8, 22), (4, 22), (4, 20), (2, 20), (2, 17), (4, 17)]
    c.polygon([(x * u, y * u) for x, y in pts], 1.1)
    c.rect(6 * u, 17 * u, 3 * u, 2 * u, 0, 'gray'); c.rect(4 * u, 20 * u, 3 * u, 2 * u, 0, 'gray'); c.rect(10 * u, 20 * u, 2 * u, 2 * u, 0, 'gray')


@figure('colossal-p230-1', 230, 110, 'A box drawn with hidden edges dashed and a string entering over its top edge and leaving below its right edge')
def box_and_string(c):
    P = cabinet(50, 95, 60, 0.5, 35)
    c.polygon([P(0, 0, 0), P(1, 0, 0), P(1, 0, 1), P(0, 0, 1)], 1.2)
    c.polygon([P(0, 0, 1), P(1, 0, 1), P(1, 1, 1), P(0, 1, 1)], 1.2)
    c.polygon([P(1, 0, 0), P(1, 1, 0), P(1, 1, 1), P(1, 0, 1)], 1.2)
    c.line(*P(0, 1, 0), *P(0, 1, 1), 0.9, (3, 3)); c.line(*P(0, 1, 0), *P(1, 1, 0), 0.9, (3, 3)); c.line(*P(0, 1, 0), *P(0, 0, 0), 0.9, (3, 3))
    a, b = P(0.4, 1, 1), P(1, 0.3, 0)
    c.polyline([(8, 18), (a[0], a[1])], 1.1); c.polyline([(b[0], b[1]), (b[0] + 35, b[1] + 15), (b[0] + 70, b[1] - 8)], 1.1)
    for p in ((8, 18), a, b, (b[0] + 35, b[1] + 15), (b[0] + 70, b[1] - 8)): dot(c, *p, 1.8)


@figure('colossal-p230-2', 220, 160, 'Two linked rings A and B: a flat ring seen edge-on passes through a round ring')
def linked_tori(c):
    c.ellipse(75, 80, 62, 30, 1.3); c.ellipse(75, 80, 34, 12, 1.3)
    c.circle(150, 70, 60, 1.3); c.circle(150, 70, 36, 1.3)
    c.ellipse(75, 80, 62, 30, 0, 'white'); c.ellipse(75, 80, 34, 12, 1.3, 'white')
    c.arc(150, 70, 60, 100, 260, 1.3); c.arc(150, 70, 36, 120, 240, 1.3)
    c.ellipse(75, 80, 62, 30, 1.3); c.ellipse(75, 80, 34, 12, 1.3)
    c.text(28, 128, 'A', 11, bold=True); c.text(140, 150, 'B', 11, bold=True)


@figure('colossal-p231-1', 280, 150, 'Two forms of the same doubly linked band: two small loops threaded through a ring, and the band with one loop pulled free')
def band_forms(c):
    def ring(x, y, rx, ry):
        c.ellipse(x, y, rx, ry, 1.2); c.ellipse(x, y, rx - 6, ry - 6, 1.2)
    ring(85, 70, 46, 52); ring(60, 48, 22, 18); ring(60, 92, 22, 18)
    c.arrow(142, 75, 170, 75, 6, 1.2, both=True)
    ring(230, 62, 36, 46); ring(203, 40, 18, 14); ring(205, 112, 16, 24)


@figure('colossal-p249-1', 120, 115, 'A circular orbit around a shaded central body, with a small body on the orbit at the right')
def orbit(c):
    c.circle(55, 57, 50, 1); c.circle(55, 57, 14, 0, 'gray'); dot(c, 108, 57, 3.5)


@figure('colossal-p250-1', 50, 70, 'A stem above an open rectangular cup, like a tuning fork')
def cup_shape(c):
    c.line(25, 4, 25, 30, 1.6); c.polyline([(8, 62), (8, 30), (42, 30), (42, 62)], 1.6)


@figure('colossal-p250-2', 100, 190, 'Four matches forming a cocktail glass, two uprights, a horizontal bottom and a stem, with a cherry inside')
def match_glass(c):
    matchstick(c, 22, 90, 22, 14); matchstick(c, 78, 90, 78, 14); matchstick(c, 78, 98, 22, 98); matchstick(c, 50, 104, 50, 180)
    c.circle(50, 68, 13, 1.1); c.line(50, 55, 46, 42, 1); c.hatch(c.ellipse_segments(50, 68, 13, 13), 3, 45, 0.4)


@figure('colossal-p251-1', 140, 105, 'A blob-shaped closed curve crossed by a straight line')
def blob_and_line(c):
    pts = [(30, 36), (48, 20), (72, 30), (92, 18), (115, 34), (118, 58), (100, 72), (92, 92), (68, 98), (50, 86), (28, 90), (18, 66), (24, 50)]
    c.curve(pts, 1.3, close=True, tension=0.28)
    c.line(8, 30, 132, 92, 1.3)


@figure('colossal-p253-1', 70, 80, 'A spring scale: a flat pan on top, a round dial with a pointer, and a stand below')
def spring_scale(c):
    c.rect(6, 6, 58, 5, 1); c.line(35, 11, 35, 22, 1.6); c.circle(35, 46, 22, 1.2); c.circle(35, 46, 18, 0.7)
    c.arrow(35, 46, 48, 33, 5, 1); c.polygon([(18, 76), (52, 76), (42, 66), (28, 66)], 1)


@figure('colossal-p260-1', 340, 240, 'A dragon curve: a fractal path of right-angled turns filling an irregular region')
def dragon_curve(c):
    turns = []
    for _ in range(11):
        turns = turns + [1] + [-t for t in reversed(turns)]
    x, y, d = 0, 0, 0
    pts = [(0, 0)]
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for t in turns:
        x += dirs[d][0]; y += dirs[d][1]; pts.append((x, y)); d = (d + t) % 4
    x += dirs[d][0]; y += dirs[d][1]; pts.append((x, y))
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    sx = 320 / (max(xs) - min(xs)); sy = 220 / (max(ys) - min(ys)); k = min(sx, sy)
    ox, oy = 10 - min(xs) * k, 10 - min(ys) * k
    c.polyline([(ox + px * k, oy + py * k) for px, py in pts], 0.6)


@figure('colossal-p292-1', 280, 50, 'Eight coins in a row')
def eight_coins(c):
    for k in range(8): coin(c, 20 + k * 34, 25, 15)


@figure('colossal-p293-1', 280, 130, 'Ten coins in a triangle pointing up and ten coins in a triangle pointing down')
def coin_triangles(c):
    r, d = 14, 30
    for row in range(4):
        for k in range(row + 1):
            coin(c, 70 + (k - row / 2) * d, 22 + row * d * 0.87, r)
            coin(c, 210 + (k - row / 2) * d, 22 + (3 - row) * d * 0.87, r)


@figure('colossal-p294-1', 280, 130, 'Three coins resting on a line, and below them three coins with the outlines of two more positions on another line')
def coins_on_lines(c):
    for x in (40, 118, 196): coin(c, x, 32, 20)
    c.line(10, 52, 270, 52, 0.8, (4, 3))
    for x in (40, 80, 120): coin(c, x, 98, 20)
    for x in (178, 230): c.circle(x, 98, 20, 0.8, dash=(3, 3))
    c.line(10, 118, 270, 118, 0.8, (4, 3))


@figure('colossal-p294-2', 280, 110, 'Six coins in two staggered rows of three, and an arrow to six coins in a ring')
def coins_to_ring(c):
    r = 15
    for k in range(3): coin(c, 40 + k * 32, 38, r); coin(c, 24 + k * 32, 66, r)
    c.arrow(130, 55, 170, 55, 7, 1.2)
    for k in range(6):
        a = math.radians(k * 60 - 90); coin(c, 225 + 32 * math.cos(a), 55 + 32 * math.sin(a), r)


@figure('colossal-p295-1', 250, 165, 'Two rooms 9 feet wide and 12 feet long; one shows a bar AB of 8.5 feet at the top and a bar CD of 4.5 feet at the bottom, the other the same bars reversed')
def two_rooms(c):
    for x0, top, bottom, flip in ((12, ('A', 'B'), ('C', 'D'), False), (140, ('B', 'A'), ('D', 'C'), True)):
        c.rect(x0, 18, 100, 135, 1.2)
        c.line(x0 + 4, 24, x0 + 96, 24, 4); c.text(x0 + 2, 36, top[0], 8, bold=True); c.text(x0 + 92, 36, top[1], 8, bold=True)
        bx = x0 + 28 if not flip else x0 + 22
        c.line(bx, 147, bx + 50, 147, 4); c.text(bx - 2, 143, bottom[0], 8, bold=True); c.text(bx + 48, 143, bottom[1], 8, bold=True)
        if not flip:
            c.text(x0 + 50, 12, '9 FEET', 8, anchor='middle', bold=True); c.text(x0 + 50, 38, '8 1/2 FEET', 7, anchor='middle', bold=True)
            c.text(bx + 25, 142, '4 1/2 FEET', 7, anchor='middle', bold=True); c.text(x0 - 4, 90, '12 FEET', 8, anchor='middle', rotate=-90, bold=True)


@figure('colossal-p297-1', 260, 260, 'A circular dial with twenty ticks labelled 0, 5, 10 up to 95')
def dial(c):
    cx, cy, r = 130, 132, 95
    c.circle(cx, cy, r, 1.2)
    for k in range(20):
        a = math.radians(k * 18 - 90)
        c.line(cx + r * math.cos(a), cy + r * math.sin(a), cx + (r + 12) * math.cos(a), cy + (r + 12) * math.sin(a), 1)
        c.text(cx + (r + 24) * math.cos(a), cy + (r + 24) * math.sin(a) + 3, k * 5, 8, anchor='middle')


@figure('colossal-p298-1', 140, 115, 'A 6 by 5 array of dots cut by a diagonal line: dots above and left of the line are filled, the others hollow')
def dots_diagonal(c):
    for row in range(5):
        for col in range(6):
            x, y = 15 + col * 22, 15 + row * 22
            c.circle(x, y, 5, 1, 'black' if col + row <= 4 else 'white')
    c.line(6, 108, 128, 6, 1.6)


@figure('colossal-p299-1', 350, 175, 'A model railway: an oval track with a siding and a short dead-end spur, and two trains on the line')
def railway(c):
    def track(pts, close=False):
        c.curve(pts, 2.2, close=close); c.curve(pts, 1, close=close)
    oval = [(100, 45), (250, 45), (300, 60), (320, 100), (300, 140), (250, 150), (100, 150), (60, 130), (50, 100), (60, 65)]
    track(oval, True)
    track([(10, 45), (100, 45)]); track([(10, 150), (100, 150)])
    c.rect(300, 85, 28, 36, 1.2, 'white'); c.arc(314, 85, 14, 180, 360, 1.2)
    for x, y in ((40, 36), (180, 36), (160, 141)): c.rect(x, y, 34, 14, 1.1, 'white')
    c.rect(14, 38, 20, 12, 1.1, 'white')


@figure('colossal-p301-1', 350, 240, 'Four 4 by 4 boards seen diagonally, labelled A to D, with marked cells, and a 4 by 4 by 4 cube with layers A to D')
def layered_boards(c):
    for k, (lab, cells) in enumerate((('A', [(1, 1), (2, 2)]), ('B', [(0, 2), (1, 1), (2, 3)]), ('C', [(1, 2)]), ('D', [(0, 1), (1, 2), (2, 3), (3, 0)]))):
        cx, cy = (60 + k * 110, 60) if k < 3 else (100, 170)
        with c.rotated(45, cx, cy):
            for j in range(4):
                for i in range(4):
                    c.rect(cx - 40 + i * 20, cy - 40 + j * 20, 20, 20, 0.8, 'gray' if (i, j) in cells else None)
        c.text(cx - 58, cy - 40, lab, 9, bold=True)
    P = iso(265, 215, 16)
    box(c, P, 4, 4, 4, 1.2, ('white', 'white', 'white'), subdivide=True)
    for n, lab in enumerate('ABCD'):
        p = P(4, 0, 3.5 - n); c.text(p[0] + 6, p[1] + 3, lab, 8, bold=True)
    c.arrow(P(4, 0, 4)[0] + 24, P(4, 0, 4)[1] - 8, P(4, 0, 4)[0] + 4, P(4, 0, 4)[1], 5, 0.9)


@figure('colossal-p303-1', 190, 190, 'A 4 by 4 board holding eight dotted pieces, placed in some cells either upright or lying sideways')
def dotted_pieces(c):
    cell, x0, y0 = 44, 7, 7
    grid(c, x0, y0, 4, 4, cell, 1)

    def piece(col, row, dots, vertical):
        cx, cy = x0 + col * cell + cell / 2, y0 + row * cell + cell / 2
        if vertical:
            c.rect(cx - 5, cy - 18, 10, 30, 1, 'white', radius=2); c.arc(cx, cy + 12, 5, 0, 180, 1)
            for k in range(dots): dot(c, cx, cy - 12 + k * 7, 1.4)
        else:
            c.rect(cx - 18, cy - 5, 30, 10, 1, 'white', radius=2); c.arc(cx + 12, cy, 5, -90, 90, 1)
            for k in range(dots): dot(c, cx - 12 + k * 7, cy, 1.4)
    piece(0, 0, 3, True); piece(1, 0, 2, True); piece(3, 0, 3, False); piece(1, 2, 2, False)
    piece(3, 2, 2, True); piece(0, 3, 1, False); piece(1, 3, 3, True)


@figure('colossal-p304-1', 230, 110, 'A sliding-block puzzle: the tiles read 8 7 6, 5 4 3, 2 1 and a gap; beside it the goal 1 2 3, 4 5 6, 7 8 and a gap')
def sliding_puzzle(c):
    number_grid(c, 10, 10, 30, [[8, 7, 6], [5, 4, 3], [2, 1, '']], 15)
    number_grid(c, 125, 10, 30, [[1, 2, 3], [4, 5, 6], [7, 8, '']], 15)
    c.rect(10, 10, 90, 90, 1.5); c.rect(125, 10, 90, 90, 1.5)


@figure('colossal-p305-1', 280, 140, 'A square tray holding eight black tiles around an empty centre, and an arrow to the same tray emptied')
def tile_tray(c):
    def tray(x):
        c.rect(x, 10, 110, 110, 1.2); c.rect(x + 12, 22, 86, 86, 1.2)
        for px, py in ((x, 10), (x + 110, 10), (x, 120), (x + 110, 120)):
            c.line(px, py, px + (12 if px == x else -12), py + (12 if py == 10 else -12), 1)
    tray(10)
    for j in range(3):
        for i in range(3):
            if (i, j) != (1, 1): c.rect(24 + i * 28, 24 + j * 28, 26, 26, 0, 'black')
    c.arrow(130, 65, 160, 65, 7, 1.3)
    tray(165)
    c.polyline([(215, 60), (230, 60), (230, 75)], 1)


def board_with_pieces(c, x, y, pieces, cell=18, dark='light'):
    """pieces: 'e4' -> (letter, is_black); a8 is the top-left square."""
    chessboard(c, x, y, cell, 8, dark)
    for square, (letter, black) in pieces.items():
        col, row = 'abcdefgh'.index(square[0]), 8 - int(square[1])
        chess_piece(c, x + col * cell + cell / 2, y + row * cell + cell / 2, letter, black, cell * 0.36)


@figure('colossal-p306-1', 290, 190, 'Two 10 by 10 grids of a hotel plan: the left one shows rooms 1 to 10 and a VACANCY, the right one rooms 7, 10, 2 and 1')
def hotel_grids(c):
    for x0, cell_nums, rooms in ((10, [(1.2, 2.3, '1'), (3.7, 1.1, '2'), (6.2, 1.1, '3'), (8.6, 2.1, '4'), (6.2, 3, '5'), (3.7, 6.9, '6'), (8.6, 7.5, '7'), (1.2, 7.9, '8'), (3.7, 8.9, '9'), (6.2, 8.9, '10')],
                                        [(2.5, 0, 2.5, 2), (2.5, 2, 5, 2), (5, 0, 5, 3), (5, 3, 7.5, 3), (7.5, 2, 7.5, 4), (7.5, 1, 10, 1), (0, 4, 10, 4), (0, 6, 10, 6), (2.5, 6, 2.5, 10), (0, 8, 2.5, 8), (5, 7, 5, 10), (5, 7, 7.5, 7), (7.5, 6, 7.5, 9)]),
                                   (155, [(3.6, 1.7, '7'), (1.1, 3, '10'), (8.6, 6.9, '2'), (6.1, 8.9, '1')],
                                        [(2.5, 0, 2.5, 4), (2.5, 4, 5, 4), (5, 0, 5, 4), (0, 2, 2.5, 2), (7.5, 6, 7.5, 10), (7.5, 6, 10, 6), (5, 8, 7.5, 8), (5, 8, 5, 10)])):
        cw, ch = 12, 16
        for j in range(10):
            for i in range(10): c.rect(x0 + i * cw, 10 + j * ch, cw, ch, 0.4)
        c.rect(x0, 10, 10 * cw, 10 * ch, 1.6)
        for a, b, p, q in rooms: c.line(x0 + a * cw, 10 + b * ch, x0 + p * cw, 10 + q * ch, 1.6)
        for i, j, n in cell_nums: c.text(x0 + i * cw, 10 + j * ch + 4, n, 8, anchor='middle')
        if x0 == 10: c.text(x0 + 60, 10 + 5.3 * ch, 'VACANCY', 8, anchor='middle')


@figure('colossal-p307-1', 240, 220, 'Ten coins numbered 1 to 10 in a triangle: one, two, three and four per row')
def numbered_pennies(c):
    r, d, n = 17, 52, 1
    for row in range(4):
        for k in range(row + 1):
            x, y = 120 + (k - row / 2) * d, 25 + row * 50
            coin(c, x, y, r); c.text(x, y + r + 12, n, 10, anchor='middle', bold=True); n += 1


@figure('colossal-p333-1', 90, 75, 'A staircase of cells: three in the top row, three below with 0 squared in the middle, and four at the bottom with X cubed and X to the first')
def exponent_cells(c):
    u = 20
    for j, cols in enumerate((3, 3, 4)):
        for i in range(cols): c.rect(5 + i * u, 5 + j * u, u, u, 1.1)
    for i, j, base, exp in ((1, 1, '0', '2'), (1, 2, 'X', '3'), (2, 2, 'X', '1')):
        c.text(5 + i * u + 5, 5 + j * u + 15, base, 12, bold=True); c.text(5 + i * u + 14, 5 + j * u + 9, exp, 7, bold=True)


@figure('colossal-p335-1', 120, 70, 'A table headed EVEN and ODD: DAY, MAY, BUY on the even side and SAY, DUE, TEN on the odd side')
def even_odd_table(c):
    c.text(32, 14, 'EVEN', 9, anchor='middle'); c.text(88, 14, 'ODD', 9, anchor='middle'); c.line(5, 18, 115, 18, 0.8)
    for k, (a, b) in enumerate((('DAY', 'SAY'), ('MAY', 'DUE'), ('BUY', 'TEN'))):
        c.text(32, 34 + k * 16, a, 11, anchor='middle'); c.text(88, 34 + k * 16, b, 11, anchor='middle')


@figure('colossal-p336-1', 250, 275, 'A network inside a circle: PENNY at node 2 on top, DIME at node 15 at the bottom, and numbered nodes 1 to 14 joined by curved paths')
def penny_dime_network(c):
    k = 0.5
    T = lambda x, y: ((x - 520) * k, (y - 550) * k)
    nodes = {1: (617, 655), 2: (757, 610), 3: (898, 655), 4: (648, 722), 5: (863, 722), 6: (572, 780), 7: (727, 780), 8: (787, 780), 9: (940, 780),
             10: (643, 835), 11: (757, 855), 12: (868, 835), 13: (680, 912), 14: (833, 912), 15: (757, 990)}
    c.circle(*T(757, 795), 225 * k, 1.2)
    edges = [(1, 4), (4, 6), (4, 7), (6, 10), (7, 10), (2, 7), (2, 8), (8, 5), (5, 3), (5, 9), (9, 12), (8, 12), (7, 11), (8, 11), (11, 13), (11, 14), (13, 15), (14, 15), (10, 13), (12, 14), (1, 2), (3, 2)]
    for a, b in edges:
        p, q = T(*nodes[a]), T(*nodes[b]); m = midpoint(p, q); ux, uy = unit(p, q)
        c.curve([p, (m[0] - uy * 10, m[1] + ux * 10), q], 1.1)
    for n, (x, y) in nodes.items():
        px, py = T(x, y)
        if n in (2, 15):
            c.circle(px, py, 19, 1.2, 'white'); c.text(px, py + 4, n, 10, anchor='middle')
        else:
            c.circle(px, py, 7, 0, 'black'); c.text(px, py + 2.5, n, 6, anchor='middle', bold=False)
            c.circle(px, py, 7, 0.8)
    c.text(*T(757, 565), 'PENNY', 8, anchor='middle'); c.text(T(757, 1035)[0], T(757, 1035)[1], 'DIME', 8, anchor='middle')


@figure('colossal-p339-1', 125, 110, 'Ten points joined by lines: a triangle with points inside it connected so that several lines pass through three points')
def ten_point_graph(c):
    k = 0.37
    T = lambda x, y: ((x - 1050) * k, (y - 555) * k)
    P = {'T': (1213, 570), 'L': (1073, 813), 'R': (1355, 813), 'B': (1180, 813), 'a': (1160, 665), 'b': (1193, 718), 'c': (1235, 718), 'd': (1300, 718), 'e': (1213, 752), 'f': (1300, 760)}
    pts = {n: T(*p) for n, p in P.items()}
    for pair in ('TL', 'TR', 'LR', 'Tb', 'Te', 'ad', 'Ld', 'Ra', 'Bb', 'Bc', 'Tf', 'Lf'):
        segment(c, pts[pair[0]], pts[pair[1]], 1.1)
    for p in pts.values(): c.circle(*p, 3.2, 1, 'white')


@figure('colossal-p340-1', 250, 195, 'A folded card with a double-arched slot and a tall card with a nested paper-clip slot')
def card_slots(c):
    c.polygon([(15, 100), (95, 95), (100, 175), (20, 180)], 1.1); c.line(15, 100, 10, 110, 1.1); c.line(10, 110, 15, 185, 1.1); c.line(15, 185, 20, 180, 1.1)
    c.polyline([(35, 100), (35, 150)], 1.1); c.arc(45, 150, 10, 180, 360, 1.1); c.polyline([(55, 150), (55, 100)], 1.1)
    c.polyline([(60, 100), (60, 155)], 1.1); c.arc(70, 155, 10, 180, 360, 1.1); c.polyline([(80, 155), (80, 100)], 1.1)
    c.rect(150, 10, 90, 180, 1.1)
    for k in (0, 1):
        x = 170 + k * 12; r = 14 - k * 4
        c.polyline([(x, 30 + k * 6), (x, 150)], 1.1); c.arc(x + r, 150, r, 180, 360, 1.1)
        c.polyline([(x + 2 * r, 150), (x + 2 * r, 45)], 1.1); c.arc(x + 2 * r + 8, 45, 8, 90, 270, 1.1)


@figure('colossal-p341-1', 190, 200, 'Four squares of different sizes, tilted and overlapping')
def four_squares(c):
    with c.rotated(-20, 110, 110): c.rect(40, 40, 140, 140, 1.4)
    with c.rotated(30, 110, 75): c.rect(70, 35, 80, 80, 1.4)
    c.rect(20, 110, 60, 60, 1.4)
    with c.rotated(45, 150, 150): c.rect(128, 128, 44, 44, 1.4)


@figure('colossal-p361-1', 160, 160, 'A chess position with white bishops, rooks, knights and pawns, black rook, bishop and pawns, white king on g8 and black king on e4')
def chess_position_1(c):
    board_with_pieces(c, 8, 8, {'a8': ('B', False), 'g8': ('K', False), 'h8': ('R', False), 'b7': ('R', True), 'h7': ('B', False), 'g6': ('R', False),
                                'c5': ('B', True), 'e5': ('P', True), 'g5': ('P', True), 'c4': ('P', False), 'e4': ('K', True), 'g4': ('P', False),
                                'b3': ('P', True), 'e3': ('P', False), 'h3': ('P', True), 'b2': ('P', False), 'e2': ('P', False), 'h2': ('P', False),
                                'd1': ('N', False), 'f1': ('N', False)})


@figure('colossal-p362-1', 160, 160, 'The opening chess position, except that the black king and queen have changed places')
def chess_swapped_royals(c):
    pieces = {}
    for i, f in enumerate('abcdefgh'):
        pieces[f + '7'] = ('P', True); pieces[f + '2'] = ('P', False)
        pieces[f + '8'] = ('RNBKQBNR'[i], True); pieces[f + '1'] = ('RNBQKBNR'[i], False)
    board_with_pieces(c, 8, 8, pieces)


@figure('colossal-p363-1', 340, 180, 'Two chessboards with shaded squares: eight white pieces clustered in a corner, and the same pieces spread over the board')
def chess_spread(c):
    board_with_pieces(c, 8, 8, {'a8': ('R', False), 'b8': ('Q', False), 'c8': ('B', False), 'a7': ('R', False), 'b7': ('K', False), 'c7': ('N', False), 'a6': ('B', False), 'b6': ('N', False)}, 20)
    board_with_pieces(c, 180, 8, {'c7': ('B', False), 'g7': ('K', False), 'e6': ('R', False), 'd5': ('Q', False), 'g4': ('N', False), 'c3': ('R', False), 'a2': ('N', False), 'f2': ('B', False)}, 20)
    c.text(260, 178, 'Figure 12.4', 8, anchor='middle', bold=True)


@figure('colossal-p364-1', 230, 170, "The opening chess position after Black's e-pawn has advanced two squares, beside White's moves N-KB3, N-K5, N-QB6, N takes N")
def chess_knight_tour(c):
    pieces = {}
    for i, f in enumerate('abcdefgh'):
        pieces[f + '2'] = ('P', False); pieces[f + '8'] = ('RNBQKBNR'[i], True); pieces[f + '1'] = ('RNBQKBNR'[i], False)
        if f != 'e': pieces[f + '7'] = ('P', True)
    pieces['e5'] = ('P', True)
    board_with_pieces(c, 8, 8, pieces)
    c.text(165, 60, 'White', 10, True); c.text(165, 78, 'N-KB3', 10); c.text(165, 92, 'N-K5', 10); c.text(165, 106, 'N-QB6', 10); c.text(165, 120, 'N takes N', 10)


@figure('colossal-p367-1', 160, 160, 'A chess position: black rook on b5, black bishop on d5, white bishop on a4 and black king on d1')
def chess_position_2(c):
    board_with_pieces(c, 8, 8, {'b5': ('R', True), 'd5': ('B', True), 'a4': ('B', False), 'd1': ('K', True)})


@figure('colossal-p368-1', 160, 180, 'A chess ending, Black above and White below: black king f7, white king d6, white pawns g3, d2 and f2')
def chess_ending(c):
    c.text(80, 10, 'BLACK', 8, anchor='middle'); c.text(80, 176, 'WHITE', 8, anchor='middle')
    board_with_pieces(c, 8, 16, {'f7': ('K', True), 'd6': ('K', False), 'g3': ('P', False), 'd2': ('P', False), 'f2': ('P', False)})


@figure('colossal-p370-1', 160, 160, 'The opening chess position with all of Black, but White has only pawns, two knights and the king')
def chess_missing_pieces(c):
    pieces = {}
    for i, f in enumerate('abcdefgh'):
        pieces[f + '7'] = ('P', True); pieces[f + '2'] = ('P', False); pieces[f + '8'] = ('RNBQKBNR'[i], True)
    pieces.update({'b1': ('N', False), 'e1': ('K', False), 'g1': ('N', False)})
    board_with_pieces(c, 8, 8, pieces)


@figure('colossal-p370-2', 160, 160, 'A chessboard with only two kings: white on b3 and black on a1')
def chess_two_kings(c):
    board_with_pieces(c, 8, 8, {'b3': ('K', False), 'a1': ('K', True)})


@figure('colossal-p372-1', 280, 340, 'Zigzag paths through square lattices of orders 3 to 8, with lengths 2, 5, 10, 16, 24 and 35')
def lattice_zigzags(c):
    layouts = [(3, 2, 30, 20), (4, 5, 150, 10), (5, 10, 20, 95), (6, 16, 150, 85), (7, 24, 10, 195), (8, 35, 150, 190)]
    import random
    rng = random.Random(7)
    for n, length, x0, y0 in layouts:
        u = 14
        grid(c, x0, y0, n - 1, n - 1, u, 0.6)
        pts = [(x0 + rng.randrange(n) * u, y0 + rng.randrange(n) * u) for _ in range(length + 1)]
        c.polyline(pts, 1.3)
        c.text(x0 + (n - 1) * u / 2, y0 + (n - 1) * u + 12, f'ORDER {n}, LENGTH {length}', 6.5, anchor='middle', bold=True)


@figure('colossal-p373-1', 230, 100, 'Three square grids labelled A, B and C with points A and B marked; the first has a zigzag path joining them')
def grid_paths(c):
    u = 12
    grid(c, 10, 15, 4, 4, u, 0.8); c.polyline([(10 + u, 15 + u), (10 + 3 * u, 15 + 2 * u), (10 + 2 * u, 15 + 2.5 * u), (10 + 3.5 * u, 15 + 3.2 * u)], 1.3)
    c.text(12, 25, 'A', 7, bold=True); c.text(44, 60, 'B', 7, bold=True); c.text(34, 78, 'A', 9, bold=True)
    grid(c, 75, 10, 5, 5, u, 0.8); c.text(90, 36, 'A', 7, bold=True); c.text(114, 58, 'B', 7, bold=True); c.text(105, 82, 'B', 9, bold=True)
    grid(c, 150, 5, 6, 6, u, 0.8); c.text(168, 30, 'A', 7, bold=True); c.text(200, 56, 'B', 7, bold=True); c.text(186, 92, 'C', 9, bold=True)


@figure('colossal-p390-1', 220, 220, 'Eight small figures: a square with both diagonals and midlines, a square halved, a three-line asterisk, a square with a diagonal, a plain square, a diagonal line, a square with a small square on a vertical line, and a small square on a line')
def symmetry_figures(c):
    s = 55
    c.rect(10, 10, s, s, 1.2); c.line(10, 10, 10 + s, 10 + s, 1); c.line(10 + s, 10, 10, 10 + s, 1); c.line(10 + s / 2, 10, 10 + s / 2, 10 + s, 1); c.line(10, 10 + s / 2, 10 + s, 10 + s / 2, 1)
    c.rect(85, 10, s, s, 1.2); c.line(85 + s / 2, 10, 85 + s / 2, 10 + s, 1)
    c.line(158, 15, 215, 65, 1); c.line(158, 65, 215, 15, 1); c.line(158, 40, 215, 40, 1)
    c.rect(10, 85, s, s, 1.2); c.line(10, 85, 10 + s, 85 + s, 1)
    c.rect(85, 85, s, s, 1.2)
    c.line(158, 90, 215, 140, 1)
    c.rect(10, 160, s, s, 1.2); c.line(10 + s / 2, 160, 10 + s / 2, 160 + s, 1); c.rect(10 + s / 2 - 10, 160 + s / 2 - 10, 20, 20, 1)
    c.line(112, 160, 112, 215, 1); c.rect(102, 177, 20, 20, 1)


@figure('colossal-p390-2', 230, 55, 'Five bold symbols numbered 1 to 5, each symmetric about a vertical axis')
def symmetric_symbols(c):
    for k in range(5): c.text(8 + k * 45, 10, k + 1, 7, bold=True)
    c.polyline([(14, 42), (14, 18), (30, 34), (46, 18), (46, 42)], 4); c.line(10, 44, 50, 44, 4)
    c.circle(66, 24, 8, 3.5); c.circle(88, 24, 8, 3.5); c.polyline([(60, 30), (77, 44), (94, 30)], 3.5); c.line(62, 46, 92, 46, 3.5)
    for cx, cy in ((110, 24), (126, 24), (110, 40), (126, 40)): c.circle(cx, cy, 8, 3.5)
    c.polyline([(150, 44), (150, 18), (164, 32), (178, 18), (178, 44)], 4); c.polygon([(152, 28), (176, 28), (164, 40)], 0, 'black')
    c.line(196, 18, 220, 18, 4); c.line(208, 18, 208, 28, 4); c.ellipse(208, 36, 12, 8, 4); c.line(196, 46, 220, 46, 4)


@figure('colossal-p391-1', 220, 65, 'Four bold symbols numbered 2 to 5: a square with a dot, a triangle with a dot, an empty square and a square with a dot')
def dot_symbols(c):
    for k, kind in enumerate(('sq-dot', 'tri-dot', 'sq', 'sq-dot')):
        x = 10 + k * 55; c.text(x, 12, k + 2, 9, bold=True)
        if kind.startswith('sq'): c.rect(x + 2, 20, 36, 36, 5)
        else: c.polygon([(x + 2, 56), (x + 38, 56), (x + 20, 20)], 5)
        if kind.endswith('dot'): dot(c, x + 20, 40 if kind == 'sq-dot' else 46, 4)


@figure('colossal-p394-1', 150, 165, 'A dartboard of an outer ring in six sectors A to F and an inner disk with six arrows from the centre numbered 0 to 5')
def dartboard(c):
    cx, cy, R, r = 75, 88, 60, 30
    c.circle(cx, cy, R, 1.2); c.circle(cx, cy, r, 1.2)
    for k in range(6):
        a = math.radians(k * 60 - 60)
        c.line(cx + r * math.cos(a), cy + r * math.sin(a), cx + R * math.cos(a), cy + R * math.sin(a), 1)
    for lab, ang in zip('ABCDEF', (-90, -30, 30, 90, 150, 210)):
        a = math.radians(ang); c.text(cx + (R + 12) * math.cos(a), cy + (R + 12) * math.sin(a) + 4, lab, 10, anchor='middle')
    dot(c, cx, cy, 2)
    for n, ang in enumerate((225, 270, 315, 135, 90, 45)):
        a = math.radians(ang); c.arrow(cx + 8 * math.cos(a), cy + 8 * math.sin(a), cx + (r - 2) * math.cos(a), cy + (r - 2) * math.sin(a), 5, 0.9)
        c.text(cx + 17 * math.cos(a) + (8 if 45 <= ang <= 135 and ang != 90 else -8 if ang in (225, 135) else 0), cy + 17 * math.sin(a) + 3, n, 8, anchor='middle')


@figure('colossal-p411-1', 130, 125, 'A long-division skeleton: a three-digit divisor into an eight-digit dividend, quotient digit 8 shown, all other digits replaced by X')
def long_division(c):
    c.text(84, 14, '8', 11, anchor='middle')
    c.text(8, 32, 'X X X', 10); c.polyline([(38, 36), (42, 22)], 0.9); c.line(42, 22, 125, 22, 0.9); c.text(44, 32, 'X X X X X X X X', 10)
    rows = [('X X X', 54, 50, 85), ('X X X X', 64, 60, 85), ('X X X', 74, 72, 85), ('X X X X', 84, 84, 85), ('X X X X', 94, 92, 85)]
    for text, x, y, w in rows:
        c.text(x, y, text, 10)
    for x, y in ((50, 53), (72, 75), (84, 97)): c.line(x, y, x + 38, y, 0.9)


def spaced(c, x, y, s, size=11, gap=None, anchor='end', bold=False):
    """Letters or digits spaced out like a cryptarithm, right-aligned at x."""
    gap = gap or size * 0.95
    chars = list(s)
    for k, ch in enumerate(reversed(chars) if anchor == 'end' else chars):
        px = x - k * gap if anchor == 'end' else x + k * gap
        if ch != ' ': c.text(px, y, ch, size, anchor='middle', bold=bold)


@figure('colossal-p412-1', 170, 70, 'Two multiplication skeletons in letters: EEO times OO giving EOEO plus EOO equals OOOOO, and PPP times PP giving PPPP plus PPPP equals PPPPP')
def letter_multiplications(c):
    x = 70
    spaced(c, x, 14, 'EEO', 10); spaced(c, x, 26, 'OO', 10); c.line(x - 32, 30, x + 6, 30, 0.8)
    spaced(c, x, 42, 'EOEO', 10); spaced(c, x - 9.5, 54, 'EOO', 10); c.line(x - 44, 58, x + 6, 58, 0.8); spaced(c, x, 68, 'OOOOO', 10)
    x = 160
    spaced(c, x, 14, 'PPP', 10); spaced(c, x, 26, 'PP', 10); c.line(x - 32, 30, x + 6, 30, 0.8)
    spaced(c, x, 42, 'PPPP', 10); spaced(c, x - 9.5, 54, 'PPPP', 10); c.line(x - 50, 58, x + 6, 58, 0.8); spaced(c, x, 68, 'PPPPP', 10)


@figure('colossal-p412-2', 345, 105, 'Three multiplication skeletons in which every digit is a dot: two digits times two, three digits times two, and three digits times two with longer partial products')
def dot_multiplications(c):
    def skeleton(x, rows):
        y = 12
        for row, mark, line in rows:
            if mark: c.text(x - 8 * len(row) - 14, y + 3, mark, 9)
            for k in range(len(row)):
                dot(c, x - k * 9, y, 1.6)
            if line: c.line(x - 9 * max(len(r[0]) for r in rows) - 2, y + 6, x + 6, y + 6, 0.8)
            y += 14
    skeleton(90, [('..', '', False), ('..', '×', True), ('....', '', False), ('...', '', False), ('...', '+', True), ('......', '', False)])
    skeleton(200, [('..', '', False), ('..', '×', True), ('...', '', False), ('...', '+', True), ('...', '', False)])
    skeleton(330, [('...', '', False), ('..', '×', True), ('....', '', False), ('...', '', False), ('...', '+', True), ('.....', '', False)])


@figure('colossal-p414-1', 170, 80, 'Two word sums: VINGT plus CINQ plus CINQ equals TRENTE, and EIN plus EIN plus EIN plus EIN equals VIER')
def word_sums(c):
    spaced(c, 70, 14, 'VINGT', 10, 9); spaced(c, 70, 27, 'CINQ', 10, 9); c.text(12, 40, '+', 10); spaced(c, 70, 40, 'CINQ', 10, 9)
    c.line(14, 45, 76, 45, 0.8); spaced(c, 70, 58, 'TRENTE', 10, 9)
    for k in range(4):
        spaced(c, 160, 14 + k * 13, 'EIN', 10, 9)
    c.text(118, 53, '+', 10); c.line(120, 58, 166, 58, 0.8); spaced(c, 160, 72, 'VIER', 10, 9)


@figure('colossal-p414-2', 140, 80, 'The sum 318 plus 654 equals 972, and a 3 by 3 grid 7 6 1, 8 5 2, 9 4 3 with a rook above its top right cell and a dashed rook tour from 1 to 9')
def rook_sum(c):
    c.text(6, 24, '+', 12); spaced(c, 58, 24, '318', 12, 11); spaced(c, 58, 40, '654', 12, 11); c.line(8, 45, 66, 45, 0.9); spaced(c, 58, 60, '972', 12, 11)
    number_grid(c, 78, 18, 19, [[7, 6, 1], [8, 5, 2], [9, 4, 3]], 11)
    chess_piece(c, 130, 10, 'R', True, 5)
    C = lambda i, j: (78 + i * 19 + 9.5, 18 + j * 19 + 9.5)
    c.polyline([C(2, 0), C(2, 2), C(1, 2), C(1, 0), C(0, 0), C(0, 2)], 1, (3, 2))


@figure('colossal-p422-1', 175, 60, 'The word IRON spelled with matches')
def iron_matches(c):
    matchstick(c, 12, 50, 12, 10)
    matchstick(c, 32, 50, 32, 10); matchstick(c, 34, 12, 66, 24); matchstick(c, 36, 30, 66, 50)
    matchstick(c, 82, 12, 118, 12); matchstick(c, 120, 14, 120, 48); matchstick(c, 118, 50, 82, 50); matchstick(c, 80, 48, 80, 14)
    matchstick(c, 136, 50, 136, 10); matchstick(c, 138, 12, 164, 48); matchstick(c, 166, 50, 166, 10)


@figure('colossal-p422-2', 85, 85, 'A 4 by 4 grid whose first row is numbered 1, 5, 6, 7 in the corners of the cells and whose first column continues 2, 3, 4')
def numbered_corners(c):
    grid(c, 5, 5, 4, 4, 18, 1.2)
    for i, n in enumerate((1, 5, 6, 7)): c.text(7 + i * 18, 12, n, 7, bold=True)
    for j, n in enumerate((2, 3, 4)): c.text(7, 12 + (j + 1) * 18, n, 7, bold=True)


@figure('colossal-p425-1', 145, 145, 'A 3 by 3 grid of letters: T E A, U R N, B A Y')
def tea_urn_bay(c):
    number_grid(c, 5, 5, 45, [['T', 'E', 'A'], ['U', 'R', 'N'], ['B', 'A', 'Y']], 20)


@figure('colossal-p443-1', 95, 95, 'Four matches forming a plus sign, heads outward')
def plus_matches(c):
    matchstick(c, 47, 44, 47, 8); matchstick(c, 50, 47, 88, 47); matchstick(c, 47, 50, 47, 88); matchstick(c, 44, 47, 6, 47)


@figure('colossal-p444-1', 180, 65, 'Three small match figures: a double cup, a divided rectangle and a slanted frame')
def three_match_figures(c):
    u = 22
    for p, q in (((8, 8), (8, 8 + u)), ((8 + u, 8), (8 + u, 8 + u)), ((8 + 2 * u, 8), (8 + 2 * u, 8 + u)), ((10, 8), (8 + u - 2, 8)), ((14, 8 + u + 4), (8 + 2 * u + 4, 8 + u + 4))):
        matchstick(c, *p, *q)
    x = 70
    for p, q in (((x + 2, 8), (x + u - 2, 8)), ((x + u + 2, 8), (x + 2 * u - 2, 8)), ((x, 10), (x, 8 + u - 2)), ((x + 2 * u, 10), (x + 2 * u, 8 + u - 2)),
                 ((x + 6, 8 + u / 2), (x + 2 * u - 2, 8 + u / 2)), ((x + 2, 8 + u), (x + u - 2, 8 + u)), ((x + u + 2, 8 + u), (x + 2 * u - 2, 8 + u))):
        matchstick(c, *p, *q)
    x = 128
    for p, q in (((x, 10), (x, 8 + u)), ((x + 2 * u, 10), (x + 2 * u, 8 + u)), ((x + 2, 9), (x + 1.4 * u, 8 + u)), ((x + 6, 8 + u + 4), (x + 2 * u + 4, 8 + u + 4))):
        matchstick(c, *p, *q)


@figure('colossal-p444-2', 140, 60, 'Three coins labelled A, B and C: heads, tails and heads, the third set apart')
def three_coins_abc(c):
    for x, lab in ((22, 'A'), (56, 'B'), (118, 'C')):
        coin(c, x, 22, 16)
        if lab == 'B': c.rect(x - 8, 16, 16, 10, 0.7)
        c.text(x, 52, lab, 10, anchor='middle', bold=True)


@figure('colossal-p444-3', 220, 180, 'A fish made of eight matches drawn as thin spindles, with a button for its eye')
def match_fish(c):
    def spindle(p, q):
        ux, uy = unit(p, q); n = math.hypot(q[0] - p[0], q[1] - p[1]); m = midpoint(p, q)
        c.path([('M', *p), ('C', m[0] - uy * 3, m[1] + ux * 3, m[0] - uy * 3, m[1] + ux * 3, *q), ('C', m[0] + uy * 3, m[1] - ux * 3, m[0] + uy * 3, m[1] - ux * 3, *p)], 1, close=True)
    spindle((8, 95), (70, 50)); spindle((8, 95), (70, 140))
    spindle((75, 45), (135, 85)); spindle((75, 145), (135, 105))
    spindle((140, 88), (200, 48)); spindle((140, 102), (200, 142))
    spindle((95, 40), (160, 15)); spindle((95, 150), (160, 175))
    c.circle(45, 92, 7, 1); dots(c, [(42, 90), (48, 90), (42, 95), (48, 95)], 1)


@figure('colossal-p447-1', 245, 170, 'A chain-link fence pattern of linked diamonds')
def chain_link(c):
    w, h = 28, 30
    for row in range(5):
        for col in range(9):
            x = 10 + col * w + (w / 2 if row % 2 else 0); y = 10 + row * h
            c.polyline([(x, y + h * 0.15), (x + w / 2, y - h * 0.12), (x + w, y + h * 0.15), (x + w, y + h * 0.55), (x + w / 2, y + h * 0.82), (x, y + h * 0.55), (x, y + h * 0.15)], 0.9)
            c.line(x + w / 2, y - h * 0.12, x + w / 2 + 3, y - h * 0.2, 0.9); c.line(x + w / 2, y + h * 0.82, x + w / 2 - 3, y + h * 0.9, 0.9)


@figure('colossal-p449-1', 210, 105, 'Three balls stacked in a triangle, and three round pads leaning together to form a cup')
def balls_and_cup(c):
    c.circle(38, 70, 26, 1.2); c.circle(92, 70, 26, 1.2); c.circle(65, 32, 26, 1.2, 'white')
    for cx, cy in ((38, 70), (92, 70), (65, 32)):
        for k in range(6):
            a = math.radians(200 + k * 25); dot(c, cx + 20 * math.cos(a), cy + 20 * math.sin(a), 1)
    c.ellipse(165, 78, 38, 14, 1.2)
    with c.rotated(-60, 140, 55): c.ellipse(140, 55, 34, 11, 1.2)
    with c.rotated(60, 190, 55): c.ellipse(190, 55, 34, 11, 1.2)


@figure('colossal-p450-1', 285, 40, 'A long thin cylindrical rod with a small insect at its left end')
def rod_and_fly(c):
    c.line(14, 12, 272, 12, 1.1); c.line(14, 28, 272, 28, 1.1); c.ellipse(14, 20, 4, 8, 1.1); c.arc(272, 20, 4, -90, 90, 1.1)
    c.ellipse(32, 10, 5, 3, 0, 'black'); c.line(27, 9, 22, 6, 0.6); c.line(37, 9, 42, 6, 0.6)
