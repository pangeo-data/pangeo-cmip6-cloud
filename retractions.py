import requests
import json
import time

def query_retraction(url, params, batchsize):
    print(f"Downloading Retraction Data from {url}...")
    resp = requests.get(url=url, params=params)
    header = resp.json()  # Check the JSON Response Content documentation below
    params["limit"] = batchsize
    
    batch_jsons = []
    print(f"batchsize= {batchsize}")
    
    has_data = True
    offset = 0
    while has_data:
        print('----------')
        print(f"offset={offset}")
        params["offset"] = offset
        resp = requests.get(url=url, params=params)
        if resp.status_code != 200:
            print(resp.status_code)
        data = resp.json()
        n_data = len(data["response"]["docs"])
        print(f"{n_data} entries found")
        
        batch_jsons.append(data)
        offset +=batchsize
        
        if len(data["response"]["docs"]) == 0:
            has_data = False
            print('No more data found')

    # Convert to list of instance ids
    print("Extracting instance_ids...")
    all_retracted_instance_ids = []
    for data in batch_jsons:
        extracted = [i["instance_id"] for i in data["response"]["docs"]]
        all_retracted_instance_ids.extend(extracted)

    n_retracted = len(all_retracted_instance_ids)
    
    print(f'Downloaded {n_retracted} retraction info')
 
    # There is the possibility that we are getting duplicate instance_ids here because we query replicas
    # Make sure dubplicates are not carried forward
    # TODO: Do we need to check that retracted is indeed true here?
    retracted_instance_ids = set(all_retracted_instance_ids)
    print(f"{len(all_retracted_instance_ids)-len(retracted_instance_ids)} replicas found")
    return retracted_instance_ids
