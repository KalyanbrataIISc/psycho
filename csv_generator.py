import os
import json
import csv

def json_to_csv():
    # Directories for raw data and csv output
    raw_data_dir = os.path.join(os.path.dirname(__file__), 'raw_data')
    csv_data_dir = os.path.join(os.path.dirname(__file__), 'csv_data')

    # Ensure the csv_data folder exists
    os.makedirs(csv_data_dir, exist_ok=True)

    # Loop over all files in the raw_data directory
    for json_filename in os.listdir(raw_data_dir):
        if json_filename.endswith('.json'):
            json_filepath = os.path.join(raw_data_dir, json_filename)

            # Read the JSON file
            with open(json_filepath, 'r') as json_file:
                data = json.load(json_file)

            # Create the corresponding CSV filename
            csv_filename = json_filename.replace('.json', '.csv')
            csv_filepath = os.path.join(csv_data_dir, csv_filename)

            # Extract relevant data and write to CSV
            with open(csv_filepath, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)

                # Write user information once at the top, using "NIL" for missing data
                user_info_headers = ['name', 'age', 'gender', 'email', 'phone']
                user_info = [
                    data.get('name', 'NIL'), 
                    data.get('age', 'NIL'), 
                    data.get('gender', 'NIL'), 
                    data.get('email', 'NIL'), 
                    data.get('phone', 'NIL')
                ]
                csv_writer.writerow(user_info_headers)
                csv_writer.writerow(user_info)

                # Write usable data headers, now with trial_direction and trial_speed
                data_headers = ['frequency', 'trial_direction', 'trial_speed', 'change_detected', 'direction', 'speed']
                csv_writer.writerow(data_headers)

                # Iterate through the responses and write usable data, using "NIL" for missing data
                for response in data['responses']:
                    trial_sound = response.get('trial_sound', 'NIL')

                    # Default values for trial_direction and trial_speed
                    trial_direction = 'NIL'
                    trial_speed = 'NIL'

                    # Check if trial_sound is left/right and fast/slow, and split accordingly
                    if trial_sound != 'constant' and trial_sound != 'NIL':
                        direction, speed = trial_sound.split('_')
                        trial_direction = direction
                        trial_speed = speed

                    # Write row with broken trial_direction and trial_speed
                    row = [
                        response.get('frequency', 'NIL'),
                        trial_direction,
                        trial_speed,
                        response.get('change_detected', 'NIL'),
                        response.get('direction', 'NIL'),
                        response.get('speed', 'NIL')
                    ]
                    csv_writer.writerow(row)

            print(f"Converted {json_filename} to {csv_filename}")

if __name__ == '__main__':
    json_to_csv()