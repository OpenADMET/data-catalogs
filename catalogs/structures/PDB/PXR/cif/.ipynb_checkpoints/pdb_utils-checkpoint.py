import requests
from typing import List, Dict, Optional, Any



def _run_graphql_query(query: str, variables: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Helper function to run a GraphQL query against the RCSB PDB API."""
    url = "https://data.rcsb.org/graphql"
    try:
        response = requests.post(url, json={"query": query, "variables": variables})
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            # Errors can be logged here instead of printed
            # print(f"API returned errors: {data.get('errors')}")
            return None
        return data.get("data")
    except requests.exceptions.RequestException as e:
        # Errors can be logged here
        # print(f"Error connecting to API: {e}")
        return None

def get_ligand_smiles(pdb_id: str) -> Optional[List[Dict[str, str]]]:
    """
    Retrieves SMILES strings and component IDs for all ligands (non-polymer entities)
    associated with a given PDB ID using the RCSB PDB GraphQL API.

    Args:
        pdb_id: The PDB ID (e.g., "5NJ8").

    Returns:
        A list of dictionaries, each with 'smiles' and 'comp_id', or None if an error occurs.
    """
    query = """
    query($id: String!) {
      entry(entry_id: $id) {
        nonpolymer_entities {
          pdbx_entity_nonpoly {
            comp_id
            name
          }
          nonpolymer_comp {
            pdbx_chem_comp_descriptor {
              descriptor
              type
            }
          }
        }
      }
    }
    """
    variables = {"id": pdb_id.upper()}
    response_data = _run_graphql_query(query, variables)

    if not response_data:
        return None

    entry = response_data.get("entry")
    if not entry:
        return None

    entities = entry.get("nonpolymer_entities", [])
    if not entities:
        return []

    ligand_data_list = []
    for entity in entities:
        comp_id = entity.get("pdbx_entity_nonpoly", {}).get("comp_id")
        descriptors = entity.get("nonpolymer_comp", {}).get("pdbx_chem_comp_descriptor", [])
        smiles = "N/A"
        for desc in descriptors:
            if desc.get("type") in ["SMILES", "SMILES_CANONICAL"]:
                smiles = desc.get("descriptor")
                break
        if comp_id: # Only add if we have a comp_id
            ligand_data_list.append({"comp_id": comp_id, "smiles": smiles})

    return ligand_data_list

def get_protein_sequences(pdb_id: str) -> Optional[Dict[str, str]]:
    """
    Retrieves the amino acid sequences for protein entities in a PDB entry.

    Args:
        pdb_id: The PDB ID (e.g., "1OQ5").

    Returns:
        A dictionary mapping chain IDs (e.g., 'A,B') to their sequence,
        or None if an error occurs.
    """
    query = """
    query($id: String!) {
      entry(entry_id: $id) {
        polymer_entities {
          entity_poly {
            pdbx_seq_one_letter_code_can
            type
          }
          rcsb_polymer_entity_container_identifiers {
            auth_asym_ids
          }
        }
      }
    }
    """
    variables = {"id": pdb_id.upper()}
    response_data = _run_graphql_query(query, variables)

    if not response_data:
        return None

    entry = response_data.get("entry")
    if not entry:
        return None

    polymers = entry.get("polymer_entities", [])
    sequences = {}

    for poly in polymers:
        entity_poly = poly.get("entity_poly", {})
        if "polypeptide" not in entity_poly.get("type", ""):
            continue

        seq = entity_poly.get("pdbx_seq_one_letter_code_can")
        chains = poly.get("rcsb_polymer_entity_container_identifiers", {}).get("auth_asym_ids", [])

        if seq and chains:
            chain_label = ",".join(chains)
            sequences[chain_label] = seq
            
    return sequences


def write_boltz2_input(
    proteins: Dict[str, str],
    ligands: List[Dict[str, str]],
    output_path: str,
    binder_id: str,
) -> None:
    """
    Generates and writes a YAML input file for Boltz-2.
    Args:
        proteins: A dictionary mapping protein IDs to their amino acid sequences.
        ligands: A list of dictionaries, each with 'id' and 'smiles'.
        output_path: The path where the input file will be saved.
        binder_id: The ID of the ligand that is the binder.
    """
    file_content = "version: 1\n"
    file_content += "sequences:\n"
    for protein_id, sequence in proteins.items():
        file_content += f"  - protein:\n"
        file_content += f"      id: {protein_id}\n"
        file_content += f"      sequence: {sequence}\n"
    for ligand in ligands:
        file_content += f"  - ligand:\n"
        file_content += f"      id: {ligand['id']}\n"
        file_content += f"      smiles: '{ligand['smiles']}'\n"
    file_content += "properties:\n"
    file_content += "  - affinity:\n"
    file_content += f"      binder: {binder_id}\n"

    with open(output_path, 'w') as f:
        f.write(file_content)


if __name__ == "__main__":
    pdb_ids_to_test = ["1BMK"]

    for pdb_id in pdb_ids_to_test:
        print(f"--- Data for {pdb_id} ---")

        # Get and print ligand SMILES
        ligand_data_list = get_ligand_smiles(pdb_id)
        if ligand_data_list:
            print(f"  Ligands found: {len(ligand_data_list)}")
            for ligand in ligand_data_list:
                print(f"    - CID: {ligand['comp_id']}, SMILES: {ligand['smiles']}")
        else:
            print("  No ligands found or failed to retrieve.")

        # Get and print protein sequences
        sequences = get_protein_sequences(pdb_id)
        if sequences:
            print("  Protein Sequences found.")
        else:
            print("  No protein sequences found or failed to retrieve.")

        if sequences and ligand_data_list:
            protein_id = next(iter(sequences))
            # Assuming the first ligand in the list is the binder for demonstration
            # In a real scenario, you'd have logic to determine the actual binder
            binder_id = ligand_data_list[0]['comp_id']
            
            proteins_to_write = {protein_id: sequences[protein_id]}
            ligands_to_write = [{"id": ligand['comp_id'], "smiles": ligand['smiles']} for ligand in ligand_data_list]

            output_filename = f"{pdb_id.lower()}_generated.yaml"
            write_boltz2_input(
                proteins=proteins_to_write,
                ligands=ligands_to_write,
                output_path=output_filename,
                binder_id=binder_id,
            )
            print(f"  Generated Boltz2 input file: {output_filename}")

        print("-" * 30)
