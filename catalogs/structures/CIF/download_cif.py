import os
import requests
import sys

def get_pdb_ids(uniprot_id):
    """
    Get PDB IDs for a given UniProt ID from RCSB PDB.
    """
    query = {
        "query": {
            "type": "group",
            "logical_operator": "and",
            "nodes": [
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
                        "operator": "in",
                        "value": [uniprot_id]
                    }
                },
                {
                    "type": "terminal",
                    "service": "text",
                    "parameters": {
                        "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_name",
                        "operator": "exact_match",
                        "value": "UniProt"
                    }
                }
            ]
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": 200
            }
        }
    }
    response = requests.post("https://search.rcsb.org/rcsbsearch/v2/query", json=query)
    if response.status_code == 200:
        response_json = response.json()
        total_count = response_json.get("total_count", 0)
        if total_count > 200:
            print(f"Warning: Total PDB IDs ({total_count}) is greater than the number of results fetched (200).")
        result_set = response_json.get("result_set", [])
        return [item["identifier"] for item in result_set]
    else:
        print(f"Error searching for PDB IDs: {response.status_code}")
        print(response.text)
        return []

def download_cif_files(directory_name, uniprot_id):
    """
    Downloads all CIF files for a given UniProt ID.

    Args:
        directory_name (str): The directory to save the CIF files.
        uniprot_id (str): The UniProt ID.
    """
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
        print(f"Created directory: {directory_name}")

    pdb_ids = get_pdb_ids(uniprot_id)
    if not pdb_ids:
        print(f"No PDB IDs found for UniProt ID: {uniprot_id}")
        return

    print(f"Found {len(pdb_ids)} PDB IDs for UniProt ID: {uniprot_id}")

    for pdb_id in pdb_ids:
        cif_url = f"https://files.rcsb.org/download/{pdb_id}.cif"
        file_path = os.path.join(directory_name, f"{pdb_id}.cif")

        if os.path.exists(file_path):
            print(f"File already exists: {file_path}")
            continue

        print(f"Downloading {cif_url} to {file_path}")
        response = requests.get(cif_url)
        if response.status_code == 200:
            with open(file_path, 'w') as f:
                f.write(response.text)
        else:
            print(f"Error downloading {cif_url}: {response.status_code}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python download_cif.py <directory_name> <uniprot_id>")
        sys.exit(1)

    directory = sys.argv[1]
    uniprot = sys.argv[2]
    download_cif_files(directory, uniprot)
