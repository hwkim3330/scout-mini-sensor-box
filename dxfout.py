import ezdxf, math, geom as g
from shapely.geometry import MultiPolygon
from ezdxf.enums import TextEntityAlignment

PARTS = {
  "P01_BOTTOM_PLATE": (g.bottom_plate, "AL5052-H32 3.0T", 1),
  "P02_WALL_HALF_FRONT": (lambda: g.wall_flat(g.HALF_A), "AL5052-H32 2.0T", 1),
  "P03_WALL_HALF_REAR": (lambda: g.wall_flat(g.HALF_B), "AL5052-H32 2.0T", 1),
  "P04_TOP_COVER": (g.top_cover, "AL5052-H32 2.0T", 1),
  "P05_OS1_PLATE": (g.os1_plate, "AL6061-T6 5.0T", 1),
  "P06_CAMERA_PLATE": (g.cam_plate, "AL5052-H32 2.0T", 8),
  "P07_SERVICE_PANEL": (g.svc_plate, "AL5052-H32 2.0T", 1),
  "P08_AGX_TRAY": (g.agx_tray_flat, "AL5052-H32 2.0T", 1),
  "P09_SPLICE_BRACKET": (g.splice_flat, "AL5052-H32 2.0T", 2),
  "P10_ELEC_PLATE": (g.eplate, "AL5052-H32 2.0T", 1),
  "P11_OS1_RISER": (g.riser, "AL6061-T6 25T (CNC)", 1),
}

def write(name, part, mat, qty, path):
    doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
    for ln, col, lt in [("CUT", 7, "CONTINUOUS"), ("BEND", 1, "DASHED"), ("PEM", 3, "CONTINUOUS"), ("CSK", 4, "CONTINUOUS"), ("TAP", 5, "CONTINUOUS"),
                        ("ETCH", 6, "CONTINUOUS"), ("NOTE", 8, "CONTINUOUS")]:
        doc.layers.add(ln, color=col, linetype=lt)
    msp = doc.modelspace()
    o = part["outline"]
    for p in (o.geoms if isinstance(o, MultiPolygon) else [o]):
        msp.add_lwpolyline(list(p.exterior.coords), close=True, dxfattribs={"layer": "CUT"})
        for i in p.interiors: msp.add_lwpolyline(list(i.coords), close=True, dxfattribs={"layer": "CUT"})
    for s in part.get("slots", []):
        msp.add_lwpolyline(list(s["shape"].exterior.coords), close=True, dxfattribs={"layer": "CUT"})
    for h in part["holes"]:
        if h["kind"] == "mark":
            r = 1.5
            msp.add_line((h["x"] - r, h["y"]), (h["x"] + r, h["y"]), dxfattribs={"layer": "ETCH"})
            msp.add_line((h["x"], h["y"] - r), (h["x"], h["y"] + r), dxfattribs={"layer": "ETCH"})
            continue
        if h["kind"] == "tap" and "DP" in h["label"]:   # blind tap: mark only
            msp.add_circle((h["x"], h["y"]), h["d"] / 2, dxfattribs={"layer": "TAP"}); msp.add_circle((h["x"], h["y"]), 2.5, dxfattribs={"layer": "TAP"}); continue
        msp.add_circle((h["x"], h["y"]), h["d"] / 2, dxfattribs={"layer": "CUT"})
        if h["kind"] == "tap": msp.add_circle((h["x"], h["y"]), 2.5, dxfattribs={"layer": "TAP"})
        if h["kind"] == "pem":
            msp.add_circle((h["x"], h["y"]), h["d"] / 2 + 1.2, dxfattribs={"layer": "PEM"})
        if h["kind"] == "csk":
            msp.add_circle((h["x"], h["y"]), 4.5, dxfattribs={"layer": "CSK"})
    for b in part.get("bends", []):
        msp.add_line(b["p1"], b["p2"], dxfattribs={"layer": "BEND"})
        mx, my = (b["p1"][0] + b["p2"][0]) / 2, (b["p1"][1] + b["p2"][1]) / 2
        rot = 90 if b["kind"] == "v" else 0
        t = msp.add_text(b["note"], height=2.5, rotation=rot, dxfattribs={"layer": "NOTE"})
        t.set_placement((mx + (3 if rot else 0), my + (0 if rot else 1.5)), align=TextEntityAlignment.BOTTOM_CENTER)
    for txt, (x, y) in part.get("marks", []):
        t = msp.add_text(txt, height=5, dxfattribs={"layer": "ETCH"}); t.set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)
    minx, miny, maxx, maxy = o.bounds
    t = msp.add_text(f"{name}  {mat}  QTY {qty}  REV9  KETI  (ETCH:part no. only, NOTE/BEND layers: do not cut)", height=3, dxfattribs={"layer": "NOTE"})
    t.set_placement((minx, miny - 10))
    doc.saveas(path)

if __name__ == "__main__":
    import os; os.makedirs("out/dxf", exist_ok=True)
    for n, (fn, mat, q) in PARTS.items():
        write(n, fn(), mat, q, f"out/dxf/{n}.dxf")
    print(os.listdir("out/dxf"))
