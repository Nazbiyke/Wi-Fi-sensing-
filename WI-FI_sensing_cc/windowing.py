from datetime import timedelta, datetime 
from collections import Counter 




def create_windows(

    packets,

    window_size=300,

    step=60

):

    if len(packets) == 0:

        return []

    packets = sorted(

        packets,

        key=lambda x: x["time"]

    )

    start_time = packets[0]["time"] # first packet time as start time 

    final_time = packets[-1]["time"] # Last packet time as end time - first from the end 

    

    windows = []

    current_start = start_time
    
    left = 0    #now we just use the left and right indexes to keep track of the packets that fall within the current window. 
    right = 0    # this technique will reduce the complexity of the windowing process, as we won't need to iterate through all the packets for each window.

    

   
        
# Iterate while the current end is less than or equal to the final time. 

    while (

        current_start

        + timedelta(seconds=window_size)

        <= final_time

    ):

        current_end = (

            current_start

            +

            timedelta(seconds=window_size)

        )


        
        

        

        # Move left boundary

        while (

            left < len(packets)

            and

            packets[left]["time"]    # while the time of the packet under the left index is less than the current starttime, we kind slide the left boundary forward.

            < current_start

        ):

            left += 1

        # Move right boundary

        while (

            right < len(packets)

            and

            packets[right]["time"]

            < current_end

        ):

            right += 1 # same process for the right boundary, but we compare it to the current end time.

        window_packets = (

            packets[left:right]

        )

        windows.append({

            "start": current_start,

            "end": current_end,

            "packets": window_packets

        })

        current_start += timedelta(seconds=step)      # slide the window forward by the step size, that is why we slide the left index forward until we reach the current start time instead of step size. 


    return windows