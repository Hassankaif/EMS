import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow.keras.models import load_model
import joblib
import numpy as np

# Load the dataset
df = pd.read_csv('energy_consumption_dataset.csv')
df['datetime'] = pd.to_datetime(df['datetime'])

def floor_wise_energy_consumption():
    plt.figure(figsize=(12, 6))
    for floor in df['floor_no'].unique():
        floor_data = df[df['floor_no'] == floor].set_index('datetime')
        floor_data = floor_data.resample('D')['energy_consumption'].sum()
        plt.plot(floor_data.index, floor_data.values, label=f'Floor {floor}')
    plt.title('Floor-wise Energy Consumption')
    plt.xlabel('Date')
    plt.ylabel('Energy Consumption (kWh)')
    plt.legend()
    plt.savefig('floor_wise_consumption.png')
    plt.close()

def appliance_wise_energy_consumption():
    appliance_consumption = df.groupby('appliance_name')['energy_consumption'].sum().sort_values(ascending=False)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=appliance_consumption.index, y=appliance_consumption.values)
    plt.title('Appliance-wise Energy Consumption')
    plt.xlabel('Appliance')
    plt.ylabel('Energy Consumption (kWh)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('appliance_wise_consumption.png')
    plt.close()

def floor_appliance_wise_energy_consumption():
    pivot_data = df.pivot_table(values='energy_consumption', index='floor_no', columns='appliance_name', aggfunc='sum')
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_data, annot=True, fmt='.0f', cmap='YlOrRd')
    plt.title('Floor and Appliance-wise Energy Consumption')
    plt.xlabel('Appliance')
    plt.ylabel('Floor')
    plt.tight_layout()
    plt.savefig('floor_appliance_wise_consumption.png')
    plt.close()

def hourly_consumption_pattern():
    df['hour'] = df['datetime'].dt.hour
    hourly_consumption = df.groupby('hour')['energy_consumption'].mean()
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=hourly_consumption.index, y=hourly_consumption.values)
    plt.title('Average Hourly Energy Consumption Pattern')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Average Energy Consumption (kWh)')
    plt.savefig('hourly_consumption_pattern.png')
    plt.close()

def predicted_vs_actual_consumption(floor, start_date, end_date):
    floor_data = df[df['floor_no'] == floor].set_index('datetime')
    floor_data = floor_data.resample('H')['energy_consumption'].sum()
    floor_data = floor_data.loc[start_date:end_date]
    
    model = load_model(f'lstm_model_floor_{floor}.h5')
    scaler = joblib.load(f'scaler_floor_{floor}.pkl')
    
    # Prepare data for prediction
    scaled_data = scaler.transform(floor_data.values.reshape(-1, 1))
    X = np.array([scaled_data[i-24:i] for i in range(24, len(scaled_data))])
    
    # Make predictions
    predictions = model.predict(X)
    predictions = scaler.inverse_transform(predictions)
    
    # Plot actual vs predicted
    plt.figure(figsize=(12, 6))
    plt.plot(floor_data.index[24:], floor_data.values[24:], label='Actual')
    plt.plot(floor_data.index[24:], predictions, label='Predicted')
    plt.title(f'Predicted vs Actual Energy Consumption - Floor {floor}')
    plt.xlabel('Date')
    plt.ylabel('Energy Consumption (kWh)')
    plt.legend()
    plt.savefig(f'predicted_vs_actual_floor_{floor}.png')
    plt.close()

# Generate visualizations
floor_wise_energy_consumption()
appliance_wise_energy_consumption()
floor_appliance_wise_energy_consumption()
hourly_consumption_pattern()

# Example usage of predicted_vs_actual_consumption
predicted_vs_actual_consumption(floor='Ground Floor', start_date='2023-06-01', end_date='2023-06-30')

print("All visualizations created successfully!")

export default function Component() {
  return (
    <div className="bg-gray-100 p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">Visualization Script</h2>
      <p className="mb-4">
        This script creates various visualizations for energy consumption data.
      </p>
      <ul className="list-disc list-inside mb-4">
        <li>Floor-wise energy consumption over time</li>
        <li>Appliance-wise total energy consumption</li>
        <li>Floor and appliance-wise energy consumption heatmap</li>
        <li>Average hourly energy consumption pattern</li>
        <li>Predicted  vs actual energy consumption for a specific floor and date range</li>
      </ul>
      <p className="text-sm text-gray-600">
        Note: Make sure to run this script after creating the dataset and training the models.
      </p>
    </div>
  )
}