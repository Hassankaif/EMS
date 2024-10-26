import pandas as pd
import random
import numpy as np
from datetime import datetime

def read_appliance_data(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=None)
    
    appliance_data = []
    for floor, sheet in df.items():
        if 'Block' in floor:
            floor_number = floor.split()[-1]
            for _, row in sheet.iterrows():
                if pd.notna(row['Appliance']):
                    appliance_data.append({
                        'floor': floor_number,
                        'appliance': row['Appliance'],
                        'quantity': row['Quantity'],
                        'power_rating': row['Power Rating'],
                        'time_duration': row['Time Duration'],
                        'consumption': row['Consumption']
                    })
    
    return pd.DataFrame(appliance_data)

def create_dataset(appliance_data, timetable_data, start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq='h')
    result = []

    for dt in date_range:
        day = dt.strftime('%A')  # Automatically generate the day
        hour = dt.hour
        
        # Since the 'Day' column doesn't exist in your timetable, generate random 'Yes' or 'No' for class times.
        # Modify this logic based on your needs later.
        is_class_time = np.random.choice(['Yes', 'No']) == 'Yes'

        for _, appliance in appliance_data.iterrows():
            if pd.isna(appliance['time_duration']) or appliance['time_duration'] == '?':
                # If time duration is unknown, assume it's on during class time
                if is_class_time:
                    consumption = appliance['quantity'] * appliance['power_rating']
                else:
                    consumption = 0
            else:
                # If time duration is known, distribute it evenly throughout the day
                daily_hours = float(appliance['time_duration'])
                hourly_probability = daily_hours / 24
                if np.random.random() < hourly_probability:
                    consumption = appliance['quantity'] * appliance['power_rating']
                else:
                    consumption = 0

            result.append({
                'datetime': dt,
                'day': day,  # Automatically add day here
                'energy_consumption': consumption,
                'floor_no': appliance['floor'],
                'appliance_name': appliance['appliance']
            })

    df= pd.DataFrame(result)
    #df.to_csv('dataset.csv', index=True)
    return df 

appliance_data = read_appliance_data("BLOCK A.xlsx")

# Read the timetable data (assuming it's in the same Excel file)
timetable = pd.read_excel("BLOCK A.xlsx", sheet_name="BLOCK A")

# Generate the dataset
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31, 23, 0)
dataset = create_dataset(appliance_data, timetable, start_date, end_date)

# Save the result to a CSV file
dataset.to_csv('energy_consumption_dataset.csv', index=False)
print("Dataset created successfully!")