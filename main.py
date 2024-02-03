from math import sqrt
import numpy as np
import pandas as pd
import os

considered_base_pair_names = ['AA', 'AU', 'AC', 'AG', 'UU', 'UC', 'UG', 'CC', 'CG', 'GG']


def euclidean_distance(point1, point2):
    return sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)


def calculate_distances(atom_info_list):
    distances = []
    for i in range(len(atom_info_list)):
        for j in range(i + 1, len(atom_info_list)):
            residue_1 = int(atom_info_list[i][2])
            residue_2 = int(atom_info_list[j][2])

            # Ensure the residues are at least 4 units apart
            if abs(residue_1 - residue_2) >= 4:
                coordinates_1 = atom_info_list[i][3:6]
                coordinates_2 = atom_info_list[j][3:6]
                dist = euclidean_distance(coordinates_1, coordinates_2)
                distances.append(dist)
    return distances


# Function to extract atom information from a PDB line
def extract_atom_info(line):
    record_type = line[0:6].strip()
    if record_type == 'ATOM' or record_type == 'HETATM':
        atom_name = line[12:16].strip()
        residue_name = line[17:20].strip()
        residue_seq_num = line[23:26].strip()
        x_coord = float(line[30:38])
        y_coord = float(line[38:46])
        z_coord = float(line[46:54])
        return atom_name, residue_name, residue_seq_num, x_coord, y_coord, z_coord
    else:
        return None


def find_C3_atoms(file_path):
    atom_info_list = []

    # Read the file and extract atom information
    with open(file_path, 'r') as file:
        for line in file:
            atom_info = extract_atom_info(line)
            if atom_info:
                atom_name, residue_name, residue_seq_num, x, y, z = atom_info
                if atom_name == "C3'":
                    atom_info_list.append(atom_info)

    return atom_info_list


def calculate_base_pair_distances(atom_info_list):
    distances = []
    for i in range(len(atom_info_list)):
        for j in range(i + 1, len(atom_info_list)):
            residue_1 = int(atom_info_list[i][2])
            residue_2 = int(atom_info_list[j][2])
            base_pair_1 = atom_info_list[i][1]
            base_pair_2 = atom_info_list[j][1]

            # Ensure the residues are at least 4 units apart
            if abs(residue_1 - residue_2) >= 3 and str(base_pair_1 + base_pair_2) in considered_base_pair_names:
                coordinates_1 = atom_info_list[i][3:6]
                coordinates_2 = atom_info_list[j][3:6]
                dist = euclidean_distance(coordinates_1, coordinates_2)
                if dist <= 20:
                    base_pair_info = f"{base_pair_1}{base_pair_2}"
                    residue_info = f"{residue_1}-{residue_2}"
                    distances.append((base_pair_info, residue_info, dist))
    return distances


def observed_probability_calculator(distances):
    # Initialize a dictionary to store counts for each base pair
    all_distance_bin_counts = {}

    # Count occurrences of each base pair
    for base_pair, _, _ in distances:
        all_distance_bin_counts[base_pair] = all_distance_bin_counts.get(base_pair, 0) + 1

    # Initialize a list to store the results
    results = []

    # Loop through distance bins
    for i in range(20):
        distances_per_bin = {base_pair: 0 for base_pair, _, _ in distances}
        bin_start, bin_end = i, i + 1
        total_base_pairs = 0  # Variable to store the total number of base pairs in the bin

        # Loop through base pairs
        for base_pair, _, distance in distances:
            if bin_start < distance <= bin_end:
                distances_per_bin[base_pair] += 1
                total_base_pairs += 1

        # Add the results to the list
        for base_pair, count in distances_per_bin.items():
            observed_probability = count / all_distance_bin_counts[base_pair]
            results.append({
                'Distance Bin': f"{bin_start}-{bin_end}",
                'Base Pair': base_pair,
                'Observed Probability': observed_probability,
                'Total Base Pairs': total_base_pairs
            })

    # Create a DataFrame from the list of results
    observed_df = pd.DataFrame(results)

    return observed_df


def reference_frequency_calculator(observed_frequency_results):
    # Calculate reference frequency for each row in the DataFrame
    df = observed_frequency_results.copy()
    df['Reference Frequency'] = df['Total Base Pairs'] / df['Total Base Pairs'].sum()

    # Group by Distance Bin and calculate the total reference frequency for each bin
    total_reference_frequencies = df.groupby('Distance Bin')['Reference Frequency'].sum()

    # Create a DataFrame with Distance Bin and Reference Frequency
    reference_df = pd.DataFrame({
        'Distance Bin': total_reference_frequencies.index,
        'Reference Frequency': total_reference_frequencies.values
    })

    return reference_df


def calculate_pseudo_energy(observed_df, reference_df):
    # Merge the two DataFrames on the 'Distance Bin' column
    merged_df = pd.merge(observed_df, reference_df, on='Distance Bin', how='left')

    # Calculate Pseudo Energy for each row
    merged_df['Pseudo Energy'] = -np.log10(np.where(
        merged_df['Observed Probability'] != 0,
        merged_df['Observed Probability'] / merged_df['Reference Frequency'],
        np.nan  # Set a nan value for cases where observed probability is zero
    ))

    # Return the DataFrame with Pseudo Energy
    return merged_df[['Distance Bin', 'Base Pair', 'Pseudo Energy']]

def write_pseudo_energy_files(file_name, pseudo_energy_results, output_folder='output_files'):
    import os
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through each base pair and write the pseudo energy results to a text file
    for base_pair in pseudo_energy_results['Base Pair'].unique():
        base_pair_df = pseudo_energy_results[pseudo_energy_results['Base Pair'] == base_pair]
        file_path = os.path.join(output_folder, f'{base_pair}_{file_name}_pseudo_energy.txt')

        with open(file_path, 'w') as file:
            file.write("Distance Bin\tPseudo Energy\n")
            for _, row in base_pair_df.iterrows():
                file.write(f"{row['Distance Bin']}\t{row['Pseudo Energy']}\n")


# Directory containing molecular structure data
directory_path = './dataset'

# List all pdb files in the directory
pdb_files = [f for f in os.listdir(directory_path) if f.endswith('.pdb')]

# Iterate through each pdb file
for pdb_file in pdb_files:
    # Construct the full file path
    file_path = os.path.join(directory_path, pdb_file)

    # Find C3 atoms
    atom_info_list = find_C3_atoms(file_path)

    # Calculate base pair distances
    distances = calculate_base_pair_distances(atom_info_list)

    # Calculate observed probabilities
    a = observed_probability_calculator(distances)

    # Calculate reference frequencies
    b = reference_frequency_calculator(a)

    # Calculate pseudo energy
    c = calculate_pseudo_energy(a, b)

    # Write pseudo energy files
    output_folder = './output_files/'
    write_pseudo_energy_files(str(pdb_file), c, output_folder)
