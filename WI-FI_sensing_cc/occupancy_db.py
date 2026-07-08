
from clustering import cluster_group



def estimate_device_based_occupancy(
    fingerprint_groups,
    eps
):
    

    if not fingerprint_groups:

        return 0
    
    

    occupancy = 0

    for fp, members in fingerprint_groups.items():   # SO we iterate over the fingerprint groups, count the labels in each one of them

        labels = cluster_group(                      #And then inside each window, we will sum up the clusters of each fingerprint group
        fp,
        members,
        eps=eps,
        verbose=False
    )

        occupancy += len(
        set(labels)
    ) # count of unique labels 

    return occupancy