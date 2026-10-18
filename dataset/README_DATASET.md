# Synthetic Dataset Documentation & Disclaimer

> **IMPORTANT NOTICE:**  
> **All data in this directory is strictly SYNTHETIC and designed solely for hackathon demonstration and academic evaluation.**  
> It does NOT contain real, confidential, or proprietary well logs from ONGC, OIL, or any commercial operator.

---

## 1. Summary of Dataset Contents

- **Total Synthetic Offset Wells:** **500 historical wells** (`dataset/wells.csv`)
- **Total Synthetic Drilling Events:** **1,779 historical operational events** (`dataset/drilling_events.csv`)
- **Geographic Context:** Indian Offshore Basins (Mumbai Offshore, Bassein, Tapti, Daman, Heera, Ratna, Mukta)
- **Data Quality:** 100% complete records, zero missing values, zero duplicate IDs, fully validated foreign key relationships.

---

## 2. File Specifications

### `wells.csv` (500 Records)
Columns:
- `well_id` (str): Unique offset well identifier (e.g., `MO-B-101`, `BS-001`, `TP-023`)
- `field` (str): Oil & Gas field (`Mumbai Offshore`, `Bassein`, `Tapti`, `Daman`, `Heera`, `Ratna`, `Mukta`)
- `formation` (str): Target geological formation (e.g., `Bassein Limestone`, `Daman Sandstone`, `Mukta Shale`, `Panna Formation`)
- `total_depth` (float): Total measured depth in meters ($m$, 1650.0m - 3950.0m)
- `mud_weight` (float): Drilling fluid density in pounds per gallon ($ppg$, 10.2 - 13.7 ppg)
- `pressure` (float): Formation / pore pressure in psi ($psi$, 2350.0 - 6050.0 psi)
- `rop` (float): Rate of penetration in meters per hour ($m/hr$, 5.0 - 26.0 m/hr)
- `wob` (float): Weight on bit in thousands of pounds ($klbs$, 13.0 - 29.0 klbs)
- `torque` (float): Surface drilling torque in kilo foot-pounds ($kft\cdot lb$, 11.0 - 21.0 kft-lb)
- `inclination` (float): Trajectory inclination in degrees ($^\circ$, 6.0° - 46.0°)
- `azimuth` (float): Trajectory azimuth compass heading in degrees ($^\circ$, 50.0° - 330.0°)

### `drilling_events.csv` (1,779 Records)
Columns:
- `event_id` (str): Unique event identifier (`EVT-0001` to `EVT-1779`, including preserved `EVT-1001`)
- `well_id` (str): Valid offset well ID referencing `wells.csv`
- `depth` (float): Specific measured depth where the operational event occurred ($m$, always $< \text{total\_depth}$)
- `event_type` (str): Classification category of the event
- `description` (str): Engineering narrative describing symptoms and circumstances
- `action_taken` (str): Immediate operational mitigation or procedure executed
- `result` (str): Documented operational outcome

---

## 3. Event Type Distribution

Across the 1,779 historical events:
- **No Significant Event:** 447 events (25.1%) — Routine stable drilling, gauge hole, casing cemented to TD
- **Tight Hole / Pack-off:** 343 events (19.3%) — Overpull, cavings, reactive shale swelling
- **High Torque:** 337 events (18.9%) — Stick-slip vibrations, erratic torque spikes, deep abrasive interbeds
- **Wellbore Instability:** 308 events (17.3%) — Splintery/blocky cavings, borehole breakout
- **Lost Circulation:** 165 events (9.3%) — Partial to total losses in cavernous/vuggy carbonates
- **Differential Sticking:** 91 events (5.1%) — High overbalance in permeable inclined sands
- **Gas Kick:** 73 events (4.1%) — Fast drilling breaks and gas influxes in overpressured gas sands
- **Pipe Sticking:** 15 events (0.8%) — Mechanical sticking in dogleg intervals

---

## 4. Reproducibility

The dataset is generated programmatically using a fixed seed (`SEED = 42`) via `scripts/generate_synthetic_data.py`. To regenerate or reseed the dataset:
```bash
python scripts/generate_synthetic_data.py
```
