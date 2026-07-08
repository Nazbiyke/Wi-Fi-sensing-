from collections import defaultdict

import numpy as np
from preprocessing import is_randomized_mac
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


    
def cluster_group(
    fp,
    members, 
    eps,
    verbose=False
):
    

    # CASE 1: only one MAC in fingerprint group

    if len(members) == 1:

        # print information if you want

        labels = np.array([0]) 


    
    else:
# --------------------------------------------------
# Build the feature matrix for DBSCAN:  # CASE 2 - two or more MACs
# --------------------------------------------------

        X = []

        for mf in members:

            X.append([

            mf["mean_rssi"],

            mf["mean_seq_num"]

            ])

        X = np.array(X)

# --------------------------------------------------
# Standardize features
# --------------------------------------------------

        X_scaled = StandardScaler().fit_transform( #  so that the features are on the same scale 
        X
    )

# --------------------------------------------------
# Run DBSCAN
# --------------------------------------------------

        dbscan = DBSCAN(

        eps=eps,

        min_samples=1

    )

        labels = dbscan.fit_predict( # Labels of the clusters 
        X_scaled
    )
    
    
# --------------------------------------------------
# Define the number of the Fixed and Randomised MAC addresses in each cluster. 
# --------------------------------------------------

    cluster_dict = defaultdict(list) # Just to know which MACS correspond to which cluster(clean printing)

    for mf, label in zip(
        members,
        labels
    ):

        cluster_dict[label].append( # The MAC addresses having the same label are gathered under the same cluster. 
            mf
        )

    randomized = 0
    fixed = 0

    for mf in members:

            if is_randomized_mac(
        mf["mac"]
    ):
             randomized += 1

            else:
             fixed += 1

# --------------------------------------------------
# Print results
# --------------------------------------------------
    if verbose: # If it's true then printing will be performed, if not -> u see no printing output, just gives us the straight answer - labels. 
       
        print()
        print("=" * 70)

        print(
        f"Fingerprint: {fp[:12]}"
    )

        print(
        f"MACs in this fingerprint group: {len(members)}"
        
    )

        print(
        f"Randomized MACs: {randomized} | "
        f"Fixed MACs: {fixed}"
    )
    
        print ()
        print("=" * 70)
    
        for cluster_id, cluster_members in cluster_dict.items():
        

            print()

            print(
            f"Cluster {cluster_id}"
        )

            print(
            "-" * 30
        )

            for mf in cluster_members:

                print()

                print(
                f"MAC: {mf['mac']}"
            )

                print(
                f"Packets: {mf['packet_count']}"
            )

                print(
                f"Mean RSSI: "
                f"{mf['mean_rssi']:.1f}"
            )


                print(
                f"Mean sequential number: "
                f"{mf['mean_seq_num']}"
            )

                
            
    return labels

