import matplotlib.pyplot as plt

# ===============================
# IMPORT MODULES
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


# ===============================
# SIMULATION PARAMETERS
# ===============================
fs = 5000                 # Sampling frequency (Hz)
t_end = 1.0               # Total simulation time (s)

fault_time = 0.02         # Fault inception time (s)
breaker_open_time = 0.04  # Breaker opening delay after trip (s)
dead_time = 0.5           # Auto-reclose dead time (s)

rms_window = int(0.02 * fs)   # 1-cycle RMS window

FAULT_TYPE = "LLL"        # LG | LL | LLL


# ===============================
# DERIVED INDICES
# ===============================
fault_idx = int(fault_time * fs)
breaker_delay_samples = int(breaker_open_time * fs)


# ===============================
# 1. SOURCE
# ===============================
t, Va, Vb, Vc = three_phase_source(
    Vrms=230,
    freq=50,
    t_end=t_end,
    fs=fs
)


# ===============================
# 2. FAULT INJECTION
# ===============================
if FAULT_TYPE == "LG":
    Va = line_to_ground_fault(Va, fault_idx)

elif FAULT_TYPE == "LL":
    Va, Vb = line_to_line_fault(Va, Vb, fault_idx)

elif FAULT_TYPE == "LLL":
    Va, Vb, Vc = three_phase_fault(Va, Vb, Vc, fault_idx)


# ===============================
# 3. TRANSMISSION LINE
# ===============================
Ia, Ib, Ic = transmission_line(
    Va, Vb, Vc,
    R=1.0,
    L=0.01,
    fs=fs
)


# ===============================
# 4. MEASUREMENTS
# ===============================
Ia_rms = rms(Ia, rms_window)
Ib_rms = rms(Ib, rms_window)
Ic_rms = rms(Ic, rms_window)

I0 = zero_sequence_current(Ia, Ib, Ic)
I0_rms = rms(I0, rms_window)

I2 = negative_sequence_current(Ia, Ib, Ic)
I2_rms = rms(I2, rms_window)


# ===============================
# 5. RELAY DECISION
# ===============================
fault_name, trip_idx = classify_fault(
    Ia_rms,
    Ib_rms,
    Ic_rms,
    I0_rms,
    I2_rms
)

print(f"🚨 {fault_name} detected at t = {t[trip_idx]:.4f} s")
print("⚡ TRIP signal issued")


# ===============================
# 6. BREAKER OPERATION
# ===============================
Ia_b, Ib_b, Ic_b, open_idx = apply_breaker(
    Ia,
    Ib,
    Ic,
    trip_idx,
    breaker_delay_samples
)

print(f"🔌 Breaker opened at t = {t[open_idx]:.4f} s")


# ===============================
# 7. AUTO-RECLOSING
# ===============================
Ia_ar, Ib_ar, Ic_ar, reclose_idx, status = auto_reclose(
    Ia_b,
    Ib_b,
    Ic_b,
    t,
    open_idx,
    fs,
    dead_time=dead_time
)

if reclose_idx is not None:
    print(f"🔄 Reclose attempted at t = {t[reclose_idx]:.4f} s")

print(f"📌 Auto-Reclose Status: {status}")


# ===============================
# 8. PLOTS
# ===============================
plt.figure(figsize=(12, 4))

plt.plot(t, Ia_ar, label="Ia")
plt.plot(t, Ib_ar, label="Ib")
plt.plot(t, Ic_ar, label="Ic")

plt.axvline(t[fault_idx], color="red", linestyle="--", label="Fault Start")
plt.axvline(t[trip_idx], color="orange", linestyle="--", label="Relay Trip")
plt.axvline(t[open_idx], color="black", linestyle="--", label="Breaker Open")

if reclose_idx is not None:
    plt.axvline(t[reclose_idx], color="green", linestyle="--", label="Reclose")

plt.xlabel("Time (s)")
plt.ylabel("Current (A)")
plt.title(f"{FAULT_TYPE} Fault with Trip, Breaker & Auto-Reclosing")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
