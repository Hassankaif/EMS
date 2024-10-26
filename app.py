from flask import Flask, render_template, request, jsonify
import pandas as pd
import tensorflow
from tensorflow.keras.models import load_model
import joblib
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('energy_consumption_dataset.csv')
df['datetime'] = pd.to_datetime(df['datetime'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forecast', methods=['POST'])
def forecast():
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    floor = request.form['floor']
    
    # floor_data = df[df['floor'] == floor].set_index('datetime')
    # floor_data = floor_data.resample('h')['energy_consumption'].sum()
    # floor_data = floor_data.loc[start_date:end_date]
    floor_data = df[df['floor'] == floor].set_index('datetime')
    floor_data = floor_data.resample('h')['energy_consumption'].sum()
    floor_data = floor_data.loc[start_date:end_date]
    # Check if the data is empty
    if floor_data.empty:
        return jsonify({"error": "No data available for the selected floor and date range."}), 400


    
    model = load_model(f'models\\lstm_model_floor_{floor}.keras')#models\lstm_model_floor_1.keras
    scaler = joblib.load(f'models\\scaler_floor_{floor}.pkl')
    
    # Prepare data for prediction
    scaled_data = scaler.transform(floor_data.values.reshape(-1, 1))
    X = np.array([scaled_data[i-24:i] for i in range(24, len(scaled_data))])
    
    # Make predictions
    predictions = model.predict(X)
    predictions = scaler.inverse_transform(predictions)
    
    # Create plot
    plt.figure(figsize=(12, 6))
    plt.plot(floor_data.index[24:], floor_data.values[24:], label='Actual')
    plt.plot(floor_data.index[24:], predictions, label='Predicted')
    plt.title(f'Predicted vs Actual Energy Consumption - Floor {floor}')
    plt.xlabel('Date')
    plt.ylabel('Energy Consumption (kWh)')
    plt.legend()
    
    # Save plot to memory
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    
    return jsonify({'plot_url': plot_url})

@app.route('/visualize')
def visualize():
    floor_wise_consumption = df.groupby(['floor', 'datetime'])['energy_consumption'].sum().reset_index()
    floor_wise_consumption = floor_wise_consumption.pivot(index='datetime', columns='floor', values='energy_consumption')
    
    appliance_wise_consumption = df.groupby('appliance')['energy_consumption'].sum().sort_values(ascending=False)
    
    floor_appliance_consumption = df.pivot_table(values='energy_consumption', index='floor', columns='appliance', aggfunc='sum')
    
    hourly_consumption = df.groupby(df['datetime'].dt.hour)['energy_consumption'].mean()
    
    return jsonify({
        'floor_wise_consumption': floor_wise_consumption.to_dict(),
        'appliance_wise_consumption': appliance_wise_consumption.to_dict(),
        'floor_appliance_consumption': floor_appliance_consumption.to_dict(),
        'hourly_consumption': hourly_consumption.to_dict()
    })

if __name__ == '__main__':
    app.run(debug=True)