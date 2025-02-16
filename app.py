from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Configure directories
MODEL_DIR = 'models'
DATA_DIR = 'datasets'

# ---------------------------------------------------
# Load Mapping and CSV Data at Application Startup
# ---------------------------------------------------

# Load the symptom and disease mappings generated via generate_mapping.py
try:
    mapping_path = os.path.join(MODEL_DIR, 'symptom_mapping.pkl')
    with open(mapping_path, 'rb') as f:
        mappings = pickle.load(f)
        symptoms_dict = mappings['symptoms_dict']   # e.g., {'chills': 0, 'vomiting': 1, ...}
        disease_dict = mappings['disease_dict']       # e.g., {'typhoid': 0, 'hepatitis a': 1, ...}
except Exception as e:
    print("Error loading mapping file:", str(e))
    raise

# Load the CSV that lists diseases and their symptoms.
# Assumes CSV format: id,disease,symptom1,symptom2, ... 
symptoms_csv_path = 'C:/Users/saksh/OneDrive/Desktop/AIClinic/datasets/symptoms_df.csv'

symptoms_df = pd.read_csv(symptoms_csv_path, header=None)
num_symptoms = symptoms_df.shape[1] - 2  # Exclude id and disease columns
column_names = ['id', 'disease'] + [f'symptom{i+1}' for i in range(num_symptoms)]
symptoms_df.columns = column_names
# Normalize disease names and symptoms to lower case and strip extra spaces.
symptoms_df['disease'] = symptoms_df['disease'].str.strip().str.lower()
for col in column_names[2:]:
    symptoms_df[col] = symptoms_df[col].astype(str).str.strip().str.lower()

# Load additional CSV files containing extra disease information.
description = pd.read_csv(os.path.join(DATA_DIR, 'description.csv'))
precautions = pd.read_csv(os.path.join(DATA_DIR, 'precautions_df.csv'))
medications = pd.read_csv(os.path.join(DATA_DIR, 'medications.csv'))
diets = pd.read_csv(os.path.join(DATA_DIR, 'diets.csv'))
workout = pd.read_csv(os.path.join(DATA_DIR, 'workout_df.csv'))

# ---------------------------------------------------
# Utility Functions
# ---------------------------------------------------

def get_disease_info(disease_name):
    """
    Retrieve extra information for a given disease from the CSV datasets.
    Assumes disease names are stored in lower case.
    """
    try:
        disease_lower = disease_name.strip().lower()
        
        # Get description
        desc_series = description[description['Disease'].str.lower() == disease_lower]['Description']
        desc = desc_series.values[0] if not desc_series.empty else "No description available."
        
        # Get precautions (assuming the first column is 'Disease')
        prec_row = precautions[precautions['Disease'].str.lower() == disease_lower]
        if not prec_row.empty:
            # Exclude the 'Disease' column and drop NaN values.
            prec = prec_row.iloc[0, 1:].dropna().tolist()
        else:
            prec = ["No precautions available."]
        
        # Get medications
        meds_series = medications[medications['Disease'].str.lower() == disease_lower]['Medication']
        meds = meds_series.tolist() if not meds_series.empty else ["No medication info available."]
        
        # Get diets
        diet_series = diets[diets['Disease'].str.lower() == disease_lower]['Diet']
        diet = diet_series.tolist() if not diet_series.empty else ["No diet recommendation available."]
        
        # Get workouts (assuming workout_df has columns: 'disease' and 'workout')
        workout_series = workout[workout['disease'].str.lower() == disease_lower]['workout']
        workouts = workout_series.tolist() if not workout_series.empty else ["No workout recommendation available."]
        
        return {
            'description': desc,
            'precautions': prec,
            'medications': meds,
            'diets': diet,
            'workouts': workouts
        }
    except Exception as e:
        print(f"Error retrieving info for {disease_name}: {str(e)}")
        return None

def simple_predict(patient_symptoms):
    """
    A simple algorithm to 'predict' a disease based on the number of matching symptoms.
    Iterates over each disease in the symptoms dataframe, counts the number of matching
    symptoms from the input, and returns the disease with the highest match count.
    """
    max_matches = 0
    predicted_disease = None
    
    for _, row in symptoms_df.iterrows():
        # Get the list of symptoms for the current disease
        disease_symptoms = [row[col] for col in column_names[2:]]
        # Count how many input symptoms match
        matches = sum(1 for s in patient_symptoms if s in disease_symptoms)
        if matches > max_matches:
            max_matches = matches
            predicted_disease = row['disease']
    
    return predicted_disease

# ---------------------------------------------------
# Flask Routes
# ---------------------------------------------------

@app.route('/')
def home():
    # Render a simple form (ensure you have a corresponding templates/index.html)
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Retrieve input symptoms from the JSON request body
        data = request.get_json()
        symptoms_input = data.get('symptoms', '')
        
        if not symptoms_input:
            return jsonify({"error": "Please enter symptoms"}), 400
        
        # Process input: split on commas, strip whitespace, and convert to lower case.
        patient_symptoms = [s.strip().lower() for s in symptoms_input.split(',')]
        
        # Predict the disease
        predicted_disease = simple_predict(patient_symptoms)
        
        if not predicted_disease:
            return jsonify({"error": "No matching disease found"}), 400

        # Get extra information about the predicted disease
        disease_info = get_disease_info(predicted_disease)
        
        return jsonify({
            'disease': predicted_disease,
            'description': disease_info['description'],
            'precautions': disease_info['precautions'],
            'medications': disease_info['medications'],
            'workouts': disease_info['workouts'],
            'diets': disease_info['diets']
        })
    
    except Exception as e:
        print("Error in prediction:", str(e))
        return jsonify({"error": "An error occurred while processing the prediction."}), 500

# ---------------------------------------------------
# Run the Application
# ---------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
