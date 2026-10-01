import geom as g, dxfout
from shapely.geometry import Point, box
from shapely.ops import unary_union
T = {"P01_BOTTOM_PLATE":3,"P05_OS1_PLATE":5,"P11_OS1_RISER":3}
bad = 0
for name, (fn, mat, q) in dxfout.PARTS.items():
    p = fn(); t = T.get(name, 2)
    o = p["outline"]
    feats = [Point(h["x"], h["y"]).buffer(h["d"]/2) for h in p["holes"] if h["kind"] != "mark"] + [s["shape"] for s in p.get("slots", [])]
    bz = []
    for b in p.get("bends", []):
        (x1,y1),(x2,y2) = b["p1"], b["p2"]
        w = g.BA60/2 if "60" in b["note"] else g.BA90/2
        bz.append(box(min(x1,x2)-(w if b["kind"]=="v" else 0), min(y1,y2)-(w if b["kind"]=="h" else 0), max(x1,x2)+(w if b["kind"]=="v" else 0), max(y1,y2)+(w if b["kind"]=="h" else 0)))
    bzu = unary_union(bz) if bz else None
    # interior cut features of the outline itself (windows) as boundary
    bnd = o.boundary
    worst = 1e9
    for i, h in enumerate(p["holes"]):
        if h["kind"] == "mark": continue
        c = Point(h["x"], h["y"]); r = h["d"]/2
        others = unary_union([f for j, f in enumerate(feats) if j != i and not f.equals(Point(h["x"],h["y"]).buffer(r))])
        de = bnd.distance(c) - r
        if not o.buffer(1e-6).contains(c): print("!! hole outside part", name, h); bad += 1; continue
        do = others.distance(c) - r if not others.is_empty else 99
        db = bzu.distance(c) - r if bzu is not None else 99
        need = max(t, 1.0)
        msg = []
        if de < need: msg.append(f"edge {de:.2f}<{need}")
        if do < need and not ("D-SIZE" in h["label"]): msg.append(f"hole-hole {do:.2f}")
        if h["kind"] == "pem":
            C = g.PEM[h["label"]][1]
            if de + r < C: msg.append(f"PEM C/L-edge {de+r:.2f}<{C}")
            if db < 2*t: msg.append(f"PEM-bend {db:.2f}<{2*t}")
        elif bzu is not None and db < 1.5*t: msg.append(f"hole-bend {db:.2f}")
        if msg: print(name, h["label"], round(h["x"],1), round(h["y"],1), "; ".join(msg)); bad += 1
    for s in p.get("slots", []):
        de = bnd.distance(s["shape"])
        if de < t: print(name, "slot edge", de); bad += 1
print("DRC issues:", bad)
