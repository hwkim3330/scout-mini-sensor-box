"""REV10-P: the sensor box as flat 3D-printed parts for a Bambu Lab A1 (256 x 256 x 256 mm), PLA for now.

A hexagon of six flat wall panels (one camera per face, 60 deg apart), six corner posts the panels screw
into, a floor, two rail bars under the floor, and six small camera plates. Every part prints lying flat
on a full face, no supports. The top is left open (the lidar mount is not decided yet), which also
lets the compute module's heat out.

Hexagon: side L = 120 mm -> 240 mm across corners (fits the bed in one piece), 208 mm across flats,
130 mm tall. Contents checked in code: Jetson AGX Orin dev kit 110 x 110 x 72 on the floor.

HOLD (placeholders until measured): camera hole and the camera's own screw pattern (CAM_HOLE_D, the
plate is the only part to reprint), rail pitch and slot (RAIL_X, RAIL_SLOT; the bars have long slots).

Screws: M3 self-tapping (pan head) panel -> post and plate -> panel, M3 floor -> post from below,
M4 bolt + nut floor <-> rail bar, rail bar -> robot rail with M5 slider nuts.

Run:  uv run --with cadquery --with trimesh --with numpy --with scipy --with networkx --with manifold3d \\
        python rev10p/box.py      ->  rev10p/out/*.stl, out/assembly.stl
"""
import math
import os

import cadquery as cq
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# --- box ---
L = 120.0                 # hexagon side (outer) = circumradius
T = 4.0                   # wall panel thickness
FLOOR_T = 4.0
H = 126.0                 # panel height (sits on the floor) -> 130 mm overall
APO = L * math.sqrt(3) / 2          # outer apothem (103.9)
LI = L - 2 * T * math.tan(math.radians(30))   # inner side length (= inner circumradius)
RI = LI

# --- posts ---
POST_A = 14.0             # rhombus arm along each inner face
PILOT = 2.6               # M3 self-tapping pilot
CLEAR3 = 3.4
PILOT_DEPTH = 9.0
Z_A = (15.0, 63.0, 111.0)         # screw heights on a panel's +x edge
Z_B = (27.0, 75.0, 99.0)          # and on its -x edge (staggered so the two holes in a post never meet)

# --- camera (REV9 values; HOLD for the real camera) ---
CAM_Z = 92.0              # camera centre above the bottom of the box
CAM_WIN = (36.0, 36.0)    # window in the wall behind the plate
CAM_PLATE = (60.0, 55.0, 3.0)
CAM_SCREWS = [(sx * 24.0, sz * 22.0) for sx in (-1, 1) for sz in (-1, 1)]
CAM_HOLE_D = 30.0         # HOLD: hole the camera's clear housing passes through

# --- vents (low, intake; the open top is the exhaust) ---
VENT_W, VENT_H, VENT_PITCH, VENT_Z = 5.0, 26.0, 10.0, 22.0

# --- floor ---
GRID = 20.0               # M3 mounting grid
AGX_C = (0.0, 15.0)
AGX_SO = [(AGX_C[0] + sx * 45, AGX_C[1] + sy * 45) for sx in (-1, 1) for sy in (-1, 1)]   # REV9 pattern
AGX_BOX = (110.0, 110.0, 72.0)

# --- rail bars (HOLD: rail pitch) ---
RAIL_X = 115.0            # half the rail spacing (REV9 value)
RAIL_SLOT = (5.5, 24.0)   # M5, long along X to absorb the unknown pitch
BAR = (248.0, 30.0, 8.0)
BAR_Y = 60.0
BAR_BOLTS_X = (-80.0, -40.0, 40.0, 80.0)
M4 = 4.5


def phi(i):
    return math.radians(30 + 60 * i)


def panel_frame(i):
    """4x4: panel-local (x across, y up, z into the box from the outer face) -> world."""
    p = phi(i)
    n = np.array([math.cos(p), math.sin(p), 0.0])
    t = np.array([math.sin(p), -math.cos(p), 0.0])
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2] = t, (0, 0, 1), -n
    m[:3, 3] = n * APO + np.array([0, 0, FLOOR_T])
    return m


def edge_holes():
    """Panel-local (x, y) of the post screws: +x edge at Z_A, -x edge at Z_B, half an arm in from the corner."""
    xh = LI / 2 - POST_A / 2
    return [(xh, z) for z in Z_A] + [(-xh, z) for z in Z_B]


def cyl_z(x, y, z0, h, d):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(h)


def panel():
    k = T * math.tan(math.radians(30))
    p = (cq.Workplane("XY").polyline([(-L / 2, 0), (L / 2, 0), (L / 2 - k, T), (-L / 2 + k, T)]).close()
         .extrude(H))                                   # in XY = (x, z-thickness), extruded along Z = height
    p = p.rotate((0, 0, 0), (1, 0, 0), 90).mirror("XZ")  # -> x across, y up (0..H), z thickness (0..T)
    bb = p.val().BoundingBox()
    p = p.translate((0, -bb.ymin, -bb.zmin))
    cz = CAM_Z - FLOOR_T
    p = p.cut(cq.Workplane("XY").center(0, cz).rect(*CAM_WIN).extrude(T + 2).translate((0, 0, -1)))
    for sx, sz in CAM_SCREWS:
        p = p.cut(cyl_z(sx, cz + sz, -1, T + 2, PILOT))
    for x, y in edge_holes():
        p = p.cut(cyl_z(x, y, -1, T + 2, CLEAR3))
    n = int((LI - 50) // VENT_PITCH)
    for j in range(n):
        x = (j - (n - 1) / 2) * VENT_PITCH
        p = p.cut(cq.Workplane("XY").center(x, VENT_Z + VENT_H / 2).rect(VENT_W, VENT_H).extrude(T + 2)
                  .translate((0, 0, -1)).edges("|Z").fillet(VENT_W / 2 - 0.01))
    return p


def inner_vertex(k):
    a = math.radians(60 * k)
    return np.array([RI * math.cos(a), RI * math.sin(a)])


def post(k):
    """World-placed corner post k (at inner vertex k), with pilots for both panels and the floor."""
    v = inner_vertex(k)
    u1 = inner_vertex(k + 1) - v
    u1 /= np.linalg.norm(u1)
    u2 = inner_vertex(k - 1) - v
    u2 /= np.linalg.norm(u2)
    pts = [v, v + POST_A * u1, v + POST_A * (u1 + u2), v + POST_A * u2]
    s = cq.Workplane("XY").workplane(offset=FLOOR_T).polyline([tuple(p) for p in pts]).close().extrude(H)
    c = v + POST_A * (u1 + u2) / 2
    s = s.cut(cyl_z(c[0], c[1], FLOOR_T - 1, PILOT_DEPTH + 1, PILOT))          # floor screw
    s = s.cut(cyl_z(c[0], c[1], FLOOR_T + H - PILOT_DEPTH, PILOT_DEPTH + 1, PILOT))   # future lid
    for i in (k, k - 1):                                # the two panels meeting at this corner
        m = panel_frame(i)
        for x, y in edge_holes():
            w = m @ np.array([x, y, T, 1.0])
            if np.linalg.norm(w[:2] - c) > POST_A:      # this hole belongs to the panel's other end
                continue
            d = -m[:3, 2]                               # panel-local +z = into the box
            s = s.cut(cq.Workplane(obj=cq.Solid.makeCylinder(PILOT / 2, PILOT_DEPTH,
                                                             cq.Vector(*w[:3]), cq.Vector(*(-d)))))
    return s, c, pts


def floor():
    f = cq.Workplane("XY").polygon(6, 2 * L).extrude(FLOOR_T)
    pts = []
    for k in range(6):
        _, c, _ = post(k)
        pts.append(tuple(c))
    f = f.cut(cq.Workplane("XY").pushPoints(pts).circle(CLEAR3 / 2).extrude(FLOOR_T))
    f = f.cut(cq.Workplane("XY").pushPoints(pts).circle(3.2).extrude(1.8))   # pan heads sit flush below
    grid = []
    r = APO - T - 16
    for gx in np.arange(-200, 201, GRID):
        for gy in np.arange(-200, 201, GRID):
            if all(abs(gx * math.cos(phi(i)) + gy * math.sin(phi(i))) < r for i in range(3)):
                if all(abs(gy - sy * BAR_Y) > BAR[1] / 2 + 3 for sy in (-1, 1)):
                    grid.append((gx, gy))
    f = f.cut(cq.Workplane("XY").pushPoints(grid).circle(CLEAR3 / 2).extrude(FLOOR_T))
    f = f.cut(cq.Workplane("XY").pushPoints(AGX_SO).circle(CLEAR3 / 2).extrude(FLOOR_T))
    bolts = [(x, sy * BAR_Y) for x in BAR_BOLTS_X for sy in (-1, 1)]
    return f.cut(cq.Workplane("XY").pushPoints(bolts).circle(M4 / 2).extrude(FLOOR_T))


def rail_bar():
    b = cq.Workplane("XY").box(*BAR, centered=(True, True, False)).edges("|Z").fillet(4)
    b = b.cut(cq.Workplane("XY").pushPoints([(x, 0) for x in BAR_BOLTS_X]).circle(M4 / 2).extrude(BAR[2]))
    b = b.cut(cq.Workplane("XY").pushPoints([(x, 0) for x in BAR_BOLTS_X]).polygon(6, 8.1).extrude(3.2))  # M4 nut
    for sx in (-1, 1):
        b = b.cut(cq.Workplane("XY").center(sx * RAIL_X, 0).slot2D(RAIL_SLOT[1], RAIL_SLOT[0]).extrude(BAR[2]))
    return b


def cam_plate():
    w, h, t = CAM_PLATE
    p = cq.Workplane("XY").box(w, h, t, centered=(True, True, False)).edges("|Z").fillet(4)
    p = p.cut(cq.Workplane("XY").pushPoints(CAM_SCREWS).circle(CLEAR3 / 2).extrude(t))
    return p.cut(cq.Workplane("XY").circle(CAM_HOLE_D / 2).extrude(t))


def to_mesh(wp):
    path = os.path.join(OUT, "_tmp.stl")
    cq.exporters.export(wp, path)
    m = trimesh.load(path)
    os.remove(path)
    return m


def lay_flat(m, normal):
    """Rotate so `normal` points down, drop onto z=0, centre on the A1 bed."""
    r = trimesh.geometry.align_vectors(normal, [0, 0, -1])
    m = m.copy()
    m.apply_transform(r)
    m.apply_translation([128 - m.bounds.mean(0)[0], 128 - m.bounds.mean(0)[1], -m.bounds[0][2]])
    return m


def build():
    parts, assy = {}, []
    pm = to_mesh(panel())                       # outer face is z=0: prints face down as built
    pm.apply_translation([128, 128 - H / 2, 0])
    parts["panel"] = pm
    for i in range(6):
        m = to_mesh(panel())
        m.apply_transform(panel_frame(i))
        assy.append(("panel%d" % i, m))
    for k in range(6):
        s, c, pts = post(k)
        m = to_mesh(s)
        assy.append(("post%d" % k, m))
        if k == 0:
            e = np.array(pts[1]) - np.array(pts[0])
            n = np.array([e[1], -e[0], 0.0])         # outward normal of the face against panel 0
            if np.dot(n[:2], np.array(pts[2]) - np.array(pts[0])) > 0:
                n = -n
            parts["post"] = lay_flat(m, n / np.linalg.norm(n))
    fm = to_mesh(floor())
    assy.append(("floor", fm))
    f2 = fm.copy()
    f2.apply_translation([128, 128, 0])
    parts["floor"] = f2
    bm = to_mesh(rail_bar())
    for sy in (-1, 1):
        b = bm.copy()
        b.apply_translation([0, sy * BAR_Y, -BAR[2]])     # under the floor, nut traps facing down
        assy.append(("bar", b))
    b2 = bm.copy()
    b2.apply_translation([128, 128, 0])
    parts["rail_bar"] = b2
    cm = to_mesh(cam_plate())
    for i in range(6):
        loc = panel_frame(i) @ np.array([0, CAM_Z - FLOOR_T, -CAM_PLATE[2], 1.0])
        c2 = cm.copy()
        rot = np.eye(4)
        rot[:3, :3] = panel_frame(i)[:3, :3]
        c2.apply_transform(rot)
        c2.apply_translation(loc[:3])
        assy.append(("cam%d" % i, c2))
    c3 = cm.copy()
    c3.apply_translation([128, 128, 0])
    parts["cam_plate"] = c3
    return parts, assy


def check(assy):
    names = [n for n, _ in assy]
    bad = 0
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            ma, mb = assy[a][1], assy[b][1]
            if np.any(ma.bounds[1] < mb.bounds[0]) or np.any(mb.bounds[1] < ma.bounds[0]):
                continue
            v = trimesh.boolean.intersection([ma, mb], engine="manifold").volume
            if v > 0.5:
                print(f"  overlap {names[a]} / {names[b]}: {v:.1f} mm3")
                bad += 1
    agx = trimesh.creation.box(AGX_BOX)
    agx.apply_translation([AGX_C[0], AGX_C[1], FLOOR_T + AGX_BOX[2] / 2 + 0.5])
    for n, m in assy:
        if n.startswith(("panel", "post", "cam")):
            v = trimesh.boolean.intersection([agx, m], engine="manifold").volume
            if v > 0.1:
                print(f"  AGX hits {n}: {v:.1f} mm3")
                bad += 1
    return bad


if __name__ == "__main__":
    parts, assy = build()
    for name, m in parts.items():
        m.export(os.path.join(OUT, name + ".stl"))
        e = m.extents
        print(f"{name:10s} {e[0]:6.1f} x {e[1]:6.1f} x {e[2]:5.1f}  watertight={m.is_watertight}  fits_bed={max(e[:2]) <= 250}")
    trimesh.util.concatenate([m for _, m in assy]).export(os.path.join(OUT, "assembly.stl"))
    print("clearance problems:", check(assy))
