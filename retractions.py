from tqdm.autonotebook import tqdm
import requests
import json


def query_retraction(url: str, params: dict[str, str]) -> list[str]:
    resp = requests.get(url=url, params=params)
    header = resp.json()  # Check the JSON Response Content documentation below
    n_items = header["response"]["numFound"]

    batchsize = 5000

    batches = range(0, n_items+1, batchsize)  # if I offset these, can
    params["limit"] = batchsize

    batch_jsons = []

    print(f"Downloading Retraction Data from {url}...")
    for batch in tqdm(batches):
        params["offset"] = batch
        resp = requests.get(url=url, params=params)
        if resp.status_code != 200:
            print(batch)
            print(resp.status_code)
        data = resp.json()
        batch_jsons.append(data)

    # Convert to list of instance ids
    print("Extracting instance_ids...")
    all_retracted_instance_ids = []
    for data in tqdm(batch_jsons):
        extracted = [i["instance_id"] for i in data["response"]["docs"]]
        all_retracted_instance_ids.extend(extracted)

    # Fail out here if the total number of items is not what was promised in the header
    # I had a few instances today, where that was the case, I think a simple retry is
    # a good enough solution for now.
    n_retracted = len(all_retracted_instance_ids)
    if n_retracted == n_items:
        print('Successfully downloaded all retraction info')
    else:
        raise RuntimeError(f'Downloaded retraction info is incomplete. Found {n_retracted} items, expected {n_items}')

    # There is the possibility that we are getting duplicate instance_ids here because we query replicas
    # Make sure dubplicates are not carried forward
    retracted_instance_ids = set(all_retracted_instance_ids)
    print(f"{len(all_retracted_instance_ids)-len(retracted_instance_ids)} replicas found")
    return retracted_instance_ids