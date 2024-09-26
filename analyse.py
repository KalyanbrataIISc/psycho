import os
import pandas as pd
from scipy.stats import norm
import numpy as np

# Helper function to calculate d' and Beta
def calculate_signal_detection_metrics(hit_rate, false_alarm_rate):
    # Ensure hit_rate and false_alarm_rate are not 0 or 1 (to avoid infinities in Z-scores)
    hit_rate = np.clip(hit_rate, 1e-6, 1 - 1e-6)
    false_alarm_rate = np.clip(false_alarm_rate, 1e-6, 1 - 1e-6)

    # Calculate Z-scores
    z_hit = norm.ppf(hit_rate)
    z_fa = norm.ppf(false_alarm_rate)

    # Sensitivity (d')
    d_prime = z_hit - z_fa

    # Response Bias (Beta)
    beta = np.exp((z_fa ** 2 - z_hit ** 2) / 2)

    return d_prime, beta

# Updated function to analyze data and generate report with signal detection theory metrics
def analyze_and_generate_report_sdt(csv_file_path, report_file_path):
    # Load the CSV file and skip the first 2 rows (metadata)
    try:
        data = pd.read_csv(csv_file_path, skiprows=2)
    except Exception as e:
        return f"Error reading {csv_file_path}: {str(e)}"
    
    # Calculate hits and false alarms
    actual_change_trials = data[data['trial_direction'] != 'NIL']
    no_change_trials = data[data['trial_direction'] == 'NIL']

    hits = actual_change_trials['change_detected'].sum()  # When actual change detected as true
    misses = len(actual_change_trials) - hits  # When change was present but not detected

    false_alarms = no_change_trials['change_detected'].sum()  # When no change, but detected
    correct_rejections = len(no_change_trials) - false_alarms  # When no change and no detection

    # Calculate rates
    hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0
    false_alarm_rate = false_alarms / (false_alarms + correct_rejections) if (false_alarms + correct_rejections) > 0 else 0

    # Calculate d' and Beta using the helper function
    d_prime, beta = calculate_signal_detection_metrics(hit_rate, false_alarm_rate)

    # Previous metrics (correct detection rate, etc.) can still be calculated similarly
    correct_detection_rate = len(actual_change_trials[actual_change_trials['change_detected'] == True]) / len(actual_change_trials) * 100 if len(actual_change_trials) > 0 else 0
    false_positive_rate = len(no_change_trials[no_change_trials['change_detected'] == True]) / len(no_change_trials) * 100 if len(no_change_trials) > 0 else 0

    direction_bias_corrected = actual_change_trials.groupby('trial_direction')['change_detected'].mean() * 100
    speed_influence_corrected = actual_change_trials.groupby('trial_speed')['change_detected'].mean() * 100

    direction_accuracy_corrected = actual_change_trials[actual_change_trials['trial_direction'] == actual_change_trials['direction']]
    speed_accuracy_corrected = actual_change_trials[actual_change_trials['trial_speed'] == actual_change_trials['speed']]

    direction_accuracy_rate_corrected = len(direction_accuracy_corrected) / len(actual_change_trials) * 100 if len(actual_change_trials) > 0 else 0
    speed_accuracy_rate_corrected = len(speed_accuracy_corrected) / len(actual_change_trials) * 100 if len(actual_change_trials) > 0 else 0

    # Generate report content with SDT metrics
    report_content = f"""
    Report for {os.path.basename(csv_file_path)}:
    ------------------------------------------
    Correct Change Detection Rate: {correct_detection_rate:.2f}%
    False Positive Rate: {false_positive_rate:.2f}%

    Signal Detection Theory Metrics:
    d' (Sensitivity): {d_prime:.2f}
    Beta (Response Bias): {beta:.2f}

    Direction Bias:
    Left: {direction_bias_corrected.get('left', 0):.2f}%
    Right: {direction_bias_corrected.get('right', 0):.2f}%

    Speed Influence:
    Fast: {speed_influence_corrected.get('fast', 0):.2f}%
    Slow: {speed_influence_corrected.get('slow', 0):.2f}%

    Direction Accuracy Rate: {direction_accuracy_rate_corrected:.2f}%
    Speed Accuracy Rate: {speed_accuracy_rate_corrected:.2f}%
    """

    # Write report to file
    with open(report_file_path, 'w') as report_file:
        report_file.write(report_content)

    return f"Report generated for {csv_file_path}"

# Main function to process all CSVs in a folder and generate reports
def process_folder_sdt(csv_folder, reports_folder):
    # Check if reports folder exists, if not, create it
    if not os.path.exists(reports_folder):
        os.makedirs(reports_folder)

    # Process each CSV file in the csv_folder
    for csv_file in os.listdir(csv_folder):
        if csv_file.endswith('.csv'):
            csv_file_path = os.path.join(csv_folder, csv_file)
            report_file_path = os.path.join(reports_folder, f"{os.path.splitext(csv_file)[0]}_report.txt")

            # Analyze and generate report for each CSV
            result = analyze_and_generate_report_sdt(csv_file_path, report_file_path)
            print(result)

if __name__ == "__main__":
    # Specify the directory paths
    csv_folder = os.path.join(os.getcwd(), 'csv_data')
    reports_folder = os.path.join(os.getcwd(), 'reports')

    # Process the folder of CSV files
    process_folder_sdt(csv_folder, reports_folder)