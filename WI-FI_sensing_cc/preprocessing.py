from collections import defaultdict
import numpy as np 

    


#--------------------------------------------------------------------------------
# Separate the beacon packets from the probe packets
#--------------------------------------------------------------------------------
def separate_probe_beacon(data):

    probe_packets = []

    beacon_packets = []

    for pkt in data: 

        if pkt["type"] == "B":

            beacon_packets.append(pkt)

        elif pkt["type"] == "P":

            probe_packets.append(pkt)

    return probe_packets, beacon_packets



# Analysing the time difference between the packets having the same MAC address and sequence number 
# And for the potential duplicates with small time difference, set the threshold to 5 

def suppress_multirouter_duplicate_packets(probe_packets):

    groups = defaultdict(list)

    for pkt in probe_packets:

        key = (
            pkt["device"],
            pkt["sequence"]
        )

        groups[key].append(pkt) # here we are just grouping packets by the key, it's possible that the keys have only one value
    

    
    cleaned_probes = []
    for (mac, seq), packets in groups.items():

        routers = {

            pkt["router"]

            for pkt in packets

        } # in a single group we check whether what router has each packet 

        packets = sorted(
            packets,
            key=lambda x: x["time"]
        )

        first_time = packets[0]["time"]

        last_time = packets[-1]["time"]

        delta = (
            last_time - first_time
        ).total_seconds()

        # True duplicate group
        if (
            len(routers) > 1
            and
            delta <= 5
        ):
        
            best_packet = max(

                packets,

                key=lambda pkt:
                    pkt["rssi"]
            )

            
            cleaned_probes.append(
                best_packet
            )

        # Not duplicates, THE CASES WHERE (MAC, SEQ) HAVE ONLY 1 PACKET
        else:

            cleaned_probes.extend(
                packets
            ) # we store all other packets with the unique case of (mac, seq)
        
    
    
    return cleaned_probes
        



#---------------------------------------------------------------------------------------------
# Let's estimate the reference Access Point that is located the closest to the specific monitoring router
#----------------------------------------------------------------------------------------------

def find_reference_access_points(beacon_packets):

    router_beacons = defaultdict(list)

    MIN_BEACONS = 1000
    RSSI_THRESHOLD = 1.5

    for pkt in beacon_packets:

        router_beacons[pkt["router"]].append(pkt) # first group all the beacon packets by the router that has received them.

    reference_aps = {}

    for router, beacons in router_beacons.items(): # then this loop iterates over each router and its associated beacon packets.

        ap_rssi = defaultdict(list)

        for pkt in beacons:

            ap_rssi[pkt["ap"]].append(pkt["rssi"]) # here we are grouping the RSSI values by access point for each router.


        
        # Keep only persistent APs
        # ----------------------------------------------------

        ap_statistics = {}

        for ap, rssi_values in ap_rssi.items():

            if len(rssi_values) < MIN_BEACONS: # thus we don't consider the APs that have less than 1000 beacons

                continue

            ap_statistics[ap] = {

                "count": len(rssi_values),

                "mean_rssi": np.mean(rssi_values)

            }

       
        # Strongest persistent AP
        # ----------------------------------------------------

        best_mean_rssi = max(

            stats["mean_rssi"]

            for stats in ap_statistics.values() # stats are the values of the dictionary, which are dictionaries themselves containing the count and mean_rssi for each AP.

        ) # we find the highest average RSSI only among the APs that have passed the condition of minimum 1000 beacons 

        
        # Select every AP within 1.5 dB
        # ----------------------------------------------------

        selected_aps = []

        for ap, stats in ap_statistics.items():

            if (

                best_mean_rssi

                -

                stats["mean_rssi"]

                <= RSSI_THRESHOLD

            ):

                selected_aps.append(ap) # if there are multiple APs that have the similar RSSI values to the best one we store them. 

        # Store
        
        reference_aps[router] = {

            "aps": selected_aps,

            "best_mean_rssi": best_mean_rssi

        }

    return reference_aps


#---------------------------------------------------------------------------------------------
# Now we filter the beacon packets to keep only those of the reference AP and eliminate the rest 
#----------------------------------------------------------------------------------------------


def filter_beacons(
        
    beacon_packets,

    reference_aps
):

    reference_beacons = []

    for pkt in beacon_packets:

        if pkt["ap"] in reference_aps[pkt["router"]]["aps"]:

            reference_beacons.append(pkt)

    return reference_beacons





#--------------------------------------------------------------------------------
# - Now merge the cleaned probe packets with the beacon packets in order to perform windowing later on the whole database.
#--------------------------------------------------------------------------------

def merge_beacon_probe(
       
       cleaned_probes, 
                       
       reference_beacons):
    
    cleaned_dataset = sorted(
        cleaned_probes + reference_beacons,
        key=lambda pkt: pkt["time"]
    )

    return cleaned_dataset





#------------------------------------------------------------------------------
# Let's group all the packets, including the beacon packets, regarding the routers
#-------------------------------------------------------------------------------

def group_by_router(cleaned_dataset):

    router_packets = defaultdict(list) # A dictionary where each key is a router and the value is the list of packets associated with that router
    
    for pkt in cleaned_dataset: 

        router_packets[pkt["router"]].append(pkt) # For each packet, we append it to the list of packets associated with its router


    return router_packets



#------------------------------------------------------------------------------
# LETS COMPUTE THE COUNTS OF RANDOMISED MAC AND FIXED MAC ADDRESSES. 
#------------------------------------------------------------------------------

def is_randomized_mac(mac):

    first_byte = mac.split(":")[0]

    second_hex = first_byte[1].upper()

    return second_hex in {
        "2",
        "6",
        "A",
        "E"
    } # returns TRUE in case the second bit of the second[1] is in the list, FALSE in case it's different from the values provided by the list.  """