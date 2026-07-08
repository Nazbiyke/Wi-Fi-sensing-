import hashlib


# -------------------------------------------------------
# Invariant Information Elements from the paper
# -------------------------------------------------------

INVARIANT_IES = {   # 

    1,      # Supported Rates

    50,     # Extended Supported Rates

    45,     # HT Capabilities

    191,    # VHT Capabilities

    127     # Extended Capabilities

}


# -------------------------------------------------------
# Extract all Information Elements from payload
# -------------------------------------------------------

def extract_ies(payload_hex):

    ies = {}

    try:

        payload = bytes.fromhex(
            payload_hex
        ) 

    except ValueError:

        return ies

    i = 0

    while i + 2 <= len(payload): # I+2 gives us the index where our actual info for the ie is placed at 

        ie_id = payload[i]

        ie_length = payload[i + 1]

        if i + 2 + ie_length > len(payload):

            break

        ie_data = payload[
            i + 2 :
            i + 2 + ie_length  # data is located between i+2 and i+2+ie_length 
        ]

        ies[ie_id] = ie_data.hex()

        i += 2 + ie_length # every time we encounter the ie_data in our hexadecimal string

    return ies


# -------------------------------------------------------
# Extract only invariant IEs
# -------------------------------------------------------

def extract_invariant_ies(payload_hex):

    all_ies = extract_ies(
        payload_hex
    )

    invariant_ies = {}

    for ie_id, ie_data in all_ies.items():

        if ie_id in INVARIANT_IES:

            invariant_ies[
                ie_id
            ] = ie_data

    return invariant_ies


# -------------------------------------------------------
# Build invariant IEs string aka fingerprint 
# -------------------------------------------------------

def build_fingerprint(payload_hex):

    invariant_ies = extract_invariant_ies(
        payload_hex
    )

    fingerprint_parts = []

    for ie_id in sorted(
        invariant_ies.keys()
    ):

        fingerprint_parts.append(

            f"{ie_id}:{invariant_ies[ie_id]}"

        )

    fingerprint = "|".join(
        fingerprint_parts
    )

    return fingerprint





#--------------------------------------------------------------------------------
# - Group by fingerprint
#--------------------------------------------------------------------------------
from collections import defaultdict


def group_by_fingerprint(

    mac_features

):

    groups = defaultdict(list)

    for mf in mac_features:

        groups[
            mf["representative_fingerprint"]
        ].append(mf)  # We group the mac feature vectors by their representative fingerprint

    return groups


