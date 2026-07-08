

import time as timer

from windowing import create_windows
from preprocessing import filter_beacons, suppress_multirouter_duplicate_packets 
from beacon_features import extract_beacon_features
from preprocessing import separate_probe_beacon, merge_beacon_probe, group_by_router, find_reference_access_points
from fingerprint import build_fingerprint, extract_invariant_ies, group_by_fingerprint
from mac_features import build_mac_features
from packet_parser import parse_file 
from collections import defaultdict
from occupancy_db import estimate_device_based_occupancy
import numpy as np
from collections import Counter 
import math
from visualisation import (
    create_output_folder,
    plot_mae_heatmap,
    plot_occupancy_comparison,
    plot_variance_occupancy_relationship,
    plot_occupancy_distribution,
    plot_router_mae
)




# Loading the data from the file.
filepath = "data_30.10.2023.txt"
data = parse_file(filepath)

# PREPROCESS
probe_packets, beacon_packets = separate_probe_beacon(data)
cleaned_probes = suppress_multirouter_duplicate_packets(probe_packets)

reference_aps = find_reference_access_points(
    beacon_packets
)



reference_beacons = filter_beacons(

    beacon_packets,

    reference_aps

)


cleaned_dataset = merge_beacon_probe(cleaned_probes, reference_beacons)


start = timer.time()

router_packets = group_by_router(
    cleaned_dataset
)

print("Grouping:", timer.time() - start)


all_variances = [] # the list to store all the router's variances in order to get the global mean variance 

device_based_results = {}  # dict to store the each windows db occupancy estimation for each [eps][router] pair

global_max_occupancy = 0

max_router = None
max_window = None
max_eps = None
max_probe_packets = None
max_mac_features = None

router_variances = {}

router_packet_statistics = {}

eps_values = np.arange( 
    1.5, # lower band

    8.5, # stop values is not icluded, that's why we set smth a bit greater than 2.5 

    0.5 # step 
)


router_windows = {}

router_window_times = {}

for router, packets in router_packets.items():

    total_probe_packets = sum(
        1 for pkt in packets
        if pkt["type"] == "P"
    )

    total_ref_ap_beacon_packets = sum(

    1

    for pkt in packets

    if pkt["type"] == "B"

)

    selected_aps = reference_aps[router]["aps"]

    router_packet_statistics[router] = {

        "total_probe_packets":
            total_probe_packets,

        "total_ref_ap_beacon_packets":
            total_ref_ap_beacon_packets,

        "reference_aps":
            selected_aps,

        "reference_ap_mean_rssi":
            reference_aps[router]["best_mean_rssi"]

    }

    router_windows[router] = create_windows(
        packets,
        window_size=300,
        step=60
    )

    



# =====================================================
# PREPROCESS THE WINDOWS ONLY ONCE AND COMPUTE THE VARIANCE FOR EACH WINDOW 
# =====================================================

for router, windows in router_windows.items():

    router_variances[router] = []

    zero_probe_windows = 0
    zero_beacon_windows = 0
    zero_variance_windows = 0

    router_window_times[router] = [      # it should be run once per router, not once per window 

            window["start"]

            for window in windows

        ]

    for window in windows:

        packets = window["packets"]

        window["probe_packets"] = [
            pkt
            for pkt in packets
            if pkt["type"] == "P"
        ]

        window["beacon_packets"] = [
            pkt
            for pkt in packets
            if pkt["type"] == "B"
        ]

        window["mac_features"] = build_mac_features( # building mac features once, since it doesn't depend on eps
                    window["probe_packets"]
        )

        window["fingerprint_groups"] = group_by_fingerprint( # we compute it once and then store it 
                    window["mac_features"]
        )


        


        # -----------------------------
        # Packet statistics
        # -----------------------------

        if len(window["probe_packets"]) <= 1:
            zero_probe_windows += 1

        if len(window["beacon_packets"]) <= 1:
            zero_beacon_windows += 1

        # -----------------------------
        # Device-free feature
        # -----------------------------

        variance = extract_beacon_features(
            window["beacon_packets"]
        )

        window["variance"] = variance

        if variance == 0:
            zero_variance_windows += 1

        all_variances.append(variance)

        router_variances[router].append(variance)

    # -----------------------------
    # Store router statistics
    # -----------------------------

    router_packet_statistics[router]["zero_probe_windows"] = zero_probe_windows

    router_packet_statistics[router]["zero_beacon_windows"] = zero_beacon_windows

    router_packet_statistics[router]["zero_variance_windows"] = zero_variance_windows

    router_packet_statistics[router]["num_windows"] = len(windows)




# ----------------------------------
# FIRST EPS SWEEP: 
# 1. Compute and store DB occupancies 
# 2. Find device_based global_max_occupancy 
# ----------------------------------


print("Starting optimization...")

for eps in eps_values: 

    
    device_based_results[eps] = {}

    for router, windows in router_windows.items(): # we just iterate over the router_windows dict, since we already preprocessed the windows and stored them in a dict for each router
        

        device_based_results[eps][router] = []


        for window_id, window in enumerate(windows): # iterate over list of windows of the current router


            probe_packets = window["probe_packets"]
            

            occupancy = estimate_device_based_occupancy(
                    window["fingerprint_groups"],
                    eps
            )
            
            device_based_results[eps][router].append(occupancy) # Storing for each [eps][router] every window's occupancy 

            if occupancy > global_max_occupancy:

                global_max_occupancy = occupancy

                max_router = router

                max_window = window_id

                max_eps = eps

                max_window_start = window["packets"][0]["time"]

                max_mac_features = len( # we just access the macf, since we already computed it once and stored
                       window["mac_features"]
                )
                

                max_probe_packets = len(
                    probe_packets
                )




# ----------------------------------
# COMPUTE ALPHA RANGE
# ----------------------------------
print ("Starting alpha range computation...")
global_mean_variance = np.mean(
    all_variances
)

max_window_variance = (
    router_variances[max_router][max_window] # window with global max db occupancy
)

alpha_max = (

    math.log(
        global_max_occupancy
    )

    /

    math.log(
        global_mean_variance
    )

    )


alpha_values = np.arange(

    0.05,

    alpha_max + 0.05,

    0.05

)

print()
print("=" * 80)

print(
    f"Global mean variance: "
    f"{global_mean_variance:.1f}" # window-wise!
)

print(
    f"Global max occupancy: "
    f"{global_max_occupancy}" #windows-wise!
)

print(
    f"Alpha center: "
    f"{alpha_max:.2f}"
)


print (
    f"The start time of the window that has the max db occupancy: "
    f"{max_window_start}"
)
print("=" * 80)

print()

print("=" * 80)


print(
    f"Router: "
    f"{max_router}"
)

print(
    f"Window: "
    f"{max_window}"
)

print(
    f"EPS: "
    f"{max_eps:.1f}"
)

print(
    f"MAC feature vectors: "
    f"{max_mac_features}"
)

print(
    f"Probe packets: "
    f"{max_probe_packets}"
)

print("=" * 80)

 


# ----------------------------------
# COMPUTE THE DF OCCUPANCY AND PERFORM THE GRID SEARCH FOR ESTIMATING THE BEST PAIR {EPS, ALPHA} W THE SMALLEST MAE
# ----------------------------------
print("Grid search for best eps and alpha...")
best_parameters = {}

results = {}

for router in router_packets: # gives us just the keys, cause the packets have been already processed and stored 

    mae_grid = np.zeros(
    (len(alpha_values), len(eps_values)) # to store all the values if mae for each pair {eps, alpha}
    )    #so the rows are the alpha values and the columns are epsilon values 



    best_mae = float("inf") # cause later we compare every calculated mae with the mae computed for the next pair and for the conditions to start we set the first value to infinity.

    best_alpha = None

    best_eps = None


    for eps_index, eps in enumerate(eps_values): # eps_index is the position of the current eps in the eps_values array, so we can store the mae value in the correct position in the mae_grid

        db_occupancies = np.array(device_based_results[
                eps][router]) # simply retrieving the already computed db occupancies for each eps-router pair and making it an array just once (for mae))
       

        for alpha_index, alpha in enumerate(alpha_values): # same to know what position in the mae_grid we should store the mae value for the current pair {eps, alpha}
        
            df_occupancies = [] # creating a list to store the DF occupancies for each window of the current router for the current pair {eps, alpha}

            for variance in router_variances[
                router]: # access the variances of the current iteration router 

                occupancy = round(

                    variance

                    **

                    alpha

                )

                df_occupancies.append(
                    occupancy
                )

            df_occupancies = np.array(df_occupancies)

            mae = np.mean(

                np.abs(

                    db_occupancies - df_occupancies 
                )

            )

            mae_grid[alpha_index, eps_index] = mae # storing each mae value; so the rows are the alpha values and the columns are epsilon values, for the heatmap visualization later on.

            

            if mae < best_mae:

                best_db_occupancies = db_occupancies # just to store the winning pairs occupancies for both methods 

                best_df_occupancies = df_occupancies

                best_mae = mae

                best_alpha = alpha

                best_eps = eps
                

    best_parameters[router] = {

    "eps": best_eps,

    "alpha": best_alpha

    }

    variances = np.array(
    router_variances[router]
    )

    min_var = np.min(
    variances
    )

    max_var = np.max(
    variances
    )

    mean_var = np.mean(
    variances
    )

    median_var = np.median(
    variances
    )

    p95_var = np.percentile(
    variances,
    95
    )

    
    correlation = np.corrcoef(
    variances,
    best_db_occupancies
    )[0, 1] # bw the variances and best eps db occupancy 
    
    min_occ_db = np.min(
    best_db_occupancies
    )

    max_occ_db = np.max(
    best_db_occupancies
    )

    mean_occ_db = np.mean(
    best_db_occupancies
    )

    median_occ_db = np.median(
    best_db_occupancies
    )

    p95_occ_db = np.percentile(
    best_db_occupancies,
    95
    )

    print()

    print("=" * 80)

    print(
        f"ROUTER: {router}"
    )

    print("=" * 80)

    print(
        f"Best eps: "
        f"{best_eps:.1f}"
    )

    print(
        f"Best alpha: "
        f"{best_alpha:.3f}"
    )

    print(
        f"MAE: "
        f"{best_mae:.3f}"
    )
    
    print(
    f"Correlation: "
    f"{correlation:.3f}"
    )

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    stats = router_packet_statistics[router]
   # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    print()

    print("Packet Statistics")

    print("-" * 80)

    print(
        f"Total Probe packets: "
        f"{stats['total_probe_packets']}"
    )

    print(
        f"Total Beacon packets of the selected APs: "
        f"{stats['total_ref_ap_beacon_packets']} "
      
    )

  
    print(
    f"Number of selected APs: "
    f"{len(stats['reference_aps'])}"
)

    print()


    print("Selected APs:")

    for ap in stats["reference_aps"]:

        print(f"   {ap}")


    print(
        f"Best mean RSSI: "
        f"{stats['reference_ap_mean_rssi']:.2f} dBm" # the best mean RSSI of the strongest AP-router link
    )

   
    print(

        f"Average Reference Beacon packets/window: "

        f"{stats['total_ref_ap_beacon_packets']/stats['num_windows']:.1f}"

    )


    print(
        f"Windows with <=1 Probe packet: "
        f"{stats['zero_probe_windows']}/"
        f"{stats['num_windows']}"
    )

    print(
        f"Windows with <=1 Beacon packet: "
        f"{stats['zero_beacon_windows']}/"
        f"{stats['num_windows']}"
    )

    print(
        f"Zero-variance windows: "
        f"{stats['zero_variance_windows']}/"
        f"{stats['num_windows']}"
    )
        
    print()

    print("Device-based Occupancy Statistics")
    
    print ("-" * 80 )

    print(
    f"Min occupancy: "
    f"{min_occ_db}"
    )

    print(
        f"Max occupancy: "
        f"{max_occ_db}"
    )

    print(
        f"Mean occupancy: "
        f"{mean_occ_db:.2f}"
    )

    print(
        f"Median occupancy: "
        f"{median_occ_db:.1f}"
        )

    print( 
        f"95th percentile: "
        f"{p95_occ_db:.1f}"
        )
    
    print()

    print ("Variance Statistics")

    print ("-" * 80)

    print(
        f"Min variance: "
        f"{min_var:.3f}"
        )
    
    print(
        f"Max variance: "
        f"{max_var:.3f}"
    )

    print(
        f"Mean variance: "
        f"{mean_var:.3f}"
    )

    print(
        f"Median variance: "
        f"{median_var:.3f}"
    )

    print(
        f"95th percentile variance: "
        f"{p95_var:.3f}"
    )

    results[router] = {

    "best_eps": best_eps,

    "best_alpha": best_alpha,

    "best_mae": best_mae,

    "mae_grid": mae_grid,

    "window_times": router_window_times[router],

    "db_occupancies": best_db_occupancies,

    "df_occupancies": best_df_occupancies,

    "variances": router_variances[router],

    "packet_statistics": router_packet_statistics[router],

    "correlation": correlation

    }




# =====================================================
# VISUALISATIONS
# =====================================================

create_output_folder()


# FIRST THE ROUTER SPECIFIC PLOTS, MAE HEATMAPS, DF AND DB OCCUPANCE COMPARISON OVER TIME 
for i, (router, data) in enumerate(

    results.items(),

    start=1

):

    plot_mae_heatmap(

    i,

    data["mae_grid"],

    eps_values,

    alpha_values,

    data["best_eps"],

    data["best_alpha"]

    )

    
    plot_occupancy_comparison(

        i,

        data["window_times"],

        data["db_occupancies"],

        data["df_occupancies"]

    )


# NEXT ALL ROUTERS COMBINED PLOTS: VARIANCE VS DB AND DF OCCUPANCY, OCCUPANCY DISTRIBUTION, ROUTER MAE COMPARISON

plot_variance_occupancy_relationship(
    results
)

plot_occupancy_distribution(
    results
)

plot_router_mae(
    results
)

print()
print("=" * 80)
print("All visualizations saved successfully.")
print("Results are available in: results/figures/")
print("=" * 80)

    

        

    

    



    

        

        
            
                

              


              
           

        
    
    

        
