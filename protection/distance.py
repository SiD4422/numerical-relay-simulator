
def zone1_distance_trip(Z_app, Z_reach):
    """
    Zone-1 distance relay
    Trips if apparent impedance < reach
    """
    for i in range(len(Z_app)):
        if Z_app[i] < Z_reach:
            return True, i
    return False, None
