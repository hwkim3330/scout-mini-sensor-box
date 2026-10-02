import math, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly, Circle, FancyArrowPatch, Rectangle
from shapely.geometry import MultiPolygon, Polygon, LineString
# Hangul-capable font: Noto Sans CJK (Linux), Apple SD Gothic Neo (macOS), Malgun Gothic (Windows)
CJK_FONTS = [("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "Noto Sans CJK JP"),
             ("/System/Library/Fonts/AppleSDGothicNeo.ttc", "Apple SD Gothic Neo"),
             ("C:/Windows/Fonts/malgun.ttf", "Malgun Gothic")]
for path, name in CJK_FONTS:
    try:
        fm.fontManager.addfont(path)
    except (FileNotFoundError, RuntimeError):
        continue
    plt.rcParams["font.family"] = plt.rcParams["font.sans-serif"] = [name]
    break
else:
    print("warning: no Hangul font found; Korean text in the drawings will not render")
PT = 1 / 0.3528          # pt per mm
LW_O, LW_T, LW_C = 0.5 * PT, 0.18 * PT, 0.13 * PT
FS = 6.0                  # default text pt
INK = "#111111"; BLUE = "#1f4e79"; RED = "#b00020"; GRAY = "#777777"

class Sheet:
    def __init__(self, title, no, total, sub="SCOUT MINI OMNI / Jetson AGX Orin / Arducam B0473 / Ouster OS1", part=None):
        self.fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1]); ax = self.ax
        ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.axis("off")
        ax.add_patch(Rectangle((10, 10), 400, 277, fill=False, lw=0.7 * PT, ec=INK))
        ax.add_patch(Rectangle((5, 5), 410, 287, fill=False, lw=0.25 * PT, ec=INK))
        # zone ticks
        for i in range(9):
            x = 10 + 400 * i / 8
            if 0 < i < 8: ax.plot([x, x], [5, 10], color=INK, lw=LW_T); ax.plot([x, x], [287, 292], color=INK, lw=LW_T)
        for i, c in enumerate("12345678"): ax.text(10 + 400 * (i + .5) / 8, 289.5, c, ha="center", va="center", fontsize=5)
        for i, c in enumerate("FEDCBA"): ax.text(7.5, 10 + 277 * (i + .5) / 6, c, ha="center", va="center", fontsize=5)
        ax.text(14, 281, title, fontsize=11, weight="bold", va="center", color=INK)
        ax.text(406, 281, sub, fontsize=5.5, va="center", ha="right", color=GRAY)
        ax.plot([10, 410], [275, 275], color=INK, lw=LW_T)
        self.title_block(title, no, total, part)
        ax.text(14, 13, "DIMENSIONS IN mm · 3RD ANGLE PROJECTION · DO NOT SCALE · DXF = MASTER FOR CUT GEOMETRY · 도면/DXF 상이 시 문의",
                fontsize=4.8, color=GRAY, va="center")

    def title_block(self, title, no, total, part):
        ax = self.ax; x0, y0, w, h = 250, 10, 160, 34
        ax.add_patch(Rectangle((x0, y0), w, h, fill=True, fc="white", lw=0.5 * PT, ec=INK, zorder=5))
        rows = [y0 + 26, y0 + 18, y0 + 10]
        for y in rows: ax.plot([x0, x0 + w], [y, y], color=INK, lw=LW_T, zorder=6)
        for x in (x0 + 55, x0 + 110, x0 + 135): ax.plot([x, x], [y0, y0 + 26], color=INK, lw=LW_T, zorder=6)
        t = lambda x, y, s, **k: ax.text(x, y, s, zorder=7, **k)
        t(x0 + 2, y0 + 30, "KETI  Mobility Platform Research Center", fontsize=7, weight="bold", va="center")
        t(x0 + w - 2, y0 + 30, "PROJECT: SCOUT-OMNI-SBOX", fontsize=5.5, va="center", ha="right")
        p = part or {}
        cells = [
            (x0 + 2, y0 + 22, "PART NO.", p.get("no", "—")), (x0 + 57, y0 + 22, "MATERIAL", p.get("mat", "—")),
            (x0 + 112, y0 + 22, "QTY", p.get("qty", "—")), (x0 + 137, y0 + 22, "SCALE", p.get("scale", "AS NOTED")),
            (x0 + 2, y0 + 14, "TITLE", p.get("name", title)), (x0 + 57, y0 + 14, "FINISH", p.get("finish", "RAW / OPT. BLACK P/C")),
            (x0 + 112, y0 + 14, "REV", "9"), (x0 + 137, y0 + 14, "SHEET", f"{no} / {total}"),
            (x0 + 2, y0 + 6, "DRAWN", "hwkim3 / KETI"), (x0 + 57, y0 + 6, "TOL.", "ISO 2768-m (UNO)"),
            (x0 + 112, y0 + 6, "DATE", "2026-10-01"), (x0 + 137, y0 + 6, "STATUS", "RFQ FINAL"),
        ]
        for x, y, k, v in cells:
            t(x, y + 2.6, k, fontsize=3.6, color=GRAY, va="center")
            t(x, y - 1.2, v, fontsize=5.4 if len(str(v)) < 26 else 4.4, va="center", weight="bold" if k in ("PART NO.", "REV") else "normal")

    def text(self, x, y, s, fs=FS, **k): self.ax.text(x, y, s, fontsize=fs, color=k.pop("color", INK), **k)
    def box(self, x, y, w, h, title=None, lines=(), fs=5.6, title_color=BLUE, lh=3.6):
        self.ax.add_patch(Rectangle((x, y), w, h, fill=False, lw=0.3 * PT, ec=INK))
        cy = y + h - 4
        if title: self.ax.text(x + 2.5, cy, title, fontsize=fs + 1.2, weight="bold", color=title_color, va="center"); cy -= lh + 1.2
        for ln in lines:
            col = RED if ln.startswith("!") else INK
            self.ax.text(x + 2.5, cy, ln.lstrip("!"), fontsize=fs, va="center", color=col); cy -= lh
        return cy
    def table(self, x, y, cols, rows, fs=5.0, rh=4.0, head_fc="#e8eef5"):
        """cols: [(title,width)], rows: list of lists. y is top."""
        ax = self.ax; W = sum(w for _, w in cols)
        ax.add_patch(Rectangle((x, y - rh), W, rh, fc=head_fc, ec=INK, lw=0.25 * PT))
        cx = x
        for (tt, w) in cols:
            ax.text(cx + 1.2, y - rh / 2, tt, fontsize=fs, weight="bold", va="center"); cx += w
        for i, r in enumerate(rows):
            yy = y - rh * (i + 2)
            ax.add_patch(Rectangle((x, yy), W, rh, fill=False, ec=INK, lw=0.15 * PT))
            cx = x
            for (tt, w), v in zip(cols, r):
                s = str(v); col = RED if s.startswith("!") else INK
                ax.text(cx + 1.2, yy + rh / 2, s.lstrip("!"), fontsize=fs, va="center", color=col, clip_on=False); cx += w
        cx = x
        for (_, w) in cols[:-1]:
            cx += w; ax.plot([cx, cx], [y, y - rh * (len(rows) + 1)], color=INK, lw=0.15 * PT)
        return y - rh * (len(rows) + 1)
    def image(self, path, x, y, w, h=None):
        import matplotlib.image as mpimg
        im = mpimg.imread(path)
        # crop white
        import numpy as np
        m = (im[:, :, :3].sum(axis=2) < 2.95)
        ys, xs = np.where(m)
        if len(xs): im = im[max(ys.min() - 5, 0):ys.max() + 5, max(xs.min() - 5, 0):xs.max() + 5]
        ih, iw = im.shape[:2]
        if h is None: h = w * ih / iw
        else:
            w2 = h * iw / ih
            if w2 > w: h = w * ih / iw
            else: w = w2
        self.ax.imshow(im, extent=(x, x + w, y, y + h), zorder=1, interpolation="lanczos")
        return w, h
    def save(self, pdf): pdf.savefig(self.fig); plt.close(self.fig)

class View:
    def __init__(self, sh, ox, oy, scale, label=None, lx=None, ly=None):
        self.sh, self.ax, self.ox, self.oy, self.s = sh, sh.ax, ox, oy, scale
        if label: sh.ax.text(lx if lx is not None else ox, ly if ly is not None else oy, label, fontsize=6.5, weight="bold", ha="center", color=INK)
    def P(self, x, y): return (self.ox + x * self.s, self.oy + y * self.s)
    def poly(self, geom, lw=LW_O, color=INK, ls="-", fill=None, z=3):
        gs = geom.geoms if hasattr(geom, "geoms") else [geom]
        for p in gs:
            if isinstance(p, Polygon):
                rings = [p.exterior] + list(p.interiors)
                for r in rings:
                    xs, ys = zip(*[self.P(*c) for c in r.coords])
                    self.ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=z)
                if fill:
                    xs = [self.P(*c) for c in p.exterior.coords]
                    self.ax.add_patch(MPoly(xs, closed=True, fc=fill, ec="none", zorder=z - 1))
            else:
                xs, ys = zip(*[self.P(*c) for c in p.coords]); self.ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=z)
    def line(self, p1, p2, lw=LW_T, color=INK, ls="-", z=3):
        a, b = self.P(*p1), self.P(*p2); self.ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=lw, ls=ls, zorder=z)
    def circle(self, x, y, d, lw=LW_O, color=INK, ls="-", fill=None):
        c = self.P(x, y); self.ax.add_patch(Circle(c, d / 2 * self.s, fill=fill is not None, fc=fill or "none", ec=color, lw=lw, ls=ls, zorder=3))
    def cmark(self, x, y, r=3):
        a = self.P(x, y); rr = r
        self.ax.plot([a[0] - rr, a[0] + rr], [a[1], a[1]], color=GRAY, lw=LW_C, zorder=2)
        self.ax.plot([a[0], a[0]], [a[1] - rr, a[1] + rr], color=GRAY, lw=LW_C, zorder=2)
    def text(self, x, y, s, fs=FS, **k):
        a = self.P(x, y); self.ax.text(a[0], a[1], s, fontsize=fs, zorder=8, **k)
    def tag(self, x, y, s, fs=4.6, color=BLUE):
        a = self.P(x, y)
        self.ax.text(a[0], a[1], s, fontsize=fs, ha="center", va="center", color=color, zorder=9,
                     bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=0.3))
    def _arrow(self, a, b):
        self.ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="<|-|>", lw=LW_T * 0.9, color=INK, mutation_scale=4.5, shrinkA=0, shrinkB=0), zorder=6)
    def dim(self, p1, p2, off, txt=None, fs=5.4, ext=1.5, gap=0.8, orient=None):
        """aligned/linear dim between model pts; off in paper mm (perp, positive = left of p1->p2). orient 'h','v' forces."""
        a, b = self.P(*p1), self.P(*p2)
        if orient == "h": d = (1, 0)
        elif orient == "v": d = (0, 1)
        else:
            L = math.hypot(b[0] - a[0], b[1] - a[1]); d = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
        nrm = (-d[1], d[0])
        # project both to dim line
        base = a
        def proj(p):
            t = (p[0] - base[0]) * d[0] + (p[1] - base[1]) * d[1]
            return (base[0] + t * d[0] + nrm[0] * off, base[1] + t * d[1] + nrm[1] * off)
        da, db = proj(a), proj(b)
        sg = 1 if off >= 0 else -1
        for p, q in ((a, da), (b, db)):
            s = (p[0] + nrm[0] * gap * sg, p[1] + nrm[1] * gap * sg); e = (q[0] + nrm[0] * ext * sg, q[1] + nrm[1] * ext * sg)
            self.ax.plot([s[0], e[0]], [s[1], e[1]], color=INK, lw=LW_C, zorder=5)
        self._arrow(da, db)
        val = math.hypot(db[0] - da[0], db[1] - da[1]) / self.s
        if txt is None: txt = f"{val:.1f}".rstrip("0").rstrip(".")
        m = ((da[0] + db[0]) / 2 + nrm[0] * 1.3 * (1 if off >= 0 else -1) * 0 + nrm[0] * 1.2, (da[1] + db[1]) / 2 + nrm[1] * 1.2)
        ang = math.degrees(math.atan2(d[1], d[0]))
        if ang > 90.1 or ang < -89.9: ang += 180
        self.ax.text(m[0], m[1], txt, fontsize=fs, ha="center", va="center", rotation=ang, zorder=7,
                     bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none"))
    def leader(self, p, txt, dx, dy, fs=5.0, color=INK):
        a = self.P(*p); b = (a[0] + dx, a[1] + dy)
        self.ax.annotate("", xy=a, xytext=b, arrowprops=dict(arrowstyle="-|>", lw=LW_T * 0.9, color=color, mutation_scale=4, shrinkA=0, shrinkB=0), zorder=6)
        e = (b[0] + (6 if dx >= 0 else -6), b[1]); self.ax.plot([b[0], e[0]], [b[1], e[1]], color=color, lw=LW_T * 0.9)
        self.ax.text(e[0] + (0.8 if dx >= 0 else -0.8), e[1], txt, fontsize=fs, ha="left" if dx >= 0 else "right", va="center", color=color, zorder=8,
                     bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none"))
