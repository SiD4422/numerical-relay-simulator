def auto_reclose(Ia, Ib, Ic, t, open_idx, fs,
                 dead_time=0.5,
                 Ith=5.0):
    """
    Single-shot auto-reclose logic
    """
    dead_samples = int(dead_time * fs)
    reclose_idx = open_idx + dead_samples

    Ia_ar = Ia.copy()
    Ib_ar = Ib.copy()
    Ic_ar = Ic.copy()

    if reclose_idx >= len(t):
        return Ia_ar, Ib_ar, Ic_ar, None, "LOCKOUT"

    # Reclose: currents restored (use pre-fault values)
    Ia_ar[reclose_idx:] = Ia[:len(Ia)-reclose_idx]
    Ib_ar[reclose_idx:] = Ib[:len(Ib)-reclose_idx]
    Ic_ar[reclose_idx:] = Ic[:len(Ic)-reclose_idx]

    # Check if fault persists (simple threshold check)
    if abs(Ia_ar[reclose_idx]) > Ith or abs(Ib_ar[reclose_idx]) > Ith or abs(Ic_ar[reclose_idx]) > Ith:
        # Fault still present → lockout
        Ia_ar[reclose_idx:] = 0
        Ib_ar[reclose_idx:] = 0
        Ic_ar[reclose_idx:] = 0
        return Ia_ar, Ib_ar, Ic_ar, reclose_idx, "LOCKOUT"

    return Ia_ar, Ib_ar, Ic_ar, reclose_idx, "RECLOSE SUCCESS"
