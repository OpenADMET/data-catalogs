import requests

def get_protein_sequence(uniprot_id: str) -> str | None:
    """
    Retrieves the protein sequence for a given UniProt accession ID.

    Args:
        uniprot_id (str): The UniProt accession ID (e.g., 'P0DP23').

    Returns:
        str: The protein sequence as a string, or None if not found or an error occurs.
    """
    base_url = "https://www.uniprot.org/uniprot/"
    # Using the accession directly in the URL is more direct for specific entries
    url = f"{base_url}{uniprot_id}.fasta"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        fasta_data = response.text
        if fasta_data.strip():
            # Split by lines, remove the header (first line), and join the rest
            lines = fasta_data.strip().split('\n')
            if len(lines) > 1:
                sequence = "".join(lines[1:])
                return sequence
            else:
                print(f"No sequence data found for UniProt ID: {uniprot_id}. Response: {fasta_data}")
                return None
        else:
            print(f"No data returned for UniProt ID: {uniprot_id}. Check if the ID is valid.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for UniProt ID {uniprot_id}: {e}")
        return None

if __name__ == "__main__":
    # Ensure 'requests' library is installed: pip install requests

    print("--- Example 1: Valid UniProt ID (Human Insulin) ---")
    uniprot_id_valid = "P0DP23"
    sequence_valid = get_protein_sequence(uniprot_id_valid)

    if sequence_valid:
        print(f"Protein sequence for {uniprot_id_valid}:\n{sequence_valid}")
        print(f"Sequence length: {len(sequence_valid)}")
    else:
        print(f"Could not retrieve sequence for {uniprot_id_valid}.")

    print("\n--- Example 2: Another Valid UniProt ID (P53_HUMAN) ---")
    uniprot_id_p53 = "P04637"
    sequence_p53 = get_protein_sequence(uniprot_id_p53)

    if sequence_p53:
        print(f"Protein sequence for {uniprot_id_p53}:\n{sequence_p53[:100]}...") # Print first 100 chars
        print(f"Sequence length: {len(sequence_p53)}")
    else:
        print(f"Could not retrieve sequence for {uniprot_id_p53}.")


    print("\n--- Example 3: Non-existent UniProt ID ---")
    uniprot_id_non_existent = "NONEXISTENT123"
    sequence_non_existent = get_protein_sequence(uniprot_id_non_existent)
    if sequence_non_existent:
        print(f"Protein sequence for {uniprot_id_non_existent}:\n{sequence_non_existent}")
    else:
        print(f"Could not retrieve sequence for {uniprot_id_non_existent}.")

    print("\n--- Example 4: Invalid UniProt ID format ---")
    uniprot_id_invalid_format = "INVALID"
    sequence_invalid_format = get_protein_sequence(uniprot_id_invalid_format)
    if sequence_invalid_format:
        print(f"Protein sequence for {uniprot_id_invalid_format}:\n{sequence_invalid_format}")
    else:
        print(f"Could not retrieve sequence for {uniprot_id_invalid_format}.")
