print("Starting the mapping generation script...")
import pandas as pd
import pickle
import os

# Define paths
DATA_DIR = 'data'
MODEL_DIR = 'models'
CSV_FILE = 'datasets/symptoms_df.csv'

OUTPUT_FILE = os.path.join(MODEL_DIR, 'symptom_mapping.pkl')

 
df = pd.read_csv(CSV_FILE, header=None)
 
num_symptoms = df.shape[1] - 2  # all columns minus id and disease
column_names = ['id', 'disease'] + [f'symptom{i+1}' for i in range(num_symptoms)]
df.columns = column_names
 
df['disease'] = df['disease'].str.strip().str.lower()

# Create a set of unique symptoms
unique_symptoms = set()
for col in column_names[2:]:
    # Drop NaN values, strip whitespace and convert to lowercase
    symptoms = df[col].dropna().str.strip().str.lower().tolist()
    unique_symptoms.update(symptoms)
 
symptoms_list = sorted(unique_symptoms)
symptoms_dict = {symptom: idx for idx, symptom in enumerate(symptoms_list)}
 
unique_diseases = sorted(df['disease'].unique())
disease_dict = {disease: idx for idx, disease in enumerate(unique_diseases)}
 
mappings = {
    'symptoms_dict': symptoms_dict,
    'disease_dict': disease_dict
}
 
os.makedirs(MODEL_DIR, exist_ok=True)

 
with open(OUTPUT_FILE, 'wb') as f:
    pickle.dump(mappings, f)

print("Mapping saved successfully!")
print("Symptom Mapping:", symptoms_dict)
print("Disease Mapping:", disease_dict)

