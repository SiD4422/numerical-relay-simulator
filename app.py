import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ===============================
# IMPORT CORE MODULES
# ===============================
from system.source import three_phase_source
from system.line import transmission_line
from system.breaker import apply_breaker
from system.autoreclose import auto_reclose

from faults.fault_models import (
    line_to_ground_fault,
    line_to_line_fault,
    three_phase_fault
)

from protection.measurements import (
    rms,
    zero_sequence_current,
    negative_sequence_current
)

from protection.detection import classify_fault
from protection.distance import zone1_distance_trip
from protection.fault_location import estimate_fault_location


# ===============================
# STREAMLIT CONFIG
# ===============================
st.set_page_config(page_title="Power System Protection Simulator", layout="wide")
st.title("⚡ Numerical Relay, Distance Protection & Fault Location Simulator")


# ===============================
# SIDEBAR INPUTS
# ===============================
st.sidebar.header("🔧 Fault Inputs")

FAULT_TYPE = st.sidebar.selectbox("Fault Type", ["LG", "LL", "LLL"])
FAULT_NATURE = st.sidebar.selectbox("Fault Nature", ["Temporary", "Permanent"])
fault_resistance = st.sidebar.slider("Fault Resistance (Ω)", 0.01, 20.0, 0.01)

st.sidebar.header("📍 Line & Location Inputs")

line_length_km = st.sidebar.number_input(
    "Line Length (km)", min_value=10.0, max_value=500.0, value=100.0, step=10.0
)

Z_line = st.sidebar.slider("Line Impedance (Ω)", 5.0, 50.0, 20.0)

actual_fault_location = st.sidebar.slider(
    "Actual Fault Location (% of line)", 5, 95, 40
)

st.sidebar.header("🛡 Protection Scheme")

RELAY_TYPE = st.sidebar.selectbox(
    "Relay Type", ["Overcurrent Relay", "Distance Relay"]
)

st.sidebar.header("⚙ Breaker & System")

breaker_open_time = st.sidebar.slider("Breaker Opening Time (s)", 0.02, 0.1, 0.04)
dead_time = st.sidebar.slider("Auto-Reclose Dead Time (s)", 0.2, 1.0, 0.5)

fs = st.sidebar.selectbox("Sampling Frequency (Hz)", [2000, 5000, 10000])
t_end = st.sidebar.selectbox("Simulation Duration (s)", [0.5, 1.0, 1.5])

run = st.sidebar.button("▶ Run Simulation")


# ===============================
# MAIN SIMULATION
# ===============================
if run:

    event_log = []

    rms_window = int(0.02 * fs)
    fault_idx = int((actual_fault_location / 100) * fs * t_end)
    breaker_delay_samples = int(breaker_open_time * fs)

    Z1 = 0.8 * Z_line
    Z2 = 1.2 * Z_line
    Z3 = 2.0 * Z_line

    # ---------- SOURCE ----------
    t, Va, Vb, Vc = three_phase_source(230, 50, t_end, fs)

    # ---------- FAULT ----------
    if FAULT_TYPE == "LG":
        Va = line_to_ground_fault(Va, fault_idx, fault_resistance)
    elif FAULT_TYPE == "LL":
        Va, Vb = line_to_line_fault(Va, Vb, fault_idx, fault_resistance)
    else:
        Va, Vb, Vc = three_phase_fault(Va, Vb, Vc, fault_idx, fault_resistance)

    event_log.append((t[fault_idx], "Fault Applied"))

    # ---------- LINE ----------
    Ia, Ib, Ic = transmission_line(Va, Vb, Vc, fs=fs)

    # ---------- MEASUREMENTS ----------
    Ia_rms = rms(Ia, rms_window)
    Ib_rms = rms(Ib, rms_window)
    Ic_rms = rms(Ic, rms_window)

    I0 = zero_sequence_current(Ia, Ib, Ic)
    I2 = negative_sequence_current(Ia, Ib, Ic)

    trip_idx = None
    Z_app = None
    fault_name = "No Trip"

    # ---------- RELAY LOGIC ----------
    if RELAY_TYPE == "Overcurrent Relay":

        fault_name, trip_idx = classify_fault(
            Ia_rms, Ib_rms, Ic_rms,
            rms(I0, rms_window),
            rms(I2, rms_window)
        )

        event_log.append((t[trip_idx], "Overcurrent Trip"))

    else:
        # Distance Relay
        Va_r = rms(Va, rms_window)
        Ia_r = rms(Ia, rms_window)
        Z_app = Va_r / (Ia_r + 1e-6)

        for i in range(len(Z_app)):
            if Z_app[i] < Z1:
                trip_idx = i
                fault_name = "Zone-1 Distance Trip"
                break
            elif Z_app[i] < Z2:
                trip_idx = i + int(0.3 * fs)
                fault_name = "Zone-2 Distance Trip"
                break
            elif Z_app[i] < Z3:
                trip_idx = i + int(1.0 * fs)
                fault_name = "Zone-3 Distance Trip"
                break

        event_log.append((t[trip_idx], fault_name))

    # ---------- BREAKER ----------
    Ia_b, Ib_b, Ic_b, open_idx = apply_breaker(
        Ia, Ib, Ic, trip_idx, breaker_delay_samples
    )

    event_log.append((t[open_idx], "Breaker Open"))

    # ---------- FAULT CLEARING ----------
    if FAULT_NATURE == "Temporary":
        Va[open_idx:] = 0

    # ---------- AUTO-RECLOSE ----------
    Ia_ar, Ib_ar, Ic_ar, reclose_idx, status = auto_reclose(
        Ia_b, Ib_b, Ic_b, t, open_idx, fs, dead_time
    )

    event_log.append((t[reclose_idx], "Reclose Attempt"))
    event_log.append((t[reclose_idx], status))

    # ---------- FAULT LOCATION (Distance Relay Only) ----------
    if RELAY_TYPE == "Distance Relay" and trip_idx is not None:
        Z_measured = Z_app[trip_idx]
        estimated_location_pct = estimate_fault_location(Z_measured, Z_line)
        estimated_location_km = (estimated_location_pct / 100) * line_length_km
        actual_location_km = (actual_fault_location / 100) * line_length_km

    # ===============================
    # STATUS
    # ===============================
    st.subheader("📊 Relay Status")
    st.write(f"**Fault:** {fault_name}")
    st.write(f"**Auto-Reclose:** {status}")

    # ===============================
    # FAULT LOCATION DISPLAY
    # ===============================
    if RELAY_TYPE == "Distance Relay" and trip_idx is not None:

        st.subheader("📍 Fault Location Estimation")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Actual Location",
            f"{actual_fault_location:.1f} %",
            f"{actual_location_km:.1f} km"
        )

        c2.metric(
            "Estimated Location",
            f"{estimated_location_pct:.1f} %",
            f"{estimated_location_km:.1f} km"
        )

        c3.metric(
            "Error",
            f"{abs(estimated_location_pct - actual_fault_location):.2f} %"
        )

    # ===============================
    # EVENT LOG
    # ===============================
    st.subheader("📜 Event Log")

    log_df = pd.DataFrame(event_log, columns=["Time (s)", "Event"])
    st.dataframe(log_df)

    # ===============================
    # CURRENT WAVEFORMS
    # ===============================
    st.subheader("📈 Phase Currents")

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(t, Ia_ar, label="Ia")
    ax.plot(t, Ib_ar, label="Ib")
    ax.plot(t, Ic_ar, label="Ic")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
