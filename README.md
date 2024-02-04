# RNA folding problem
The objective of this project is to propose an interpolative solution to the RNA folding problem. The project itself is composed of three scripts. Below will be a more detailed description of each of the scripts and a short tutorial on how to use the code.

## Quick-start guide

1. Put your sample .pdb files in the `./dataset` directory
2. Run the first script - main.py in order to generate pseudo energy and distance calculations. Results will be found in the `./output_files` directory.
3. Run the second script - Inperaction_profiler.py in order to train the regression model and generate line plots of the results from the previous step. The resulting plots can be found in the `./figures` directory.
4. Put the .pdb files for which you want to generate structural predictions to the `./unknown_instances` directory.
5. Run the thirds script - predictor.py to calculate predictions for Gibbs free energy. The results can be found in the `./results` directory.

Sample instances of all files can be found in all mentioned directories, and should be deleted before usage. The script does not automatically delete old files in case input directories are changed - be shure to clean the folders of unused or unwanted results.

# Pseudo Energy Calculation from Molecular Structures

This script calculates pseudo energy values based on distances between specific atoms in molecular structures provided in PDB format. The calculated pseudo energy values are derived from observed probabilities and reference frequencies.

## Overview

The script performs the following steps:

1. **Find C3 Atoms:** Extracts information about C3 atoms from the provided PDB file.

2. **Calculate Base Pair Distances:** Determines distances between base pairs in the molecular structure, considering only pairs that are at least 3 places apart.

3. **Calculate Observed Probabilities:** Calculates observed probabilities for each base pair in different distance bins.

4. **Calculate Reference Frequencies:** Computes reference frequencies for each distance bin based on total occurrences of base pairs.

5. **Calculate Pseudo Energy:** Derives pseudo energy values by comparing observed probabilities to reference frequencies.

6. **Write Pseudo Energy Files:** Outputs pseudo energy values to individual text files for each base pair.

## Dependencies

- Python 3.x
- NumPy
- Pandas
- Math

# Interaction profiler

This script is used to train a regression model on the prediction of pseudo energy values for each base pair and distance bin. The data is derived from text files containing information about base pairs and their corresponding pseudo energy values, generated with the main.py script.

## Overview

The script performs the following steps:

1. **Train Model:** Creates a data frame from the output files of the first script and divides the dataset into a train and validation subset. The model is saved for further usage.
2. **Generate Line Plots:** Generates line plot representations of the dataset for each base pair, and each file. Results are saved as .png files, and contain information about base pair and origin .pdb file in file name.
3. **Save Line Plot Files:** Outputs the line plot .png files.

The result is organized as follows:

- `figures/`: Stores line plots depicting the relationship between pseudo energy and distance bins.
- `pseudo_energy_evaluator.joblib`: Trained machine learning model for predicting pseudo energy.

## Dependencies

- Python 3.x
- NumPy
- Pandas
- Matplotlib
- scikit-learn

# Predictor

This script is used to predict final Gibbs free energy values for an unknown group of one or more .pdb file instances, using the results of the previous scripts and the model for energy prediction. The Gibbs free energy is given as a sum of all pseudo energy values for all predicted base pairs.

## Overview

The script achieves:

1. **Find C3 Atoms:** Extracts information about C3 atoms from the provided PDB file.
2. **Distance Bin Calculation:**  Determines distances between base pairs in the molecular structure, considering only pairs that are at least 3 places apart.
3. **Pseudo Evergy Prediction:** Predicts pseudo energy of each pair and distance bin using the trained model.
4. **Gibbs Free Energy Calculation:** Calculates Gibbs free energy by summing all the predictions.
5. **Writes a File To Save Results:** Outputs a .txt file for each .pdb structure.

## Dependencies

- Python 3.x
- Pandas
- scikit-learn






