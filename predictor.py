import os
import pandas as pd
import joblib
from main import find_C3_atoms, calculate_base_pair_distances

def distance_bin_calculator(distances):
    result_list = []

    # Loop through distance bins
    for i in range(20):
        bin_start, bin_end = i, i + 1

        # Loop through base pairs
        for base_pair, _, distance in distances:
            if bin_start < distance <= bin_end:
                result_list.append({
                    'Distance Bin': f"{bin_start}-{bin_end}",
                    'Base Pair': base_pair,
                })

    # Create a DataFrame from the list of results
    result_df = pd.DataFrame(result_list)

    return result_df


directory_path = './unknown_instances/'
results_dir = './results/'

# Check if the "results" directory exists, and create it if not
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

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
    working_data = distance_bin_calculator(distances)

    # Load the saved model and label encoders
    model_filename = 'pseudo_energy_evaluator.joblib'
    model, le_base_pair, le_distance_bin = joblib.load(model_filename)

    input_data = working_data.copy()  # Make a copy to avoid modifying the original DataFrame

    # Transform categorical features using label encoders
    input_data['Base Pair'] = le_base_pair.transform(input_data['Base Pair'])
    input_data['Distance Bin'] = le_distance_bin.transform(input_data['Distance Bin'])

    # Make predictions using the loaded model
    predictions = model.predict(input_data[['Base Pair', 'Distance Bin']])

    # Add the predictions to the input_data DataFrame
    input_data['Pseudoenergy Prediction'] = predictions

    # Inverse transform numeric labels back to original categorical values
    input_data['Base Pair'] = le_base_pair.inverse_transform(input_data['Base Pair'])
    input_data['Distance Bin'] = le_distance_bin.inverse_transform(input_data['Distance Bin'])

    #calculate the Gibbs free energy by summing all the predictions and add to data frame
    gibbs_free_energy = sum(input_data['Pseudoenergy Prediction'])

    # Print the predictions along with 'Base Pair' information
    result_file_name = str(pdb_file)
    output_file_path = f'./results/{result_file_name}_pseudo_energy.txt'
    input_data[['Base Pair', 'Distance Bin', 'Pseudoenergy Prediction']].to_csv(output_file_path, index=False, sep='\t')
    print(f"Results written to {output_file_path}")

    with open(output_file_path, 'a') as file:
        file.write(f"\n Resulting Gibbs free energy: {gibbs_free_energy}")



