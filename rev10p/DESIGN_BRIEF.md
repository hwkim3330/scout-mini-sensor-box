# REV10-P: 3D-printed variant (design brief)

> **2026-10-27 update:** the first version is built as **flat panels assembled into a hexagon** in PLA, not a round one-piece PETG body. The cameras and rails haven't been measured yet, and a one-piece body would be a 15–20 hour print where any failure loses the whole thing. Flat panels print in about 2 hours each and only the affected part needs reprinting. See [README.md](README.md); the table below is the original brief.

REV9 (the hexagonal sheet-metal box in this repo) stays as it is. REV10-P is the same sensor box redesigned to be
printed on a **Bambu Lab A1** (256 x 256 x 256 mm bed) in **PETG**. This file is the hand-over: decisions already made,
the hardware, what is still unknown, and how to slice for the A1 from Linux.

## Decisions (agreed)

| Topic | Decision | Why |
|---|---|---|
| Shape | **Round** (cylinder), not hexagonal | On a 256 mm bed a circle gives ~21 % more floor area than the hexagon that fits; no seams or corners; flat camera faces come from pads (below) |
| Pieces | **Three**: (1) one-piece body = cup with integral floor, (2) lid, (3) rail coupling plate | Splitting the walls into panels was rejected as too weak |
| Body | Diameter as large as the bed allows with margin (about **245 mm**), printed floor-down, no supports; walls 3-4 mm, inner ribs, fillets | Fits the A1; strongest print orientation |
| Lid | Carries the lidar; ribbed so the lidar load goes into the walls; skirt overlapping the wall by 3-5 mm; groove for a printed **TPU gasket** | Rain runs off instead of into the seam |
| Rail plate | Bolts to the robot's top rails and the body bolts to it with brass heat-set inserts (M3/M4) | Rail pitch can change without reprinting the body |
| Cameras | Six flat pads on the outside of the cylinder, 60° apart; each pad has a window and 4 x M3 inserts for a **small replaceable camera plate** (separate STL) | Camera housing dimensions are not known yet: only the small plate is reprinted when they are measured |
| Material | **PETG** for all structural parts (PLA softens at the temperatures a 60 W computer makes inside); TPU for the gasket | |
| Thermal | Intake low, exhaust high (louvres or labyrinth); optional 80/92 mm fan mount | The compute module draws up to 60 W |
| Cables | Gland holes (PG7 / PG9) | |

## Contents (for clearance checks)

| Item | Size | Status |
|---|---|---|
| Lidar (Ouster OS1) | Ø85 x 73.5 mm, on the lid | Mounting pattern is a HOLD in REV9 (`geom.py`) |
| Compute (Jetson AGX Orin dev kit) | 110 x 110 x 71.65 mm | |
| Cameras (Arducam B0473 kit, 6 x IMX477) | Board 25 x 24 mm in a housing; M12 lens 2.75 mm, 120° HFOV; 30 cm FPC | **Housing size, screw pitch and lens bore: to be measured** — keep the camera plate parametric with clearly marked placeholders |
| Power / CAN board | see REV9 P10 electrical plate | |

Model the contents as boxes/cylinders and check clearances in code before exporting.

## Deliverables expected

- `rev10p/` CadQuery source (parametric), STEP + STL per part, PNG renders.
- A1 print files: sliced `.gcode.3mf` per part (PETG), with slicer time and grams in a table.
- `rev10p/README.md`: parts, print settings, insert sizes, assembly order, what is HOLD.

## Slicing for the A1 from the command line (Linux, Bambu Studio AppImage)

The CLI slicer refuses user presets whose `inherits` it cannot resolve ("process not compatible with printer").
Flatten them first with `tools/flatten_bambu_preset.py` against the AppImage's bundled profiles:

```bash
P=<extracted AppImage>/resources/profiles/BBL      # ./BambuStudio*.AppImage --appimage-extract
python3 tools/flatten_bambu_preset.py $P "$P/machine/Bambu Lab A1 0.4 nozzle.json" machine_A1.json
python3 tools/flatten_bambu_preset.py $P my_process.json process.json        # a user process preset, or a system one
python3 tools/flatten_bambu_preset.py $P my_petg.json filament.json
# the A1 ships with a Textured PEI plate: set "curr_bed_type": "Textured PEI Plate" in process.json
env -u WAYLAND_DISPLAY XDG_SESSION_TYPE=x11 xvfb-run -a bambu-studio --slice 0 --arrange 1 \
  --load-settings "machine_A1.json;process.json" --load-filaments filament.json \
  --export-3mf part.gcode.3mf part.stl
unzip -p part.gcode.3mf Metadata/plate_1.gcode | grep -m2 -E "total estimated time|total filament weight"
```

Copy the `.gcode.3mf` to the printer's microSD and print from the printer's screen (Print Files).
