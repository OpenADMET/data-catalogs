def get_biotite_ligand_as_rdmol(atom_array, chain_id, res_name):
    mask = (atom_array.chain_id == chain_id) & (atom_array.res_name == res_name)
    lig_atom_array = atom_array[mask]
    ligand_rd_mol = rdkit_interface.to_mol(lig_atom_array)
    ligand_rd_mol = Chem.RemoveHs(ligand_rd_mol)
    return ligand_rd_mol

def fix_boltz_ligand(rd_mol,tmplt_mol):
    rdDetermineBonds.DetermineConnectivity(rd_mol)
    for atm in rd_mol.GetAtoms():
        atm.SetNumRadicalElectrons(0)
        atm.SetNoImplicit(False)
    rd_mol.UpdatePropertyCache(strict=False)
    Chem.SanitizeMol(rd_mol)
    with rdBase.BlockLogs():
        rd_mol = AllChem.AssignBondOrdersFromTemplate(tmplt_mol, rd_mol)
    return rd_mol    

def get_boltz_rmsd(pdb_name, ccd_name, chain_id):
    ref_filename = f"../{pdb_name}/{pdb_name}.cif"
    ref_pdbx_file = pdbx.CIFFile.read(ref_filename)
    ref_atom_array = pdbx.get_structure(ref_pdbx_file, model=1, include_bonds=True)
    chain_mask = (ref_atom_array.chain_id == chain_id)
    ref_atom_array = ref_atom_array[chain_mask]
    ref_rd_mol = get_biotite_ligand_as_rdmol(ref_atom_array,chain_id,ccd_name)
    rmsd_list = []
    confidence_list = []
    for i in range(0,5):
        boltz_filename = f"Boltz_inputs/boltz_results_{pdb_name}/predictions/{pdb_name}/{pdb_name}_model_{i}.cif"        
        json_filename = f"Boltz_inputs/boltz_results_{pdb_name}/predictions/{pdb_name}/confidence_{pdb_name}_model_{i}.json" 
        with open(json_filename) as ifs:
            confidence_dict = json.load(ifs)
        confidence_list.append(confidence_dict)
        pdbx_file = pdbx.CIFFile.read(boltz_filename)
        boltz_atom_array = pdbx.get_structure(pdbx_file, model=1, include_bonds=True)
        boltz_atom_array,_,_,_ = superimpose_chain(ref_atom_array,boltz_atom_array)
        boltz_rd_mol = get_biotite_ligand_as_rdmol(boltz_atom_array,"B","LIG1")
        boltz_rd_mol = fix_boltz_ligand(boltz_rd_mol, ref_rd_mol)
        rmsd = CalcRMS(ref_rd_mol, boltz_rd_mol)
        rmsd_list.append(rmsd)
    return rmsd_list, confidence_list

def get_of3_rmsd(pdb_name, ccd_name, chain_id):
    ref_filename = f"{pdb_name}.cif"
    ref_pdbx_file = pdbx.CIFFile.read(ref_filename)
    ref_atom_array = pdbx.get_structure(ref_pdbx_file, model=1, include_bonds=True)
    chain_mask = (ref_atom_array.chain_id == chain_id)
    ref_atom_array = ref_atom_array[chain_mask]
    ref_rd_mol = get_biotite_ligand_as_rdmol(ref_atom_array,chain_id,ccd_name)
    rmsd_list = []
    confidence_list = []
    for i in range(1,6):
        of3_filename = f"OF3_inputs/{pdb_name}/seed_42/{pdb_name}_seed_42_sample_{i}_model.cif"        
        json_filename = f"OF3_inputs/{pdb_name}/seed_42/{pdb_name}_seed_42_sample_1_confidences_aggregated.json"
        with open(json_filename) as ifs:
            confidence_dict = json.load(ifs)
        confidence_list.append(confidence_dict)
        pdbx_file = pdbx.CIFFile.read(of3_filename)
        of3_atom_array = pdbx.get_structure(pdbx_file, model=1, include_bonds=True)
        of3_atom_array,_,_,_ = superimpose_chain(ref_atom_array,of3_atom_array)
        of3_rd_mol = get_biotite_ligand_as_rdmol(of3_atom_array,"B","LIG0")
        rmsd = CalcRMS(ref_rd_mol, of3_rd_mol)
        rmsd_list.append(rmsd)
    return rmsd_list, confidence_list
