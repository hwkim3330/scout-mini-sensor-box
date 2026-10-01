import math, geom as g
from drawlib import *
from shapely.geometry import Polygon, box, Point, LineString
from sheets_a import TOTAL

def draw_part(v, part, tags=None, lw=LW_O):
    v.poly(part["outline"], lw=lw)
    for s in part.get("slots", []): v.poly(s["shape"], lw=lw * 0.8)
    for h in part["holes"]:
        if h["kind"] == "mark": v.cmark(h["x"], h["y"], 2.0); continue
        v.circle(h["x"], h["y"], h["d"], lw=LW_T * 1.3)
        if h["kind"] == "pem": v.circle(h["x"], h["y"], h["d"] + 3.0, lw=LW_C, color=GRAY, ls=(0, (2, 1)))
        if h["kind"] == "csk": v.circle(h["x"], h["y"], 9.0, lw=LW_C, color=GRAY)
    for b in part.get("bends", []):
        v.line(b["p1"], b["p2"], lw=LW_T, color=RED, ls=(0, (6, 2)))
    if tags:
        for h in part["holes"]:
            t = tags(h)
            if t: v.tag(h["x"] + h["d"] / 2 + 2.5 / v.s, h["y"] + h["d"] / 2 + 2.0 / v.s, t, fs=3.6)

# ---------------- SHEET 3 : P01 ----------------
def sheet_p01(pdf):
    sh = Sheet("P01  BOTTOM PLATE", 3, TOTAL, part=dict(no="P01", name="BOTTOM PLATE", mat="AL5052-H32  3.0T", qty="1", scale="1:2"))
    s = 0.5; v = View(sh, 118, 160, s, "TOP VIEW (INSIDE SURFACE)   1:2", 118, 248)
    p = g.bottom_plate()
    tag = lambda h: {"csk": "A", "pem": ("E" if h.get("grp") == "E" else "B")}.get(h["kind"])
    draw_part(v, p, tag)
    v.cmark(0, 0, 4)
    for sl in p["slots"]: v.cmark(sl["x"], sl["y"], 3); v.tag(sl["x"] + 9, sl["y"] - 12, "S", fs=3.6)
    bx0, by0, bx1, by1 = p["outline"].bounds
    v.dim((bx0, 0), (bx1, 0), -98, f"{bx1-bx0:.1f}", orient="h")
    v.dim((-g.SIDE / 2, -150), (g.SIDE / 2, -150), -6, "173.2", orient="h")
    v.dim((-132, 150), (132, 150), 18, "264", orient="h")
    v.dim((-g.RAIL_X, g.RAIL_Y), (g.RAIL_X, g.RAIL_Y), 10, "230", orient="h")
    v.dim((bx1, -150), (bx1, 150), -12, "300", orient="v")
    v.dim((g.RAIL_X, -g.RAIL_Y), (g.RAIL_X, g.RAIL_Y), -22, "264", orient="v")
    v.dim((132, 95), (132, 150), -4, "55", orient="v")
    v.dim((-45, 60), (45, 60), 8, "90", orient="h")
    v.dim((-45, -30), (-45, 60), 6, "90", orient="v")
    v.dim((-45, 0), (-45, -30), 14, "30", orient="v")
    v.leader((0, 0), "DATUM (0,0) = 육각 중심", 40, -12, fs=4.6)
    v.leader((g.RAIL_X, g.RAIL_Y + 10), "S: SLOT 9×20 (4×) 장축 // Y", 26, 8, fs=4.6)
    v.text(0, 128, "FRONT ↑  (ETCH)", fs=5, ha="center", color=RED)
    # tables
    A = [h for h in p["holes"] if h["kind"] == "csk"]; B = [h for h in p["holes"] if h["kind"] == "pem" and h.get("grp") != "E"]
    C = [h for h in p["holes"] if h.get("grp") == "E"]
    rows = [[f"A{i+1}", h["face"], f"{h['x']:.2f}", f"{h['y']:.2f}"] for i, h in enumerate(A)]
    y = sh.table(232, 268, [("ID", 10), ("FACE", 12), ("X", 18), ("Y", 18)], rows, fs=4.5, rh=3.6)
    sh.text(232, y - 3, "A: Ø4.5 THRU + CSK 90°×Ø9.0, 하면(BOTTOM)에서\n    M4×8 FH (ISO 10642) → 벽 하부 플랜지 CLSS-M4-1", fs=4.4, va="top")
    rows = [[f"B{i+1}", f"{h['x']:.1f}", f"{h['y']:.1f}"] for i, h in enumerate(B)]
    y2 = sh.table(232, y - 14, [("ID", 10), ("X", 24), ("Y", 24)], rows, fs=4.5, rh=3.6)
    sh.text(232, y2 - 3, "B: CLSS-M4-2 (Ø5.40 +0.08), 상면(TOP)측 체결\n    AGX 트레이 스탠드오프 M4 M-F", fs=4.4, va="top")
    rows = [[f"E{i+1}", f"{h['x']:.1f}", f"{h['y']:.1f}"] for i, h in enumerate(C)]
    y3 = sh.table(298, 268, [("ID", 10), ("X", 24), ("Y", 24)], rows, fs=4.5, rh=3.6)
    sh.text(298, y3 - 3, "E: CLSS-M4-2 (Ø5.40 +0.08) ×6, 상면 체결\n    P10 전장판 스탠드오프 M4 M-F 10\n\nREV9: REV8 M3 PEM 그리드 ×54 삭제\n    → 부품은 탈착식 전장판 P10에 장착\n    (부품 변경 시 P10만 재가공)\n\nPEM 합계 P01 = 10 (B 4 + E 6)", fs=4.4, va="top")
    sh.text(232, 108, "S: RAIL SLOT 9×20 R4.5 (4×) @ X±115, Y±132  → SCOUT 레일 T-너트 + M8 SHCS + 평와셔", fs=4.6)
    notes = ["1. 외형/홀 = DXF P01_BOTTOM_PLATE.dxf (CUT 레이어).",
             "2. PEM B/E 압입면 = 상면(내부). 하면 돌출 없음(플러시) 확인.",
             "3. 접시 A = 하면에서 가공. M4 FH 머리 하면 플러시 ±0.2 / 돌출 금지.",
             "4. 평면도 0.5 이하 (전면). 레이저 후 버 제거, 외곽 C0.5.",
             "5. 오목 R6 / 볼록 R4 (외곽 코너 = 벽 외측 R4 일치).",
             "6. 레일 슬롯 피치 230±0.2, 264±0.2.",
             "!7. REV7 슬롯 (X±115,Y±80) 폐기 — 벽 간섭.",
             "8. 품번 'P01-R9' 상면 각인."]
    sh.box(232, 48, 85, 56, "NOTES", notes, fs=4.6, lh=5.2)
    # detail slot & csk
    d = View(sh, 340, 78, 2.0, "DETAIL S (2:1)", 340, 101)
    d.poly(g.obround(0, 0, 9, 20)); d.cmark(0, 0, 6)
    d.dim((-4.5, -5.5), (4.5, -5.5), -14, "9", orient="h"); d.dim((4.5, -10), (4.5, 10), -6, "20", orient="v")
    d.text(0, -14, "R4.5 FULL", fs=4.2, ha="center")
    k = View(sh, 384, 80, 3.0, "SECTION A (3:1)", 384, 101)
    left = Polygon([(-7, 0), (-4.5, 0), (-2.25, 2.25), (-2.25, 3), (-7, 3)])
    right = Polygon([(7, 0), (4.5, 0), (2.25, 2.25), (2.25, 3), (7, 3)])
    k.poly(left, fill="#dfe6ee"); k.poly(right, fill="#dfe6ee")
    k.dim((-4.5, 0), (4.5, 0), -6, "Ø9.0", orient="h"); k.dim((-2.25, 3), (2.25, 3), 6, "Ø4.5", orient="h")
    k.text(0, -6.5, "CSK 90° from BOTTOM\n(M4 FH ISO10642)", fs=4.2, ha="center", va="top")
    k.text(-7, 4.2, "TOP (INSIDE)", fs=3.8, color=GRAY)
    sh.save(pdf)

# ---------------- WALL SHEETS ----------------
def sheet_wall(pdf, no, faces, pno, pname):
    sh = Sheet(f"{pno}  {pname}", no, TOTAL, part=dict(no=pno, name=pname, mat="AL5052-H32  2.0T", qty="1", scale="1:2 / 1:1"))
    w = g.wall_flat(faces); I = w["info"]
    s = 0.5; v = View(sh, 24, 172, s, None)
    sh.text(24, 270, f"FLAT PATTERN (외면 보기, OUTSIDE FACE)  1:2   — 모든 절곡 = 지면 반대방향(내측)", fs=6.5, weight="bold")
    draw_part(v, w)
    for b in w["bends"]:
        if b["kind"] == "v":
            v.text(b["p1"][0], I["V_TOT"] + 5, "60° IN", fs=4.2, ha="center", color=RED)
    v.text(I["TOT"] + 3, (I["v_w0"] - g.BA90 / 2), "90° IN", fs=4.2, va="center", color=RED)
    v.text(I["TOT"] + 3, (I["v_w1"] + g.BA90 / 2), "90° IN", fs=4.2, va="center", color=RED)
    for f, face in enumerate(faces):
        uc = w["u"](f, g.SIDE / 2); v.cmark(uc, w["v_of_z"](g.CAM_Z), 5)
        v.tag(uc, w["v_of_z"](64) if face != g.SERVICE_FACE else w["v_of_z"](60), face, fs=5.5)
    vb1 = I["v_w0"] - g.BA90 / 2; vb2 = I["v_w1"] + g.BA90 / 2
    bc = [b["p1"][0] for b in w["bends"] if b["kind"] == "v"]
    v.dim((0, I["V_TOT"]), (bc[0], I["V_TOT"]), 12, orient="h"); v.dim((bc[0], I["V_TOT"]), (bc[1], I["V_TOT"]), 12, orient="h")
    v.dim((bc[1], I["V_TOT"]), (I["TOT"], I["V_TOT"]), 12, orient="h")
    v.dim((0, 0), (I["TOT"], 0), -10, f"{I['TOT']:.2f}  (FLAT, K0.40 REF)", orient="h")
    v.dim((0, 0), (0, vb1), 6, orient="v"); v.dim((0, vb1), (0, vb2), 6, orient="v"); v.dim((0, vb2), (0, I["V_TOT"]), 6, orient="v")
    v.dim((I["TOT"], 0), (I["TOT"], I["V_TOT"]), -16, f"{I['V_TOT']:.2f}", orient="v")
    # formed section A-A (1:1)
    a = View(sh, 40, 52, 1.0, "SECTION A-A (FORMED)  1:1.6", 70, 40)
    t = 2.0; H = g.Z_WALL_TOP
    prof = Polygon([(0, 3), (g.F, 3), (g.F, 5), (t, 5), (t, H - 2), (g.F, H - 2), (g.F, H), (0, H)])
    # we draw the profile rotated: x = depth inward, y = z ; scale fits 128 tall? use half scale
    a.s = 0.62
    a.poly(prof, lw=LW_O, fill="#dfe6ee")
    a.poly(box(-5, 0, 60, 3), lw=LW_T, color=GRAY, ls=(0, (4, 2))); a.poly(box(-5, H, 60, H + 2), lw=LW_T, color=GRAY, ls=(0, (4, 2)))
    a.text(62, 1.5, "P01 3T", fs=4.2, va="center", color=GRAY); a.text(62, H + 1, "P04 2T", fs=4.2, va="center", color=GRAY)
    a.dim((0, 3), (0, H), 6, "125 (MOLD)", orient="v"); a.dim((0, H), (g.F, H), 9, "19", orient="h")
    a.dim((0, 3), (g.F, 3), -9, "19", orient="h"); a.dim((0, 3), (g.D_PEM, 3), -16, "11 PEM CL", orient="h")
    a.text(22, 20, "Ri 2.0 (ALL)\nt = 2.0\n외측 = 0", fs=4.4)
    a.text(22, 92, f"CL CAM Z{g.CAM_Z:.0f}", fs=4.4); a.line((0, g.CAM_Z), (20, g.CAM_Z), color=GRAY, ls=(0, (6, 2, 1, 2)))
    # face detail (1:1) — typical face
    face = faces[1]
    fd = View(sh, 175, 52, 0.62, f"FACE DETAIL — {face} 외면 (typ. 1:1.6)", 175, 40)
    L = g.SIDE
    fd.poly(box(-L / 2, 3, L / 2, H), lw=LW_O)
    for kind, geo, label in g.face_features(face, 1):
        if kind in ("win", "vent"): fd.poly(geo, lw=LW_T * 1.3)
        if kind == "pem": fd.circle(geo[0], geo[1], 4.22, lw=LW_T)
    for sg in (-1, 1):
        fd.circle(sg * g.TAU_PEM, 5, 3, lw=LW_C, color=GRAY, ls=(0, (2, 1)))
        fd.circle(sg * g.TAU_PEM, H - 2, 3, lw=LW_C, color=GRAY, ls=(0, (2, 1)))
    fd.cmark(0, g.CAM_Z, 8)
    fd.dim((-L / 2, H), (L / 2, H), 8, "173.2 (MOLD)", orient="h")
    fd.dim((-24, g.CAM_Z + 22), (24, g.CAM_Z + 22), 3.5, "48", orient="h")
    fd.dim((-18, g.CAM_Z - 18), (18, g.CAM_Z - 18), -8 - (40 if face == g.SERVICE_FACE else 0) * 0, "36", orient="h")
    fd.dim((L / 2, g.CAM_Z - 22), (L / 2, g.CAM_Z + 22), -6, "44", orient="v")
    fd.dim((L / 2, 3), (L / 2, g.CAM_Z), -13, "89 (Z92)", orient="v")
    fd.dim((-L / 2, g.CAM_Z - 18), (-L / 2, g.CAM_Z + 18), 8, "36", orient="v")
    if face == g.SERVICE_FACE:
        fd.dim((-70, 20), (70, 20), -4, "140", orient="h")
        fd.dim((-L / 2, 3), (-L / 2, 20), 18, "17 (Z20)", orient="v"); fd.dim((-L / 2, 20), (-L / 2, 50), 18, "30", orient="v")
        fd.dim((-40, 14), (40, 14), -10, "80 (PEM)", orient="h")
        fd.dim((-L / 2, 14), (-L / 2, 56), 28, "42 (PEM)", orient="v")
    else:
        fd.dim((-g.TAU_PEM, 3), (g.TAU_PEM, 3), -5, "90 (FLANGE PEM, hidden)", orient="h")
    # VENT detail
    if any(f in g.VENT_FACES for f in faces):
        vd = View(sh, 352, 180, 0.8, "VENT DETAIL (C1/C3/C4/C6)  1:1.25", 352, 238)
        for i in range(9):
            x = (i - 4) * 9.0; vd.poly(g.obround(x, 36, 4, 36), lw=LW_T * 1.3)
        vd.dim((-36, 54), (36, 54), 6, "8×9 = 72", orient="h"); vd.dim((40, 18), (40, 54), -6, "36", orient="v")
        vd.dim((-36, 18), (-32, 18), -4, "4", orient="h"); vd.text(-42, 10, "z 18 ~ 54, 슬롯 폭 4 R2 ×9", fs=4.4)
    # feature table
    rows = []
    for f, fc in enumerate(faces):
        ft = g.face_features(fc, f)
        win = "36×36" + (" + 140×30" if fc == g.SERVICE_FACE else "")
        pem = sum(1 for k, *_ in ft if k == "pem")
        rows.append([fc, f"{w['u'](f, g.SIDE/2):.2f}", win, f"M3-1 ×{pem}", "4×36 ×9" if fc in g.VENT_FACES else "—",
                     f"Ø3.3 ×{sum(1 for k,*_ in ft if k=='rivet')}" if f in (0, 2) else "—", "M3-1×2 / M4-1×2"])
    y = sh.table(250, 125, [("FACE", 11), ("u_CL", 16), ("WINDOW", 24), ("PEM(외면)", 18), ("VENT", 15), ("RIVET", 14), ("FLANGE PEM", 28)], rows, fs=4.3, rh=3.6)
    notes = ["1. CUT/PEM/BEND = DXF " + f"{pno}_WALL_HALF_{'FRONT' if pno=='P02' else 'REAR'}.dxf",
             "2. 성형 후 기준치수: 면 외측 173.2±0.3 (MOLD), 벽 H125±0.3, 플랜지 19±0.3, 내각 120°±0.5°.",
             "3. 전개는 K0.40/Ri2 가정 참고치 — 제작사 BD로 재전개 후 성형치수 맞춤.",
             "4. PEM: 굽힘 전 압입. 면 PEM 상대물 = 외면 / 상플랜지 = 윗면 / 하플랜지 = 아랫면.",
             "5. 코너 노치(Relief) 깊이 = 플랜지 굽힘부 + 0.5. 스플라이스 리벳홀은 P09와 합 가공 허용.",
             "6. 끝단 트림 1.5 (이음 코너). P02+P03+P09 리벳 조립 후 AF300±0.5 확인.",
             "7. 리벳홀 Ø3.3: 이음 꼭짓점(MOLD)에서 13.2, Z30/65/100 — P09 합 가공 권장.",
             "8. 창/PEM/벤트 위치 = 면 중심(u_CL) 기준, FACE DETAIL 치수(성형 외면).",
             "9. 품번 'P0x-R9' 내면 각인. 외면 흠집 금지(보호필름 유지 권장)."]
    sh.box(250, 48, 160 - 0, 52, "NOTES", notes, fs=4.5, lh=6.2) if False else sh.box(250, 46, 160, y - 48, "NOTES", notes, fs=4.4, lh=4.9)
    sh.save(pdf)

def sheet_p02(pdf): sheet_wall(pdf, 4, g.HALF_A, "P02", "WALL HALF – FRONT (C1/C2/C3)")
def sheet_p03(pdf): sheet_wall(pdf, 5, g.HALF_B, "P03", "WALL HALF – REAR (C4/C5/C6)")

# ---------------- SHEET 6 : P04 / P05 ----------------
def sheet_p04(pdf):
    sh = Sheet("P04  TOP COVER  /  P05  OS1 MOUNT PLATE", 6, TOTAL, part=dict(no="P04 / P05", name="TOP COVER / OS1 PLATE", mat="5052-H32 2.0T / 6061-T6 5.0T", qty="1 / 1", scale="1:2 / 1:1.8"))
    s = 0.5; v = View(sh, 105, 160, s, "P04 TOP COVER — TOP VIEW  1:2", 105, 246)
    p = g.top_cover()
    tag = lambda h: "D" if h["label"].startswith("Ø3.4") else ("E" if h["label"].startswith("Ø5.5") else ("F" if h["d"] > 30 else None))
    draw_part(v, p, tag); v.cmark(0, 0, 4)
    v.poly(g.rrect(0, 0, 140, 140, 10), lw=LW_T, color=RED, ls=(0, (5, 2)))
    v.text(0, 74, "P11 접촉부 140×140 — NO POWDER COAT / MASK (BARE AL)", fs=4.4, ha="center", color=RED)
    v.text(0, 115, "FRONT ↑ (ETCH, 상면)", fs=5, ha="center", color=RED)
    rc = g.COVER_AF / math.sqrt(3)
    bb = p["outline"].bounds; v.dim((bb[0], 0), (bb[2], 0), -84, f"{bb[2]-bb[0]:.1f} (R4 코너 포함)", orient="h")
    v.dim((-g.COVER_AF / (2*math.sqrt(3)), g.COVER_AF / 2), (g.COVER_AF / (2*math.sqrt(3)), g.COVER_AF / 2), 6, f"{g.COVER_AF/math.sqrt(3):.1f}", orient="h")
    v.dim((rc * 0.5, -g.COVER_AF / 2), (rc * 0.5, g.COVER_AF / 2), -48, f"{g.COVER_AF} AF  (-0.3/0)", orient="v")
    v.dim((-62, 0), (62, 0), -40, "124", orient="h"); v.dim((0, -62), (0, 62), -10, "124", orient="v")
    v.dim((-16.25, -100), (16.25, -100), -12, "Ø32.5", orient="h"); v.dim((0, -100), (0, 0), 40, "100", orient="v")
    D = [h for h in p["holes"] if h["label"].startswith("Ø3.4")]
    rows = [[f"D{i+1}", h["face"], f"{h['x']:.2f}", f"{h['y']:.2f}"] for i, h in enumerate(D)]
    y = sh.table(206, 268, [("ID", 10), ("FACE", 11), ("X", 17), ("Y", 17)], rows, fs=4.4, rh=3.5)
    sh.text(206, y - 3, "D: Ø3.4 THRU ×12 (M3×8 BH)\n   = 벽 상부 플랜지 PEM 위치 (중심에서 139.0)\nE: Ø5.5 THRU ×4 (패턴 B, 124 십자)\n   하면에서 M5×10 SHCS+W → P11 탭 B\n   (직결 옵션 시 → P05 탭 B)\nF: Ø32.5 THRU — M32 분할형 글랜드\n   (OS1 케이블, 커넥터 통과형)", fs=4.4, va="top")
    notes = ["1. 외형/홀 = DXF P04_TOP_COVER.dxf",
             "2. 외곽 AF299.5 (벽 외면 대비 편측 -0.25) — 커버 돌출 방지",
             "3. 코너 R4 (벽 외측 절곡 R와 일치)",
             "4. 평면도 0.5 이하, P11 접촉부 0.3 이하",
             "5. 하면 외곽 10mm 폭 EPDM 가스켓 부착면 — 도장 시 포함",
             "6. 품번 'P04-R9' 하면 각인",
             "!7. 도장 시 P11 접촉부 140×140 마스킹 (열경로)"]
    sh.box(206, 46, 66, 66, "NOTES (P04)", notes, fs=4.3, lh=5.6)
    # P05
    q = View(sh, 345, 182, 0.55, "P05 OS1 MOUNT PLATE — 1:1.8", 345, 232)
    o = g.os1_plate(); draw_part(q, o)
    q.dim((-70, 70), (70, 70), 6, "140", orient="h"); q.dim((70, -70), (70, 70), -6, "140", orient="v")
    q.dim((-60, -60), (60, -60), -10, "120", orient="h"); q.dim((-60, -60), (-60, 60), 10, "120", orient="v")
    q.dim((-62, 0), (62, 0), -46, "124 (B)", orient="h")
    q.leader((-60, 60), "A: 4× Ø5.5 THRU (M5×12 → P11 탭 A)", -8, 10, fs=4.4)
    q.leader((-62, 0), "B: 4× M5 TAP THRU (직결 옵션)", -14, 14, fs=4.4)
    q.leader((70, -60), "R10 ×4", 6, -8, fs=4.4)
    q.circle(0, 0, 87, lw=LW_C, color=BLUE, ls=(0, (5, 2))); q.text(0, -48, "OS1 Ø87 (REF)", fs=4.2, ha="center", color=BLUE)
    q.text(0, 52, "FRONT ↑ (ETCH)", fs=4.6, ha="center", color=RED)
    hold = ["!HOLD — OS1 장착홀 (본 발주 제외): 4× M3 + 2× Ø2 핀홀",
            "  보유 OS1 실측/템플릿 → KETI 가공 (Ø3.4 + 하면 C'BORE, 핀 Ø2 H7)",
            "  중심 = 각인 센터마크, 커넥터 방향 후면(−Y) → 케이블 P04 F홀",
            "AL6061-T6 5.0T, 평면도 0.1 (OS1 접촉면), 탭 B M5 관통",
            "!P05 OS1 CONTACT SURFACE: NO POWDER COAT / MASK",
            "!THERMAL CONTACT SURFACE KEEP BARE ALUMINUM",
            "!  상면 Ø100 (OS1 접촉) + 하면 전체 (P11 접촉) 마스킹",
            "  나머지 상면·측면만 흑색 (옵션 B). 아노다이징 시도 동일 마스킹",
            "기본 구성: OS1 → P05 → P11 라이저 25T → P04 (SHEET 8)",
            "직결 옵션: P05 → P04 (탭 B), 하향 가림 −15.4°",
            "품번 'P05-R9' 측면 각인"]
    sh.box(280, 46, 128, 68, "P05 NOTES", hold, fs=4.4, lh=5.3)
    sh.save(pdf)

# ---------------- SHEET 7 : small parts ----------------
def sheet_small(pdf):
    sh = Sheet("P06 / P07 / P08 / P09  SMALL PARTS", 7, TOTAL, part=dict(no="P06~P09", name="SMALL PARTS", mat="AL5052-H32  2.0T", qty="8 / 1 / 1 / 2", scale="1:1"))
    # P06
    a = View(sh, 50, 225, 1.0, "P06 CAMERA ADAPTER PLATE  1:1  (QTY 8 = 6+2 SPARE)", 70, 266)
    draw_part(a, g.cam_plate())
    a.dim((-30, 27.5), (30, 27.5), 5, "60", orient="h"); a.dim((30, -27.5), (30, 27.5), -5, "55", orient="v")
    a.dim((-24, -22), (24, -22), -10, "48", orient="h"); a.dim((-24, -22), (-24, 22), 12, "44", orient="v")
    a.leader((24, 22), "4× Ø3.4 THRU (M3×8 BH)", 12, 6, fs=4.4); a.leader((30, -27.5), "R4 ×4", 6, -6, fs=4.4)
    a.text(0, 15, "UP ↑ (ETCH)", fs=4.4, ha="center", color=RED)
    sh.box(100, 200, 95, 52, None, ["!HOLD — 카메라 홀더/렌즈 홀 (본 발주 제외)", "B0473 모듈 25×24mm, M12 렌즈", "→ 납품 키트 실측 후 KETI 가공:", "  렌즈 클리어런스 + 모듈 고정홀(M2)", "  센터 = 각인 센터마크 = 창 중심", "블랭크 + 4× Ø3.4만 가공 납품", "흑색 도장/아노다이징 권장(반사 저감)"], fs=4.5, lh=5.6)
    # P07
    b = View(sh, 290, 228, 1.0, "P07 REAR SERVICE PANEL  1:1", 290, 267)
    sp = g.svc_plate(); draw_part(b, sp)
    for (x, y, k) in g.SVC_ITEMS: b.cmark(x, y, 3)
    b.dim((-78, 26), (78, 26), 6, "156", orient="h"); b.dim((78, -26), (78, 26), -6, "52", orient="v")
    b.dim((-40, -21), (40, -21), -9, "80", orient="h"); b.dim((-78, -21), (-78, 21), 6, "42", orient="v")
    b.dim((-56, 0), (-28, 0), -34, "28", orient="h"); b.dim((-28, 0), (0, 0), -34, "28", orient="h"); b.dim((0, 0), (28, 0), -34, "28", orient="h")
    b.dim((28, 0), (50, 0), -34, "22", orient="h"); b.dim((50, 0), (62, 0), -34, "12", orient="h")
    b.dim((62, -8), (62, 8), -4, "16", orient="v")
    rows = [["M16", "-56, 0", "Ø16.2", "M16×1.5 케이블 글랜드 — SCOUT 24V/CAN 피그테일"],
            ["D1", "-28, 0", "Ø24 + 2×Ø3.2", "D-size: RJ45 피드스루 (Neutrik NE8FDP 등)"],
            ["D2", "0, 0", "Ø24 + 2×Ø3.2", "D-size: USB-A 피드스루 (Neutrik NAUSB3 등)"],
            ["D3", "28, 0", "Ø24 + 2×Ø3.2", "D-size: 예비 / 12V DC 입력 (블랭크 캡)"],
            ["SMA", "50/62, ±8", "Ø6.5 ×4", "SMA 벌크헤드 (5G 안테나)"],
            ["MTG", "±40, ±21", "Ø3.4 ×4", "M3×8 BH → P03 C5 PEM"]]
    sh.table(225, 189, [("ID", 12), ("X, Y", 22), ("HOLE", 26), ("USE", 92)], rows, fs=4.3, rh=3.4)
    sh.text(225, 160, "D-size 홀 패턴: Ø24 + Ø3.2 대각 2개 (19×24 피치) — 표준 D 시리즈 판넬컷", fs=4.4)
    # P08
    c = View(sh, 95, 112, 0.7, "P08 AGX TRAY — FLAT PATTERN  1:1.4", 95, 172)
    t = g.agx_tray_flat(); draw_part(c, t)
    full = t["info"]["flat"] / 2
    c.dim((-full, 54), (full, 54), 0, None, orient="h") if False else None
    c.dim((-full, -54), (full, -54), -24, f"{2*full:.1f}", orient="h")
    c.dim((-54, -full), (54, -full), -8, "108", orient="h")
    c.dim((full, -54), (full, 54), -6, "108", orient="v")
    c.dim((-45, 45), (45, 45), 4, "90", orient="h"); c.dim((-35, -35), (35, -35), 4, "70", orient="h")
    c.leader((45, 45), "4× Ø4.5 CSK 90°×Ø9 (TOP)", 20, 14, fs=4.3)
    c.leader((t["slots"][1]["x"], t["slots"][1]["y"]), "STRAP SLOT 4×27 ×4", 18, 6, fs=4.3)
    sh.box(150, 70, 70, 82, "P08 NOTES", ["성형: 4변 90° UP, Ri2, 높이 12 (MOLD)", "내측 포켓 112×112 (AGX 110 + EPDM 1t)",
         "!중앙 70×70 = ADAPTER / CABLE CLEARANCE", "!HOLD UNTIL B0473 ADAPTER FIT CHECK", "  어댑터 결합 후 하부 돌출 확인 → 유지/축소",
         "  (J509 = 캐리어보드 상면, 모듈 하부 영역)", "  70×70 그대로 가공 가능 (축소는 재가공 불요)", "스탠드오프 M4 M-F 25 (30/35 = fit check 결과)",
         "스트랩 25mm 벨크로 ×2, 코너 릴리프 = 절곡부 제거"], fs=4.3, lh=5.6)
    c.text(0, 0, "70×70\nADAPTER / CABLE\nCLEARANCE\nHOLD: FIT CHECK", fs=4.4, ha="center", va="center", color=RED)
    # P09
    d = View(sh, 262, 66, 0.7, "P09 SPLICE BRACKET — FLAT  1:1.4 (QTY 2)", 278, 148)
    sp9 = g.splice_flat(); draw_part(d, sp9)
    tot = sp9["info"]["flat"]
    d.dim((0, 100), (tot, 100), 5, f"{tot:.2f}", orient="h"); d.dim((tot, 0), (tot, 100), -5, "100", orient="v")
    hx = sorted(set(round(h["x"], 2) for h in sp9["holes"]))
    d.dim((hx[0], 15), (hx[1], 15), -14, f"{hx[1]-hx[0]:.2f}", orient="h"); d.dim((0, 15), (hx[0], 15), -14, f"{hx[0]:.1f}", orient="h")
    d.dim((0, 15), (0, 50), 6, "35", orient="v"); d.dim((0, 50), (0, 85), 6, "35", orient="v"); d.dim((0, 0), (0, 15), 6, "15", orient="v")
    sh.box(310, 66, 98, 84, "P09 NOTES", ["성형: 60° 1회 (내각 120°), Ri2", "다리 22 (MOLD, 외면 기준) ×2, 높이 100",
         "6× Ø3.3 — Al 블라인드 리벳 Ø3.2", "  (그립 3.0~4.8, 돔헤드 외측)", "설치: 벽 이음 코너 내측, Z15~115",
         "벽 리벳홀과 합 가공(Match drill) 허용", "리벳 조립 후 이음부 단차 ≤0.3", "옵션: 이음부 외측 실리콘/에폭시 실링"], fs=4.4, lh=5.6)
    sh.save(pdf)

# ---------------- SHEET 8 : layout / wiring / power ----------------
def sheet_layout(pdf):
    sh = Sheet("INTERNAL LAYOUT / WIRING / POWER BUDGET", 9, TOTAL, part=dict(no="ASSY-SBOX-R9", name="INTERNAL LAYOUT & WIRING", mat="—", qty="—", scale="1:3"))
    v = View(sh, 75, 185, 1 / 3, "INTERNAL LAYOUT — TOP (cover removed)  1:3", 75, 246)
    v.poly(g.bottom_plate()["outline"], lw=LW_T, color=GRAY)
    v.poly(g.hex_poly(g.AF)); v.poly(g.hex_poly(g.AF - 2 * g.T_WALL), lw=LW_T)
    v.poly(g.hex_poly(g.AF - 2 * g.F), lw=LW_C, color=GRAY, ls=(0, (4, 2)))
    ep = g.eplate(); v.poly(ep["outline"], lw=LW_T, color="#3a6b3a", fill="#eef5ee", z=1)
    for h in ep["holes"]: v.circle(h["x"], h["y"], h["d"] if h["grp"] == "SO" else 2.5, lw=LW_C, color="#3a6b3a")
    v.text(-128, -40, "P10", fs=5, color="#3a6b3a", weight="bold")
    zones = [("AGX ORIN\n110×110 (tray 116)", (0, 15), 116, 116, "#d8ead3"),
             ("DC/DC 24→12V\n(existing, TBD)", (50, -85), 60, 50, "#fde9d9"),
             ("CAN Pal + FUSE\n+ WAGO 221", (-50, -85), 60, 50, "#fff2cc"),
             ("5G MODEM\n(TBD) 50×90", (95, 0), 50, 90, "#e1e1f5"),
             ("OS1 I/F BOX\nor SPARE 50×90", (-95, 0), 50, 90, "#eeeeee")]
    for name, (cx, cy), w_, h_, col in zones:
        v.poly(g.rrect(cx, cy, w_, h_, 3), lw=LW_T, fill=col, z=2); v.text(cx, cy, name, fs=4.3, ha="center", va="center")
    for f in g.FACES:
        x, y = g.face_point(f, 0, -8); v.tag(x, y, f, fs=4.2)
    v.text(0, -178, "C5 SERVICE PANEL (REAR)", fs=4.4, ha="center", color=BLUE)
    sh.box(14, 48, 120, 66, "배치 원칙", ["• AGX 팬 흡/배기: C3·C4 벤트(흡기) → C1·C6 벤트(배기) 측 개방 유지",
        "• B0473 어댑터 = AGX 카메라 커넥터 J509 직결 → FPC 30cm ×6, 고전류선과 분리",
        "• CAN Pal은 후면 인입부 근처, CAN_H/L 트위스트 페어 유지",
        "• 24V 인입 → 퓨즈(5A) → WAGO 분배 → DC/DC / OS1 / 5G",
        "• 부품 고정: 탈착식 전장판 P10 (Ø3.4 25mm 그리드, M3 볼트+나일록)",
        "• 커버 탈착 시 OS1 케이블만 분리(커넥터) — 나머지 하네스 하판측 고정",
        "• FPC 굽힘 R≥5, 벽 관통 없음(카메라 내측 장착)",
        "• 녹색 = P10 (스탠드오프 M4×10 ×6, 높이 Z13), 점선 = 플랜지 내측 경계"], fs=4.5, lh=6.6)
    # wiring block diagram
    bx = lambda x, y, w_, h_, t, col="#ffffff": (sh.ax.add_patch(Rectangle((x, y), w_, h_, fc=col, ec=INK, lw=0.4 * PT)), sh.text(x + w_ / 2, y + h_ / 2, t, fs=4.6, ha="center", va="center"))
    X0, Y0 = 150, 175
    bx(X0, Y0 + 40, 48, 26, "SCOUT MINI\n4-pin AVIATION\n1 VCC 23~29.2V 5A max\n2 GND  3 CAN_H  4 CAN_L", "#f2f2f2")
    bx(X0 + 62, Y0 + 52, 30, 14, "FUSE 5A\n(ATO, slow)", "#fde9d9")
    bx(X0 + 104, Y0 + 52, 30, 14, "WAGO 221\n24V / GND", "#fde9d9")
    bx(X0 + 146, Y0 + 58, 34, 14, "DC/DC 24→12V\n≥8A cont.", "#fde9d9")
    bx(X0 + 196, Y0 + 58, 40, 14, "AGX ORIN J41\n5.5/2.5 center +", "#d8ead3")
    bx(X0 + 146, Y0 + 38, 34, 12, "OUSTER OS1\n24V direct (9.5~51V)", "#dce9f7")
    bx(X0 + 196, Y0 + 38, 40, 12, "5G MODEM (TBD)\n12V or USB", "#e1e1f5")
    bx(X0 + 62, Y0 + 14, 40, 18, "ADAFRUIT CAN Pal\nTJA1051T/3 [ada-5708]\n3.3V 구동 (내부 5V 생성)", "#fff2cc")
    bx(X0 + 120, Y0 + 14, 56, 18, "AGX J30 40-pin\npin 29 CAN0_DIN ← RX\npin 31 CAN0_DOUT → TX\npin 1 3.3V / pin 6 GND", "#d8ead3")
    bx(X0 + 196, Y0 + 14, 40, 18, "B0473 6-CSI ADAPTER\n→ J509 직결 (fit check)\nFPC ×6 → CAM C1~C6", "#fbe5d6")
    L = lambda pts, col, lw=0.8, ls="-": sh.ax.plot(*zip(*pts), color=col, lw=lw, ls=ls)
    L([(X0 + 48, Y0 + 60), (X0 + 62, Y0 + 60)], RED, 1.2); L([(X0 + 92, Y0 + 60), (X0 + 104, Y0 + 60)], RED, 1.2)
    L([(X0 + 134, Y0 + 62), (X0 + 146, Y0 + 65)], RED, 1.2); L([(X0 + 134, Y0 + 58), (X0 + 146, Y0 + 44)], RED, 1.2)
    L([(X0 + 180, Y0 + 65), (X0 + 196, Y0 + 65)], "#e69500", 1.2); L([(X0 + 180, Y0 + 63), (X0 + 190, Y0 + 63), (X0 + 190, Y0 + 44), (X0 + 196, Y0 + 44)], "#e69500", 1.0)
    L([(X0 + 30, Y0 + 40), (X0 + 30, Y0 + 26), (X0 + 62, Y0 + 26)], "#c9a400", 1.0); L([(X0 + 34, Y0 + 40), (X0 + 34, Y0 + 22), (X0 + 62, Y0 + 22)], "#2f5597", 1.0)
    L([(X0 + 102, Y0 + 23), (X0 + 120, Y0 + 23)], INK, 0.8)
    L([(X0 + 176, Y0 + 23), (X0 + 196, Y0 + 23)], "#8064a2", 0.8, (0, (3, 1)))
    sh.text(X0 + 36, Y0 + 30, "CAN_H(Y)/CAN_L(B) twisted", fs=4.0); sh.text(X0 + 104, Y0 + 25, "RX/TX/3V3/GND", fs=4.0)
    sh.text(X0 + 48, Y0 + 63, "24V", fs=4.2, color=RED); sh.text(X0 + 182, Y0 + 67, "12V", fs=4.2, color="#e69500")
    sh.text(X0, Y0 + 6, "CAN 2.0B 500 kbps · CAN Pal 종단 120Ω 기본 OFF → 전원 OFF 상태 H-L 저항 측정(≈60Ω면 OFF 유지) 후 결정 · OS1 Ethernet → AGX RJ45(10GbE) 직결", fs=4.3)
    # power budget
    rows = [["AGX Orin 64GB (MAXN 60W)", "12V via DC/DC", "60", "66.7"], ["AGX Orin (50W mode, 권장)", "12V via DC/DC", "50", "(55.6)"],
            ["Ouster OS1 Rev7 (14~20W)", "24V direct", "20", "20.0"], ["5G modem (TBD, ~8W)", "12V via DC/DC", "8", "8.9"],
            ["B0473 cam ×6 + CAN Pal", "AGX 내부", "—", "(AGX 포함)"], ["TOTAL @ 24V (MAXN)", "η(DC/DC)=0.90", "", "95.6 W ≈ 4.0 A"],
            ["SCOUT 확장 한계", "24V × 5A", "", "!120 W — 여유 20%"]]
    sh.table(150, 160, [("LOAD", 52), ("FEED", 30), ("P_load W", 18), ("P_in @24V W", 30)], rows, fs=4.4, rh=4.0)
    sh.box(282, 48, 126, 82, "전원 판단", ["• MAXN + OS1 + 5G = 약 4.0A (한계 5A, 여유 1A) — 돌입/피크 고려 시 빠듯",
        "!• 권장: AGX 50W 모드(nvpmodel) 고정 → 약 3.6A",
        "• 퓨즈 5A slow-blow (로봇 확장 한계와 동일), 와이어 AWG18",
        "!• DC/DC HOLD 6: 기존품 12V 연속 ≥8A / 피크 ≥10A / 효율 ≥90% 확인 전 확정 금지",
        "  (AGX 60W/12V = 5A + 5G 0.7A + 여유)",
        "• 실측: AGX 부하 시 J41 전압 ≥11.5V 확인",
        "• 24V 측 전류 클램프 측정 후 퓨즈/모드 최종 확정",
        "• 장시간 MAXN 필요 시 별도 배터리/전원 검토"], fs=4.5, lh=7.6)
    sh.save(pdf)

# ---------------- SHEET 9 : harness / hold / inspection / RFQ ----------------
def sheet_hold(pdf):
    sh = Sheet("HARNESS / HOLD RELEASE / INSPECTION / RFQ", 10, TOTAL, part=dict(no="ASSY-SBOX-R9", name="HARNESS / HOLD / INSPECTION", mat="—", qty="—", scale="—"))
    rows = [["H1", "SCOUT 4-pin", "C5 M16 gland", "AgileX 메이팅 피그테일", "24V + CAN", "커넥터 셸 추측 가공 금지"],
            ["H2", "H1 24V", "FUSE 5A → WAGO", "AWG18 R/B", "24V 분배", "퓨즈는 인입 직후"],
            ["H3", "WAGO", "DC/DC IN", "AWG18", "컨버터 입력", ""],
            ["H4", "DC/DC 12V", "AGX J41", "5.5/2.5 배럴 AWG18", "AGX 전원", "센터 +, 극성 확인"],
            ["H5", "WAGO", "OS1 (I/F)", "AWG18", "OS1 24V", "OS1 9.5~51V"],
            ["H6", "SCOUT CAN", "CAN Pal H/L/GND", "트위스트 페어", "CAN 물리층", "CAN_H→H, CAN_L→L, GND 공통"],
            ["H7", "CAN Pal", "AGX J30", "4선 듀폰", "CAN 로직", "3.3V p1, GND p6, RX p29, TX p31"],
            ["H8", "B0473 ×6", "B0473 어댑터", "FPC 30cm ×6", "카메라", "굽힘 보호/스트레인 릴리프"],
            ["H9", "B0473 어댑터", "AGX J509", "어댑터 직결", "카메라 IF", "범용 CSI 배선 대체 금지"],
            ["H10", "OS1", "AGX RJ45", "OS1 케이블 / Cat6", "LiDAR 데이터", "P04 F홀 분할 글랜드"],
            ["H11", "C5 D1/D2", "AGX RJ45/USB", "패널 피드스루", "서비스", "작업용 연장"],
            ["H12", "C5 SMA ×4", "5G 모뎀", "SMA-IPEX 15cm", "안테나", "모뎀 확정 후"]]
    y = sh.table(14, 270, [("ID", 10), ("FROM", 28), ("TO", 32), ("CABLE", 36), ("FUNC", 22), ("NOTE", 68)], rows, fs=4.4, rh=4.0)
    hold = [["1", "SCOUT 메이팅 커넥터 셸/나사/성별", "공급 피그테일 사용 → M16 글랜드 통과 (가공 영향 없음)", "본체 발주 무관"],
            ["2", "레일 T-너트/볼트 규격", "실물 레일 확인 → 볼트 길이 결정 (슬롯 9 = M8까지)", "본체 발주 무관"],
            ["3", "OS1 4×M3 + 핀 패턴", "보유 OS1 실측/템플릿 → P05 KETI 후가공", "P05 블랭크 납품"],
            ["4", "B0473 홀더 홀 / 렌즈 위치", "납품 키트 실측 → P06 KETI 후가공", "P06 블랭크 납품"],
            ["5", "B0473 어댑터 FIT CHECK", "AGX 결합 후 하부 돌출/케이블 경로 → P08 70×70 유지·축소, 스탠드오프 25/30/35", "P08 그대로 가공 가능"],
            ["6", "기존 24→12V DC/DC 실물 사양", "연속 ≥8A·피크 ≥10A·효율 ≥90% 확인, 미달 시 교체 → P10 장착", "판금 무관 (P10)"],
            ["7", "5G 모뎀 모델 / 안테나", "P10 그리드 장착 + SMA 4홀 기가공", "판금 무관"]]
    y2 = sh.table(14, y - 6, [("#", 6), ("HOLD 항목", 52), ("해제 방법", 104), ("발주 영향", 34)], hold, fs=4.4, rh=4.0)
    sh.text(14, y2 - 4, "→ 모든 HOLD는 판금·가공품 P01~P11 발주에 영향 없음 — 즉시 발주 가능 (P05/P06 장치홀만 KETI 후가공)", fs=5.2, color=RED, weight="bold")
    insp = ["[제작사 출하검사]",
            "□ AF 300±0.5 (벽 링 리벳 조립 후, 3방향 측정)   □ 벽 높이 125±0.3 / 플랜지 19±0.3",
            "□ 커버(P04)·하판(P01) 가조립: M3×12, M4×12 전 홀 무리 없이 체결",
            "□ PEM 전수 탭 게이지 확인 / 압입 플러시 / 탈락·회전 없음",
            "□ 레일 슬롯 피치 230±0.2 / 264±0.2     □ 평면도 P01·P04 ≤0.5, P05 ≤0.1",
            "□ 버 제거 / 벤트·창·슬롯 에지 상태     □ 각인 품번 확인",
            "□ P11 평면도 0.05·탭 M5 ×8 게이지   □ 도장 시 마스킹(P04 140□ / P05 / P11 BARE)",
            "[KETI 입고검사]",
            "□ SCOUT 레일 실장착 (T-너트 4개)       □ AGX + 트레이 + 커버 간섭 없음 (상부 ≥15)",
            "□ 카메라 플레이트 6면 체결, FPC 30cm 도달   □ OS1 플레이트 수평 ≤0.2°",
            "□ B0473 어댑터 FIT CHECK → P08 70×70 판정   □ DC/DC 부하시험 (J41 ≥11.5V)"]
    sh.box(14, 46, 196, y2 - 54, "INSPECTION CHECKLIST", insp, fs=4.6, lh=6.0)
    rfq = ["[견적 요청] KETI 모빌리티플랫폼연구센터 — 센서 박스 판금 (REV 9)",
           "",
           "1. 품목: P01~P11 (도면 SHEET 1 PART LIST), 수량 1세트 (P06 8개, P09 2개)",
           "   + 옵션 수량 견적: 3세트 / 5세트",
           "2. 재질: AL5052-H32 2.0T / 3.0T, AL6061-T6 5.0T (P05), 25T (P11 CNC)",
           "3. 공정: 레이저 → PEM 압입(CLSS 62개) → 절곡 → 리벳 조립(벽 링), P05/P11 탭·CNC",
           "4. 표면: [A] 무처리  [B] 흑색 분체도장 — 분리 견적. P05/P11/P04 열접촉면 BARE 마스킹",
           "5. 첨부: 도면 PDF 10매, DXF 11종(전개·홀 MASTER), STEP(조립/부품), BOM",
           "6. 요청: 견적서(A/B), 납기, 재전개 DXF(BD 반영) 사전 회신,",
           "   첫 절곡 시편(벽 1면) 치수 확인 후 본 가공 진행 희망",
           "7. 제외: 체결류·커넥터·장치 (BOM 구매품, 별도 구매)",
           "8. 문의: hwkim3@keti.re.kr"]
    sh.box(214, 46, 196, 100, "RFQ — 제작사 전달 문구", rfq, fs=4.6, lh=5.8)
    seq = ["1. 벽 링: P02+P03 맞대기 → P09 ×2 내측 → Al 리벳 ×12 (제작사)",
           "2. P06 후가공(KETI) → B0473 모듈 장착 → 벽 외면 M3×8 ×4/면, FPC 내측 인입",
           "3. P07에 글랜드·D-size·SMA 장착 → C5 외면 M3×8 ×4",
           "4. P01: M4×25 ×4 → P08 트레이 / M4×10 ×6 → P10 (DC/DC·CAN Pal·WAGO·5G 선장착)",
           "5. 벽 링을 P01 위에 안착 → 하면에서 M4×8 FH ×12 (가스켓 옵션)",
           "6. AGX 장착, B0473 어댑터 → AGX J509 결합, FPC·CAN(J30)·J41 전원, 하네스 타이",
           "7. P04 상면 P11 ← 하면 M5×10 ×4(B) / P05+OS1 → P11 M5×12 ×4(A), 케이블 → F홀",
           "8. P04 → 벽 상부 플랜지 M3×8 BH ×12",
           "9. 로봇: 이어 슬롯 → 레일 T-너트, M8 SHCS + 와셔 ×4",
           "체결 토크(참고): M3→PEM 0.6 / M4→PEM 1.3 / M5→Al 탭 3.0 N·m",
           "  M8 → 레일 T-너트: 레일 제조사 값 (Al 프로파일 일반 10 N·m 이하)",
           "  나사 고착: 중강도 고착제(블루) — PEM 나사부 / 진동부 체결"]
    sh.box(214, 150, 196, 120, "ASSEMBLY SEQUENCE / TORQUE", seq, fs=4.7, lh=6.6)
    sh.save(pdf)



# ---------------- SHEET 8 : P10 / P11 ----------------
def sheet_p10(pdf):
    sh = Sheet("P10  ELECTRICAL PLATE  /  P11  OS1 RISER FRAME", 8, TOTAL, part=dict(no="P10 / P11", name="ELEC PLATE / OS1 RISER", mat="5052-H32 2.0T / 6061-T6 25T", qty="1 / 1", scale="1:2.5 / AS NOTED", finish="P10 RAW·P/C / P11 BARE"))
    v = View(sh, 90, 188, 0.4, "P10 ELECTRICAL PLATE (탈착식) — TOP  1:2.5", 90, 256)
    e = g.eplate()
    v.poly(g.hex_poly(g.AF), lw=LW_C, color=GRAY, ls=(0, (4, 2)))
    draw_part(v, e)
    so = [h for h in e["holes"] if h["grp"] == "SO"]
    for i, h in enumerate(so): v.tag(h["x"] + 9, h["y"] + 8, f"S{i+1}", fs=3.8)
    bb = e["outline"].bounds
    v.dim((bb[0], bb[1]), (bb[2], bb[1]), -10, f"{bb[2]-bb[0]:.1f}", orient="h")
    v.dim((bb[2], bb[1]), (bb[2], bb[3]), -8, f"{bb[3]-bb[1]:.1f}", orient="v")
    v.dim((-70, -55), (70, -55), 6, "140 (AGX TRAY 개구)", orient="h")
    v.text(0, 20, "AGX TRAY\n(P08)", fs=4.6, ha="center", va="center", color=GRAY)
    rows = [[f"S{i+1}", f"{h['x']:.1f}", f"{h['y']:.1f}", "Ø4.5 — M4×8 BH → M4 M-F 10 → P01 PEM E"] for i, h in enumerate(so)]
    y = sh.table(14, 120, [("ID", 9), ("X", 14), ("Y", 14), ("NOTE", 80)], rows, fs=4.4, rh=3.7)
    ng = sum(1 for h in e["holes"] if h["grp"] == "G")
    sh.box(14, 46, 117, y - 50, "P10 NOTES", [f"1. 레이저만 (PEM 없음). Ø3.4 그리드 ×{ng} (25 피치, 원점 +12.5 오프셋)",
        "2. 부품: M3 볼트 + 나일론 스페이서 + 나일록 (하면 너트) — 위치 자유",
        "3. 부품 변경 시 P10만 재가공 (DXF 그리드 수정)", "4. 높이: 하판 상면 +10 (Z13~15), 벽 벤트(Z18~) 하단",
        "5. 외곽 = 벽 외면 24 안쪽(AF252) − 중앙 140 개구(Y ≥ −55)", "6. 표면: 무처리 또는 흑색 P/C (옵션 B), 품번 'P10-R9' 각인"], fs=4.4, lh=5.2)
    # P11 top
    r = View(sh, 222, 196, 0.6, "P11 OS1 RISER FRAME — TOP  1:1.7", 222, 248)
    rp = g.riser(); r.poly(rp["outline"])
    for h in rp["holes"]:
        r.circle(h["x"], h["y"], 4.2, lw=LW_T); r.circle(h["x"], h["y"], 5.0, lw=LW_C, color=GRAY, ls=(0, (2, 1)))
        r.tag(h["x"] + 7, h["y"] + 7, h["grp"], fs=3.8)
    r.dim((-70, 70), (70, 70), 5, "140", orient="h"); r.dim((70, -70), (70, 70), -5, "140", orient="v")
    r.dim((-54, -54), (54, -54), 6, "108 (POCKET THRU, R6)", orient="h")
    r.dim((-60, 60), (60, 60), -6, "120 (A)", orient="h"); r.dim((-62, 0), (62, 0), -6, "124 (B)", orient="h")
    r.text(0, 0, "A: M5 TAP 10 DP 상면 ×4\n(P05 → M5×12)\nB: M5 TAP 10 DP 하면 ×4\n(P04 하면 → M5×10)", fs=4.2, ha="center", va="center")
    # stack + FOV section (radius vs Z)
    f = View(sh, 292, 60, 0.55, "SECTION — OS1 STACK & LOWER FOV (1:1.8)", 340, 200)
    zr = g.H_TOTAL; z5 = zr + g.RISER_T; zo = z5 + g.T_OS1
    f.line((150, 112), (150, g.Z_WALL_TOP), color=GRAY); f.line((0, 112), (150, 112), color=GRAY, ls=(0, (2, 2))); f.text(100, 116, "BOX (WALL R150)", fs=4.0, color=GRAY)
    f.poly(box(0, g.Z_WALL_TOP, 149.75, g.H_TOTAL), fill="#dddddd")
    f.poly(box(54, zr, 70, z5), fill="#cfd4dc"); f.poly(box(0, z5, 70, zo), fill="#e8e8e8")
    f.poly(box(0, zo, 43.5, zo + 74.2), color=BLUE)
    ob = zo + 36.18
    import math as _m
    t = _m.tan(_m.radians(22.5))
    f.line((0, ob), (150, ob - 150 * t), color=RED, lw=LW_T * 1.4)
    f.line((0, ob), (175, ob), color=GRAY, ls=(0, (6, 2, 1, 2)))
    ob2 = g.H_TOTAL + g.T_OS1 + 36.18
    f.line((0, ob2), (150, ob2 - 150 * t), color=GRAY, ls=(0, (3, 2)), lw=LW_T)
    f.text(60, 222, f"REV9: −22.5° @ R150 → Z{ob-150*t:.1f} > Z130 (OK)", fs=4.2, color=RED)
    f.text(60, 214, f"직결 옵션: Z{ob2-150*t:.1f} < Z130 (가림 −15.4°)", fs=4.0, color=GRAY)
    f.dim((70, zr), (70, z5), -5, "25", orient="v"); f.dim((70, z5), (70, zo), -12, "5", orient="v")
    f.dim((0, zo), (0, ob), 6, "36.2 BEAM", orient="v")
    f.text(58, zr + 12, "P11", fs=4.2); f.text(20, z5 + 1, "P05", fs=4.0); f.text(20, g.Z_WALL_TOP - 0.5, "P04", fs=4.0, va="top")
    f.text(10, zo + 50, "OS1", fs=4.6, color=BLUE)
    sh.box(280, 46, 128, 66, "P11 NOTES", ["1. AL6061-T6 25T 판재 CNC (상·하면 플라이컷, 두께 24.0~25.0)",
        "2. 평면도 0.05 (양면), 평행도 0.05 — OS1 열·진동 경로",
        "!3. 표면 무처리 (BARE AL) — 도장/아노다이징 금지",
        "4. 탭 A(상) / B(하) 각 M5 깊이 10, 서로 다른 위치 (간섭 없음)",
        "5. 중앙 108□ 관통 포켓 R6 — 경량화, 질량 약 0.54 kg",
        "6. 프레임이 P04 중앙을 140□로 보강 (2T 커버 진동 저감)",
        "7. 열경로: OS1 → P05(BARE) → P11 → P04 140□(BARE) → 벽",
        "8. 라이저 생략(직결) 시 SLAM 위주 운용, 근거리 지면점 감소",
        "9. 품번 'P11-R9' 측면 각인"], fs=4.3, lh=5.8)
    sh.save(pdf)

SHEETS = [sheet_p01, sheet_p02, sheet_p03, sheet_p04, sheet_small, sheet_p10, sheet_layout, sheet_hold]
