import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def read_appliance_data(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Remove any unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Rename columns to remove any extra spaces
    df.columns = df.columns.str.strip()
    
    return df

def create_dataset(appliance_data, start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq='h')
    result = []

    for dt in date_range:
        hour = dt.hour
        is_working_hours = 8 <= hour <= 18  # Assume working hours are 8 AM to 6 PM

        for _, appliance in appliance_data.iterrows():
            if is_working_hours and hour < (8 + appliance['Time Duration']):
                consumption = appliance['Consumption'] / appliance['Time Duration']
            else:
                consumption = 0

            result.append({
                'datetime': dt,
                'energy_consumption': consumption,
                'floor': appliance['Floor'],
                'appliance': appliance['Appliance']
            })

    return pd.DataFrame(result)

# Read the appliance data
appliance_data = read_appliance_data("abc.csv")

# Generate the dataset
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31, 23, 0)
dataset = create_dataset(appliance_data, start_date, end_date)

# Save the result to a CSV file
dataset.to_csv('energy_consumption_dataset.csv', index=False)
print("Dataset created successfully!")