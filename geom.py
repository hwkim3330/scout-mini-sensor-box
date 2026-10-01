"""SCOUT MINI OMNI sensor box REV8 – single source of geometry (mm)."""
import math
from shapely.geometry import Polygon, box, Point, LineString
from shapely import affinity
from shapely.ops import unary_union

# ---------------- global ----------------
AF = 300.0                     # across flats (outer wall)
SIDE = AF / math.sqrt(3)       # 173.205
RC = SIDE                      # circumradius
T_WALL = 2.0; T_BOT = 3.0; T_COV = 2.0; T_OS1 = 5.0
RI = 2.0; K = 0.40             # inner bend radius, K-factor (reference)
Z_BOT_TOP = T_BOT              # 3
Z_WALL_TOP = 128.0             # top flange outer surface
H_TOTAL = Z_WALL_TOP + T_COV   # 130
F = 19.0                       # flange mold length (from wall outer face)
E_TRIM = 1.5                   # wall half end trim from mold vertex
D_PEM = 11.0                   # flange PEM depth from outer face
TAU_PEM = 45.0

def ossb(deg, ri=RI, t=T_WALL): return math.tan(math.radians(deg) / 2) * (ri + t)
def ba(deg, ri=RI, t=T_WALL):   return math.radians(deg) * (ri + K * t)
OSSB60, BA60 = ossb(60), ba(60)
OSSB90, BA90 = ossb(90), ba(90)
BD60 = 2 * OSSB60 - BA60; BD90 = 2 * OSSB90 - BA90

FACES = {f"C{i+1}": 30 + 60 * i for i in range(6)}   # outward normal angle (deg)
HALF_A = ["C1", "C2", "C3"]   # front half  (corner 0deg -> 180deg)
HALF_B = ["C4", "C5", "C6"]   # rear half   (corner 180deg -> 360deg)
VENT_FACES = ["C1", "C3", "C4", "C6"]
SERVICE_FACE = "C5"

def nvec(face):
    a = math.radians(FACES[face]); return (math.cos(a), math.sin(a))
def tvec(face):
    a = math.radians(FACES[face]); return (-math.sin(a), math.cos(a))
def face_point(face, tau, depth=0.0):
    n, t = nvec(face), tvec(face); r = AF / 2 - depth
    return (r * n[0] + tau * t[0], r * n[1] + tau * t[1])

def hex_poly(af, rot_deg=0.0):
    rc = af / math.sqrt(3)
    pts = [(rc * math.cos(math.radians(60 * i + rot_deg)), rc * math.sin(math.radians(60 * i + rot_deg))) for i in range(6)]
    return Polygon(pts)

def round_convex(p, r):  return p.buffer(-r, join_style=1).buffer(r, join_style=1)
def round_concave(p, r): return p.buffer(r, join_style=1).buffer(-r, join_style=1)

def obround(cx, cy, w, h):
    """slot centred at cx,cy, overall width w (x) and height h (y)."""
    r = min(w, h) / 2
    if w >= h: ls = LineString([(cx - w/2 + r, cy), (cx + w/2 - r, cy)])
    else:      ls = LineString([(cx, cy - h/2 + r), (cx, cy + h/2 - r)])
    return ls.buffer(r, quad_segs=16)

def rrect(cx, cy, w, h, r):
    b = box(cx - w/2, cy - h/2, cx + w/2, cy + h/2)
    return round_convex(b, r) if r > 0 else b

# hole record: dict(x,y,d,kind,label)  kind: 'thru','pem','csk','rivet','pin'
PEM = {  # PennEngineering CLSS (stainless) self-clinching nuts, hole dia, min C/L-to-edge
    "CLSS-M3-1": (4.22, 4.8), "CLSS-M4-1": (5.40, 6.9), "CLSS-M5-1": (6.40, 7.1),
    "CLSS-M3-2": (4.22, 4.8), "CLSS-M4-2": (5.40, 6.9),
}

# ---------------- face features (s = tau along face from centre, z = height) -------------
CAM_Z = 92.0
CAM_WIN = (36.0, 36.0)          # w x h window in wall
CAM_PEM = [(sx * 24.0, CAM_Z + sz * 22.0) for sx in (-1, 1) for sz in (-1, 1)]
CAM_PLATE = (60.0, 55.0)
VENT = dict(n=9, pitch=9.0, w=4.0, z0=18.0, z1=54.0)
SVC_Z = 35.0
SVC_OPEN = (140.0, 30.0)         # tau +-70, z 20..50
SVC_PEM = [(sx * 40.0, SVC_Z + sz * 21.0) for sx in (-1, 1) for sz in (-1, 1)]
SVC_PLATE = (156.0, 52.0)
SPLICE_S = 1.155 + 12.0          # rivet hole from seam vertex along face
SPLICE_Z = [30.0, 65.0, 100.0]

def face_features(face, half_pos):
    """returns list of (shape, meta) in face coords (tau, z). half_pos: 0 first face,2 last."""
    feats = []
    feats.append(("win", rrect(0, CAM_Z, *CAM_WIN, 2.0), "CAMERA WINDOW 36x36 R2"))
    for (x, z) in CAM_PEM: feats.append(("pem", (x, z, "CLSS-M3-1"), "CAM PLATE"))
    if face in VENT_FACES:
        n, p = VENT["n"], VENT["pitch"]
        for i in range(n):
            x = (i - (n - 1) / 2) * p
            feats.append(("vent", obround(x, (VENT["z0"] + VENT["z1"]) / 2, VENT["w"], VENT["z1"] - VENT["z0"]), "VENT 4x36"))
    if face == SERVICE_FACE:
        feats.append(("win", rrect(0, SVC_Z, *SVC_OPEN, 3.0), "SERVICE OPENING 140x30 R3"))
        for (x, z) in SVC_PEM: feats.append(("pem", (x, z, "CLSS-M3-1"), "SERVICE PANEL"))
    half = SIDE / 2
    if half_pos == 0:
        for z in SPLICE_Z: feats.append(("rivet", (-half + SPLICE_S, z, 3.3), "SPLICE RIVET"))
    if half_pos == 2:
        for z in SPLICE_Z: feats.append(("rivet", (half - SPLICE_S, z, 3.3), "SPLICE RIVET"))
    return feats

def flange_a(d):  # flange end setback from face mold vertex at depth d
    return 4.0 + 0.383 * d

# ---------------- wall flat pattern ----------------
def wall_flat(faces):
    L = SIDE
    sstart = [E_TRIM, OSSB60, OSSB60]
    U0 = [0.0]
    U0.append((L - OSSB60 - E_TRIM) + BA60)
    U0.append(U0[1] + (L - 2 * OSSB60) + BA60)
    TOT = U0[2] + (L - E_TRIM - OSSB60)
    def u(f, s): return U0[f] + (s - sstart[f])
    v_bf_tip, v_bf_root = 0.0, F - OSSB90                 # 0 .. 14
    v_w0 = v_bf_root + BA90                                # 18.398 (z=7)
    v_w1 = v_w0 + (Z_WALL_TOP - Z_BOT_TOP - 2 * OSSB90)   # 135.398 (z=124)
    v_tf_root = v_w1 + BA90                                # 139.796
    V_TOT = v_tf_root + (F - OSSB90)                       # 153.796
    def v_of_z(z): return v_w0 + (z - (Z_BOT_TOP + OSSB90))
    relief = 0.5
    core = box(0, v_w0 - relief - 0.0, TOT, v_w1 + relief)
    # remove? core spans; we add flange regions
    parts = [box(0, v_w0 + relief, TOT, v_w1 - relief)]
    for f in range(3):
        a4, a18 = flange_a(OSSB90), flange_a(F)
        # bend zones + flanges (bottom)
        ua, ub = u(f, max(a4, sstart[f])), u(f, L - a4)
        parts.append(box(ua, v_bf_root, ub, v_w0 + relief + 0.01))
        parts.append(Polygon([(u(f, a4), v_bf_root), (u(f, L - a4), v_bf_root), (u(f, L - a18), v_bf_tip), (u(f, a18), v_bf_tip)]))
        parts.append(box(ua, v_w1 - relief - 0.01, ub, v_tf_root))
        parts.append(Polygon([(u(f, a4), v_tf_root), (u(f, L - a4), v_tf_root), (u(f, L - a18), V_TOT), (u(f, a18), V_TOT)]))
    # wall core between notches: full length but only straight wall height
    outline = unary_union(parts)
    # but the wall core must reach v_w0-relief.. only where not notched: add strip between flange ends
    outline = round_concave(outline, 0.5)
    holes = []; cut = []
    meta = []
    for f, face in enumerate(faces):
        sc = SIDE / 2
        for kind, g, label in face_features(face, f):
            if kind in ("win", "vent"):
                gg = affinity.affine_transform(g, [1, 0, 0, 1, u(f, sc) , v_of_z(0)])
                cut.append(gg); meta.append((face, label))
            elif kind == "pem":
                x, z, pn = g
                holes.append(dict(x=u(f, sc + x), y=v_of_z(z), d=PEM[pn][0], kind="pem", label=pn, face=face, mate="OUTER"))
            elif kind == "rivet":
                x, z, d = g
                holes.append(dict(x=u(f, sc + x), y=v_of_z(z), d=d, kind="rivet", label="RIVET Ø3.2 Al", face=face, mate="-"))
        for sg in (-1, 1):
            holes.append(dict(x=u(f, sc + sg * TAU_PEM), y=F - D_PEM, d=PEM["CLSS-M4-1"][0], kind="pem", label="CLSS-M4-1", face=face, mate="FLANGE BOTTOM"))
            holes.append(dict(x=u(f, sc + sg * TAU_PEM), y=v_tf_root + (D_PEM - OSSB90), d=PEM["CLSS-M3-1"][0], kind="pem", label="CLSS-M3-1", face=face, mate="FLANGE TOP"))
    outline = outline.difference(unary_union(cut)) if cut else outline
    bends = []
    for f in range(2):
        uc = U0[f + 1] - BA60 / 2
        bends.append(dict(p1=(uc, v_w0), p2=(uc, v_w1), note="BEND 60° IN  Ri2", kind="v"))
    bends.append(dict(p1=(0, v_bf_root + BA90 / 2), p2=(TOT, v_bf_root + BA90 / 2), note="BEND 90° IN  Ri2 (bottom flange)", kind="h"))
    bends.append(dict(p1=(0, v_w1 + BA90 / 2), p2=(TOT, v_w1 + BA90 / 2), note="BEND 90° IN  Ri2 (top flange)", kind="h"))
    info = dict(TOT=TOT, V_TOT=V_TOT, U0=U0, sstart=sstart, v_w0=v_w0, v_w1=v_w1, v_tf_root=v_tf_root)
    return dict(outline=outline, holes=holes, bends=bends, info=info, u=u, v_of_z=v_of_z)

# ---------------- flat parts ----------------
RAIL_X, RAIL_Y, RAIL_SLOT = 115.0, 132.0, (9.0, 20.0)
AGX_C = (0.0, 15.0)
AGX_SO = [(AGX_C[0] + sx * 45, AGX_C[1] + sy * 45) for sx in (-1, 1) for sy in (-1, 1)]
EPL_SO = [(-95.0, 40.0), (95.0, 40.0), (-95.0, -45.0), (95.0, -45.0), (-40.0, -105.0), (40.0, -105.0)]
EPL_H = 10.0          # e-plate standoff height
RISER_T = 25.0        # OS1 riser thickness (AL6061 25T stock)
RISER_IN = 108.0      # riser inner pocket (wall 16)
OS1_A = [(sx * 60.0, sy * 60.0) for sx in (-1, 1) for sy in (-1, 1)]   # P05 -> riser (top taps)
OS1_B = [(0.0, 62.0), (0.0, -62.0), (62.0, 0.0), (-62.0, 0.0)]          # riser -> P04 (bottom taps) / direct-mount

def flange_screw_pts():
    pts = []
    for face in FACES:
        for sg in (-1, 1): pts.append((face, *face_point(face, sg * TAU_PEM, D_PEM)))
    return pts

def depth_min(x, y):
    return min(AF / 2 - (x * nvec(f)[0] + y * nvec(f)[1]) for f in FACES)

def bottom_plate():
    hexp = hex_poly(AF)
    ears = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            ears.append(box(min(sx * 86.6, sx * 132), min(sy * 95, sy * 150), max(sx * 86.6, sx * 132), max(sy * 95, sy * 150)))
    out = unary_union([hexp] + ears)
    out = round_concave(out, 6.0)
    out = round_convex(out, 4.0)
    slots = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            slots.append(dict(shape=obround(sx * RAIL_X, sy * RAIL_Y, RAIL_SLOT[0], RAIL_SLOT[1]), label="RAIL SLOT 9x20", x=sx * RAIL_X, y=sy * RAIL_Y))
    holes = []
    for face, x, y in flange_screw_pts():
        holes.append(dict(x=x, y=y, d=4.5, kind="csk", label="Ø4.5 CSK 90°xØ9.0 (BOTTOM SIDE) M4 FH", face=face))
    for (x, y) in AGX_SO:
        holes.append(dict(x=x, y=y, d=PEM["CLSS-M4-2"][0], kind="pem", label="CLSS-M4-2", mate="TOP"))
    for (x, y) in EPL_SO:
        holes.append(dict(x=x, y=y, d=PEM["CLSS-M4-2"][0], kind="pem", label="CLSS-M4-2", mate="TOP", grp="E"))
    marks = [("FRONT", (0, 120))]
    return dict(outline=out, holes=holes, slots=slots, marks=marks)

COVER_AF = 299.5
OS1_PEM = [(sx * 60.0, sy * 60.0) for sx in (-1, 1) for sy in (-1, 1)]
OS1_GLAND = (0.0, -100.0, 32.5)
def top_cover():
    out = round_convex(hex_poly(COVER_AF), 4.0)
    holes = [dict(x=x, y=y, d=3.4, kind="thru", label="Ø3.4 THRU (M3 BH)", face=f) for f, x, y in flange_screw_pts()]
    holes += [dict(x=x, y=y, d=5.5, kind="thru", label="Ø5.5 THRU (M5×10 from BELOW → P11/P05)") for x, y in OS1_B]
    holes.append(dict(x=OS1_GLAND[0], y=OS1_GLAND[1], d=OS1_GLAND[2], kind="thru", label="Ø32.5 THRU (M32 split gland)"))
    return dict(outline=out, holes=holes, slots=[], marks=[("FRONT", (0, 115))])

def os1_plate():
    out = rrect(0, 0, 140, 140, 10)
    holes = [dict(x=x, y=y, d=5.5, kind="thru", label="Ø5.5 THRU (M5×12 → P11 TAP A)") for x, y in OS1_A]
    holes += [dict(x=x, y=y, d=4.2, kind="tap", label="M5 TAP THRU (Ø4.2) – DIRECT-MOUNT OPTION") for x, y in OS1_B]
    holes.append(dict(x=0, y=0, d=1.0, kind="mark", label="CENTER MARK (etch, no thru)"))
    return dict(outline=out, holes=holes, slots=[], marks=[("FRONT", (0, 55))])

def cam_plate():
    out = rrect(0, 0, *CAM_PLATE, 4)
    holes = [dict(x=x, y=z - CAM_Z, d=3.4, kind="thru", label="Ø3.4 THRU (M3 BH)") for x, z in CAM_PEM]
    holes.append(dict(x=0, y=0, d=1.0, kind="mark", label="CENTER MARK (etch)"))
    return dict(outline=out, holes=holes, slots=[], marks=[("UP", (0, 20))])

SVC_ITEMS = [  # x, y(local), kind
    (-56, 0, "M16"), (-28, 0, "D"), (0, 0, "D"), (28, 0, "D"),
    (50, 8, "SMA"), (50, -8, "SMA"), (62, 8, "SMA"), (62, -8, "SMA")]
SVC_LABEL = {(-56, 0): "M16 GLAND – SCOUT 24V/CAN", (-28, 0): "D-SIZE – RJ45 (etherCON)", (0, 0): "D-SIZE – USB-A",
             (28, 0): "D-SIZE – SPARE / 12V DC"}
def svc_plate():
    out = rrect(0, 0, *SVC_PLATE, 4)
    holes = [dict(x=x, y=z - SVC_Z, d=3.4, kind="thru", label="Ø3.4 THRU (M3 BH)") for x, z in SVC_PEM]
    for x, y, k in SVC_ITEMS:
        if k == "M16": holes.append(dict(x=x, y=y, d=16.2, kind="thru", label="Ø16.2 M16x1.5 GLAND"))
        if k == "SMA": holes.append(dict(x=x, y=y, d=6.5, kind="thru", label="Ø6.5 SMA BULKHEAD"))
        if k == "D":
            holes.append(dict(x=x, y=y, d=24.0, kind="thru", label="Ø24 D-SIZE"))
            holes.append(dict(x=x - 9.5, y=y + 12, d=3.2, kind="thru", label="Ø3.2 D-SIZE MTG"))
            holes.append(dict(x=x + 9.5, y=y - 12, d=3.2, kind="thru", label="Ø3.2 D-SIZE MTG"))
    return dict(outline=out, holes=holes, slots=[], marks=[])

# AGX tray (2T, 4 lips)
TRAY_MOLD, TRAY_LIP = 116.0, 12.0
def agx_tray_flat():
    base = TRAY_MOLD - 2 * OSSB90           # 108
    lip = TRAY_LIP - OSSB90                 # 8
    half_b = base / 2; full = half_b + BA90 + lip
    out = box(-full, -half_b, full, half_b).union(box(-half_b, -full, half_b, full))
    # include bend zones fully at corners? no - corner square notched
    out = round_concave(out, 0.6)
    cut = rrect(0, 0, 70, 70, 5)
    out = out.difference(cut)
    holes = [dict(x=sx * 45.0, y=sy * 45.0, d=4.5, kind="csk", label="Ø4.5 CSK 90°xØ9.0 (TOP) M4 FH") for sx in (-1, 1) for sy in (-1, 1)]
    slots = []
    ylip = half_b + BA90 + (6.0 - OSSB90 + 2.0)   # lip slot centre at z=8 mold
    for sx in (-1, 1):
        for sy in (-1, 1):
            slots.append(dict(shape=obround(sx * ylip, sy * 30.0, 4.0, 27.0), label="STRAP SLOT 4x27", x=sx * ylip, y=sy * 30))
    bends = []
    for s in (-1, 1):
        c = s * (half_b + BA90 / 2)
        bends.append(dict(p1=(c, -half_b), p2=(c, half_b), note="BEND 90° UP Ri2", kind="v"))
        bends.append(dict(p1=(-half_b, c), p2=(half_b, c), note="BEND 90° UP Ri2", kind="h"))
    return dict(outline=out, holes=holes, slots=slots, bends=bends, marks=[], info=dict(flat=2 * full, base=base))

# splice bracket (2T, 60° bend)
SPL_LEG, SPL_H, SPL_Z0 = 22.0, 100.0, 15.0
def splice_flat():
    leg = SPL_LEG - OSSB60
    tot = 2 * leg + BA60
    out = box(0, 0, tot, SPL_H)
    out = round_convex(out, 2)
    holes = []
    for z in SPLICE_Z:
        for x in (leg - (12 - OSSB60), leg + BA60 + (12 - OSSB60)):
            holes.append(dict(x=x, y=z - SPL_Z0, d=3.3, kind="rivet", label="Ø3.3 RIVET"))
    bends = [dict(p1=(leg + BA60 / 2, 0), p2=(leg + BA60 / 2, SPL_H), note="BEND 60° Ri2", kind="v")]
    return dict(outline=out, holes=holes, slots=[], bends=bends, marks=[], info=dict(flat=tot))


# ---------------- REV9 new parts ----------------
def eplate():
    """P10 removable electrical plate, AL5052 2T, U-shape around AGX tray."""
    inner = hex_poly(AF - 2 * 24.0)
    out = inner.difference(box(-70, -55, 70, 300))
    out = round_concave(out, 5.0); out = round_convex(out, 5.0)
    holes = [dict(x=x, y=y, d=4.5, kind="thru", label="Ø4.5 THRU (M4×8 BH → STANDOFF)", grp="SO") for x, y in EPL_SO]
    for i in range(-6, 7):
        for j in range(-6, 7):
            x, y = 25.0 * i + 12.5, 25.0 * j + 12.5
            p = Point(x, y)
            if not out.buffer(-7.0).contains(p): continue
            if any(math.hypot(x - a, y - b) < 11 for a, b in EPL_SO): continue
            holes.append(dict(x=x, y=y, d=3.4, kind="thru", label="Ø3.4 GRID 25", grp="G"))
    return dict(outline=out, holes=holes, slots=[], marks=[("P10-R9", (0, -125 + 8))])

def riser():
    """P11 OS1 riser frame, AL6061-T6 25T, CNC."""
    out = rrect(0, 0, 140, 140, 10).difference(rrect(0, 0, RISER_IN, RISER_IN, 6))
    holes = [dict(x=x, y=y, d=4.2, kind="tap", label="M5 TAP 10 DP (TOP) – A", grp="A") for x, y in OS1_A]
    holes += [dict(x=x, y=y, d=4.2, kind="tap", label="M5 TAP 10 DP (BOTTOM) – B", grp="B") for x, y in OS1_B]
    return dict(outline=out, holes=holes, slots=[], marks=[])
