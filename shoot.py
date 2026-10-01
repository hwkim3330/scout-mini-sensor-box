import json, pickle, sys, urllib.parse, subprocess, time, os
from playwright.sync_api import sync_playwright
tess = pickle.load(open("out/tess.pkl", "rb"))
json.dump({k: {"v": [c for p in vs for c in p], "f": [i for t in fs for i in t], "c": c} for k, (vs, fs, c) in tess.items()}, open("web/mesh.json", "w"))
VIEWS = {
 "iso_front": dict(cam=[600, 900, 600]),
 "iso_rear": dict(cam=[-500, -900, 600]),
 "iso_open": dict(cam=[650, 800, 900], scale=290, target=[0,0,150], explode={"P04_TOP_COVER":[0,0,150],"P05_OS1_PLATE":[0,0,150],"P11_OS1_RISER":[0,0,150],"OUSTER_OS1(dummy)":[0,0,150]}),
 "iso_inside": dict(cam=[500, 700, 1000], skip=["P04","P05","P11","OUSTER"], target=[0,0,60]),
 "top": dict(cam=[0, 0, 1000], skip=["P04","P05","OUSTER"], target=[0,0,0], scale=200),
}
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8765"], cwd="web", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 1400, "height": 1000})
    for n, v in VIEWS.items():
        pg.goto("http://localhost:8765/render.html#" + urllib.parse.quote(json.dumps(v)))
        pg.reload(); pg.wait_for_function("window.DONE===true", timeout=60000)
        pg.screenshot(path=f"out/{n}.png")
    b.close()
srv.terminate(); print("done")
