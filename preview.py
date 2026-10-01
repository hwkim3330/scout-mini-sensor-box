import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, geom as g
from shapely.geometry import Polygon, MultiPolygon
def draw(ax, part, title):
    o = part["outline"]
    geoms = o.geoms if isinstance(o, MultiPolygon) else [o]
    for p in geoms:
        ax.plot(*p.exterior.xy, "k", lw=.6)
        for i in p.interiors: ax.plot(*i.xy, "b", lw=.5)
    for h in part["holes"]:
        c = {"pem": "r", "csk": "g", "rivet": "m"}.get(h["kind"], "b")
        ax.add_patch(plt.Circle((h["x"], h["y"]), h["d"]/2, fill=False, color=c, lw=.5))
    for s in part.get("slots", []): ax.plot(*s["shape"].exterior.xy, "b", lw=.5)
    for b in part.get("bends", []): ax.plot(*zip(b["p1"], b["p2"]), "c--", lw=.5)
    ax.set_aspect("equal"); ax.set_title(title, fontsize=8)
fig, axs = plt.subplots(2, 3, figsize=(18, 10))
draw(axs[0,0], g.wall_flat(g.HALF_A), "wall A"); draw(axs[0,1], g.wall_flat(g.HALF_B), "wall B")
draw(axs[0,2], g.bottom_plate(), "bottom"); draw(axs[1,0], g.top_cover(), "cover")
draw(axs[1,1], g.agx_tray_flat(), "tray"); draw(axs[1,2], g.svc_plate(), "svc")
plt.tight_layout(); plt.savefig("out/preview.png", dpi=110)
