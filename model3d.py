import math, cadquery as cq, geom as g
from shapely.geometry import Polygon, MultiPolygon

def poly_wp(poly, plane="XY"):
    """shapely polygon (with interiors) -> cq Workplane face sketch (outer + inner wires)."""
    return [list(poly.exterior.coords)[:-1]] + [list(i.coords)[:-1] for i in poly.interiors]

def extrude_poly(poly, t, holes=(), slots=(), z0=0.0):
    geoms = poly.geoms if isinstance(poly, MultiPolygon) else [poly]
    solid = None
    for p in geoms:
        ext = list(p.exterior.coords)[:-1]
        s = cq.Workplane("XY").workplane(offset=z0).polyline(ext).close().extrude(t)
        for i in p.interiors:
            c = cq.Workplane("XY").workplane(offset=z0 - 1).polyline(list(i.coords)[:-1]).close().extrude(t + 2)
            s = s.cut(c)
        solid = s if solid is None else solid.union(s)
    for h in holes:
        if h["kind"] == "mark": continue
        c = cq.Workplane("XY").workplane(offset=z0 - 1).center(h["x"], h["y"]).circle(h["d"] / 2).extrude(t + 2)
        solid = solid.cut(c)
    for sl in slots:
        c = cq.Workplane("XY").workplane(offset=z0 - 1).polyline(list(sl["shape"].exterior.coords)[:-1]).close().extrude(t + 2)
        solid = solid.cut(c)
    return solid

def face_plane(face, depth=0.0, z=0.0):
    n, t = g.nvec(face), g.tvec(face)
    o = g.face_point(face, 0, depth)
    return cq.Plane(origin=(o[0], o[1], z), xDir=(t[0], t[1], 0), normal=(n[0], n[1], 0))

def wall_half(faces):
    L = g.SIDE; t = g.T_WALL; h = g.Z_WALL_TOP - g.Z_BOT_TOP
    solid = None
    m = 1.155
    for idx, face in enumerate(faces):
        # trapezoid in top view between outer (depth0) and inner (depth t)
        a0 = L / 2 - (g.E_TRIM if idx == 0 else 0); b0 = L / 2 - (g.E_TRIM if idx == 2 else 0)
        pts = [g.face_point(face, -a0, 0), g.face_point(face, b0, 0), g.face_point(face, b0 - (0 if idx == 2 else m), t), g.face_point(face, -a0 + (0 if idx == 0 else m), t)]
        p = cq.Workplane("XY").workplane(offset=g.Z_BOT_TOP).polyline(pts).close().extrude(h)
        # flanges
        for zf in (g.Z_BOT_TOP, g.Z_WALL_TOP - t):
            fp = [g.face_point(face, -L / 2 + g.flange_a(t), t), g.face_point(face, L / 2 - g.flange_a(t), t),
                  g.face_point(face, L / 2 - g.flange_a(g.F), g.F), g.face_point(face, -L / 2 + g.flange_a(g.F), g.F)]
            fl = cq.Workplane("XY").workplane(offset=zf).polyline(fp).close().extrude(t)
            p = p.union(fl)
            for sg in (-1, 1):
                x, y = g.face_point(face, sg * g.TAU_PEM, g.D_PEM)
                d = 5.4 if zf < 10 else 4.22
                p = p.cut(cq.Workplane("XY").workplane(offset=zf - 1).center(x, y).circle(d / 2).extrude(t + 2))
        # face features
        pl = face_plane(face, depth=-1)
        for kind, geo, label in g.face_features(face, idx):
            wp = cq.Workplane(pl)
            if kind in ("win", "vent"):
                c = wp.polyline(list(geo.exterior.coords)[:-1]).close().extrude(-(t + 2))
            elif kind == "pem":
                x, z, pn = geo; c = wp.center(x, z).circle(g.PEM[pn][0] / 2).extrude(-(t + 2))
            elif kind == "rivet":
                x, z, d = geo; c = wp.center(x, z).circle(d / 2).extrude(-(t + 2))
            p = p.cut(c)
        solid = p if solid is None else solid.union(p)
    return solid

def bottom():
    b = g.bottom_plate(); return extrude_poly(b["outline"], g.T_BOT, b["holes"], b["slots"], 0)
def cover():
    c = g.top_cover(); return extrude_poly(c["outline"], g.T_COV, c["holes"], [], g.Z_WALL_TOP)
Z_RISER = g.H_TOTAL
Z_P05 = g.H_TOTAL + g.RISER_T
Z_OS1 = Z_P05 + g.T_OS1
def os1_plate():
    c = g.os1_plate(); return extrude_poly(c["outline"], g.T_OS1, c["holes"], [], Z_P05)
def riser():
    r = g.riser(); s = extrude_poly(r["outline"], g.RISER_T, [], [], Z_RISER)
    for h in r["holes"]:
        z0 = Z_RISER + g.RISER_T - 10 if h["grp"] == "A" else Z_RISER - 0.01
        s = s.cut(cq.Workplane("XY").workplane(offset=z0).center(h["x"], h["y"]).circle(2.1).extrude(10.01))
    return s
def eplate():
    e = g.eplate(); return extrude_poly(e["outline"], 2.0, e["holes"], [], g.Z_BOT_TOP + g.EPL_H)
def on_face(face, part2d, zc, t=2.0, gap=0.0):
    pl = face_plane(face, depth=-gap, z=zc)
    p = part2d["outline"]
    sol = cq.Workplane(pl).polyline(list(p.exterior.coords)[:-1]).close().extrude(t)
    for h in part2d["holes"]:
        if h["kind"] == "mark": continue
        sol = sol.cut(cq.Workplane(face_plane(face, depth=-gap + 1, z=zc)).center(h["x"], h["y"]).circle(h["d"] / 2).extrude(t + 2))
    return sol

def tray():
    # formed approx: base 116x116x2 with 4 lips, cutout, holes
    m, lip, t = g.TRAY_MOLD, g.TRAY_LIP, 2.0
    z0 = g.Z_BOT_TOP + 25.0
    s = cq.Workplane("XY").workplane(offset=z0).rect(m, m).extrude(lip)
    s = s.cut(cq.Workplane("XY").workplane(offset=z0 + t).rect(m - 2 * t, m - 2 * t).extrude(lip))
    s = s.cut(cq.Workplane("XY").workplane(offset=z0 - 1).rect(70, 70).extrude(t + 2))
    for sx in (-1, 1):
        for sy in (-1, 1):
            s = s.cut(cq.Workplane("XY").workplane(offset=z0 - 1).center(sx * 45, sy * 45).circle(2.25).extrude(t + 2))
            s = s.cut(cq.Workplane("YZ").workplane(offset=sx * m / 2 - 3).center(sy * 30, z0 + 8).rect(27, 4).extrude(6))
    return s.translate((g.AGX_C[0], g.AGX_C[1], 0))

def splice(corner_deg):
    a = math.radians(corner_deg)
    # inner vertex
    rc_in = (g.AF - 2 * g.T_WALL) / math.sqrt(3)
    v = (rc_in * math.cos(a), rc_in * math.sin(a))
    sol = None
    for fa in (corner_deg - 30, corner_deg + 30):   # the two face normals adjacent to this corner
        n = (math.cos(math.radians(fa)), math.sin(math.radians(fa)))
        tdir = (-n[1], n[0])
        # leg direction from vertex along face away from corner
        d = (v[0] * tdir[0] + v[1] * tdir[1])
        sgn = -1 if d > 0 else 1
        p0 = v; p1 = (v[0] + sgn * tdir[0] * g.SPL_LEG, v[1] + sgn * tdir[1] * g.SPL_LEG)
        q1 = (p1[0] - n[0] * 2, p1[1] - n[1] * 2); q0 = (p0[0] - n[0] * 2, p0[1] - n[1] * 2)
        leg = cq.Workplane("XY").workplane(offset=g.SPL_Z0).polyline([p0, p1, q1, q0]).close().extrude(g.SPL_H)
        sol = leg if sol is None else sol.union(leg)
    return sol

def dummies():
    d = {}
    z0 = g.Z_BOT_TOP + 25 + 2 + 1
    d["AGX_ORIN_DEVKIT(dummy)"] = cq.Workplane("XY").workplane(offset=z0).center(*g.AGX_C).rect(110, 110).extrude(71.65)
    d["OUSTER_OS1(dummy)"] = cq.Workplane("XY").workplane(offset=Z_OS1).circle(43.5).extrude(74.2)
    so = None
    for (x, y) in g.AGX_SO:
        s = cq.Workplane("XY").workplane(offset=g.Z_BOT_TOP).center(x, y).polygon(6, 8 / math.cos(math.pi / 6)).extrude(25)
        so = s if so is None else so.union(s)
    d["STANDOFF_M4x25(4)"] = so
    so2 = None
    for (x, y) in g.EPL_SO:
        s2 = cq.Workplane("XY").workplane(offset=g.Z_BOT_TOP).center(x, y).polygon(6, 7 / math.cos(math.pi / 6)).extrude(g.EPL_H)
        so2 = s2 if so2 is None else so2.union(s2)
    d["STANDOFF_M4x10(6)"] = so2
    for nm, (cx, cy, w, h, hh) in {"DCDC(dummy)": (50, -85, 60, 45, 30), "CANPAL_WAGO(dummy)": (-50, -85, 50, 35, 18), "5G_MODEM(dummy)": (100, 0, 40, 80, 15)}.items():
        d[nm] = cq.Workplane("XY").workplane(offset=g.Z_BOT_TOP + g.EPL_H + 2).center(cx, cy).rect(w, h).extrude(hh)
    cams = None
    for f in g.FACES:
        n = g.nvec(f); x, y = g.face_point(f, 0, 2 + 6)
        c = cq.Workplane("XY").box(10, 25, 24).rotate((0, 0, 0), (0, 0, 1), g.FACES[f]).translate((x, y, g.CAM_Z))
        cams = c if cams is None else cams.union(c)
    d["B0473_CAM_MODULES(dummy)"] = cams
    return d

if __name__ == "__main__":
    import os
    os.makedirs("out/step", exist_ok=True)
    parts = {}
    parts["P01_BOTTOM_PLATE"] = (bottom(), (0.75, 0.75, 0.78))
    parts["P02_WALL_HALF_FRONT"] = (wall_half(g.HALF_A), (0.62, 0.66, 0.72))
    parts["P03_WALL_HALF_REAR"] = (wall_half(g.HALF_B), (0.58, 0.62, 0.70))
    parts["P04_TOP_COVER"] = (cover(), (0.80, 0.80, 0.82))
    parts["P05_OS1_PLATE"] = (os1_plate(), (0.55, 0.55, 0.60))
    for f in g.FACES:
        parts[f"P06_CAM_PLATE_{f}"] = (on_face(f, g.cam_plate(), g.CAM_Z), (0.25, 0.25, 0.28))
    parts["P07_SERVICE_PANEL"] = (on_face(g.SERVICE_FACE, g.svc_plate(), g.SVC_Z), (0.25, 0.25, 0.28))
    parts["P08_AGX_TRAY"] = (tray(), (0.7, 0.7, 0.74))
    parts["P10_ELEC_PLATE"] = (eplate(), (0.62, 0.70, 0.62))
    parts["P11_OS1_RISER"] = (riser(), (0.68, 0.68, 0.72))
    parts["P09_SPLICE_0deg"] = (splice(0), (0.5, 0.5, 0.55))
    parts["P09_SPLICE_180deg"] = (splice(180), (0.5, 0.5, 0.55))
    for k, v in dummies().items(): parts[k] = (v, (0.2, 0.45, 0.75) if "OS1" in k else (0.35, 0.65, 0.35) if "AGX" in k else (0.85, 0.5, 0.2) if "CAM" in k else (0.75, 0.6, 0.35))
    assy = cq.Assembly(name="SCOUT_MINI_OMNI_SENSOR_BOX_REV9")
    for k, (s, c) in parts.items():
        assy.add(s, name=k, color=cq.Color(*c))
        if (k.startswith("P0") or k.startswith("P1")) and not k.startswith("P06_CAM_PLATE_C2") and ("P06" not in k or k.endswith("C1")) and "P09_SPLICE_180" not in k:
            cq.exporters.export(s, f"out/step/{k.replace('_C1','').replace('_0deg','')}.step")
    assy.save("out/step/ASSY_SENSOR_BOX_REV9.step")
    # interference check between fabricated parts
    import itertools
    names = [k for k in parts]
    for a, b in itertools.combinations(names, 2):
        try:
            v = parts[a][0].val().intersect(parts[b][0].val()).Volume()
        except Exception as e:
            v = -1
        if v > 1.0: print(f"INTERFERENCE {a} x {b}: {v:.1f} mm3")
    import pickle
    tess = {}
    for k, (s, c) in parts.items():
        vs, fs = s.val().tessellate(0.3, 0.3)
        tess[k] = ([(p.x, p.y, p.z) for p in vs], fs, c)
    pickle.dump(tess, open("out/tess.pkl", "wb"))
    print("ok", len(parts))
