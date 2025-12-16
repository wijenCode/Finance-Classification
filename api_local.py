# Using flask to make an api
# import necessary libraries and functions
from flask import Flask, jsonify, request, render_template
import time
import logging
from datetime import datetime
import joblib
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import xgboost as xgb
import pandas as pd
import numpy as np
import os
import json
import io

dir_path = os.path.dirname(os.path.realpath(__file__))

# Load all models
model_boosting = dir_path+'/model/finance_boosting_model.sav'
model_bagging = dir_path+'/model/finance_bagging_model.sav'
model_voting = dir_path+'/model/finance_voting_model.sav'

# Dictionary to store all classifiers
classifiers = {}
boosting_model = None
bagging_model = None
voting_model = None

# Load models (with error handling for models that don't exist yet)
try:
    boosting_model = joblib.load(model_boosting)
    classifiers['boosting'] = boosting_model
    print("✓ Boosting model loaded")
except FileNotFoundError:
    print("⚠ Boosting model not found")
    classifiers['boosting'] = None
except Exception as e:
    print(f"⚠ Error loading Boosting model: {str(e)}")
    classifiers['boosting'] = None

try:
    bagging_model = joblib.load(model_bagging)
    classifiers['bagging'] = bagging_model
    print("✓ Bagging model loaded")
except FileNotFoundError:
    print("⚠ Bagging model not found")
    classifiers['bagging'] = None
except Exception as e:
    print(f"⚠ Error loading Bagging model: {str(e)}")
    classifiers['bagging'] = None

# Load Voting Classifier from file
try:
    voting_model = joblib.load(model_voting)
    classifiers['voting'] = voting_model
    print("✓ Voting model loaded")
except FileNotFoundError:
    print("⚠ Voting model not found")
    classifiers['voting'] = None
except Exception as e:
    print(f"⚠ Error loading Voting model: {str(e)}")
    classifiers['voting'] = None

scaler_finance = dir_path+'/model/scaler_finance.sav'
scaler_finance = joblib.load(scaler_finance)
print("✓ Scaler loaded")

def getLabel(x):
    if(x==0):
        res='Rawan Finansial'
    elif(x==1):
        res='Menengah Stabil'
    elif(x==2):
        res='Sehat Finansial'
    else:
        res='Unknown'
    return res

def reorder_features(df):
    """
    Reorder features according to feature selection order.
    Original order (user input) -> Feature selection order (model training)
    """
    # Urutan yang benar sesuai seleksi fitur
    correct_order = [
        'Tabungan / Investasi',
        'Pengeluaran Tidak Esensial',
        'Tempat Tinggal',
        'Tabungan Lama',
        'Investasi',
        'Pemasukan Lainnya',
        'Tipe',
        'Barang & Jasa Sekunder',
        'Sosial & Budaya',
        'Pajak',
        'Konsumsi Praktis',
        'Protein & Gizi Tambahan',
        'Asuransi',
        'Bahan Pokok',
        'Gaji',
        'Sandang'
    ]
    return df[correct_order]

# creating a Flask app
app = Flask(__name__)
  
# Web routes for HTML pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# API routes
# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/api', methods = ['GET', 'POST'])
def home():
    if(request.method == 'GET'):
  
        data = "Welcome to Finance Classification API"
        return jsonify({'data': data})
  
  
# A simple function to calculate the square of a number
# the number to be squared is sent in the URL when we use GET
# on the terminal type: curl http://127.0.0.1:5000 / home / 10
# this returns 100 (square of 10)
@app.route('/home/<int:num>', methods = ['GET'])
def disp(num):
    return jsonify({'data': num**2})


@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    """Handle CSV file upload for batch prediction"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be CSV format'}), 400
        
        # Get selected model
        selected_model = request.form.get('model', 'boosting').lower()
        
        # Validate model selection
        if selected_model not in classifiers:
            return jsonify({'error': f'Invalid model: {selected_model}'}), 400
        
        if classifiers.get(selected_model) is None:
            available_models = [k for k, v in classifiers.items() if v is not None]
            return jsonify({
                'error': f'Model {selected_model.upper()} is not available.',
                'available_models': available_models
            }), 400
        
        # Read CSV file
        df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))
        
        # Expected columns
        expected_columns = ['Gaji', 'Tabungan Lama', 'Investasi', 'Pemasukan Lainnya', 
                           'Tipe', 'Bahan Pokok', 'Protein & Gizi Tambahan', 
                           'Tempat Tinggal', 'Sandang', 'Konsumsi Praktis', 
                           'Barang & Jasa Sekunder', 'Pengeluaran Tidak Esensial', 
                           'Pajak', 'Asuransi', 'Sosial & Budaya', 'Tabungan / Investasi']
        
        # Validate columns
        missing_cols = set(expected_columns) - set(df.columns)
        if missing_cols:
            return jsonify({'error': f'Missing columns: {list(missing_cols)}'}), 400
        
        # Select only needed columns in correct order
        df = df[expected_columns]
        
        # Encode 'Tipe' column: hemat=0, normal=1, boros=2
        tipe_mapping = {'hemat': 0, 'normal': 1, 'boros': 2}
        df['Tipe'] = df['Tipe'].map(tipe_mapping)
        
        # Reorder features sesuai urutan seleksi fitur
        df = reorder_features(df)
        
        print("DataFrame after reordering:")
        print(df.head())
        
        # Scale features
        features = scaler_finance.transform(df)
        
        # Predict
        classifier = classifiers[selected_model]
        predictions = classifier.predict(features)
        
        # Build results
        results = []
        for i, pred in enumerate(predictions):
            cluster_label = getLabel(pred)
            results.append({
                'row': i + 1,
                'cluster': int(pred),
                'cluster_label': cluster_label
            })
        
        return jsonify({
            'total_rows': len(results),
            'model_used': selected_model.upper(),
            'predictions': results
        })
        
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
  

@app.route('/finance_classification', methods=['POST'])
def process_json():
    content_type = request.headers.get('Content-Type')
    print(content_type)
    if (content_type == 'application/json'):
        try:
            json_req = request.json
            data=[]
            for i in json_req['data']:
                data.append(i)
            
            # Get selected model (default to boosting if not specified)
            selected_model = json_req.get('model', 'boosting').lower()
            
            # Validate model selection
            if selected_model not in classifiers:
                return jsonify({'error': f'Invalid model: {selected_model}. Choose from: boosting, bagging, deep_learning'}), 400
            
            if classifiers[selected_model] is None:
                return jsonify({'error': f'Model {selected_model} is not available. Please train it first.'}), 400
            
            print(f"Using model: {selected_model}")
              
            #print(data)  
            df = pd.DataFrame(data, columns = ['Gaji', 'Tabungan Lama', 'Investasi', 'Pemasukan Lainnya', 
                                                'Tipe', 'Bahan Pokok', 'Protein & Gizi Tambahan', 
                                                'Tempat Tinggal', 'Sandang', 'Konsumsi Praktis', 
                                                'Barang & Jasa Sekunder', 'Pengeluaran Tidak Esensial', 
                                                'Pajak', 'Asuransi', 'Sosial & Budaya', 'Tabungan / Investasi'])
            print("Original DataFrame:")
            print(df)
            
            # Encode 'Tipe' column: hemat=0, normal=1, boros=2
            tipe_mapping = {'hemat': 0, 'normal': 1, 'boros': 2}
            df['Tipe'] = df['Tipe'].map(tipe_mapping)
            
            print("After encoding:")
            print(df)
            
            # Reorder features sesuai urutan seleksi fitur
            df = reorder_features(df)
            
            print("After reordering features:")
            print(df)
            
            features = scaler_finance.transform(df)
            #print(features)
            hasil = pd.DataFrame(columns = ['cluster', 'cluster_label', 'model_used'])
            
            # Use selected classifier
            classifier = classifiers[selected_model]
            
            for feat in features:
                feat = np.array([feat])
                print(feat)
                finance_cluster = classifier.predict(feat)
                cluster_label = getLabel(finance_cluster[0])
                print(f"Model: {selected_model}, Cluster: {finance_cluster[0]}, Label: {cluster_label}")
                new_row = {
                    'cluster': int(finance_cluster[0]), 
                    'cluster_label': cluster_label,
                    'model_used': selected_model.upper()
                }
                #hasil = hasil.append(new_row,ignore_index=True)
                hasil = pd.concat([hasil, pd.DataFrame([new_row])], ignore_index=True) 
            #json_rep = {'cluster':finance_cluster,'cluster_label':cluster_label}
            json_rep = hasil.to_json(orient='index')
            print(json_rep)
            return json_rep
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    else:
        return 'Content-Type not supported!'
  
# driver function
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Finance Classification API Server")
    print("="*60)
    print(f"Available models:")
    for model_name, model_obj in classifiers.items():
        status = "✓ Ready" if model_obj is not None else "✗ Not available"
        print(f"  - {model_name.upper()}: {status}")
    print("="*60 + "\n")
    
    #website_url = '10.251.251.169:8080'
    website_url = 'localhost:8080'
    app.config['SERVER_NAME'] = website_url
    app.run()
