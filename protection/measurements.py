import numpy as np

def rms(signal, window):
    rms_vals = np.zeros_like(signal)
    for i in range(window, len(signal)):
        rms_vals[i] = np.sqrt(np.mean(signal[i-window:i]**2))
    return rms_vals


def zero_sequence_current(Ia, Ib, Ic):
    return (Ia + Ib + Ic) / 3
import numpy as np

def rms(signal, window):
    rms_vals = np.zeros_like(signal)
    for i in range(window, len(signal)):
        rms_vals[i] = np.sqrt(np.mean(signal[i-window:i]**2))
    return rms_vals


def zero_sequence_current(Ia, Ib, Ic):
    return (Ia + Ib + Ic) / 3


def negative_sequence_current(Ia, Ib, Ic):
    a = np.exp(1j * 2 * np.pi / 3)
    I_neg = (Ia + a**2 * Ib + a * Ic) / 3
    return np.abs(I_neg)
def rms_pair(V, I, window):
    Vr = rms(V, window)
    Ir = rms(I, window)
    return Vr, Ir


def apparent_impedance(Vrms, Irms):
    Z = Vrms / (Irms + 1e-6)  # avoid divide by zero
    return Z
import numpy as np

def impedance_rx(V, I):
    """
    Compute R and X components of impedance
    """
    Z = V / (I + 1e-6)
    R = np.real(Z)
    X = np.imag(Z)
    return R, X
