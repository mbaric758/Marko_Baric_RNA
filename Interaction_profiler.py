import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
import joblib

# Path to the folder containing the text files
folder_path = './output_files'

#path to save output figures
figures_dir = "./figures"

# Check if the "figures" directory exists, and create it if not
if not os.path.exists(figures_dir):
    os.makedirs(figures_dir)

# List all text files in the folder
txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]


# Function to train the machine learning model
def train_model(data):
    # create label encoders for the base pairs and distance bins
    le_base_pair = LabelEncoder()
    le_distance_bin = LabelEncoder()

    # Transform base pair and distance bin names into numerical labels
    data['Base Pair'] = le_base_pair.fit_transform(data['Base Pair'])
    data['Distance Bin'] = le_distance_bin.fit_transform(data['Distance Bin'])

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        data[['Base Pair', 'Distance Bin']], data['Pseudo Energy'], test_size=0.2, random_state=42
    )

    # Train a Random Forest Regressor model, based of regression and interpolative prediction
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error on Test Set: {mse}')

    # Save the trained model
    model_filename = 'pseudo_energy_evaluator.joblib'
    joblib.dump((model, le_base_pair, le_distance_bin), model_filename)


# Initialize an empty DataFrame to store all data
all_data = pd.DataFrame()

# Iterate through each text file and create line plots
for txt_file in txt_files:
    # extract base pair name from file title
    base_pair = txt_file.split('_')[0]

    # Read the data from the text file
    file_path = os.path.join(folder_path, txt_file)
    data = pd.read_csv(file_path, delimiter='\t')

    # Treat nan values as 0
    data['Pseudo Energy'] = data['Pseudo Energy'].fillna(0)
    data['Base Pair'] = base_pair

    # Append data to the overall DataFrame
    all_data = pd.concat([all_data, data], ignore_index=True)

    # Create a line plot with numeric x-axis
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Pseudo Energy'], marker='o', linestyle='-')  # Line plot
    plt.title(f"Pseudo Energy as a Function of Distance - {txt_file[:-4]}")
    plt.xlabel("Distance Bin")
    plt.ylabel("Pseudo Energy")

    # Set x-axis ticks and labels
    plt.xticks(data.index, data['Distance Bin'], rotation=45, ha="right")

    plt.savefig(os.path.join(figures_dir, f"{txt_file[:-4]}_line_plot.png"))
    plt.close()

# Train the model using the accumulated data
train_model(all_data)
