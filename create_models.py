import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib
import sys

# Set default encoding to UTF-8 to handle special characters in output
sys.stdout.reconfigure(encoding='utf-8')

def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:(i + seq_length)])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

def create_lstm_model(X_train, y_train, X_test, y_test):
    model = Sequential([
        LSTM(100, activation='relu', return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.2),
        LSTM(50, activation='relu'),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    
    # Set verbose to 2 to avoid printing special characters
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), verbose=2)
    
    return model

# Load the dataset
df = pd.read_csv('energy_consumption_dataset.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.set_index('datetime')

# Create models for each floor
for floor in df['floor'].unique():
    print(f"Creating model for Floor {floor}")
    
    # Filter data for the current floor
    floor_data = df[df['floor'] == floor].resample('h')['energy_consumption'].sum()  # Use lowercase 'h' for hours
    
    # Normalize the data
    scaler = MinMaxScaler()
    floor_data_scaled = scaler.fit_transform(floor_data.values.reshape(-1, 1))
    
    # Create sequences
    seq_length = 24  # Use 24 hours of data to predict the next hour
    X, y = create_sequences(floor_data_scaled, seq_length)
    
    # Split into train and test sets
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Create and train the model
    model = create_lstm_model(X_train, y_train, X_test, y_test)
    
    # Make predictions
    train_predict = model.predict(X_train)
    test_predict = model.predict(X_test)
    
    # Inverse transform predictions
    train_predict = scaler.inverse_transform(train_predict)
    y_train = scaler.inverse_transform(y_train.reshape(-1, 1))
    test_predict = scaler.inverse_transform(test_predict)
    y_test = scaler.inverse_transform(y_test.reshape(-1, 1))
    
    # Calculate RMSE
    train_rmse = np.sqrt(mean_squared_error(y_train, train_predict))
    test_rmse = np.sqrt(mean_squared_error(y_test, test_predict))
    print(f"Train RMSE: {train_rmse:.2f}")
    print(f"Test RMSE: {test_rmse:.2f}")
    
    # Save the model and scaler
    model.save(f'models\\lstm_model_floor_{floor}.keras') #templates\index.html
    joblib.dump(scaler, f'scaler_floor_{floor}.pkl')

print("All models created and saved successfully!")
