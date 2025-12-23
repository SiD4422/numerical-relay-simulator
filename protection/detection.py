def classify_fault(Ia_rms, Ib_rms, Ic_rms, I0_rms, I2_rms,
                   Ith=20, I0th=5, I2th=5):

    for i in range(len(Ia_rms)):

        a = Ia_rms[i] > Ith
        b = Ib_rms[i] > Ith
        c = Ic_rms[i] > Ith

        if a and not b and not c and I0_rms[i] > I0th:
            return "LG Fault (Phase A)", i

        if a and b and not c and I0_rms[i] < I0th:
            return "LL Fault (A-B)", i

        if a and b and c:
            return "LLL Fault", i

    return "No Fault", None
