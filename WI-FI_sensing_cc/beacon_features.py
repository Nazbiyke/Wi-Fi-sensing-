import numpy as np


def extract_beacon_features(

    beacon_packets

):

    if len(beacon_packets) <= 1:
        # u can print like empty beacon window stuff 
        return 0

            

    rssi = [

        pkt["rssi"]

        for pkt in beacon_packets

    ]

    return  np.var(rssi)

    