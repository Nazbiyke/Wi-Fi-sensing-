from datetime import datetime

from sympy import sequence

def parse_file(filepath, max_probe_packets=None):
    data = []
    
    with open(filepath, "r") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines): # Limit to first 2000 lines for testing
        line = lines[i].strip()
        parts = line.split("|")

        if len(parts) < 8:
            i += 1
            continue

        timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
        packet_type = parts[2]

        if packet_type == "B":
            data.append({
                "time": timestamp,
                "type": "B",
                "ap": parts[3],
                "router": parts[4],
                "rssi": int(parts[7])
            })
            i += 1
 
        elif packet_type == "P":
            data.append({
                "time": timestamp,
                "type": "P",
                "device": parts[3],
                "router": parts[4],
                "rssi": int(parts[5]),
                "payload_hex": parts[8], 
                "sequence": int(parts[9]) 
            })
            i += 1
           
    return data
               

            
           

  
        




""" 
# Consider only first 100 probes 
from datetime import datetime


def parse_file(filepath, max_probe_packets=None):

    data = []

    probe_count = 0

    with open(filepath, "r") as f:

        lines = f.readlines()

    i = 0

    while i < len(lines):

        line = lines[i].strip()

        parts = line.split("|")

        # ---------------------------------
        # BASIC VALIDATION
        # ---------------------------------

        if len(parts) < 6:

            i += 1
            continue

        # ---------------------------------
        # SAFE TIMESTAMP PARSING
        # ---------------------------------

        try:

            timestamp = datetime.strptime(
                parts[0],
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:

            i += 1
            continue

        packet_type = parts[2]

        # ---------------------------------
        # BEACON PACKETS
        # ---------------------------------

        if packet_type == "B":

            data.append({

                "time": timestamp,

                "type": "B",

                "ap": parts[3],

                "router": parts[4],

                "ssid": parts[5],

                "rssi": int(parts[7])
            })

        # ---------------------------------
        # PROBE PACKETS
        # ---------------------------------

        elif packet_type == "P":

            try:

                data.append({

                    "time": timestamp,

                    "type": "P",

                    "device": parts[3],

                    "router": parts[4],

                    "rssi": int(parts[5]),

                    "payload_hex": parts[8],

                    "sequence": int(parts[9])
                })

                probe_count += 1

                # -------------------------
                # STOP CONDITION
                # -------------------------

                if (
                    max_probe_packets is not None
                    and
                    probe_count >= max_probe_packets
                ):

                    break

            except:

                pass

        i += 1

    return data """