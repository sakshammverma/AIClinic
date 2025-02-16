print("Starting the mapping generation script...")
import pandas as pd
import pickle
import os

# Define paths
DATA_DIR = 'data'
MODEL_DIR = 'models'
CSV_FILE = 'datasets/symptoms_df.csv'

OUTPUT_FILE = os.path.join(MODEL_DIR, 'symptom_mapping.pkl')

# Load the CSV file
# Assuming the CSV file doesn't have a header.
df = pd.read_csv(CSV_FILE, header=None)

# Assuming the CSV structure: id, disease, symptom1, symptom2, symptom3, symptom4, symptom5
num_symptoms = df.shape[1] - 2  # all columns minus id and disease
column_names = ['id', 'disease'] + [f'symptom{i+1}' for i in range(num_symptoms)]
df.columns = column_names

# Clean up: strip extra spaces and convert to lowercase
df['disease'] = df['disease'].str.strip().str.lower()

# Create a set of unique symptoms
unique_symptoms = set()
for col in column_names[2:]:
    # Drop NaN values, strip whitespace and convert to lowercase
    symptoms = df[col].dropna().str.strip().str.lower().tolist()
    unique_symptoms.update(symptoms)

# Sort the symptoms to have a consistent order and create a mapping (symptom -> index)
symptoms_list = sorted(unique_symptoms)
symptoms_dict = {symptom: idx for idx, symptom in enumerate(symptoms_list)}

# Optionally, create a disease mapping as well (disease -> index)
unique_diseases = sorted(df['disease'].unique())
disease_dict = {disease: idx for idx, disease in enumerate(unique_diseases)}

# Combine the mappings into one dictionary
mappings = {
    'symptoms_dict': symptoms_dict,
    'disease_dict': disease_dict
}

# Ensure the models directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Save the mapping dictionary to a pickle file for later use
with open(OUTPUT_FILE, 'wb') as f:
    pickle.dump(mappings, f)

print("Mapping saved successfully!")
print("Symptom Mapping:", symptoms_dict)
print("Disease Mapping:", disease_dict)
