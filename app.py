from flask import Flask, render_template, request, jsonify
import pandas as pd
import tensorflow as tf
from tensorflow import keras
#from tensorflow.keras.models import load_model
import joblib
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Add this line before importing pyplot
import matplotlib.pyplot as plt
import io
import base64
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_url_path='/static')

# Load the dataset
df = pd.read_csv('energy_consumption_dataset.csv')
df['datetime'] = pd.to_datetime(df['datetime'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forecast', methods=['POST'])
def forecast():
    try:
        start_date = pd.to_datetime(request.form['start_date'])
        end_date = pd.to_datetime(request.form['end_date'])
        floor = int(request.form['floor'])

        logging.debug(f"Received request for floor {floor} from {start_date} to {end_date}")

        # Filter data for the specified floor
        floor_data = df[df['floor'] == floor].set_index('datetime')
        floor_data = floor_data.resample('h')['energy_consumption'].sum()

        # Get the last date in the dataset
        last_data_date = floor_data.index.max()

        logging.debug(f"Last data date: {last_data_date}")

        # Check if we're predicting beyond the available data
        if end_date > last_data_date:
            # Use all available data for training
            train_data = floor_data
        else:
            # Use data up to the end_date for training
            train_data = floor_data.loc[:end_date]

        logging.debug(f"Training data shape: {train_data.shape}")

        model = keras.models.load_model(f'models/lstm_model_floor_{floor}.keras')
        scaler = joblib.load(f'models/scaler_floor_{floor}.pkl')

        # Scale the training data
        scaled_data = scaler.transform(train_data.values.reshape(-1, 1))

        # Generate predictions
        predictions = []
        input_sequence = scaled_data[-24:].reshape(1, 24, 1)

        current_date = max(start_date, last_data_date + pd.Timedelta(hours=1))
        dates = pd.date_range(current_date, end_date, freq='h')

        logging.debug(f"Generating predictions for {len(dates)} time steps")

        for _ in range(len(dates)):
            pred = model.predict(input_sequence, verbose=0)
            predictions.append(pred[0, 0])
            input_sequence = np.roll(input_sequence, -1, axis=1)
            input_sequence[0, -1, 0] = pred[0, 0]

        # Inverse transform predictions
        predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()

        logging.debug(f"Generated {len(predictions)} predictions")

        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        if start_date <= last_data_date:
            ax.plot(floor_data.loc[start_date:last_data_date].index, 
                    floor_data.loc[start_date:last_data_date].values, 
                    label='Actual', color='blue')
        ax.plot(dates, predictions, label='Predicted', color='red')
        ax.set_title(f'Energy Consumption Forecast - Floor {floor}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Energy Consumption (kWh)')
        ax.legend()

        # Save plot to memory
        img = io.BytesIO()
        fig.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        # Close the figure to free up memory
        plt.close(fig)

        logging.debug("Forecast generated successfully")

        return jsonify({
            'plot_url': f'data:image/png;base64,{plot_url}',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'last_data_date': last_data_date.strftime('%Y-%m-%d')
        })

    except Exception as e:
        logging.error(f"Error in forecast function: {str(e)}", exc_info=True)
        return jsonify({'error': f'An error occurred while fetching the forecast: {str(e)}. Please try again.'}), 500

@app.route('/visualize')
def visualize():
    try:
        # Load the dataset
        df = pd.read_csv('energy_consumption_dataset.csv')
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Group by floor and date, then sum the energy consumption
        daily_consumption = df.groupby(['floor', df['datetime'].dt.date])['energy_consumption'].sum().reset_index()
        
        # Convert date to string to avoid Timestamp key issues
        daily_consumption['datetime'] = daily_consumption['datetime'].astype(str)
        
        # Create a dictionary with floor numbers as keys and lists of [date, consumption] as values
        floor_data = {}
        for floor in daily_consumption['floor'].unique():
            floor_df = daily_consumption[daily_consumption['floor'] == floor]
            # Convert numpy.int64 to regular Python int
            floor_key = int(floor)
            # Ensure dates are in ISO format
            floor_data[floor_key] = floor_df[['datetime', 'energy_consumption']].apply(
                lambda row: [row['datetime'], float(row['energy_consumption'])], axis=1
            ).tolist()
        
        app.logger.debug(f"Visualization data prepared: {floor_data}")
        return jsonify(floor_data)
    except Exception as e:
        app.logger.error(f"Error in /visualize route: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
