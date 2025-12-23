import numpy as np

def three_phase_source(Vrms=230, freq=50, t_end=0.2, fs=5000):
    t = np.arange(0, t_end, 1/fs)
    omega = 2 * np.pi * freq
    Vm = Vrms * np.sqrt(2)

    Va = Vm * np.sin(omega * t)
    Vb = Vm * np.sin(omega * t - 2*np.pi/3)
    Vc = Vm * np.sin(omega * t + 2*np.pi/3)

    return t, Va, Vb, Vc
