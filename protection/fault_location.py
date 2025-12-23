def estimate_fault_location(Z_measured, Z_line):
    """
    Estimate fault location as percentage of line length
    """
    if Z_line == 0:
        return 0.0
    return min((Z_measured / Z_line) * 100, 100.0)
