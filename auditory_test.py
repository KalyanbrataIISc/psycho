# auditory_experiment_pyqt5.py

import sys
import numpy as np
import random
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtGui, QtCore
import sounddevice as sd
import threading
from scipy.optimize import curve_fit
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# -------------------------------
# Participant Information Dialog
# -------------------------------

class ParticipantInfoDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Participant Information')
        self.setFixedSize(300, 200)
        self.username = ''
        self.age = ''
        self.gender = ''

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.username_edit = QtWidgets.QLineEdit()
        self.age_edit = QtWidgets.QLineEdit()
        self.gender_combo = QtWidgets.QComboBox()
        self.gender_combo.addItems(['Male', 'Female', 'Other'])

        layout.addWidget(QtWidgets.QLabel('Username:'))
        layout.addWidget(self.username_edit)
        layout.addWidget(QtWidgets.QLabel('Age:'))
        layout.addWidget(self.age_edit)
        layout.addWidget(QtWidgets.QLabel('Gender:'))
        layout.addWidget(self.gender_combo)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept(self):
        self.username = self.username_edit.text()
        self.age = self.age_edit.text()
        self.gender = self.gender_combo.currentText()
        if self.username and self.age and self.gender:
            super().accept()
        else:
            QtWidgets.QMessageBox.warning(self, 'Input Error', 'Please fill in all fields.')

# -------------------------------
# Experiment Main Window
# -------------------------------

class ExperimentWindow(QtWidgets.QMainWindow):
    def __init__(self, participant_info):
        super().__init__()
        self.participant_info = participant_info
        self.setWindowTitle('Auditory Experiment')
        self.setFixedSize(800, 600)
        self.current_trial = 0
        self.results = []
        self.trials = self.create_trials()
        self.total_trials = len(self.trials)
        self.is_playing = False

        self.init_ui()

    def init_ui(self):
        self.label = QtWidgets.QLabel('Press "Start" to begin the experiment.', self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFont(QtGui.QFont('Arial', 16))
        self.label.setGeometry(50, 50, 700, 100)

        self.start_button = QtWidgets.QPushButton('Start', self)
        self.start_button.setFont(QtGui.QFont('Arial', 14))
        self.start_button.setGeometry(350, 200, 100, 50)
        self.start_button.clicked.connect(self.start_experiment)

        self.response_label = QtWidgets.QLabel('', self)
        self.response_label.setAlignment(QtCore.Qt.AlignCenter)
        self.response_label.setFont(QtGui.QFont('Arial', 16))
        self.response_label.setGeometry(50, 300, 700, 100)

        self.progress_label = QtWidgets.QLabel('', self)
        self.progress_label.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_label.setFont(QtGui.QFont('Arial', 12))
        self.progress_label.setGeometry(50, 500, 700, 50)

        self.show()

    # Experiment Parameters
    FREQUENCY = 1000  # Hz
    DURATION = 0.5  # seconds
    SAMPLE_RATE = 44100  # Hz

    # Amplitude and phase differences
    AMPLITUDE_DIFFS = np.arange(0, 11, 1)  # 0 to 10 dB
    PHASE_DIFFS = np.arange(0, 195, 15)  # 0° to 180°

    # Trial settings
    TRIALS_PER_LEVEL = 20
    CATCH_TRIALS = int(0.1 * (len(AMPLITUDE_DIFFS) + len(PHASE_DIFFS)) * TRIALS_PER_LEVEL)

    # Response keys
    RESPONSE_KEYS = {'j': 'Left', 'k': 'Center', 'l': 'Right'}

    def create_trials(self):
        trials = []

        # Amplitude difference trials
        for amp_diff in self.AMPLITUDE_DIFFS:
            for _ in range(self.TRIALS_PER_LEVEL):
                amplitude_left = 1.0
                amplitude_right = 1.0 * (10 ** (-amp_diff / 20))
                label = 'Left' if amp_diff > 0 else 'Center'
                trials.append({'type': 'Amplitude', 'amp_diff': amp_diff, 'phase_diff': 0,
                               'amplitude_left': amplitude_left, 'amplitude_right': amplitude_right,
                               'label': label})

        # Phase difference trials
        for phase_diff in self.PHASE_DIFFS:
            for _ in range(self.TRIALS_PER_LEVEL):
                amplitude_left = 1.0
                amplitude_right = 1.0
                label = 'Left' if phase_diff > 0 else 'Center'
                trials.append({'type': 'Phase', 'amp_diff': 0, 'phase_diff': phase_diff,
                               'amplitude_left': amplitude_left, 'amplitude_right': amplitude_right,
                               'label': label})

        # Catch trials (no difference)
        for _ in range(self.CATCH_TRIALS):
            trials.append({'type': 'Catch', 'amp_diff': 0, 'phase_diff': 0,
                           'amplitude_left': 1.0, 'amplitude_right': 1.0, 'label': 'Center'})

        random.shuffle(trials)
        return trials

    def start_experiment(self):
        self.start_button.setDisabled(True)
        self.label.setText('Experiment Started.\nPress "J" for Left, "K" for Center, "L" for Right.')
        self.progress_label.setText(f'Trial {self.current_trial + 1} of {self.total_trials}')
        QtCore.QTimer.singleShot(1000, self.next_trial)

    def next_trial(self):
        if self.current_trial >= self.total_trials:
            self.end_experiment()
            return

        trial = self.trials[self.current_trial]
        self.response_label.setText('')
        self.progress_label.setText(f'Trial {self.current_trial + 1} of {self.total_trials}')

        # Generate and play stimulus
        threading.Thread(target=self.play_stimulus, args=(trial,)).start()

        # Set a timer for response collection
        QtCore.QTimer.singleShot(int((self.DURATION + 0.5) * 1000), self.collect_response)

    def play_stimulus(self, trial):
        self.is_playing = True
        tone = self.generate_tone(self.FREQUENCY, self.DURATION, self.SAMPLE_RATE,
                                  trial['amplitude_left'], trial['amplitude_right'], trial['phase_diff'])
        sd.play(tone, self.SAMPLE_RATE)
        sd.wait()
        self.is_playing = False

    def generate_tone(self, frequency, duration, sample_rate, amplitude_left, amplitude_right, phase_diff):
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        phase_rad = np.deg2rad(phase_diff)
        tone_left = amplitude_left * np.sin(2 * np.pi * frequency * t)
        tone_right = amplitude_right * np.sin(2 * np.pi * frequency * t + phase_rad)
        stereo_tone = np.vstack((tone_left, tone_right)).T
        return stereo_tone

    def collect_response(self):
        self.response_label.setText('Please respond now.')
        self.key_pressed = None
        self.start_time = QtCore.QTime.currentTime()
        self.key_timer = QtCore.QTimer()
        self.key_timer.timeout.connect(self.check_key_response)
        self.key_timer.start(10)

    def keyPressEvent(self, event):
        if self.key_pressed is None and not self.is_playing:
            key = event.text().lower()
            if key in self.RESPONSE_KEYS:
                self.key_pressed = self.RESPONSE_KEYS[key]
                self.response_time = self.start_time.msecsTo(QtCore.QTime.currentTime())
                self.key_timer.stop()
                self.record_response()

    def check_key_response(self):
        # Timeout after 2000 ms
        if self.start_time.msecsTo(QtCore.QTime.currentTime()) > 2000:
            self.key_pressed = 'No Response'
            self.key_timer.stop()
            self.record_response()

    def record_response(self):
        trial = self.trials[self.current_trial]
        self.results.append({'Trial': self.current_trial + 1, 'Type': trial['type'],
                             'Amplitude Difference': trial['amp_diff'],
                             'Phase Difference': trial['phase_diff'],
                             'Label': trial['label'], 'Response': self.key_pressed})

        self.current_trial += 1
        QtCore.QTimer.singleShot(1000, self.next_trial)

    def end_experiment(self):
        self.label.setText('Experiment Completed.')
        self.response_label.setText('')
        self.progress_label.setText('')
        self.analyze_results()
        self.generate_pdf()
        QtWidgets.QMessageBox.information(self, 'Experiment Completed', 'The experiment is completed. Results have been saved.')
        self.close()

    # -------------------------------
    # Data Analysis
    # -------------------------------

    def analyze_results(self):
        from scipy.optimize import curve_fit
        import pandas as pd

        df = pd.DataFrame(self.results)

        # Filter out 'No Response'
        df = df[df['Response'] != 'No Response']

        # Define sigmoid function
        def sigmoid(x, L ,x0, k, b):
            y = L / (1 + np.exp(-k*(x - x0))) + b
            return y

        self.analysis_results = {}

        # Amplitude Condition
        amp_df = df[df['Type'] == 'Amplitude']
        amp_group = amp_df.groupby('Amplitude Difference')
        amp_x = amp_group.mean().index.values
        amp_y = amp_group.apply(lambda x: np.mean(x['Response'] == x['Label'])).values

        # Fit sigmoid curve
        p0 = [max(amp_y), np.median(amp_x),1,min(amp_y)]  # initial guesses
        try:
            popt, _ = curve_fit(sigmoid, amp_x, amp_y, p0, method='dogbox')
            amp_fit_x = np.linspace(min(amp_x), max(amp_x), 100)
            amp_fit_y = sigmoid(amp_fit_x, *popt)
            amp_threshold = popt[1]
        except:
            amp_fit_x, amp_fit_y, amp_threshold = amp_x, amp_y, None

        self.analysis_results['Amplitude'] = {'x': amp_x, 'y': amp_y, 'fit_x': amp_fit_x, 'fit_y': amp_fit_y, 'threshold': amp_threshold}

        # Phase Condition
        phase_df = df[df['Type'] == 'Phase']
        phase_group = phase_df.groupby('Phase Difference')
        phase_x = phase_group.mean().index.values
        phase_y = phase_group.apply(lambda x: np.mean(x['Response'] == x['Label'])).values

        # Fit sigmoid curve
        p0 = [max(phase_y), np.median(phase_x),1,min(phase_y)]  # initial guesses
        try:
            popt, _ = curve_fit(sigmoid, phase_x, phase_y, p0, method='dogbox')
            phase_fit_x = np.linspace(min(phase_x), max(phase_x), 100)
            phase_fit_y = sigmoid(phase_fit_x, *popt)
            phase_threshold = popt[1]
        except:
            phase_fit_x, phase_fit_y, phase_threshold = phase_x, phase_y, None

        self.analysis_results['Phase'] = {'x': phase_x, 'y': phase_y, 'fit_x': phase_fit_x, 'fit_y': phase_fit_y, 'threshold': phase_threshold}

    # -------------------------------
    # Generate PDF Report
    # -------------------------------

    def generate_pdf(self):
        participant_info = self.participant_info
        analysis_results = self.analysis_results

        doc = SimpleDocTemplate(f"{participant_info['Username']}_Results.pdf")
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("Auditory Directionality Detection Experiment Results", styles['Title']))
        story.append(Spacer(1, 0.2 * inch))

        # Participant Info
        info_text = f"Username: {participant_info['Username']}<br/>Age: {participant_info['Age']}<br/>Gender: {participant_info['Gender']}"
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Amplitude Results
        plt.figure()
        plt.scatter(analysis_results['Amplitude']['x'], analysis_results['Amplitude']['y'], label='Data')
        plt.plot(analysis_results['Amplitude']['fit_x'], analysis_results['Amplitude']['fit_y'], color='red', label='Sigmoid Fit')
        plt.xlabel('Amplitude Difference (dB)')
        plt.ylabel('Proportion Correct')
        plt.title('Amplitude Difference Psychometric Curve')
        plt.legend()
        amp_image = f"{participant_info['Username']}_Amplitude.png"
        plt.savefig(amp_image)
        plt.close()

        story.append(Paragraph("Amplitude Difference Results", styles['Heading2']))
        if analysis_results['Amplitude']['threshold'] is not None:
            threshold_text = f"Threshold Amplitude Difference: {analysis_results['Amplitude']['threshold']:.2f} dB"
        else:
            threshold_text = "Threshold Amplitude Difference: Could not be calculated"
        story.append(Paragraph(threshold_text, styles['Normal']))
        story.append(RLImage(amp_image, width=6*inch, height=4*inch))
        story.append(Spacer(1, 0.2 * inch))

        # Phase Results
        plt.figure()
        plt.scatter(analysis_results['Phase']['x'], analysis_results['Phase']['y'], label='Data')
        plt.plot(analysis_results['Phase']['fit_x'], analysis_results['Phase']['fit_y'], color='red', label='Sigmoid Fit')
        plt.xlabel('Phase Difference (Degrees)')
        plt.ylabel('Proportion Correct')
        plt.title('Phase Difference Psychometric Curve')
        plt.legend()
        phase_image = f"{participant_info['Username']}_Phase.png"
        plt.savefig(phase_image)
        plt.close()

        story.append(Paragraph("Phase Difference Results", styles['Heading2']))
        if analysis_results['Phase']['threshold'] is not None:
            threshold_text = f"Threshold Phase Difference: {analysis_results['Phase']['threshold']:.2f} Degrees"
        else:
            threshold_text = "Threshold Phase Difference: Could not be calculated"
        story.append(Paragraph(threshold_text, styles['Normal']))
        story.append(RLImage(phase_image, width=6*inch, height=4*inch))
        story.append(Spacer(1, 0.2 * inch))

        # Build PDF
        doc.build(story)

        # Remove temporary images
        import os
        os.remove(amp_image)
        os.remove(phase_image)

# -------------------------------
# Main Execution
# -------------------------------

def main():
    app = QtWidgets.QApplication(sys.argv)

    # Participant Info Dialog
    info_dialog = ParticipantInfoDialog()
    if info_dialog.exec_() == QtWidgets.QDialog.Accepted:
        participant_info = {'Username': info_dialog.username,
                            'Age': info_dialog.age,
                            'Gender': info_dialog.gender}

        # Start Experiment
        ex = ExperimentWindow(participant_info)
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__ == '__main__':
    main()