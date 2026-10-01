import pickle, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
tess = pickle.load(open("out/tess.pkl", "rb"))
def render(fn, elev=24, azim=-60, skip=(), explode=None, size=(10, 8)):
    fig = plt.figure(figsize=size); ax = fig.add_subplot(111, projection="3d")
    L = np.array([0.4, -0.5, 0.8]); L = L / np.linalg.norm(L)
    for k, (vs, fs, c) in tess.items():
        if any(s in k for s in skip): continue
        V = np.array(vs)
        if explode and k in explode: V = V + np.array(explode[k])
        tri = V[np.array(fs)]
        nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); nn = np.linalg.norm(nrm, axis=1, keepdims=True); nn[nn == 0] = 1
        sh = np.clip(np.abs((nrm / nn) @ L), 0, 1) * 0.6 + 0.4
        cols = np.clip(np.array(c)[None, :] * sh[:, None], 0, 1)
        pc = Poly3DCollection(tri, facecolors=cols, edgecolors="none", linewidths=0)
        ax.add_collection3d(pc)
    ax.set_xlim(-190, 190); ax.set_ylim(-190, 190); ax.set_zlim(-60, 250)
    ax.set_box_aspect((380, 380, 310)); ax.view_init(elev, azim); ax.set_axis_off()
    plt.tight_layout(); plt.savefig(fn, dpi=130, transparent=False, facecolor="white"); plt.close()
if __name__ == "__main__":
    render("out/iso_front.png", 22, -60)
    render("out/iso_rear.png", 22, 120)
    render("out/iso_open.png", 35, -50, explode={"P04_TOP_COVER": (0, 0, 130), "P05_OS1_PLATE": (0, 0, 130), "OUSTER_OS1(dummy)": (0, 0, 130)})
