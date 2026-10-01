import sys, importlib
from matplotlib.backends.backend_pdf import PdfPages
import sheets_a; importlib.reload(sheets_a)
mods = [sheets_a]
try:
    import sheets_b; mods.append(sheets_b)
except ImportError: pass
fns = [sheets_a.sheet_cover, sheets_a.sheet_ga] + (mods[1].SHEETS if len(mods) > 1 else [])
out = sys.argv[1] if len(sys.argv) > 1 else "out/SBOX_REV8_DRAWINGS.pdf"
with PdfPages(out) as pdf:
    for f in fns: f(pdf)
print("pdf ok")
