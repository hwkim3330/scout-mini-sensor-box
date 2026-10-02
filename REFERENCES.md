# References

External material behind design decisions in REV 9, and what each one changes (or doesn't).

## Robot mounting and power

**AgileX SCOUT MINI R&D Kit Pro — user manual** ([PDF](https://static.generation-robots.com/media/scout-mini-pro-user-manual.pdf))
- The manufacturer's own sensor stack: stacked sheet-metal brackets (AGX Xavier → USB hub / USB-CAN / RealSense → voltage converters → lidar on top).
- Rail mounting: four slider nuts, two per rail, four screws. Same 4-point ear-slot method as P01.
- The manual gives no rail pitch, so **HOLD 2 stays open**.
- Power: separate 24→19 V (Xavier) and 24→12 V (lidar, hub, router) converters; the expansion port is limited to 24 V 5 A.
- CAN: USB-CAN at 500 kbps. This design uses CAN Pal on AGX J30 instead, which saves a USB port.

**Jetson AGX Orin DC input range** ([NVIDIA forum](https://forums.developer.nvidia.com/t/jeston-agx-orin-voltage-range/240687))
- The dev kit DC jack accepts 7–20 V. At 19 V the AGX draws about 3.2 A for 60 W, against 5 A at 12 V.
- Added to **HOLD 6** as an alternative: if the existing 24→12 V DC/DC can't do 8 A continuous, feed only the AGX from a separate 24→19 V converter. The 12 V rail then carries only the 5G modem (about 1 A).
- Check this against the carrier board documentation before buying a converter; the source is a forum answer.

**SCOUT MINI SolidWorks model** ([Saibts/AgileX-scout-mini-sw](https://github.com/Saibts/AgileX-scout-mini-sw), MIT)
- An unofficial model made for a ROS 2 simulation. The rails are plain blocks with no slot detail, so it can't settle the rail pitch either.
- The files are SolidWorks-only (`.SLDPRT`). If you open them in SolidWorks, the rail center distance is still only a rough cross-check.
- **HOLD 2 is released only by measuring the real robot or by the WeGo reply.**

## Lidar

**Ouster OS1 Rev7 hardware manual — mounting and thermal** ([docs](https://static.ouster.dev/sensor-docs/hw_user_manual_OS1/hw_common_sections_OS1/os1-overview.html))
- Recommends mounting on 6061 aluminium (167 W/m·K). P05 and P11 are AL6061-T6.
- Base and top should stay within +25 °C of ambient. Performance drops up to 20 % from 52 °C, and the sensor may shut down at 60 °C.
- Use a thermal pad (TIM) if the mounting surface is not flat. P05/P11 contact faces are left bare (no paint), and P11 has a 0.05 flatness callout.
- M3 screws; torque 120–146 cN·m for stainless.

## Thermal: AGX Orin in a closed box

**Orin in a sealed aluminium enclosure** ([MDPI Electronics 2026, 15(11) 2467](https://www.mdpi.com/2079-9292/15/11/2467))
- 190 × 154 × 60 mm aluminium box at MAXN, −20 to +40 °C ambient.
- A thermostat fan that turns on at 30 °C inside cut the inside-outside difference from about 30 °C to 5–7 °C.
- A real inference load (19 W) settled near 75 °C. A synthetic 36 W stress load throttled at 40 °C ambient.
- **Not in REV 9.** Candidate for REV 10: replace one exhaust vent (C1 or C6) with a 40 or 60 mm fan cutout plus a thermostat. REV 9 is the RFQ-final drawing set, so the change waits for the next revision. If the parts are already ordered, add a bolt-on fan bracket or post-machine the cutout instead.

## 360° camera layout (comparison only)

- [Stereolabs Robotics 360° Perception Kit](https://www.stereolabs.com/store/products/robotics-360-perception-kit): AGX Orin + 4 × ZED X, a commercial 360° kit.
- [360° surround view on AGX Orin](https://info-kevinjackson.medium.com/360-surround-view-camera-solution-using-nvidia-jetson-agx-orin-31d5c9511b3e): software side (stitching).
