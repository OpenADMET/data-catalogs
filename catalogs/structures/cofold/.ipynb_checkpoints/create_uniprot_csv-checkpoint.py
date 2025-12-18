import csv

def create_uniprot_csv(filename="uniprot_ids.csv"):
    """
    Creates a CSV file with protein names and their UniProt IDs.
    """
    data = [
        {"Name": "AHR", "UniProt ID": "P35869"},
        {"Name": "PXR", "UniProt ID": "O75469"},
        {"Name": "CYP1A2", "UniProt ID": "P05177"},
        {"Name": "CYP2D6", "UniProt ID": "P10635"},
        {"Name": "CYP3A4", "UniProt ID": "P08684"},
        {"Name": "CYP2C9", "UniProt ID": "P11712"},
    ]

    fieldnames = ["Name", "UniProt ID"]

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Successfully created {filename}")

if __name__ == "__main__":
    create_uniprot_csv()
