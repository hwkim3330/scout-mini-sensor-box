# SCOUT MINI OMNI Sensor / Compute Enclosure (KETI)

Single-source parametric CAD for the hex sensor box (REV 9, RFQ final).

- `geom.py` – all geometry (flat patterns, holes, PEM, new parts P10/P11)
- `model3d.py` – CadQuery 3D model → `out/step/*.step`
- `dxfout.py` – laser DXF → `out/dxf/*.dxf`
- `drc.py` – design-rule check (PEM edge/bend distance, hole spacing)
- `drawlib.py`, `sheets_a.py`, `sheets_b.py`, `build_pdf.py` – A3 drawing set → `out/SBOX_REV9_DRAWINGS.pdf`
- `bom.py` – BOM/RFQ workbook → `out/SBOX_REV9_BOM.xlsx`
- `shoot.py` + `web/render.html` – three.js renders

Rebuild: `python3 model3d.py && python3 shoot.py && python3 dxfout.py && python3 drc.py && python3 build_pdf.py out/SBOX_REV9_DRAWINGS.pdf && python3 bom.py`
