def line_to_ground_fault(Va, start_idx, Rf=0.01):
    Va_faulted = Va.copy()
    Va_faulted[start_idx:] *= Rf
    return Va_faulted


def line_to_line_fault(Va, Vb, start_idx, Rf=0.01):
    Va_f = Va.copy()
    Vb_f = Vb.copy()
    Va_f[start_idx:] *= Rf
    Vb_f[start_idx:] *= Rf
    return Va_f, Vb_f


def three_phase_fault(Va, Vb, Vc, start_idx, Rf=0.01):
    Va_f = Va.copy()
    Vb_f = Vb.copy()
    Vc_f = Vc.copy()
    Va_f[start_idx:] *= Rf
    Vb_f[start_idx:] *= Rf
    Vc_f[start_idx:] *= Rf
    return Va_f, Vb_f, Vc_f
