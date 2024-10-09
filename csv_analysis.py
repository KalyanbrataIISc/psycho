import os
import pandas as pd

# Directories
input_folder = os.path.join(os.path.dirname(__file__), 'csv_data')
output_folder = os.path.join(os.path.dirname(__file__), 'csv_ana')

# Ensure output directory exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Function to process each CSV file
def process_csv(file_path, output_path):
    # Load the CSV and skip the first two rows
    data = pd.read_csv(file_path, skiprows=2)

    # Initialize a list to hold the points for each frequency
    points_list = []

    # Group the data by frequency
    grouped_data = data.groupby('frequency')

    # Iterate over each frequency group
    for freq, group in grouped_data:
        points = 0
        
        # Iterate over the rows in each frequency group
        for index, row in group.iterrows():
            trial_dir = row['trial_direction']
            change_detected = row['change_detected']
            direction = row['direction']

            # Assign points based on conditions
            if trial_dir == 'NIL' and change_detected == True:
                points += 0  # 0 points for this case
            elif trial_dir in ['left', 'right'] and change_detected == True:
                points += 0.5  # +0.5 points for this case
            elif 'left' in group['trial_direction'].values and 'right' in group['trial_direction'].values:
                left_dir = group[(group['trial_direction'] == 'left') & (group['direction'] == 'left')]
                right_dir = group[(group['trial_direction'] == 'right') & (group['direction'] == 'right')]
                if not left_dir.empty and not right_dir.empty:
                    points += 3  # +3 points for this case

        # Append the frequency and points to the list
        points_list.append({'frequency': freq, 'points': points})

    # Create a DataFrame from the points list
    points_df = pd.DataFrame(points_list)

    # Update points: any value below 1 should be converted to 0
    points_df['points'] = points_df['points'].apply(lambda x: 0 if x < 1 else x)

    # Save the DataFrame to a new CSV file
    points_df.to_csv(output_path, index=False)

# Iterate over all files in the input folder
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):
        input_file_path = os.path.join(input_folder, file_name)
        output_file_path = os.path.join(output_folder, file_name)  # Save with the same name
        process_csv(input_file_path, output_file_path)

print("Processing complete. CSV files have been saved in the 'csv_ana' folder.")