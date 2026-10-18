"""
Synthetic Dataset Generator for AI-Powered Offset Well Platform.
Generates:
- Exactly 500 historical offset wells (dataset/wells.csv)
- At least 1500 realistic historical drilling events (dataset/drilling_events.csv)

All data is strictly SYNTHETIC for hackathon demonstration.
Reproducible with a fixed random seed (42).
Preserves realistic engineering relationships between fields, formations,
drilling parameters, depth intervals, and event types.
"""

import os
import sys
import random
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set fixed random seeds for strict reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Geological Archetypes across the 7 Indian Offshore Fields
# Each archetype defines parameter distributions and primary event affinities
FIELD_ARCHETYPES = [
    # 1. Mumbai Offshore (Target: 95 wells)
    {
        "field": "Mumbai Offshore",
        "formation": "Bassein Limestone",
        "count": 35,
        "td_range": (3350.0, 3600.0),
        "mw_range": (11.0, 11.6),
        "press_range": (4100.0, 4450.0),
        "rop_range": (10.5, 14.0),
        "wob_range": (15.0, 18.5),
        "torque_range": (12.5, 15.0),
        "inc_range": (10.0, 22.0),
        "azi_range": (195.0, 230.0),
        "primary_events": ["Lost Circulation", "Differential Sticking", "No Significant Event"]
    },
    {
        "field": "Mumbai Offshore",
        "formation": "Mukta Shale",
        "count": 25,
        "td_range": (2350.0, 2650.0),
        "mw_range": (10.4, 11.1),
        "press_range": (3000.0, 3350.0),
        "rop_range": (7.0, 10.0),
        "wob_range": (13.0, 16.0),
        "torque_range": (16.5, 20.5),
        "inc_range": (24.0, 38.0),
        "azi_range": (175.0, 200.0),
        "primary_events": ["Tight Hole / Pack-off", "Wellbore Instability", "High Torque"]
    },
    {
        "field": "Mumbai Offshore",
        "formation": "Panna Formation",
        "count": 20,
        "td_range": (3650.0, 3950.0),
        "mw_range": (12.1, 12.7),
        "press_range": (4950.0, 5300.0),
        "rop_range": (12.5, 15.5),
        "wob_range": (20.0, 24.0),
        "torque_range": (17.0, 20.0),
        "inc_range": (18.0, 28.0),
        "azi_range": (85.0, 115.0),
        "primary_events": ["High Torque", "Pipe Sticking", "No Significant Event"]
    },
    {
        "field": "Mumbai Offshore",
        "formation": "Bandra Clastics",
        "count": 15,
        "td_range": (1800.0, 2250.0),
        "mw_range": (10.2, 10.7),
        "press_range": (2400.0, 2850.0),
        "rop_range": (14.0, 18.0),
        "wob_range": (14.0, 17.5),
        "torque_range": (11.0, 13.5),
        "inc_range": (12.0, 25.0),
        "azi_range": (160.0, 190.0),
        "primary_events": ["Wellbore Instability", "Tight Hole / Pack-off", "No Significant Event"]
    },

    # 2. Bassein Field (Target: 80 wells)
    {
        "field": "Bassein",
        "formation": "Bassein Limestone",
        "count": 40,
        "td_range": (3250.0, 3550.0),
        "mw_range": (10.7, 11.3),
        "press_range": (3850.0, 4150.0),
        "rop_range": (11.5, 14.5),
        "wob_range": (14.5, 17.5),
        "torque_range": (12.0, 14.5),
        "inc_range": (8.0, 20.0),
        "azi_range": (195.0, 225.0),
        "primary_events": ["Lost Circulation", "Differential Sticking", "No Significant Event"]
    },
    {
        "field": "Bassein",
        "formation": "Panna Sandstone",
        "count": 22,
        "td_range": (3500.0, 3800.0),
        "mw_range": (11.8, 12.5),
        "press_range": (4750.0, 5100.0),
        "rop_range": (13.5, 17.0),
        "wob_range": (18.5, 22.5),
        "torque_range": (15.5, 18.5),
        "inc_range": (20.0, 30.0),
        "azi_range": (70.0, 95.0),
        "primary_events": ["High Torque", "Differential Sticking", "No Significant Event"]
    },
    {
        "field": "Bassein",
        "formation": "Mukta Shale",
        "count": 18,
        "td_range": (2300.0, 2600.0),
        "mw_range": (10.3, 10.9),
        "press_range": (2950.0, 3250.0),
        "rop_range": (8.0, 11.0),
        "wob_range": (13.0, 15.5),
        "torque_range": (15.5, 18.5),
        "inc_range": (22.0, 32.0),
        "azi_range": (165.0, 190.0),
        "primary_events": ["Tight Hole / Pack-off", "Wellbore Instability", "No Significant Event"]
    },

    # 3. Tapti Field (Target: 75 wells)
    {
        "field": "Tapti",
        "formation": "Daman Sandstone",
        "count": 35,
        "td_range": (2900.0, 3200.0),
        "mw_range": (12.6, 13.3),
        "press_range": (5300.0, 5750.0),
        "rop_range": (19.0, 24.5),
        "wob_range": (20.0, 23.5),
        "torque_range": (14.5, 17.0),
        "inc_range": (32.0, 42.0),
        "azi_range": (135.0, 155.0),
        "primary_events": ["Gas Kick", "High Torque", "Differential Sticking"]
    },
    {
        "field": "Tapti",
        "formation": "Mid-Tapti Gas Sand",
        "count": 22,
        "td_range": (2750.0, 3000.0),
        "mw_range": (12.4, 13.0),
        "press_range": (5100.0, 5450.0),
        "rop_range": (18.0, 22.0),
        "wob_range": (19.5, 22.5),
        "torque_range": (14.0, 16.5),
        "inc_range": (30.0, 38.0),
        "azi_range": (130.0, 150.0),
        "primary_events": ["Gas Kick", "Differential Sticking", "No Significant Event"]
    },
    {
        "field": "Tapti",
        "formation": "Mahuva Formation",
        "count": 18,
        "td_range": (2000.0, 2300.0),
        "mw_range": (11.2, 11.8),
        "press_range": (3500.0, 3850.0),
        "rop_range": (14.5, 18.0),
        "wob_range": (16.5, 19.5),
        "torque_range": (12.0, 14.5),
        "inc_range": (15.0, 24.0),
        "azi_range": (120.0, 145.0),
        "primary_events": ["Wellbore Instability", "High Torque", "No Significant Event"]
    },

    # 4. Daman Field (Target: 70 wells)
    {
        "field": "Daman",
        "formation": "Daman Sandstone",
        "count": 35,
        "td_range": (3050.0, 3350.0),
        "mw_range": (13.0, 13.7),
        "press_range": (5650.0, 6050.0),
        "rop_range": (21.5, 26.0),
        "wob_range": (22.0, 25.0),
        "torque_range": (16.0, 18.5),
        "inc_range": (38.0, 46.0),
        "azi_range": (145.0, 160.0),
        "primary_events": ["Gas Kick", "High Torque", "Pipe Sticking"]
    },
    {
        "field": "Daman",
        "formation": "Mahim Clastics",
        "count": 20,
        "td_range": (1650.0, 1950.0),
        "mw_range": (10.2, 10.7),
        "press_range": (2350.0, 2700.0),
        "rop_range": (5.0, 8.0),
        "wob_range": (24.0, 29.0),
        "torque_range": (11.5, 13.5),
        "inc_range": (6.0, 15.0),
        "azi_range": (50.0, 80.0),
        "primary_events": ["Tight Hole / Pack-off", "Wellbore Instability", "High Torque"]
    },
    {
        "field": "Daman",
        "formation": "Navsari Shale",
        "count": 15,
        "td_range": (2250.0, 2600.0),
        "mw_range": (10.8, 11.4),
        "press_range": (3250.0, 3650.0),
        "rop_range": (8.5, 12.0),
        "wob_range": (14.0, 17.5),
        "torque_range": (15.0, 18.0),
        "inc_range": (25.0, 35.0),
        "azi_range": (135.0, 165.0),
        "primary_events": ["Tight Hole / Pack-off", "Wellbore Instability", "No Significant Event"]
    },

    # 5. Heera Field (Target: 65 wells)
    {
        "field": "Heera",
        "formation": "Heera Carbonate",
        "count": 35,
        "td_range": (2250.0, 2550.0),
        "mw_range": (10.6, 11.2),
        "press_range": (3150.0, 3500.0),
        "rop_range": (13.0, 16.5),
        "wob_range": (15.0, 18.0),
        "torque_range": (11.5, 14.0),
        "inc_range": (16.0, 26.0),
        "azi_range": (300.0, 330.0),
        "primary_events": ["Lost Circulation", "Differential Sticking", "No Significant Event"]
    },
    {
        "field": "Heera",
        "formation": "Bandra Shale",
        "count": 20,
        "td_range": (2050.0, 2350.0),
        "mw_range": (10.5, 11.1),
        "press_range": (2850.0, 3200.0),
        "rop_range": (6.5, 9.5),
        "wob_range": (13.5, 16.5),
        "torque_range": (17.5, 21.0),
        "inc_range": (25.0, 35.0),
        "azi_range": (280.0, 310.0),
        "primary_events": ["Tight Hole / Pack-off", "Wellbore Instability", "High Torque"]
    },
    {
        "field": "Heera",
        "formation": "Bassein Deep",
        "count": 10,
        "td_range": (3150.0, 3450.0),
        "mw_range": (11.1, 11.7),
        "press_range": (4050.0, 4350.0),
        "rop_range": (11.0, 13.5),
        "wob_range": (16.0, 19.0),
        "torque_range": (13.0, 15.5),
        "inc_range": (18.0, 28.0),
        "azi_range": (290.0, 320.0),
        "primary_events": ["Lost Circulation", "High Torque", "No Significant Event"]
    },

    # 6. Ratna Field (Target: 60 wells)
    {
        "field": "Ratna",
        "formation": "Ratna Limestone",
        "count": 30,
        "td_range": (2500.0, 2800.0),
        "mw_range": (11.7, 12.3),
        "press_range": (3450.0, 3750.0),
        "rop_range": (14.0, 17.0),
        "wob_range": (17.0, 20.0),
        "torque_range": (13.5, 16.0),
        "inc_range": (30.0, 42.0),
        "azi_range": (210.0, 240.0),
        "primary_events": ["Differential Sticking", "Lost Circulation", "No Significant Event"]
    },
    {
        "field": "Ratna",
        "formation": "Chattrabuj Sand",
        "count": 18,
        "td_range": (2350.0, 2650.0),
        "mw_range": (12.0, 12.6),
        "press_range": (3300.0, 3600.0),
        "rop_range": (16.0, 19.5),
        "wob_range": (18.0, 21.0),
        "torque_range": (14.5, 17.0),
        "inc_range": (35.0, 45.0),
        "azi_range": (225.0, 250.0),
        "primary_events": ["Differential Sticking", "Pipe Sticking", "High Torque"]
    },
    {
        "field": "Ratna",
        "formation": "Panna Shale",
        "count": 12,
        "td_range": (2800.0, 3150.0),
        "mw_range": (11.4, 12.0),
        "press_range": (3850.0, 4250.0),
        "rop_range": (9.0, 12.5),
        "wob_range": (15.5, 18.5),
        "torque_range": (16.0, 19.0),
        "inc_range": (26.0, 36.0),
        "azi_range": (205.0, 235.0),
        "primary_events": ["Tight Hole / Pack-off", "Wellbore Instability", "No Significant Event"]
    },

    # 7. Mukta Field (Target: 55 wells)
    {
        "field": "Mukta",
        "formation": "Mukta Shale",
        "count": 25,
        "td_range": (2400.0, 2700.0),
        "mw_range": (10.6, 11.2),
        "press_range": (3100.0, 3400.0),
        "rop_range": (7.0, 9.8),
        "wob_range": (13.5, 16.5),
        "torque_range": (17.5, 21.0),
        "inc_range": (28.0, 38.0),
        "azi_range": (175.0, 198.0),
        "primary_events": ["Tight Hole / Pack-off", "Wellbore Instability", "High Torque"]
    },
    {
        "field": "Mukta",
        "formation": "Mukta Carbonate",
        "count": 18,
        "td_range": (2600.0, 2900.0),
        "mw_range": (10.9, 11.5),
        "press_range": (3400.0, 3750.0),
        "rop_range": (11.0, 14.5),
        "wob_range": (15.5, 18.5),
        "torque_range": (13.0, 15.5),
        "inc_range": (20.0, 30.0),
        "azi_range": (160.0, 185.0),
        "primary_events": ["Lost Circulation", "Differential Sticking", "No Significant Event"]
    },
    {
        "field": "Mukta",
        "formation": "Panna Formation",
        "count": 12,
        "td_range": (3500.0, 3850.0),
        "mw_range": (12.0, 12.6),
        "press_range": (4850.0, 5250.0),
        "rop_range": (12.5, 15.5),
        "wob_range": (19.5, 23.0),
        "torque_range": (16.5, 19.5),
        "inc_range": (18.0, 28.0),
        "azi_range": (90.0, 115.0),
        "primary_events": ["High Torque", "Pipe Sticking", "No Significant Event"]
    }
]

# Total wells sanity verification:
TOTAL_TARGET_WELLS = sum(arch["count"] for arch in FIELD_ARCHETYPES)
assert TOTAL_TARGET_WELLS == 500, f"Expected 500 wells, got {TOTAL_TARGET_WELLS}"

# Narrative Templates by Event Type for authentic domain engineering records
EVENT_TEMPLATES = {
    "Lost Circulation": [
        (
            "Encountered vuggy porosity and micro-fractures in {formation}. Dynamic mud losses observed at {loss_rate} bbl/hr with {mw} ppg mud.",
            "Bit pulled 30m off bottom. Mixed and spotted {pill_vol} bbl engineered LCM pill ({lcm_type}). Allowed {soak} hrs soak time at reduced circulating rate.",
            "Mud losses stabilized to under {final_loss} bbl/hr. Resumed controlled drilling with managed ECD without further mud loss."
        ),
        (
            "Partial mud loss of {loss_rate} bbl/hr initiated upon penetrating cavernous carbonate interval in {field}. Surface pit volume dropped {loss_pit} bbl in 30 minutes.",
            "Reduced annular flow rate from {gpm1} gpm to {gpm2} gpm to lower ECD. Pumped {pill_vol} bbl bridging pill with calibrated calcium carbonate and cellulosic fiber.",
            "Returns restored to 100%. Continued drilling section to planned casing point without requiring cement plug."
        ),
        (
            "Severe dynamic losses ({loss_rate} bbl/hr) upon crossing sub-seismic fault plane in {formation} at {depth}m.",
            "Filled annulus with treated fluid immediately. Squeezed {pill_vol} bbl thixotropic high-fluid-loss polymer LCM blend followed by hesitating squeeze pressure.",
            "Loss zone successfully sealed. Pressure integrity test verified formation LOT equivalent to {lot} ppg."
        ),
        (
            "Total loss of returns while drilling porous carbonate reef facies with {mw} ppg mud; pit level alarm activated.",
            "Shut down pumps and staged 45 bbl coarse mica and nut-plug blend pill. Waited on crosslinking reaction for 3 hours.",
            "Regained full mud returns. Maintained fluid density within strict margin and resumed drilling."
        )
    ],

    "Gas Kick": [
        (
            "Fast drilling break from {rop1} m/hr to {rop2} m/hr upon entering overpressured {formation}. Active pit gain of {pit_gain} bbl detected with positive flow check.",
            "Executed hard shut-in using annular BOP. Recorded SIDPP = {sidpp} psi, SICP = {sicp} psi. Circulated kill weight mud ({kill_mw} ppg) using Wait & Weight method.",
            "Gas influx safely circulated out through mud-gas separator. Zero residual gas observed; resumed drilling with weighted mud."
        ),
        (
            "Connection gas surged to {gas_pct}% with {pit_gain} bbl active pit gain in {field} gas sand at {depth}m.",
            "Spaced out and closed pipe rams. Executed Drillers Method across two full circulations, increasing mud density from {mw} to {kill_mw} ppg.",
            "Background gas normalized to 1.5%. Well confirmed dead on static flow check; proceeded with drilling."
        ),
        (
            "Pore pressure ramp in overpressured {formation} resulted in {pit_gain} bbl kick while drilling with {mw} ppg fluid.",
            "Shut in on annular preventer. SIDPP stabilized at {sidpp} psi. Prepared and displaced hole with {kill_mw} ppg kill fluid via rig choke manifold.",
            "Well stabilized with zero surface pressure. Maintained planned trip margin to section TD."
        )
    ],

    "Tight Hole / Pack-off": [
        (
            "Overpull of {overpull} klbs encountered while pulling BHA through reactive {formation}. Splintery shale cavings observed across shale shakers.",
            "Washed down tight interval and reamed with elevated flow rate ({gpm1} gpm). Pumped tandem 40 bbl low-vis/high-vis sweep and added 3.5% polyglycol shale inhibitor.",
            "Shale spalling arrested; drag eliminated on subsequent wiper trip. Casing run to planned setting depth without obstruction."
        ),
        (
            "Rotational torque surged erratically from {torque1} to {torque2} kft-lb with 600 psi standpipe pressure rise, indicating imminent pack-off in {formation}.",
            "Picked up string immediately off bottom, rotated slowly at 35 RPM, and worked drillstring vertically while circulating weighted high-viscosity pill.",
            "Standpipe pressure normalized and annular pack-off cleared. Increased mud weight by 0.3 ppg to provide mechanical borehole support."
        ),
        (
            "Observed {overpull} klbs drag and tight spots on every stand while tripping out of laminated {formation} at {depth}m.",
            "Back-reamed interval using roller reamer BHA. Raised KCl concentration to 7% and adjusted low-shear yield point (LSYP) to 15 lb/100ft2.",
            "Hole condition improved significantly. Tripping speeds returned to normal baseline without drag."
        )
    ],

    "Differential Sticking": [
        (
            "Drillstring became differentially stuck against permeable wall cake in {formation} during directional survey with {overbalance} psi overbalance.",
            "Spotted {pill_vol} bbl ester-based pipe-freeing soak pill around BHA. Applied {jar_force} klbs downward jar impact and 10 kft-lb left-hand torque for {soak} hours.",
            "Drillpipe freed after {soak} hrs of soaking. Conditioned mud filter cake to lower API fluid loss from 8.2 to 3.8 cc/30min."
        ),
        (
            "Static drillstring stuck in permeable {formation} after 20-minute connection delay in {inc}° inclined section.",
            "Displaced {pill_vol} bbl surfactant release pill across drill collars. Reduced hydrostatic pressure within safe kick margin while cocking mechanical jars.",
            "String jarred free on third cycle. Added solid graphite lubricants to reduce wall-cake friction factor from 0.28 to 0.14."
        ),
        (
            "High overbalance ({overbalance} psi) and 35° inclination caused drill collars to stick in porous {formation} sand.",
            "Immediately pumped specialized lubricant freeing pill and applied maximum allowable downward jarring.",
            "Drillstring freed within 2.5 hours. Maintained string rotation during all subsequent directional surveys."
        )
    ],

    "High Torque": [
        (
            "Severe torsional stick-slip vibrations (severity level 8, delta torque +/- {delta_t} kft-lb) while drilling abrasive section in {formation}.",
            "Reduced WOB by 4 klbs, increased surface RPM from 90 to 135, and engaged top drive automated soft torque vibration dampener.",
            "Stick-slip vibrations dropped to acceptable level 1. Resumed smooth penetration, extending PDC cutter life by 45 hours."
        ),
        (
            "Torque oscillations exceeded {torque2} kft-lb in high angle ({inc}°) section in {field} at {depth}m.",
            "Pumped 30 bbl high-lubricity synthetic bead sweep pill and reduced rotary speed to 85 RPM.",
            "Torque smoothed to 13.0 kft-lb; prevented mechanical sticking in directional build section."
        ),
        (
            "Downhole torsional vibration causing MWD telemetry decoding errors in hard interbeds of {formation}.",
            "Trimmed WOB to {wob1} klbs, optimized flow rate for mud motor, and recalibrated rotary dampener.",
            "Torsional chatter mitigated; MWD telemetry restored with continuous directional surveys."
        )
    ],

    "Wellbore Instability": [
        (
            "Large blocky cavings over shaker screens in {formation} with {overpull} klbs drag on connections due to stressed shale failure.",
            "Circulated hole clean for 1.5 bottom-up cycles. Conditioned mud system with asphaltic fluid loss additive to seal micro-fractures in shale.",
            "Caving volume dropped by 85%. Caliper log subsequently confirmed gauge hole with minimal washouts."
        ),
        (
            "Shale sloughing and borehole enlargement detected by LWD caliper log in {formation} interval ({depth}m).",
            "Raised mud density by 0.3 ppg to increase borehole confining pressure and optimized rheology for enhanced cutting transport.",
            "Wellbore stabilized; hole remained clean during subsequent casing deployment."
        ),
        (
            "Borehole breakout and cavings observed after prolonged open-hole exposure in {field} reactive shale.",
            "Pumped high-viscosity pill sweep and treated active system with 4% potassium silicate inhibitor.",
            "Hole cleaned effectively and wellbore stability restored through to casing depth."
        )
    ],

    "Pipe Sticking": [
        (
            "Mechanical pipe sticking occurred while slide drilling through dogleg interval in {formation} at {depth}m.",
            "Applied maximum allowable upward jarring ({jar_force} klbs) while working drillstring with alternating torque.",
            "Drillstring freed on fourth jar blow. Performed wiper trip with spiral stabilizer to remove dogleg ledge."
        ),
        (
            "Drillstring mechanically held while reaming swollen shale section in {field}; rotation stalled.",
            "Cycled hydraulic jars downwards and spotted high-lubricity penetrating wash pill across BHA.",
            "Pipe freed successfully within 45 minutes; resumed drilling with optimized reamer gauge."
        )
    ],

    "No Significant Event": [
        (
            "Routinely drilled {formation} section from {d_start}m to {depth}m with stable drilling parameters and gauge hole.",
            "Conducted scheduled wiper trip to previous casing shoe. Circulated bottoms-up clean and performed directional gyro survey.",
            "Section reached planned casing depth on schedule. Casing run and cemented smoothly with full returns."
        ),
        (
            "Smooth penetration through {formation} with {mw} ppg mud. Normal background gas (under 1.2%) and minimal connection drag.",
            "Maintained standard drilling parameters: {wob1} klbs WOB, {rop1} m/hr ROP, and 120 RPM surface rotation.",
            "Target interval drilled according to drilling program with zero NPT (Non-Productive Time)."
        ),
        (
            "Executed planned 12-1/4 inch hole section in {field} {formation} without operational anomalies.",
            "Recorded routine directional survey data and verified mud rheology parameters at flowline.",
            "Hole condition verified gauge and stable by wireline caliper log."
        )
    ]
}

def generate_wells_and_events():
    """Generate exactly 500 wells and 1500+ events with realistic relationships."""
    wells = []
    events = []

    well_counter = 1
    event_counter = 1

    field_prefixes = {
        "Mumbai Offshore": "MO",
        "Bassein": "BS",
        "Tapti": "TP",
        "Daman": "DM",
        "Heera": "HR",
        "Ratna": "RT",
        "Mukta": "MK"
    }

    # Ensure well #1 is exactly MO-B-101 to maintain 100% test compatibility with test_backend.py
    seed_mo_b101 = {
        "well_id": "MO-B-101",
        "field": "Mumbai Offshore",
        "formation": "Bassein Limestone",
        "total_depth": 3450.0,
        "mud_weight": 11.2,
        "pressure": 4250.0,
        "rop": 12.5,
        "wob": 16.0,
        "torque": 13.5,
        "inclination": 14.5,
        "azimuth": 210.0
    }
    wells.append(seed_mo_b101)

    # Track wells count per archetype
    field_counts = {arch["field"]: 0 for arch in FIELD_ARCHETYPES}
    field_counts["Mumbai Offshore"] = 1  # MO-B-101 counted

    for arch_idx, arch in enumerate(FIELD_ARCHETYPES):
        field = arch["field"]
        formation = arch["formation"]
        target_count = arch["count"]

        # Deduct 1 for Mumbai Offshore Bassein Limestone because MO-B-101 is already created
        if arch_idx == 0:
            target_count -= 1

        prefix = field_prefixes[field]

        for _ in range(target_count):
            field_counts[field] += 1
            well_num = field_counts[field]
            well_id = f"{prefix}-{well_num:03d}"

            # Make sure no collision with MO-B-101
            if well_id == "MO-B-101":
                well_id = f"{prefix}-099"

            # Sample drilling parameters within realistic distributions
            td = round(float(np.random.uniform(arch["td_range"][0], arch["td_range"][1])), 1)
            mw = round(float(np.random.uniform(arch["mw_range"][0], arch["mw_range"][1])), 1)
            press = round(float(np.random.uniform(arch["press_range"][0], arch["press_range"][1])), 1)
            rop = round(float(np.random.uniform(arch["rop_range"][0], arch["rop_range"][1])), 1)
            wob = round(float(np.random.uniform(arch["wob_range"][0], arch["wob_range"][1])), 1)
            torque = round(float(np.random.uniform(arch["torque_range"][0], arch["torque_range"][1])), 1)
            inc = round(float(np.random.uniform(arch["inc_range"][0], arch["inc_range"][1])), 1)
            azi = round(float(np.random.uniform(arch["azi_range"][0], arch["azi_range"][1])), 1)

            well_record = {
                "well_id": well_id,
                "field": field,
                "formation": formation,
                "total_depth": td,
                "mud_weight": mw,
                "pressure": press,
                "rop": rop,
                "wob": wob,
                "torque": torque,
                "inclination": inc,
                "azimuth": azi
            }
            wells.append(well_record)

    assert len(wells) == 500, f"Expected exactly 500 wells, got {len(wells)}"

    # Generate events for each well
    # Average ~3.4 events per well -> ~1700 events
    for well in wells:
        well_id = well["well_id"]
        td = well["total_depth"]
        field = well["field"]
        formation = well["formation"]
        mw = well["mud_weight"]
        press = well["pressure"]
        rop = well["rop"]
        wob = well["wob"]
        torque = well["torque"]
        inc = well["inclination"]

        # If it's MO-B-101, ensure EVT-1001 is included for test compatibility
        is_seed_well = (well_id == "MO-B-101")

        # Decide number of events for this well (3 to 5 events)
        num_events = random.choices([3, 4, 5], weights=[0.55, 0.35, 0.10])[0]

        # Depths: spaced across well sections, strictly less than total depth
        # Section 1: shallow/intermediate (35% to 60% of TD)
        # Section 2: intermediate build (60% to 80% of TD)
        # Section 3: reservoir / near TD (80% to 97% of TD)
        candidate_depths = [
            round(float(td * np.random.uniform(0.35, 0.58)), 1),
            round(float(td * np.random.uniform(0.59, 0.78)), 1),
            round(float(td * np.random.uniform(0.79, 0.96)), 1),
        ]
        if num_events >= 4:
            candidate_depths.append(round(float(td * np.random.uniform(0.85, 0.98)), 1))
        if num_events >= 5:
            candidate_depths.append(round(float(td * np.random.uniform(0.45, 0.70)), 1))

        # Sort depths in ascending order
        candidate_depths = sorted(list(set(candidate_depths)))
        # In case duplicate was generated, ensure we have at least num_events
        while len(candidate_depths) < num_events:
            candidate_depths.append(round(float(td * np.random.uniform(0.50, 0.95)), 1))
        candidate_depths = sorted(candidate_depths[:num_events])

        # Pick event types based on geological formation & parameter conditions
        for d_idx, depth in enumerate(candidate_depths):
            # Special case for MO-B-101's first event: preserve EVT-1001 details
            if is_seed_well and d_idx == 0:
                events.append({
                    "event_id": "EVT-1001",
                    "well_id": "MO-B-101",
                    "depth": 2980.0,
                    "event_type": "Lost Circulation",
                    "description": "Encountered vuggy porosity zone in Bassein Limestone. Pit volume decreased rapidly at 42 bbl/hr with dynamic mud losses.",
                    "action_taken": "Bit pulled 30m off bottom. Mixed and pumped 45 bbl engineered LCM pill containing medium nut plug and calcium carbonate (50 ppb). Allowed 2 hours soak time.",
                    "result": "Mud losses dropped to under 3 bbl/hr. Resumed controlled drilling with 11.0 ppg ECD without further mud loss."
                })
                continue

            event_id = f"EVT-{event_counter:04d}"
            # Avoid collision with EVT-1001 if counter hits 1001
            if event_id == "EVT-1001":
                event_counter += 1
                event_id = f"EVT-{event_counter:04d}"
            event_counter += 1

            # Determine likely event type based on formation and depth zone
            is_deep = (depth > td * 0.75)
            is_sandstone = any(s in formation for s in ["Sandstone", "Sand", "Clastics"])
            is_carbonate = any(c in formation for c in ["Limestone", "Carbonate"])
            is_shale = any(h in formation for h in ["Shale", "Formation"])

            if is_carbonate and is_deep:
                # Vuggy loss prone
                evt_type = random.choices(
                    ["Lost Circulation", "Differential Sticking", "No Significant Event"],
                    weights=[0.60, 0.15, 0.25]
                )[0]
            elif "Daman Sandstone" in formation or "Mid-Tapti Gas Sand" in formation:
                # High pressure gas sand
                if is_deep:
                    evt_type = random.choices(
                        ["Gas Kick", "High Torque", "Differential Sticking", "No Significant Event"],
                        weights=[0.55, 0.20, 0.15, 0.10]
                    )[0]
                else:
                    evt_type = random.choices(
                        ["Wellbore Instability", "High Torque", "No Significant Event"],
                        weights=[0.35, 0.35, 0.30]
                    )[0]
            elif is_shale:
                # Reactive swelling shale
                evt_type = random.choices(
                    ["Tight Hole / Pack-off", "Wellbore Instability", "High Torque", "No Significant Event"],
                    weights=[0.40, 0.30, 0.15, 0.15]
                )[0]
            elif is_sandstone and inc > 30.0:
                # High angle permeable sand
                evt_type = random.choices(
                    ["Differential Sticking", "Pipe Sticking", "High Torque", "No Significant Event"],
                    weights=[0.45, 0.20, 0.15, 0.20]
                )[0]
            else:
                # General distribution
                evt_type = random.choices(
                    ["No Significant Event", "High Torque", "Tight Hole / Pack-off", "Wellbore Instability"],
                    weights=[0.40, 0.25, 0.20, 0.15]
                )[0]

            # Select template and format narrative
            templates = EVENT_TEMPLATES.get(evt_type, EVENT_TEMPLATES["No Significant Event"])
            tmpl_desc, tmpl_act, tmpl_res = random.choice(templates)

            # Contextual formatting parameters
            fmt_kwargs = {
                "formation": formation,
                "field": field,
                "depth": int(depth),
                "d_start": max(100, int(depth - random.randint(150, 400))),
                "mw": mw,
                "kill_mw": round(mw + random.uniform(0.6, 1.0), 1),
                "lot": round(mw + random.uniform(1.2, 1.8), 1),
                "loss_rate": random.randint(22, 65),
                "final_loss": round(random.uniform(0.5, 2.5), 1),
                "pill_vol": random.choice([35, 40, 45, 50, 60]),
                "loss_pit": random.randint(15, 45),
                "gpm1": random.choice([650, 700, 750, 800]),
                "gpm2": random.choice([480, 520, 550, 580]),
                "soak": round(random.uniform(1.5, 3.5), 1),
                "lcm_type": random.choice([
                    "calcium carbonate 50 ppb blend",
                    "coarse nut plug and cellulosic fiber",
                    "thixotropic polymer crosslink blend",
                    "sized mica and graphite flakes"
                ]),
                "rop1": round(rop * 0.8, 1),
                "rop2": round(rop * 1.5, 1),
                "pit_gain": random.randint(12, 24),
                "gas_pct": random.randint(30, 65),
                "sidpp": random.randint(320, 510),
                "sicp": random.randint(460, 680),
                "overpull": random.randint(45, 80),
                "torque1": round(torque * 0.9, 1),
                "torque2": round(torque * 1.5, 1),
                "delta_t": round(random.uniform(6.0, 11.0), 1),
                "wob1": round(wob * 0.8, 1),
                "overbalance": random.randint(550, 850),
                "jar_force": random.randint(50, 75),
                "inc": int(inc),
            }

            desc = tmpl_desc.format(**fmt_kwargs)
            act = tmpl_act.format(**fmt_kwargs)
            res = tmpl_res.format(**fmt_kwargs)

            events.append({
                "event_id": event_id,
                "well_id": well_id,
                "depth": depth,
                "event_type": evt_type,
                "description": desc,
                "action_taken": act,
                "result": res
            })

    return wells, events

def generate_and_save():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(base_dir, "dataset")
    os.makedirs(dataset_dir, exist_ok=True)

    print("[Generator] Synthesizing 500 wells and 1500+ realistic events...")
    wells, events = generate_wells_and_events()

    wells_df = pd.DataFrame(wells)
    events_df = pd.DataFrame(events)

    # 1. Row count validation
    print(f"[Validation] Total wells generated: {len(wells_df)}")
    print(f"[Validation] Total events generated: {len(events_df)}")
    assert len(wells_df) == 500, f"Expected 500 wells, got {len(wells_df)}"
    assert len(events_df) >= 1500, f"Expected >= 1500 events, got {len(events_df)}"

    # 2. Duplicate ID validation
    assert wells_df["well_id"].is_unique, "Duplicate well_id detected!"
    assert events_df["event_id"].is_unique, "Duplicate event_id detected!"

    # 3. Missing values validation
    assert not wells_df.isnull().any().any(), "Missing values found in wells.csv!"
    assert not events_df.isnull().any().any(), "Missing values found in drilling_events.csv!"

    # 4. Foreign key integrity validation: all event well_ids exist in wells.csv
    unknown_wells = set(events_df["well_id"]) - set(wells_df["well_id"])
    assert len(unknown_wells) == 0, f"Foreign key violation: unknown well_ids {unknown_wells}"

    # 5. Depth logic validation: event depth <= total_depth
    merged = events_df.merge(wells_df[["well_id", "total_depth"]], on="well_id")
    invalid_depths = merged[merged["depth"] > merged["total_depth"]]
    assert invalid_depths.empty, f"Event depths exceed total depth: {len(invalid_depths)} occurrences"

    # Save CSV files
    wells_csv = os.path.join(dataset_dir, "wells.csv")
    events_csv = os.path.join(dataset_dir, "drilling_events.csv")

    wells_df.to_csv(wells_csv, index=False)
    events_df.to_csv(events_csv, index=False)

    print(f"[Success] Saved {len(wells_df)} wells to {wells_csv}")
    print(f"[Success] Saved {len(events_df)} drilling events to {events_csv}")

    # Event Type Breakdown
    print("\n--- Event Type Counts ---")
    type_counts = events_df["event_type"].value_counts()
    for evt_type, count in type_counts.items():
        print(f"  {evt_type:28s}: {count:5d} ({count/len(events_df)*100:5.1f}%)")

    # Sync to SQLite database if database.py exists
    try:
        from backend.database import init_db
        print("\n[Database] Refreshing SQLite database with updated dataset...")
        init_db(force_reload=True)
        print("[Database] Database refreshed successfully.")
    except Exception as e:
        print(f"[Database] Notice: DB auto-reload skipped ({e})")

if __name__ == "__main__":
    generate_and_save()
