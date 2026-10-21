"""Challenging Problems in Geometry: redrawn figures.

Point positions were read from the traced figures (pixel coordinates of the zoomed
trace) and scaled to the traced figure's size in points: pts(size, origin, {...}).
"""


def pts(size, origin, points):
    """Map zoom pixels (cell origin subtracted) to points; size is the traced (w, h)."""
    k = 512 / max(size)
    ox, oy = origin
    return {name: ((x - ox) / k, (y - oy) / k) for name, (x, y) in points.items()}


def pair_names(token):
    """'AB' -> ('A', 'B'); multi-character names are joined with '-': "C-A'"."""
    return tuple(token.split('-')) if '-' in token else (token[0], token[1:])


def draw(c, P, lines='', dashed='', thick='', where=None, rights=(), dots_at='', size=9):
    """Segments between named points, labels and right-angle marks."""
    for token in lines.split(): a, b = pair_names(token); segment(c, P[a], P[b], 1.1)
    for token in dashed.split(): a, b = pair_names(token); segment(c, P[a], P[b], 1, (4, 3))
    for token in thick.split(): a, b = pair_names(token); segment(c, P[a], P[b], 2.4)
    for corner, a, b in rights: right_angle(c, P[corner], P[a], P[b], 5)
    for name in dots_at: dot(c, *P[name], 1.6)
    shown = {k: v for k, v in P.items() if not k.startswith('_')}
    labels(c, shown, where or {}, size)


def caption(c, x, y, text):
    c.text(x, y, text, 8, bold=True)


@figure('geometry-p12-2', 251, 133, 'Problem 1-1: triangle ABC with D on BC and E on CA; segments AD and BE meet at F')
def g1_1(c):
    P = pts((251, 133), (520, 0), {'A': (752, 255), 'B': (1010, 255), 'C': (852, 85), 'D': (905, 135), 'E': (790, 200), 'F': (837, 160)})
    draw(c, P, 'AB BC CA AD BE AF BF', where={'A': 'sw', 'B': 'se', 'C': 'n', 'D': 'ne', 'E': 'w', 'F': 'n'})
    caption(c, 110, 60, '1-1')


@figure('geometry-p13-1', 225, 74, 'Problem 1-2: triangle ABC with D on CA and segment DB')
def g1_2(c):
    P = pts((225, 74), (1040, 0), {'A': (1420, 32), 'B': (1530, 152), 'C': (1070, 150), 'D': (1280, 80)})
    draw(c, P, 'CA CB AB DB', where={'A': 'n', 'B': 'e', 'C': 'w', 'D': 'nw'})
    caption(c, 70, 20, '1-2')


@figure('geometry-p13-2', 204, 101, 'Problem 1-3: triangle ABC with a line through D parallel to the base meeting AC at L and AB at M; DB crosses AC at E')
def g1_3(c):
    P = pts((204, 101), (0, 540), {'D': (35, 628), 'A': (228, 572), 'B': (485, 760), 'C': (112, 760), 'L': (195, 628), 'M': (295, 628), 'E': (178, 660), '_X': (20, 760)})
    draw(c, P, 'DM DB AC AB DC _X-B', where={'D': 'w', 'A': 'n', 'B': 'e', 'C': 's', 'L': 'n', 'M': 'ne', 'E': 'e'})
    caption(c, 30, 16, '1-3')


@figure('geometry-p13-3', 267, 120, 'Problem 1-4: right triangle ABC with the altitude CD, angle bisector CE and median CF from the right angle')
def g1_4(c):
    P = pts((267, 120), (520, 540), {'B': (758, 598), 'C': (758, 757), 'A': (1012, 757), 'D': (823, 650), 'E': (850, 660), 'F': (882, 676)})
    draw(c, P, 'BC CA AB CD CE CF', where={'B': 'n', 'C': 'sw', 'A': 'se', 'D': 'ne', 'E': 'ne', 'F': 'ne'}, rights=[('D', 'C', 'A')])
    caption(c, 68, 48, '1-4')


@figure('geometry-p14-1', 120, 112, 'Problem 1-6: triangle ABC with the right angle at B; D lies on the extension so that AD crosses BC at M')
def g1_6(c):
    P = pts((282, 112), (1040, 540), {'A': (1215, 560), 'B': (1068, 660), 'C': (1250, 655), 'D': (1120, 730), 'M': (1160, 660)})
    draw(c, P, 'AB AC BC AD BD', where={'A': 'n', 'B': 'w', 'C': 'e', 'D': 'sw', 'M': 's'}, rights=[('B', 'A', 'D')])
    caption(c, 22, 20, '1-6')


@figure('geometry-p14-4', 150, 112, 'Problem 1-8: triangle ABC with D on CA and E on CB; segments AE, DB and CF meet inside at P, Q and F', page=14)
def g1_8(c):
    P = pts((282, 112), (1040, 540), {'A': (1290, 735), 'B': (1535, 735), 'C': (1465, 580), 'D': (1385, 640), 'E': (1500, 655), 'F': (1445, 685), 'P': (1420, 665), 'Q': (1490, 675)})
    draw(c, P, 'AB BC CA AE DB CF DE AQ', where={'A': 'w', 'B': 'e', 'C': 'n', 'D': 'nw', 'E': 'e', 'F': 's', 'P': 'sw', 'Q': 'se'}, size=8)
    caption(c, 30, 22, '1-8')


@figure('geometry-p14-2', 110, 107, 'Square ABCD with diagonals meeting at E; BQ is drawn to Q on DC and FP is perpendicular to BQ at P')
def g_square_bq(c):
    P = pts((110, 107), (0, 0), {'D': (40, 45), 'C': (275, 45), 'A': (40, 275), 'B': (275, 275), 'Q': (178, 45), 'P': (205, 120), 'E': (157, 160), 'F': (120, 100)})
    draw(c, P, 'DC CB BA AD AC DB BQ FP', where={'D': 'nw', 'C': 'ne', 'A': 'sw', 'B': 'se', 'Q': 'n', 'P': 'e', 'E': 'se', 'F': 'w'}, rights=[('P', 'F', 'Q')])


@figure('geometry-p14-3', 112, 104, 'Square ABCD with a point E inside joined to the four corners')
def g_square_e(c):
    P = pts((112, 104), (520, 0), {'A': (565, 35), 'B': (800, 35), 'D': (565, 265), 'C': (800, 265), 'E': (680, 230)})
    draw(c, P, 'AB BC CD DA AE BE CE DE', where={'A': 'nw', 'B': 'ne', 'C': 'se', 'D': 'sw', 'E': 'e'})


@figure('geometry-p15-1', 170, 143, 'Problem 1-11: triangle ABC with D and G on AC, F on BC and E on AB joined by segments')
def g1_11(c):
    P = pts((334, 143), (1040, 0), {'A': (1058, 205), 'B': (1225, 205), 'C': (1175, 75), 'D': (1115, 135), 'E': (1140, 205), 'F': (1205, 140), 'G': (1130, 120)})
    draw(c, P, 'AB BC CA DF GF GE DE EF', where={'A': 'w', 'B': 'e', 'C': 'n', 'D': 'w', 'E': 's', 'F': 'e', 'G': 'n'}, size=8)
    caption(c, 22, 30, '1-11')


@figure('geometry-p15-4', 170, 143, 'Problem 1-12: right triangle ABC with GD perpendicular to AC and EF perpendicular to BC', page=15)
def g1_12(c):
    P = pts((334, 143), (1040, 0), {'A': (1245, 200), 'B': (1545, 200), 'C': (1455, 65), 'D': (1380, 200), 'E': (1490, 200), 'F': (1523, 163), 'G': (1335, 140)})
    draw(c, P, 'AB BC CA GD EF', where={'A': 'w', 'B': 'e', 'C': 'n', 'D': 's', 'E': 's', 'F': 'e', 'G': 'nw'}, rights=[('G', 'A', 'D'), ('F', 'E', 'C'), ('C', 'A', 'B')], size=8)
    caption(c, 40, 30, '1-12')


@figure('geometry-p16-1', 186, 123, 'Problem 1-15: triangle ABC with altitude AD, BE perpendicular to AC, and GK through H')
def g1_15(c):
    P = pts((186, 123), (0, 540), {'A': (135, 578), 'B': (38, 810), 'C': (468, 810), 'D': (135, 810), 'E': (190, 605), 'F': (135, 630), 'G': (85, 700), 'H': (135, 682), 'K': (240, 810)})
    draw(c, P, 'AB BC CA AD BE GK AG', where={'A': 'n', 'B': 'sw', 'C': 'se', 'D': 's', 'E': 'ne', 'F': 'e', 'G': 'w', 'H': 'e', 'K': 's'}, rights=[('D', 'A', 'C'), ('E', 'B', 'C')], size=8)
    caption(c, 10, 38, '1-15')


@figure('geometry-p16-2', 283, 176, 'Problem 1-16: parallelogram ABDC with diagonal AC, M the midpoint of BC, and T on the extension of BA with TD perpendicular to BA')
def g1_16(c):
    P = pts((283, 176), (520, 540), {'B': (680, 675), 'A': (915, 668), 'T': (950, 655), 'C': (745, 780), 'D': (990, 780), 'M': (712, 735)})
    draw(c, P, 'BT BC CD AD TD AC MA', where={'B': 'w', 'A': 'n', 'T': 'ne', 'C': 'sw', 'D': 'e', 'M': 'w'}, rights=[('T', 'A', 'D')], size=8)
    caption(c, 70, 125, '1-16')


@figure('geometry-p16-3', 153, 107, "Problem 1-18: line XZ with perpendiculars XA' and ZB; C is above the line with CY perpendicular at Y; CA', CB and A'B are drawn")
def g1_18(c):
    P = pts((153, 107), (1040, 540), {'X': (1085, 715), 'Z': (1440, 715), 'C': (1365, 580), "A'": (1095, 770), 'B': (1435, 810), 'G': (1308, 712), 'Y': (1365, 715)})
    draw(c, P, "XZ CY C-A' CB A'-B X-A' ZB", where={'X': 'n', 'Z': 'n', 'C': 'n', "A'": 'w', 'B': 'e', 'G': 'n', 'Y': 's'}, rights=[('Y', 'C', 'Z'), ('X', 'Z', "A'"), ('Z', 'X', 'B')], size=8)
    caption(c, 20, 25, '1-18')


@figure('geometry-p16-4', 120, 100, 'Problem 1-19: triangle ABC with CQ perpendicular to AQ, P on CQ with PB perpendicular to CQ, and M on AB')
def g1_19(c):
    P = pts((120, 100), (0, 0), {'C': (195, 45), 'A': (38, 240), 'B': (295, 190), 'P': (190, 190), 'M': (175, 215), 'Q': (190, 250)})
    draw(c, P, 'CA CB AB CQ PB AQ', where={'C': 'n', 'A': 'w', 'B': 'e', 'P': 'nw', 'M': 'nw', 'Q': 'e'}, rights=[('P', 'C', 'B'), ('Q', 'C', 'A')], size=8)
    caption(c, 8, 30, '1-19')


@figure('geometry-p17-1', 114, 113, 'A figure with points F, B, C, A, D and E: solid segments FB, BC, FA, AD, DC, AE and DE, with FC, FE and CE dashed')
def g_fbcade(c):
    P = pts((114, 113), (520, 0), {'F': (548, 32), 'B': (635, 80), 'C': (810, 70), 'A': (570, 145), 'D': (735, 140), 'E': (660, 275)})
    draw(c, P, 'FB BC FA AD DC AE DE', 'FC FE CE', where={'F': 'nw', 'B': 'se', 'C': 'e', 'A': 'w', 'D': 'ne', 'E': 's'})


@figure('geometry-p18-1', 150, 128, 'Problem 2-1: triangle ABC with D on AB and E on AC, DE parallel to BC, and a smaller parallel FG near A')
def g2_1(c):
    P = pts((294, 128), (1040, 0), {'A': (1135, 22), 'B': (1075, 175), 'C': (1215, 175), 'D': (1110, 90), 'E': (1175, 90), 'F': (1133, 50), 'G': (1160, 50), 'H': (1125, 38)})
    draw(c, P, 'AB BC CA DE HE DC', 'FG', where={'A': 'n', 'B': 'sw', 'C': 'se', 'D': 'w', 'E': 'e', 'F': 'w', 'G': 'e', 'H': 'w'}, size=7)
    caption(c, 10, 40, '2-1')


@figure('geometry-p18-4', 165, 128, 'Problem 2-2: triangle APC with B on PC; BD is perpendicular to AC at D, EF perpendicular to AC at F, and BE perpendicular to PA', page=18)
def g2_2(c):
    P = pts((294, 128), (1040, 0), {'A': (1440, 22), 'C': (1540, 175), 'P': (1265, 175), 'B': (1330, 175), 'E': (1305, 210), 'D': (1465, 50), 'F': (1480, 80)})
    draw(c, P, 'AP AC PC BD EF BE AB', where={'A': 'n', 'C': 'e', 'P': 'w', 'B': 'se', 'E': 's', 'D': 'e', 'F': 'e'}, rights=[('D', 'B', 'C'), ('F', 'E', 'C'), ('E', 'B', 'P')], size=7)
    caption(c, 40, 40, '2-2')


@figure('geometry-p19-2', 160, 125, 'Problem 2-8: triangle ABC with the line from A to G on BC, H on AB joined to E, and BE drawn, with a right angle at E')
def g2_8(c):
    P = pts((314, 125), (520, 540), {'A': (620, 565), 'B': (545, 720), 'C': (735, 720), 'H': (580, 645), 'E': (632, 712), 'D': (632, 720), 'G': (648, 720)})
    draw(c, P, 'AB BC CA AG HE BE', where={'A': 'n', 'B': 'w', 'C': 'e', 'H': 'nw', 'E': 'e', 'D': 's', 'G': 's'}, rights=[('E', 'H', 'B')], size=7)
    caption(c, 15, 30, '2-8')


@figure('geometry-p19-5', 160, 125, 'Problem 2-9: triangle with base HB, G above H and C above F; GB crosses CA at E; CF is perpendicular to HB', page=19)
def g2_9(c):
    P = pts((314, 125), (520, 540), {'G': (800, 660), 'H': (775, 720), 'B': (1020, 720), 'C': (955, 595), 'A': (910, 720), 'E': (920, 700), 'F': (958, 720)})
    draw(c, P, 'HB GB GH CF CA CB', where={'G': 'nw', 'H': 'sw', 'B': 'se', 'C': 'n', 'A': 's', 'E': 'ne', 'F': 's'}, rights=[('F', 'C', 'B'), ('G', 'H', 'B'), ('E', 'C', 'G')], size=7)
    caption(c, 50, 30, '2-9')


@figure('geometry-p20-1', 215, 102, 'Problem 2-10: parallelogram ABCD with diagonals AC and DB meeting near P, the thick line HG through E and F, and the thick segment AM through E')
def g2_10(c):
    P = pts((215, 102), (1040, 540), {'A': (1140, 570), 'B': (1430, 570), 'D': (1095, 755), 'C': (1525, 755), 'H': (1115, 675), 'G': (1485, 675), 'E': (1235, 675), 'F': (1360, 675), 'P': (1295, 635), 'M': (1310, 755)})
    draw(c, P, 'AB BC CD DA AC DB', thick='HG AM', where={'A': 'nw', 'B': 'ne', 'D': 'sw', 'C': 'se', 'H': 'w', 'G': 'e', 'E': 's', 'F': 'ne', 'P': 'n', 'M': 's'}, size=8)
    caption(c, 10, 45, '2-10')


@figure('geometry-p20-2', 205, 86, 'Problem 2-11: triangle APB with K and L on AB joined to P')
def g2_11(c):
    P = pts((205, 86), (0, 0), {'A': (38, 185), 'B': (485, 185), 'P': (200, 35), 'K': (140, 185), 'L': (255, 185)})
    draw(c, P, 'AB AP BP PK PL', where={'A': 'w', 'B': 'e', 'P': 'n', 'K': 's', 'L': 's'})
    caption(c, 16, 35, '2-11')


@figure('geometry-p21-1', 160, 100, 'Problem 2-13: triangle ABX with C on XB and on AY; CZ is perpendicular to AB and BY is drawn')
def g2_13(c):
    P = pts((312, 152), (520, 0), {'A': (655, 210), 'B': (835, 210), 'C': (745, 160), 'X': (700, 140), 'Y': (915, 80), 'Z': (720, 210)})
    draw(c, P, 'AY XB AB CZ BY AX', where={'A': 'w', 'B': 'e', 'C': 'n', 'X': 'n', 'Y': 'ne', 'Z': 's'}, size=8)
    caption(c, 10, 55, '2-13')


@figure('geometry-p21-2', 230, 78, 'Problem 2-16a: parallelogram ABCD with the line AF through G on DB and E on BC, F on the extension of DC shown dashed')
def g2_16a(c):
    P = pts((230, 78), (1040, 0), {'A': (1190, 22), 'B': (1430, 22), 'D': (1095, 150), 'C': (1345, 150), 'F': (1530, 150), 'G': (1315, 75), 'E': (1395, 95)})
    draw(c, P, 'AB BC CD DA AF DB', 'CF', where={'A': 'n', 'B': 'n', 'D': 'w', 'C': 's', 'F': 'e', 'G': 's', 'E': 'ne'}, size=8)
    caption(c, 8, 20, '2-16a')


@figure('geometry-p22-1', 233, 59, 'Problem 2-16b: a long thin triangle with A and E on the upper side, D and C on the lower side, and the crossing segments AD, DB, EB and BC')
def g2_16b(c):
    P = pts((233, 59), (0, 540), {'_L': (20, 612), 'A': (262, 590), 'E': (385, 580), 'G': (490, 580), 'D': (232, 640), 'B': (370, 615), 'C': (338, 655)})
    draw(c, P, '_L-G _L-C AD DB EB BC AE', where={'A': 'n', 'E': 'n', 'G': 'e', 'D': 's', 'B': 'se', 'C': 's'}, size=8)
    caption(c, 40, 10, '2-16b')


@figure('geometry-p22-2', 109, 132, 'Problem 3-1: triangle ABC with altitude AD and a point E on it joined to B and C')
def g3_1(c):
    P = pts((109, 132), (520, 540), {'A': (655, 648), 'B': (795, 875), 'C': (560, 875), 'D': (655, 875), 'E': (655, 775)})
    draw(c, P, 'AB BC CA AD CE BE', where={'A': 'n', 'B': 'e', 'C': 'w', 'D': 's', 'E': 'e'}, rights=[('D', 'A', 'B')])
    caption(c, 6, 40, '3-1')


@figure('geometry-p23-1', 160, 100, 'Problem 3-5: rectangle ABCD with E on DC and F on AB; AE, EF and FC are drawn')
def g3_5(c):
    P = pts((217, 137), (1040, 540), {'A': (1285, 612), 'B': (1525, 612), 'D': (1285, 765), 'C': (1525, 765), 'E': (1350, 765), 'F': (1450, 612)})
    draw(c, P, 'AB BC CD DA AE EF FC', where={'A': 'nw', 'B': 'ne', 'D': 'sw', 'C': 'se', 'E': 's', 'F': 'n'}, rights=[('B', 'A', 'C')])
    caption(c, 8, 50, '3-5')


@figure('geometry-p24-1', 117, 98, 'Problem 3-10: right triangle ABC with the right angle at C, D on CA, and CP perpendicular to DB')
def g3_10(c):
    P = pts((117, 98), (0, 0), {'A': (75, 30), 'B': (295, 250), 'C': (75, 250), 'D': (75, 140), 'P': (120, 165)})
    draw(c, P, 'AB BC CA DB CP', where={'A': 'n', 'B': 'e', 'C': 'sw', 'D': 'w', 'P': 'ne'}, rights=[('C', 'A', 'B'), ('P', 'C', 'B')])
    caption(c, 4, 30, '3-10')


@figure('geometry-p24-2', 89, 97, 'Problem 3-9: quadrilateral ABCD with diagonal AC; BP and DQ are perpendicular to AC')
def g3_9(c):
    P = pts((89, 97), (520, 0), {'A': (580, 118), 'C': (735, 118), 'B': (640, 45), 'D': (670, 220), 'P': (640, 118), 'Q': (668, 118)})
    draw(c, P, 'AB BC CD DA AC BP DQ', where={'A': 'w', 'C': 'e', 'B': 'n', 'D': 's', 'P': 's', 'Q': 'n'}, rights=[('P', 'B', 'C'), ('Q', 'D', 'A')])
    caption(c, 6, 20, '3-9')


@figure('geometry-p26-1', 89, 103, 'Problem 4-2: a circle with diameter BD and centre O; AB is tangent at B, AC meets the circle at C, and CE is perpendicular to BD')
def g4_2(c):
    P = pts((89, 103), (0, 540), {'A': (70, 565), 'B': (62, 733), 'D': (218, 733), 'C': (188, 668), 'O': (140, 733), 'E': (190, 733)})
    k = 512 / 103
    c.circle(*P['O'], 78 / k, 1.1)
    draw(c, P, 'AB AC BD CE', where={'A': 'n', 'B': 'w', 'D': 'e', 'C': 'ne', 'O': 's', 'E': 's'}, rights=[('E', 'C', 'D')], dots_at='O')
    caption(c, 4, 30, '4-2')


@figure('geometry-p26-2', 109, 95, 'Problem 4-4: a circle with perpendicular chords AC and DB meeting at G; AD, AB and BP are drawn and E lies outside on a short perpendicular')
def g4_4(c):
    P = pts((109, 95), (520, 540), {'A': (657, 590), 'B': (795, 705), 'C': (660, 775), 'D': (598, 705), 'E': (575, 678), 'G': (660, 705), 'P': (735, 740)})
    k = 512 / 109
    c.circle((698 - 520) / k, (690 - 540) / k, 100 / k, 1.1)
    draw(c, P, 'AC DB AD AB BP CP', where={'A': 'n', 'B': 'e', 'C': 's', 'D': 'w', 'E': 'w', 'G': 'sw', 'P': 'se'}, rights=[('G', 'A', 'B')])
    segment(c, P['E'], midpoint(P['A'], P['D']), 1.1); right_angle(c, midpoint(P['A'], P['D']), P['E'], P['A'], 4)
    caption(c, 4, 25, '4-4')


@figure('geometry-p27-1', 130, 94, 'Problem 4-6: a circle with centre O, radius OA upward through P and radius OB; AB and PB are drawn and the tangents at M and N are indicated')
def g4_6(c):
    P = pts((280, 94), (1040, 540), {'O': (1140, 635), 'M': (1125, 570), 'A': (1143, 570), 'P': (1140, 595), 'B': (1210, 635), 'N': (1210, 650), 'Q': (1180, 635)})
    k = 512 / 280
    c.circle(*P['O'], 65 / k, 1.1)
    draw(c, P, 'OA OB AB PB', where={'O': 'sw', 'M': 'nw', 'A': 'ne', 'P': 'w', 'B': 'e', 'N': 'se', 'Q': 's'}, rights=[('Q', 'O', 'P')], size=7)
    caption(c, 8, 30, '4-6')


@figure('geometry-p27-4', 150, 94, 'Problem 4-8: a circle with the secant PC through A and the secant PF through E, B and D; AB and CD are perpendicular to the secants', page=27)
def g4_8(c):
    P = pts((280, 94), (1040, 540), {'P': (1300, 632), 'A': (1400, 632), 'C': (1532, 632), 'E': (1385, 600), 'B': (1405, 595), 'D': (1500, 565), 'F': (1515, 565)})
    k = 512 / 280
    c.circle((1465 - 1040) / k, (630 - 540) / k, 67 / k, 1.1)
    draw(c, P, 'PC PF AB CD', where={'P': 'w', 'A': 's', 'C': 'e', 'E': 'nw', 'B': 'n', 'D': 'n', 'F': 'ne'}, rights=[('B', 'A', 'F'), ('D', 'C', 'F')], size=7)
    caption(c, 10, 35, '4-8')


@figure('geometry-p28-1', 99, 103, 'Problem 4-12: two circles; chords DJ and LM of the larger meet at K, and SK is perpendicular at K')
def g4_12(c):
    P = pts((99, 103), (0, 0), {'S': (175, 30), 'D': (90, 75), 'L': (48, 115), 'K': (130, 120), 'M': (220, 95), 'J': (250, 185)})
    k = 512 / 103
    c.circle(150 / k, 160 / k, 110 / k, 1.1); c.arc(170 / k, 120 / k, 90 / k, 150, 380, 1.1)
    draw(c, P, 'DJ LM SK', where={'S': 'n', 'D': 'nw', 'L': 'w', 'K': 's', 'M': 'e', 'J': 'e'}, rights=[('K', 'S', 'J')], size=8)
    caption(c, 4, 14, '4-12')


@figure('geometry-p29-1', 120, 100, 'Problem 4-17: a circle with centre O; P is outside, PA and PC are drawn, A is on the circle and DC crosses the circle through E and B')
def g4_17(c):
    P = pts((261, 139), (520, 0), {'A': (803, 60), 'P': (760, 160), 'C': (935, 160), 'B': (838, 145), 'D': (828, 60), 'E': (818, 110), 'O': (880, 120), 'T': (855, 175)})
    k = 512 / 261
    c.circle(*P['O'], 70 / k, 1.1)
    draw(c, P, 'PA PC DC AB', where={'A': 'nw', 'P': 'w', 'C': 'e', 'B': 'e', 'D': 'n', 'E': 'e', 'O': 's', 'T': 's'}, dots_at='O', size=8)
    caption(c, 6, 40, '4-17')


@figure('geometry-p30-1', 96, 94, 'Problem 4-21: a circle with centre O and a smaller circle through C and O; CA and CB cut the small circle at D and D prime, and AB is a chord of the large circle')
def g4_21(c):
    P = pts((96, 94), (1040, 0), {'C': (1190, 48), 'A': (1085, 145), 'B': (1280, 80), 'O': (1190, 160), 'D': (1125, 100), "D'": (1255, 105)})
    k = 512 / 96
    c.circle(150 / k, 150 / k, 100 / k, 1.1); c.circle(150 / k, 104 / k, 56 / k, 1.1)
    draw(c, P, "CO CA CB AB A-D' DB", where={'C': 'n', 'A': 'w', 'B': 'e', 'O': 's', 'D': 'w', "D'": 'e'}, dots_at='O', size=8)
    caption(c, 4, 14, '4-21')


@figure('geometry-p30-2', 96, 94, 'A circle with an inscribed smaller circle touching it at P; the tangent at P, chords PB and PA cutting the small circle at E and D, and chord BA touching the small circle at C')
def g_tangent_circles(c):
    P = pts((96, 94), (0, 540), {'P': (140, 595), 'T': (230, 580), 'B': (38, 680), 'A': (240, 690), 'C': (140, 690), 'E': (85, 620), 'D': (195, 630)})
    k = 512 / 96
    c.circle(140 / k, 160 / k, 100 / k, 1.1); c.circle(140 / k, 95 / k, 40 / k, 1.1)
    c.line(20 / k, 40 / k, 250 / k, 40 / k, 1.1)
    draw(c, P, 'PB PA BA', where={'P': 'n', 'T': 'n', 'B': 'w', 'A': 'e', 'C': 's', 'E': 'w', 'D': 'e'}, size=8)


@figure('geometry-p31-1', 150, 100, "Problem 4-25: two circles with centres O' and O touching at P on the line CB; the triangle ABC with D and E on the circles and AP through G")
def g4_25(c):
    P = pts((304, 193), (520, 540), {'A': (675, 575), 'C': (540, 678), 'B': (765, 678), 'D': (615, 610), 'E': (720, 622), 'G': (676, 616), 'P': (675, 678), "O'": (610, 678), 'O': (720, 678)})
    k = 512 / 304
    c.circle(*P["O'"], 68 / k, 1.1); c.circle(*P['O'], 42 / k, 1.1)
    draw(c, P, 'AC AB CB AP DE', where={'A': 'n', 'C': 'w', 'B': 'e', 'D': 'nw', 'E': 'ne', 'G': 'e', 'P': 's', "O'": 's', 'O': 's'}, dots_at=["O'", 'O'], size=7)
    caption(c, 10, 20, '4-25')


@figure('geometry-p31-4', 90, 100, 'Problem 4-27: triangle ABC with two circles inside, the larger touching the base and the smaller touching the upper sides, with D and E on the sides and F on the base', page=31)
def g4_27(c):
    P = pts((304, 193), (520, 540), {'A': (935, 580), 'B': (872, 715), 'C': (1020, 715), 'D': (962, 603), 'E': (990, 655), 'F': (948, 715), 'O': (940, 672), '_o': (940, 620)})
    k = 512 / 304
    c.circle(*P['_o'], 15 / k, 1.1); c.circle(*P['O'], 28 / k, 1.1); dot(c, *P['_o'], 1.3)
    draw(c, P, 'AB BC CA', where={'A': 'n', 'B': 'sw', 'C': 'se', 'D': 'e', 'E': 'e', 'F': 's', 'O': 'w'}, dots_at='O', size=7)
    caption(c, 4, 40, '4-27')


@figure('geometry-p32-1', 134, 147, 'Problem 4-29: a semicircular arrangement: a large circle with diameter AB, two circles on AE and FB as diameters, a small circle D above them, and the region below AB outside the small circles shaded black')
def g4_29(c):
    P = pts((134, 147), (1040, 540), {'A': (1180, 830), 'B': (1380, 830), 'O': (1280, 830), 'E': (1230, 830), 'F': (1330, 830), 'C': (1280, 730), 'D': (1280, 760)})
    k = 512 / 147
    R = 100 / k; cx, cy = P['O']
    c.path(c.arc_segments(cx, cy, R, 0, 180), 0, 'black', close=True)
    c.circle(*P['E'], 50 / k, 1.1, 'white'); c.circle(*P['F'], 50 / k, 1.1, 'white')
    c.circle(cx, cy, R, 1.3); c.circle(*P['D'], 30 / k, 1.1)
    draw(c, P, 'AB', where={'A': 'w', 'B': 'e', 'O': 's', 'E': 's', 'F': 's', 'C': 'n', 'D': 'n'}, dots_at='EFD', size=8)
    caption(c, 4, 70, '4-29')


@figure('geometry-p32-2', 131, 103, 'Problem 4-31: a quarter circle with centre O and radii OA and OB; a circle with centre P touches OA at C, OB at D and the arc at T; the region between the arc, OA and the circle near A is shaded')
def g4_31(c):
    P = pts((131, 103), (0, 0), {'O': (105, 255), 'A': (105, 30), 'B': (335, 255), 'T': (290, 110), 'C': (105, 155), 'D': (200, 255), 'P': (200, 160)})
    k = 512 / 131
    R, r = 230 / k, 95 / k
    aT = math.degrees(math.atan2(P['T'][1] - P['O'][1], P['T'][0] - P['O'][0]))
    bT = math.degrees(math.atan2(P['T'][1] - P['P'][1], P['T'][0] - P['P'][0])); bC = 180
    shade = c.arc_segments(*P['O'], R, -90, aT) + c.arc_segments(*P['P'], r, bT, bC)[1:] + [('L', *P['A'])]
    c.path(shade, 0, 'black', close=True)
    c.line(*P['O'], *P['A'], 1.2); c.line(*P['O'], *P['B'], 1.2); c.arc(*P['O'], R, -90, 0, 1.2); c.circle(*P['P'], r, 1.2)
    draw(c, P, '', where={'O': 'sw', 'A': 'nw', 'B': 'e', 'T': 'ne', 'C': 'w', 'D': 's', 'P': 'n'}, dots_at='P')
    caption(c, 4, 28, '4-31')


@figure('geometry-p34-1', 120, 120, 'A square ABCD with a point E near the top joined to A and B, and EF drawn to F on BC with a right angle at E')
def g_square_ef(c):
    P = pts((277, 120), (520, 0), {'D': (545, 20), 'C': (680, 20), 'A': (545, 155), 'B': (680, 155), 'E': (600, 45), 'F': (680, 85)})
    draw(c, P, 'DC CB BA AD AE EB EF', where={'D': 'nw', 'C': 'ne', 'A': 'sw', 'B': 'se', 'E': 'ne', 'F': 'e'}, rights=[('E', 'A', 'F')])
    c.text(P['A'][0] + (P['B'][0] - P['A'][0]) / 2, P['A'][1] + 9, 'x', 7, True, 'middle')


@figure('geometry-p34-4', 160, 120, 'Problem 4-40: a circle with centre O; from A outside, the secant AE through D and G and the line AB; the chords BC and FC', page=34)
def g4_40(c):
    P = pts((277, 120), (520, 0), {'A': (785, 118), 'B': (905, 35), 'F': (990, 40), 'D': (885, 118), 'G': (960, 118), 'E': (1015, 118), 'C': (935, 165), 'O': (948, 95), '_T': (945, 15)})
    k = 512 / 277
    c.circle(*P['O'], 65 / k, 1.1)
    draw(c, P, 'A-_T AE BC FC AC', where={'A': 'w', 'B': 'nw', 'F': 'ne', 'D': 's', 'G': 'se', 'E': 'e', 'C': 's', 'O': 'n'}, dots_at='O', size=8)
    caption(c, 8, 25, '4-40')


@figure('geometry-p35-1', 236, 101, 'Problem 5-1: parallelogram ABCD with E on AB and a second parallelogram DEFG sharing the vertex D')
def g5_1(c):
    P = pts((236, 101), (1040, 0), {'A': (1100, 30), 'E': (1200, 25), 'B': (1325, 28), 'F': (1395, 65), 'D': (1140, 125), 'C': (1360, 125), 'G': (1350, 160)})
    draw(c, P, 'AB BC CD DA DE EF FG GD', where={'A': 'w', 'E': 'n', 'B': 'ne', 'F': 'e', 'D': 'w', 'C': 'e', 'G': 'se'})
    caption(c, 8, 45, '5-1')


@figure('geometry-p36-1', 120, 112, 'Problem 5-5: a circle with centre O touching two perpendicular lines at E and F; OA meets the upper line at A with D on OA, and DC is drawn to the vertical line')
def g5_5(c):
    P = pts((206, 112), (0, 540), {'O': (390, 680), 'E': (390, 580), 'B': (430, 580), 'A': (480, 580), 'C': (485, 630), 'F': (485, 670), 'D': (455, 615)})
    kk = 512 / 206
    c.circle(*P['O'], 95 / kk, 1.1)
    c.line(310 / kk, (580 - 540) / kk, 485 / kk, (580 - 540) / kk, 1.1); c.line(485 / kk, (580 - 540) / kk, 485 / kk, (760 - 540) / kk, 1.1)
    draw(c, P, 'OA OF DC', where={'O': 'sw', 'E': 'n', 'B': 'n', 'A': 'n', 'C': 'e', 'F': 'e', 'D': 'w'}, rights=[('D', 'A', 'C')], size=8)
    caption(c, 6, 30, '5-5')


@figure('geometry-p36-2', 125, 117, 'A quadrilateral ABCD with right angles at B and C; from Q on BC the perpendicular QP meets AD at P')
def g_quad_pq(c):
    P = pts((210, 117), (520, 540), {'A': (560, 565), 'D': (780, 630), 'B': (560, 760), 'C': (780, 760), 'P': (670, 600), 'Q': (632, 760)})
    draw(c, P, 'AB BC CD DA PQ', where={'A': 'nw', 'D': 'e', 'B': 'w', 'C': 'e', 'P': 'ne', 'Q': 'se'}, rights=[('P', 'A', 'Q'), ('B', 'A', 'C'), ('C', 'B', 'D')])


@figure('geometry-p37-1', 150, 125, 'Problem 5-12: two overlapping circles with centres O and Q meeting at N and M; L is on the first circle, and LN, LM and NM are drawn')
def g5_12(c):
    P = pts((279, 125), (1040, 540), {'O': (1297, 635), 'Q': (1365, 635), 'L': (1283, 570), 'N': (1330, 565), 'K': (1297, 615), 'M': (1330, 700), 'C': (1440, 640)})
    kk = 512 / 279
    c.circle(*P['O'], 75 / kk, 1.1); c.circle(*P['Q'], 75 / kk, 1.1)
    draw(c, P, 'LN LM NM', where={'O': 'w', 'Q': 'e', 'L': 'nw', 'N': 'ne', 'K': 'w', 'M': 's', 'C': 'e'}, dots_at='OQ', size=8)
    caption(c, 8, 20, '5-12')


@figure('geometry-p38-1', 150, 140, 'Problem 5-17: triangle ABC with D on BC; AD, BG and FC are drawn, meeting at E, F and G inside')
def g5_17(c):
    P = pts((292, 140), (0, 0), {'A': (105, 95), 'B': (38, 210), 'C': (218, 210), 'E': (122, 150), 'F': (92, 190), 'G': (155, 190), 'D': (130, 210)})
    draw(c, P, 'AB BC CA AD BG FC', where={'A': 'n', 'B': 'w', 'C': 'e', 'E': 'e', 'F': 'n', 'G': 'ne', 'D': 's'}, size=8)
    caption(c, 8, 70, '5-17')


@figure('geometry-p38-4', 140, 140, 'Problem 5-18: trapezoid ABCD with AD parallel to BC; BF is perpendicular to the extension of DA at F, and FE meets DC at E', page=38)
def g5_18(c):
    P = pts((292, 140), (0, 0), {'A': (378, 100), 'D': (468, 100), 'B': (318, 205), 'C': (490, 205), 'F': (395, 85), 'E': (475, 155)})
    draw(c, P, 'AB BC CD DA BF FE AF', where={'A': 'w', 'D': 'ne', 'B': 'w', 'C': 'e', 'F': 'n', 'E': 'e'}, rights=[('F', 'A', 'B')], size=8)
    caption(c, 8, 70, '5-18')


@figure('geometry-p39-1', 153, 90, 'Problem 5-21: a segment RS with a perpendicular AT at T')
def g5_21(c):
    P = pts((153, 90), (520, 0), {'A': (760, 30), 'T': (760, 215), 'R': (568, 215), 'S': (915, 215)})
    draw(c, P, 'RS AT', where={'A': 'n', 'T': 's', 'R': 'w', 'S': 'e'})
    caption(c, 6, 50, '5-21')


@figure('geometry-p42-1', 96, 156, 'Problem 6-8: triangle ABC with CA of length 20 marked; D on CA and E on CB are joined, with DB and AE drawn; AB is marked 50 and 60')
def g6_8(c):
    P = pts((96, 156), (0, 540), {'C': (165, 610), 'A': (108, 955), 'B': (225, 955), 'D': (130, 795), 'E': (205, 835)})
    draw(c, P, 'CA CB AB DE DB AE', where={'C': 'ne', 'A': 'w', 'B': 'e', 'D': 'w', 'E': 'e'})
    c.text(P['C'][0] + 4, (P['C'][1] + P['D'][1]) / 2 + 3, '20', 8); c.text(P['A'][0] + 12, P['A'][1] - 3, '50', 8); c.text(P['B'][0] - 20, P['B'][1] - 3, '60', 8)
    caption(c, 6, 50, '6-8')


@figure('geometry-p42-2', 114, 102, 'Problem 6-7: a circle with centre O and chord AB through P, M and Q; the thick lines CD and FD meet AB, and ME is thick')
def g6_7(c):
    P = pts((114, 102), (520, 540), {'A': (595, 635), 'B': (805, 635), 'C': (715, 575), 'D': (645, 805), 'E': (815, 720), 'F': (638, 590), 'P': (632, 645), 'Q': (760, 628), 'M': (700, 640), 'O': (698, 690)})
    kk = 512 / 114
    c.circle(*P['O'], 110 / kk, 1.1)
    draw(c, P, 'AB FM', thick='CD FD ME', where={'A': 'w', 'B': 'e', 'C': 'n', 'D': 'sw', 'E': 'e', 'F': 'nw', 'P': 's', 'Q': 'ne', 'M': 's', 'O': 'e'}, dots_at='O', size=8)
    caption(c, 4, 14, '6-7')


@figure('geometry-p43-1', 150, 138, 'Problem 6-14a: triangle ABC with three circles of centres P, Q and R, each through two vertices, meeting at M inside')
def g6_14a(c):
    P = pts((298, 138), (1040, 540), {'A': (1125, 578), 'B': (1075, 725), 'C': (1240, 725), 'F': (1095, 660), 'D': (1183, 650), 'E': (1148, 738), 'M': (1155, 668), 'P': (1138, 662), 'Q': (1118, 703), 'R': (1192, 703)})
    kk = 512 / 298
    for o in 'PQR': c.circle(*P[o], 42 / kk, 1)
    draw(c, P, 'AB BC CA', where={'A': 'n', 'B': 'sw', 'C': 'se', 'F': 'w', 'D': 'e', 'E': 's', 'M': 'e', 'P': 'e', 'Q': 'w', 'R': 'e'}, dots_at='PQR', size=7)
    caption(c, 8, 20, '6-14a')


@figure('geometry-p43-4', 160, 138, 'Problem 6-14b: triangle ABC inside a large circle, with a circle of centre P through A, F and M, and lines from A and F to the base extended to G', page=43)
def g6_14b(c):
    P = pts((298, 138), (1040, 540), {'A': (1375, 610), 'B': (1310, 700), 'C': (1430, 700), 'D': (1395, 662), 'E': (1500, 700), 'F': (1393, 570), 'M': (1450, 565), 'Q': (1410, 665), 'R': (1470, 650), 'G': (1535, 700), 'P': (1420, 605)})
    kk = 512 / 298
    c.circle((1405 - 1040) / kk, (660 - 540) / kk, 120 / kk, 1); c.circle(*P['P'], 42 / kk, 1)
    draw(c, P, 'AB BG AE AC FC MC FM', where={'A': 'w', 'B': 'w', 'C': 's', 'D': 'sw', 'E': 's', 'F': 'n', 'M': 'ne', 'Q': 'se', 'R': 'e', 'G': 'e', 'P': 'e'}, dots_at='PR', size=7)
    caption(c, 8, 20, '6-14b')


@figure('geometry-p44-1', 92, 92, 'A rectangle ABCD inscribed in a circle, with F on the arc above DA; DF and CF are drawn, CF crossing DA at E')
def g_rect_circle(c):
    P = pts((92, 92), (0, 0), {'D': (40, 65), 'A': (225, 65), 'C': (40, 190), 'B': (225, 190), 'F': (205, 40), 'E': (180, 80)})
    kk = 512 / 92
    c.circle(130 / kk, 112 / kk, 108 / kk, 1)
    draw(c, P, 'DF CF', thick='DA AB BC CD', where={'D': 'w', 'A': 'e', 'C': 'w', 'B': 'e', 'F': 'ne', 'E': 's'}, size=8)


@figure('geometry-p45-1', 127, 91, 'Problem 7-4: right triangle ABC with the right angle at B; BQ is perpendicular to CA at Q and PQ joins Q to P on BA')
def g7_4(c):
    P = pts((127, 91), (520, 0), {'C': (600, 30), 'B': (600, 220), 'A': (850, 220), 'Q': (762, 160), 'P': (712, 220)})
    draw(c, P, 'CB BA CA BQ PQ', where={'C': 'n', 'B': 'w', 'A': 'e', 'Q': 'ne', 'P': 's'}, rights=[('Q', 'B', 'A'), ('B', 'C', 'A')])
    caption(c, 4, 30, '7-4')


@figure('geometry-p45-2', 127, 68, 'Problem 7-5: parallelogram ABCD with the diagonal AC; a circle through A meets AD at R, AC at Q and AB at P')
def g7_5(c):
    P = pts((127, 68), (1040, 0), {'A': (1120, 150), 'B': (1300, 150), 'C': (1375, 40), 'D': (1190, 40), 'R': (1165, 65), 'Q': (1210, 100), 'P': (1210, 150)})
    kk = 512 / 127
    c.circle(1162 / kk - 1040 / kk, 115 / kk, 46 / kk, 1)
    draw(c, P, 'AB BC CD DA AC', where={'A': 'sw', 'B': 'se', 'C': 'ne', 'D': 'n', 'R': 'nw', 'Q': 'ne', 'P': 's'}, size=8)
    caption(c, 4, 12, '7-5')


@figure('geometry-p47-1', 159, 74, 'Problem 8-1a: triangle ABC with the line through B and A extended to Q, and the thick transversal PR through Q, where P lies on the extension of CA')
def g8_1a(c):
    P = pts((159, 74), (0, 540), {'P': (38, 565), 'Q': (150, 630), 'A': (128, 635), 'B': (60, 718), 'C': (275, 718), 'R': (410, 718)})
    draw(c, P, 'BR BQ PC', thick='PR', where={'P': 'nw', 'Q': 'ne', 'A': 'w', 'B': 'w', 'C': 's', 'R': 'e'}, size=8)
    caption(c, 95, 20, '8-1a')


@figure('geometry-p47-2', 152, 66, 'Problem 8-1b: triangle ABC with the thick transversal QR through P on AC, Q on BA and R on the extension of BC')
def g8_1b(c):
    P = pts((152, 66), (520, 540), {'B': (560, 690), 'A': (640, 598), 'C': (780, 690), 'R': (915, 690), 'Q': (615, 625), 'P': (725, 645)})
    draw(c, P, 'BR BA AC', thick='QR', where={'B': 'w', 'A': 'n', 'C': 's', 'R': 'e', 'Q': 'nw', 'P': 'n'}, size=8)
    caption(c, 8, 12, '8-1b')


@figure('geometry-p48-1', 150, 107, 'Problem 8-2a: triangle ABC with the cevians AL, BM and CN meeting at P')
def g8_2a(c):
    P = pts((302, 107), (1040, 540), {'A': (1120, 610), 'B': (1075, 705), 'C': (1260, 705), 'N': (1095, 665), 'M': (1215, 665), 'L': (1185, 705), 'P': (1170, 680)})
    draw(c, P, 'AL BM CN', thick='AB BC CA', where={'A': 'n', 'B': 'sw', 'C': 'se', 'N': 'w', 'M': 'e', 'L': 's', 'P': 'n'}, size=7)
    caption(c, 10, 20, '8-2a')


@figure('geometry-p48-4', 160, 107, 'Problem 8-2b: triangle ABC with N above A and L beyond C; the lines NB, NC, AL, BL and AC meet at P and M', page=48)
def g8_2b(c):
    P = pts((302, 107), (1040, 540), {'N': (1375, 560), 'A': (1350, 628), 'B': (1320, 705), 'C': (1458, 705), 'L': (1540, 705), 'P': (1440, 655), 'M': (1410, 680)})
    draw(c, P, 'NB NC AL BL AC BP', thick='AB BC CA', where={'N': 'n', 'A': 'w', 'B': 'sw', 'C': 's', 'L': 'e', 'P': 'ne', 'M': 's'}, size=7)
    caption(c, 10, 20, '8-2b')


@figure('geometry-p50-1', 150, 75, 'Problem 8-15: square ABCD with M on DC; the diagonal AC, BM, and lines from Q and M to P far to the right')
def g8_15(c):
    P = pts((315, 75), (0, 0), {'A': (25, 20), 'B': (100, 20), 'D': (25, 100), 'C': (100, 100), 'P': (255, 20), 'Q': (72, 62), 'R': (100, 72), 'M': (60, 100)})
    draw(c, P, 'AB BC CD DA AC BM QP MP', where={'A': 'nw', 'B': 'ne', 'D': 'sw', 'C': 'se', 'P': 'e', 'Q': 'w', 'R': 'e', 'M': 's'}, size=7)
    caption(c, 100, 32, '8-15')


@figure('geometry-p50-4', 150, 75, 'Problem 8-16: triangle KAC with D on the extension of CM; the thick transversal KM crosses AC at N and KA at L; B lies on KA', page=50)
def g8_16(c):
    P = pts((315, 75), (0, 0), {'K': (278, 55), 'A': (400, 20), 'C': (290, 105), 'D': (405, 105), 'M': (505, 105), 'B': (322, 40), 'L': (305, 60), 'N': (410, 80)})
    draw(c, P, 'KA AD CM CK', thick='KM', where={'K': 'w', 'A': 'n', 'C': 'w', 'D': 's', 'M': 'e', 'B': 'n', 'L': 'sw', 'N': 'n'}, size=7)
    caption(c, 110, 32, '8-16')


@figure('geometry-p50-2', 150, 105, 'Problem 8-17: a circle with centre O; from A the secants AR through B and AP through C; BQ and QP are drawn and RP is dashed')
def g8_17(c):
    P = pts((311, 105), (520, 0), {'O': (618, 70), 'A': (668, 25), 'B': (578, 118), 'C': (645, 125), 'Q': (640, 135), 'P': (748, 118), 'R': (560, 160)})
    kk = 512 / 311
    c.circle(*P['O'], 55 / kk, 1)
    draw(c, P, 'AR AP BC BQ QP', 'RP', where={'O': 'w', 'A': 'ne', 'B': 'w', 'C': 'ne', 'Q': 's', 'P': 'e', 'R': 'sw'}, dots_at='O', size=7)
    caption(c, 6, 20, '8-17')


@figure('geometry-p50-5', 150, 105, 'Problem 8-18: a circle touching the line PP at M; from R above, RB and RC meet the line at B and C; S and S lie on the circle on the chord through A', page=50)
def g8_18(c):
    P = pts((311, 105), (520, 0), {'R': (868, 35), 'S': (848, 75), 'A': (870, 80), 'P': (805, 145), 'B': (828, 145), 'M': (912, 145), 'C': (990, 145), '_S2': (960, 122), '_P2': (1012, 145), '_O': (912, 95)})
    kk = 512 / 311
    c.circle(*P['_O'], 60 / kk, 1)
    draw(c, P, 'P-_P2 RB RC S-_S2', where={'R': 'n', 'S': 'w', 'A': 'e', 'P': 'w', 'B': 's', 'M': 's', 'C': 's'}, size=7)
    label(c, *P['_S2'], 'S', 'ne', 7); label(c, *P['_P2'], 'P', 's', 7)
    caption(c, 6, 20, '8-18')


@figure('geometry-p51-1', 160, 112, 'Problem 8-19: thick triangle ABC with lines from A to H and I, the dashed base line HJ, and the segments ML, NQ and BL inside')
def g8_19(c):
    P = pts((319, 112), (1040, 0), {'A': (1245, 15), 'B': (1120, 120), 'C': (1255, 155), 'H': (1070, 160), 'I': (1255, 165), 'J': (1325, 165), 'P': (1180, 65), 'M': (1135, 110), 'N': (1155, 130), 'L': (1262, 110), 'Q': (1195, 145), 'R': (1250, 90)})
    draw(c, P, 'AH AI ML NQ BL', 'HJ', thick='AB BC CA', where={'A': 'n', 'B': 'w', 'C': 'e', 'H': 'w', 'I': 's', 'J': 'e', 'P': 'w', 'M': 'w', 'N': 's', 'L': 'e', 'Q': 's', 'R': 'e'}, size=6)
    caption(c, 55, 14, '8-19')


@figure('geometry-p51-4', 160, 112, 'Problem 8-20: thick triangle ABC with its circumcircle and the crossing chords EF, ED and FD drawn in pairs', page=51)
def g8_20(c):
    P = pts((319, 112), (1040, 0), {'A': (1410, 20), 'B': (1355, 160), 'C': (1540, 160), 'E': (1383, 80), 'F': (1435, 45), '_F2': (1505, 115), '_E2': (1370, 105), 'D': (1410, 160), '_D2': (1478, 160)})
    kk = 512 / 319
    c.circle((1450 - 1040) / kk, 100 / kk, 66 / kk, 1)
    draw(c, P, 'E-_F2 _E2-F F-_D2 _F2-D _E2-_D2 ED', thick='AB BC CA', where={'A': 'n', 'B': 'sw', 'C': 'se', 'E': 'w', 'F': 'n', 'D': 's'}, size=7)
    label(c, *P['_F2'], 'F', 'e', 7); label(c, *P['_E2'], 'E', 'w', 7); label(c, *P['_D2'], 'D', 's', 7)
    caption(c, 8, 14, '8-20')


@figure('geometry-p51-2', 160, 84, 'Problem 8-22: triangle ABC with NP parallel to AB, AP and CQ crossing at M, the point G inside, and a dashed line through three points P')
def g8_22(c):
    P = pts((308, 84), (0, 540), {'C': (100, 555), 'A': (45, 660), 'B': (195, 660), 'P': (185, 590), 'N': (130, 590), 'M': (150, 615), 'Q': (135, 660), 'G': (105, 630), '_P1': (170, 620), '_P2': (75, 595), '_P3': (245, 665)})
    draw(c, P, 'CA AB CB NP AP CQ', '_P2-_P3', where={'C': 'n', 'A': 'w', 'B': 's', 'P': 'ne', 'N': 'n', 'M': 'n', 'Q': 's', 'G': 's'}, dots_at='G', size=7)
    caption(c, 4, 14, '8-22')


@figure('geometry-p51-5', 160, 84, 'Problem 8-23: triangle PCB with the small triangles A, B, C inside near A, and the segments from P and C to the small points', page=51)
def g8_23(c):
    P = pts((308, 84), (0, 540), {'C': (402, 560), 'P': (302, 660), '_B1': (495, 665), '_A1': (445, 595), '_C1': (460, 610), 'A': (425, 625), 'B': (435, 635), '_C2': (420, 648), '_A2': (385, 612), '_B2': (390, 668)})
    draw(c, P, 'CP C-_B1 P-_B1 P-_C1 _A2-_C1 _A1-_B2 _A2-_B1', 'CB', where={'C': 'n', 'P': 'w', 'A': 'n', 'B': 'se'}, size=7)
    for n, lab in (('_B1', 'B'), ('_A1', 'A'), ('_C1', 'C'), ('_C2', 'C'), ('_A2', 'A'), ('_B2', 'B')): label(c, *P[n], lab, 'ne' if n in ('_A1', '_C1') else 's' if n in ('_B2', '_C2') else 'e', 6)
    caption(c, 20, 14, '8-23')


@figure('geometry-p52-1', 150, 104, 'Problem 8-26: triangle with base LC; from A and M above, the lines AF, BE, CD, CN and FN cross inside, and LM is a dashed thick line')
def g8_26(c):
    P = pts((292, 104), (520, 540), {'L': (545, 690), 'B': (635, 690), 'F': (668, 690), 'C': (745, 690), 'A': (655, 580), 'M': (680, 600), 'N': (655, 610), 'D': (650, 640), 'E': (680, 630)})
    draw(c, P, 'LC AF BE CD CN FN BA', where={'L': 'sw', 'B': 's', 'F': 's', 'C': 'se', 'A': 'n', 'M': 'ne', 'N': 'w', 'D': 'w', 'E': 'e'}, size=7)
    segment(c, P['L'], P['M'], 2.2, (5, 4))
    caption(c, 8, 30, '8-26')


@figure('geometry-p52-4', 150, 104, 'Problem 8-27: thick triangle ABC with the thick cevians AL and BR, and the thin lines NC, PM, AQ and LM', page=52)
def g8_27(c):
    P = pts((292, 104), (520, 540), {'A': (960, 560), 'B': (835, 695), 'C': (1015, 695), 'L': (960, 695), 'N': (910, 610), 'P': (935, 615), 'M': (1000, 640), 'Q': (945, 650), 'R': (968, 668)})
    draw(c, P, 'NC PM AQ LM', thick='AB BC CA BR AL', where={'A': 'n', 'B': 'w', 'C': 'e', 'L': 's', 'N': 'w', 'P': 'n', 'M': 'e', 'Q': 'w', 'R': 'e'}, rights=[('R', 'B', 'A')], size=7)
    caption(c, 8, 30, '8-27')


@figure('geometry-p53-1', 120, 97, 'Problem 8-29a: hexagon ABCDEF')
def g8_29a(c):
    P = pts((274, 97), (1040, 540), {'A': (1110, 575), 'B': (1190, 570), 'C': (1230, 600), 'D': (1180, 655), 'E': (1095, 650), 'F': (1080, 625)})
    draw(c, P, 'AB BC CD DE EF FA', where={'A': 'nw', 'B': 'n', 'C': 'e', 'D': 's', 'E': 's', 'F': 'w'})
    caption(c, 4, 14, '8-29a')


@figure('geometry-p53-4', 150, 97, 'Problem 8-29b: hexagon ABCDEF inscribed in a circle with the chords AB, CD and EF extended, meeting at X, Y and Z, and the dashed lines to N', page=53)
def g8_29b(c):
    P = pts((274, 97), (1040, 540), {'A': (1340, 665), 'B': (1465, 580), 'C': (1330, 615), 'D': (1475, 660), 'E': (1410, 555), 'F': (1465, 690), 'L': (1455, 605), 'M': (1430, 580), 'X': (1395, 645), 'Y': (1445, 665), 'Z': (1428, 620), 'N': (1540, 685)})
    kk = 512 / 274
    c.circle((1430 - 1040) / kk, (640 - 540) / kk, 70 / kk, 1)
    draw(c, P, 'AB CD EF AN', 'BN EN', where={'A': 'w', 'B': 'ne', 'C': 'w', 'D': 'e', 'E': 'n', 'F': 's', 'L': 'e', 'M': 'w', 'X': 'sw', 'Y': 'se', 'Z': 'e', 'N': 'e'}, size=6)
    caption(c, 4, 14, '8-29b')


@figure('geometry-p53-2', 122, 130, "Two triangles sharing labels A, B, C on thick lines, with crossing thin lines meeting at X, Y and Z and a dashed line through C")
def g_two_triangles(c):
    P = pts((122, 130), (0, 0), {'_A1': (75, 190), '_B1': (135, 170), '_C1': (270, 150), '_B2': (75, 328), '_A2': (178, 328), '_C2': (290, 328), 'C': (100, 60), 'X': (140, 240), 'Y': (150, 275), 'Z': (160, 228), 'A': (180, 210), 'B': (205, 295), '_T': (230, 350)})
    draw(c, P, 'C-_B2 C-_A2 _A1-_C2 _C1-_B2 _A1-B _C1-_A2', 'C-_T', thick='_A1-_C1 _B2-_C2', where={'C': 'e', 'X': 'w', 'Y': 'w', 'Z': 'n', 'A': 'n', 'B': 'e'}, size=8)
    for n, lab, w in (('_A1', 'A', 'n'), ('_B1', 'B', 'n'), ('_C1', 'C', 'n'), ('_B2', 'B', 's'), ('_A2', 'A', 's'), ('_C2', 'C', 's')): label(c, *P[n], lab, w, 8)
    c.line(P['_A1'][0] - 20, P['_A1'][1] + 8, P['_C1'][0] + 10, P['_C1'][1] - 4, 2.4); c.line(P['_B2'][0] - 12, P['_B2'][1], P['_C2'][0] + 10, P['_C2'][1], 2.4)


@figure('geometry-p54-2', 150, 127, 'Problem 9-2: a circle through A, B and C with the thick line through X and Z; P is outside with PD perpendicular to the thick line and PZ perpendicular to AB, both dashed')
def g9_2(c):
    P = pts((291, 127), (1040, 0), {'A': (1090, 160), 'B': (1205, 160), 'C': (1135, 45), 'P': (1215, 95), 'X': (1125, 70), 'Z': (1215, 160), 'D': (1170, 118), '_T1': (1115, 35), '_T2': (1225, 175), '_L': (1060, 160), '_R': (1255, 160)})
    kk = 512 / 291
    c.circle((1150 - 1040) / kk, 105 / kk, 60 / kk, 1)
    draw(c, P, 'AC CB _L-_R', 'PD PZ CP', thick='_T1-_T2', where={'A': 'sw', 'B': 's', 'C': 'n', 'P': 'e', 'X': 'w', 'Z': 'e', 'D': 'w'}, rights=[('D', 'P', 'C'), ('Z', 'P', 'B')], size=7)
    caption(c, 4, 14, '9-2')


@figure('geometry-p54-5', 150, 127, 'Problem 9-4: a large circle through A, B and C and a smaller circle through C; AB, AC, the base BR and the line QR through S are drawn', page=54)
def g9_4(c):
    P = pts((291, 127), (1040, 0), {'A': (1430, 15), 'B': (1322, 165), 'C': (1455, 170), 'R': (1540, 170), 'Q': (1385, 75), 'P': (1480, 105), 'S': (1440, 120)})
    kk = 512 / 291
    c.circle((1405 - 1040) / kk, 95 / kk, 85 / kk, 1); c.circle((1495 - 1040) / kk, 140 / kk, 48 / kk, 1)
    draw(c, P, 'AB AC BR QR AP', where={'A': 'n', 'B': 'sw', 'C': 's', 'R': 'e', 'Q': 'nw', 'P': 'ne', 'S': 'w'}, size=7)
    caption(c, 4, 14, '9-4')


@figure('geometry-p55-1', 114, 114, 'Problem 9-5: a circle with centre O and diameter BC; triangle ABC, the thick line through Z, M and Y, and dashed perpendiculars from P to X and Y')
def g9_5(c):
    P = pts((114, 114), (0, 540), {'O': (170, 725), 'B': (60, 725), 'C': (290, 725), 'A': (110, 640), 'P': (265, 655), 'M': (195, 650), 'Z': (130, 595), 'X': (265, 725), 'Y': (240, 712), '_T1': (115, 575), '_T2': (310, 770)})
    kk = 512 / 114
    c.circle(*P['O'], 115 / kk, 1)
    draw(c, P, 'BC BA AC OZ OM', 'PX PY AP', thick='_T1-_T2', where={'O': 's', 'B': 'w', 'C': 'e', 'A': 'w', 'P': 'e', 'M': 'n', 'Z': 'nw', 'X': 's', 'Y': 'sw'}, rights=[('Z', 'O', '_T1'), ('X', 'P', 'C'), ('A', 'P', 'B')], dots_at='O', size=7)
    caption(c, 4, 12, '9-5')


@figure('geometry-p55-2', 123, 113, 'Problem 9-8: four circles: a large one through B, C and E, and three smaller ones through pairs of the points P, A, F, D, with the lines BC, BA, ED, PA and EA')
def g9_8(c):
    P = pts((123, 113), (520, 540), {'E': (745, 575), 'P': (655, 635), 'A': (765, 630), 'F': (710, 690), 'B': (612, 765), 'D': (675, 765), 'C': (820, 765)})
    kk = 512 / 123
    c.circle((715 - 520) / kk, (700 - 540) / kk, 110 / kk, 1); c.circle((700 - 520) / kk, (620 - 540) / kk, 58 / kk, 1)
    c.circle((640 - 520) / kk, (700 - 540) / kk, 65 / kk, 1); c.circle((760 - 520) / kk, (700 - 540) / kk, 62 / kk, 1)
    draw(c, P, 'BC BA ED PA EA', where={'E': 'n', 'P': 'w', 'A': 'e', 'F': 'e', 'B': 'sw', 'D': 's', 'C': 'se'}, size=8)
    caption(c, 4, 12, '9-8')


@figure('geometry-p56-1', 136, 99, 'Problem 10-1: triangle ABC with sides a, b, c, the thick cevian CD of length d, and BD = m, DA = n')
def g10_1(c):
    P = pts((136, 99), (1040, 540), {'C': (1185, 575), 'B': (1115, 718), 'A': (1395, 718), 'D': (1280, 718)})
    draw(c, P, 'CB CA BA', thick='CD', where={'C': 'n', 'B': 'w', 'A': 'e', 'D': 's'}, size=8)
    c.text((P['C'][0] + P['B'][0]) / 2 - 6, (P['C'][1] + P['B'][1]) / 2, 'a', 8, True); c.text((P['C'][0] + P['A'][0]) / 2 + 4, (P['C'][1] + P['A'][1]) / 2, 'b', 8, True)
    c.text((P['C'][0] + P['D'][0]) / 2 + 5, (P['C'][1] + P['D'][1]) / 2 + 3, 'd', 8, True)
    y = P['B'][1] + 8
    for x0, x1, lab in ((P['B'][0], P['D'][0], 'm'), (P['D'][0], P['A'][0], 'n')):
        c.polyline([(x0, y), (x0, y + 4), (x1, y + 4), (x1, y)], 0.7); c.text((x0 + x1) / 2, y + 13, lab, 8, True, 'middle')
    c.polyline([(P['B'][0], y + 16), (P['B'][0], y + 20), (P['A'][0], y + 20), (P['A'][0], y + 16)], 0.7); c.text((P['B'][0] + P['A'][0]) / 2, y + 29, 'c', 8, True, 'middle')
    caption(c, 4, 14, '10-1')
