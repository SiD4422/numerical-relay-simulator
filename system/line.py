import numpy as np

def transmission_line(Va, Vb, Vc, R=1.0, L=0.01, fs=5000):
    dt = 1 / fs

    Ia = np.zeros_like(Va)
    Ib = np.zeros_like(Vb)
    Ic = np.zeros_like(Vc)

    for i in range(1, len(Va)):
        Ia[i] = Ia[i-1] + dt * (Va[i] - R * Ia[i-1]) / L
        Ib[i] = Ib[i-1] + dt * (Vb[i] - R * Ib[i-1]) / L
        Ic[i] = Ic[i-1] + dt * (Vc[i] - R * Ic[i-1]) / L

    return Ia, Ib, Ic
