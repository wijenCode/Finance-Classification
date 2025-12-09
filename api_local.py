# Using flask to make an api
# import necessary libraries and functions
from flask import Flask, jsonify, request
import time
import logging
from datetime import datetime
import joblib
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import os
import json

dir_path = os.path.dirname(os.path.realpath(__file__))

# Load all models
model_boosting = dir_path+'/model/finance_boosting_model.sav'
model_bagging = dir_path+'/model/finance_bagging_model.sav'
model_deep_learning = dir_path+'/model/finance_deep_learning_model.sav'

# Dictionary to store all classifiers
classifiers = {}

# Load models (with error handling for models that don't exist yet)
try:
    classifiers['boosting'] = joblib.load(model_boosting)
    print("✓ Boosting model loaded")
except FileNotFoundError:
    print("⚠ Boosting model not found")
    classifiers['boosting'] = None

try:
    classifiers['bagging'] = joblib.load(model_bagging)
    print("✓ Bagging model loaded")
except FileNotFoundError:
    print("⚠ Bagging model not found")
    classifiers['bagging'] = None

try:
    classifiers['deep_learning'] = joblib.load(model_deep_learning)
    print("✓ Deep Learning model loaded")
except FileNotFoundError:
    print("⚠ Deep Learning model not found")
    classifiers['deep_learning'] = None

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

# creating a Flask app
app = Flask(__name__)
  
# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/', methods = ['GET', 'POST'])
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
            
            # Encode 'Tipe' column: normal=0, hemat=1, boros=2
            tipe_mapping = {'hemat': 0, 'normal': 1, 'boros': 2}
            df['Tipe'] = df['Tipe'].map(tipe_mapping)
            
            print("After encoding:")
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
