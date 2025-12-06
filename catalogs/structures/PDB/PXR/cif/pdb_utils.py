import requests
from typing import List, Dict, Optional, Any
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdDetermineBonds
from rdkit.Chem import AllChem
from rdkit.rdBase import BlockLogs
import biotite.structure.io as bsio
from biotite.interface import rdkit
import biotite.structure as struc

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _run_graphql_query(query: str, variables: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Helper function to run a GraphQL query against the RCSB PDB API."""
    url = "https://data.rcsb.org/graphql"
    try:
        response = requests.post(url, json={"query": query, "variables": variables})
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            logging.error(f"API returned errors: {data.get('errors')}")
            return None
        return data.get("data")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to API: {e}")
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




def get_pdb_ligand_stats(filename: str, ligand_id: str, ligand_smiles: str) -> Optional[tuple[str, int, int]]:
    """
    Get statistics about a ligand in a PDB file.

    Args:
        filename: The path to the PDB file.
        ligand_id: The ID of the ligand.
        ligand_smiles: The SMILES string of the ligand.

    Returns:
        A tuple containing the chain ID, number of atoms in the PDB file, and number of atoms in the SMILES string.
        Returns None if the ligand SMILES is invalid or the ligand is not found.
    """
    ligand_mol = Chem.MolFromSmiles(ligand_smiles)
    if not ligand_mol:
        logging.error(f"Invalid SMILES string for ligand {ligand_id}: {ligand_smiles}")
        return None
        
    pdb_atoms = bsio.load_structure(filename)
    mask = (pdb_atoms.element != "H")
    pdb_atoms = pdb_atoms[mask]
    
    num_ref_atoms = ligand_mol.GetNumAtoms()

    for chain_id in sorted(set(pdb_atoms.chain_id)):
        ligand_mask = (pdb_atoms.res_name == ligand_id) 
        chain_mask = (pdb_atoms.chain_id == chain_id)
        ligand_atoms = pdb_atoms[ligand_mask  & chain_mask]
        
        if len(ligand_atoms) == num_ref_atoms:
            return chain_id, len(ligand_atoms), num_ref_atoms
    
    # If no exact match is found, we could return the stats for the first chain where the ligand is found
    # but the atom count doesn't match. For now, we return None as the function's goal is to find a matching ligand.
    logging.warning(f"Ligand {ligand_id} not found with matching atom count in {filename}")
    return None

def get_biotite_ligand_as_rdmol(atom_array: struc.AtomArray, chain: str, ccid: str, smiles: str) -> Optional[Chem.Mol]:
    """
    Extract a ligand from a Biotite AtomArray and convert it to an RDKit molecule.

    Args:
        atom_array: A Biotite AtomArray containing the structure.
        chain: The chain ID of the ligand.
        ccid: The component ID of the ligand.
        smiles: The SMILES string of the ligand.

    Returns:
        An RDKit molecule object, or None if the conversion fails.
    """
    mask = (atom_array.chain_id == chain) & (atom_array.res_name == ccid)
    ligand_array = atom_array[mask]
    mask = (ligand_array.element != 'H')
    ligand_array = ligand_array[mask]
    
    if ligand_array.array_length() == 0:
        logging.warning(f"No atoms found for ligand {ccid} in chain {chain}.")
        return None

    ligand_array.bonds = struc.connect_via_distances(ligand_array)
    rd_mol = rdkit.to_mol(ligand_array)
    
    try:
        rdDetermineBonds.DetermineConnectivity(rd_mol)
        for atm in rd_mol.GetAtoms():
                atm.SetNumRadicalElectrons(0)
                atm.SetNoImplicit(False) 
        rd_mol.UpdatePropertyCache(strict=False)
        Chem.SanitizeMol(rd_mol)
        tmplt_mol = Chem.MolFromSmiles(smiles)
        if tmplt_mol:
            with BlockLogs():
                rd_mol = AllChem.AssignBondOrdersFromTemplate(tmplt_mol, rd_mol)
        else:
            logging.warning(f"Could not create template molecule from SMILES: {smiles}")
            return None
    except Exception as e:
        logging.error(f"Error processing molecule {ccid}: {e}")
        return None
        
    return rd_mol


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

            print(f"  Generated Boltz2 input file: {output_filename}")

        print("-" * 30)
