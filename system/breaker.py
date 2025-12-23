import numpy as np

def apply_breaker(Ia, Ib, Ic, trip_idx, breaker_delay_samples):
    """
    Opens breaker after trip_idx + breaker_delay_samples
    """
    Ia_b = Ia.copy()
    Ib_b = Ib.copy()
    Ic_b = Ic.copy()

    open_idx = trip_idx + breaker_delay_samples

    if open_idx < len(Ia):
        Ia_b[open_idx:] = 0.0
        Ib_b[open_idx:] = 0.0
        Ic_b[open_idx:] = 0.0

    return Ia_b, Ib_b, Ic_b, open_idx
