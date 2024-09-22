import sys
import json
import random
import os
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar, QLineEdit, QRadioButton, QButtonGroup, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon
import shift as sft

# Sound shifting functions
fl = lambda x: sft.sound_shift(x, 'phase', 'left', 'short')
fr = lambda x: sft.sound_shift(x, 'phase', 'right', 'short')
sl = lambda x: sft.sound_shift(x, 'phase', 'left', 'long')
sr = lambda x: sft.sound_shift(x, 'phase', 'right', 'long')
cnst = lambda x: sft.sound_shift(x, 'flat')

class UserDataWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('User Information')
        self.setGeometry(200, 200, 300, 200)

        self.name_label = QLabel('Name:')
        self.name_input = QLineEdit(self)

        self.age_label = QLabel('Age:')
        self.age_input = QLineEdit(self)

        self.gender_label = QLabel('Gender:')
        self.male_radio = QRadioButton('Male', self)
        self.female_radio = QRadioButton('Female', self)
        self.other_radio = QRadioButton('Other', self)
        self.gender_group = QButtonGroup(self)
        self.gender_group.addButton(self.male_radio)
        self.gender_group.addButton(self.female_radio)
        self.gender_group.addButton(self.other_radio)

        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.collect_user_data)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.age_label)
        layout.addWidget(self.age_input)
        layout.addWidget(self.gender_label)
        layout.addWidget(self.male_radio)
        layout.addWidget(self.female_radio)
        layout.addWidget(self.other_radio)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def collect_user_data(self):
        self.name = self.name_input.text()
        self.age = self.age_input.text()
        self.gender = None
        if self.male_radio.isChecked():
            self.gender = 'Male'
        elif self.female_radio.isChecked():
            self.gender = 'Female'
        elif self.other_radio.isChecked():
            self.gender = 'Other'

        if self.name and self.age and self.gender:
            self.hide()
            self.experiment_window = ExperimentWindow(self.name, self.age, self.gender)
            self.experiment_window.show()
        else:
            QMessageBox.warning(self, 'Input Error', 'Please fill out all fields!')


class ExperimentWindow(QWidget):
    def __init__(self, name, age, gender):
        super().__init__()

        self.setWindowTitle('Sound Shift Experiment')
        self.setGeometry(200, 200, 600, 400)

        # Store user data
        self.user_data = {
            'name': name,
            'age': age,
            'gender': gender,
            'responses': []
        }

        # Main label to display instructions
        self.label = QLabel('Press Space to start the experiment', self)
        self.label.setAlignment(Qt.AlignCenter)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(120)  # For 120 trials (updated)

        # Visual Arrow Buttons (for Left/Right)
        self.left_arrow = QLabel(self)
        self.right_arrow = QLabel(self)
        self.left_option_label = QLabel("")
        self.right_option_label = QLabel("")
        self.left_option_label.setAlignment(Qt.AlignCenter)  # Center align option labels
        self.right_option_label.setAlignment(Qt.AlignCenter)
        self.update_arrow_icons(False, False)  # Hide arrows initially

        arrow_layout = QHBoxLayout()
        arrow_layout.addWidget(self.left_arrow)
        arrow_layout.addWidget(self.right_arrow)

        option_layout = QHBoxLayout()
        option_layout.addWidget(self.left_option_label)
        option_layout.addWidget(self.right_option_label)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.label)
        self.vbox.addLayout(arrow_layout)
        self.vbox.addLayout(option_layout)
        self.vbox.addWidget(self.progress_bar)
        self.setLayout(self.vbox)

        # Experiment variables
        self.trial_active = False
        self.current_trial_sound = None
        self.current_trial_freq = None
        self.question_stage = None  # Q1, Q2, Q3
        self.current_trial = None

        # Generate 3 conditions per frequency (Left, Right, Flat) with random speeds
        sound_conditions = ['left', 'right', 'flat']
        frequencies = list(range(0, 2050, 50))
        speeds = ['short', 'long']

        self.trials = [
            {'sound': random.choice(['left_fast', 'left_slow']), 'frequency': freq} if condition == 'left' else
            {'sound': random.choice(['right_fast', 'right_slow']), 'frequency': freq} if condition == 'right' else
            {'sound': 'constant', 'frequency': freq}
            for condition in sound_conditions
            for freq in frequencies
        ]

        # Shuffle the trials
        random.shuffle(self.trials)

        self.current_trial_index = 0

        # Set focus for space bar to start next trial
        self.setFocusPolicy(Qt.StrongFocus)

    def update_arrow_icons(self, show_arrows=True, left_selected=False, right_selected=False):
        """
        Update the icons for the left and right arrow labels.
        If an arrow is selected, change its color to green.
        Show or hide the arrows based on the 'show_arrows' argument.
        """
        if show_arrows:
            if left_selected:
                self.left_arrow.setPixmap(QPixmap('psycho/resources/left_green.png'))
            else:
                self.left_arrow.setPixmap(QPixmap('psycho/resources/left_blue.png'))

            if right_selected:
                self.right_arrow.setPixmap(QPixmap('psycho/resources/right_green.png'))
            else:
                self.right_arrow.setPixmap(QPixmap('psycho/resources/right_blue.png'))
        else:
            self.left_arrow.clear()
            self.right_arrow.clear()

    def update_option_labels(self, left_text="", right_text=""):
        """
        Update the labels under the arrows to display the options.
        """
        self.left_option_label.setText(left_text)
        self.right_option_label.setText(right_text)

    def start_trial(self):
        if self.current_trial_index >= len(self.trials):
            self.end_experiment()
            return

        self.current_trial = self.trials[self.current_trial_index]
        self.current_trial_index += 1

        # Update progress bar
        self.progress_bar.setValue(self.current_trial_index)

        # Play the sound for the current trial
        self.play_sound_and_start_response()

    def play_sound_and_start_response(self):
        # Retrieve the condition and frequency from the current trial
        selected_condition = self.current_trial['sound']
        selected_frequency = self.current_trial['frequency']

        # Play the sound based on the condition and frequency
        if selected_condition == 'left_fast':
            fl(selected_frequency)
        elif selected_condition == 'left_slow':
            sl(selected_frequency)
        elif selected_condition == 'right_fast':
            fr(selected_frequency)
        elif selected_condition == 'right_slow':
            sr(selected_frequency)
        elif selected_condition == 'constant':
            cnst(selected_frequency)

        # Save the actual condition and frequency for the current trial
        self.current_trial_sound = selected_condition
        self.current_trial_freq = selected_frequency

        # Proceed to Q1
        self.ask_question_1()

    def ask_question_1(self):
        self.trial_active = True
        self.question_stage = "Q1"
        self.label.setText('Q1: Was there a change?')
        self.update_arrow_icons(True)  # Show arrows
        self.update_option_labels("Yes", "No")

    def ask_question_2(self):
        self.question_stage = "Q2"
        self.label.setText('Q2: Which direction?')
        self.update_arrow_icons(True)
        self.update_option_labels("Left", "Right")

    def ask_question_3(self):
        self.question_stage = "Q3"
        self.label.setText('Q3: How fast?')
        self.update_arrow_icons(True)
        self.update_option_labels("Fast", "Slow")

    def keyPressEvent(self, event):
        if not self.trial_active and event.key() == Qt.Key_Space:
            # Start the next trial when space bar is pressed
            self.update_arrow_icons(False)  # Hide arrows
            self.update_option_labels()  # Clear options
            self.start_trial()
            return

        if self.trial_active:
            if self.question_stage == "Q1":
                if event.key() == Qt.Key_Left:  # Yes, there was a change
                    self.record_response("change_detected", True)
                    self.update_arrow_icons(left_selected=True)  # Light up left arrow
                    QTimer.singleShot(500, self.ask_question_2)  # 0.5-second delay before Q2
                elif event.key() == Qt.Key_Right:  # No change
                    self.record_response("change_detected", False)
                    self.update_arrow_icons(right_selected=True)  # Light up right arrow
                    QTimer.singleShot(500, self.end_trial)  # Skip remaining questions and end trial only if "No"

            elif self.question_stage == "Q2":
                if event.key() == Qt.Key_Left:  # Left
                    self.record_response("direction", "left")
                    self.update_arrow_icons(left_selected=True)  # Light up left arrow
                    QTimer.singleShot(500, self.ask_question_3)  # 0.5-second delay before Q3
                elif event.key() == Qt.Key_Right:  # Right
                    self.record_response("direction", "right")
                    self.update_arrow_icons(right_selected=True)  # Light up right arrow
                    QTimer.singleShot(500, self.ask_question_3)  # 0.5-second delay before Q3

            elif self.question_stage == "Q3":
                if event.key() == Qt.Key_Left:  # Fast
                    self.record_response("speed", "fast")
                    self.update_arrow_icons(left_selected=True)  # Light up left arrow
                    QTimer.singleShot(500, self.end_trial)  # 0.5-second delay before ending the trial
                elif event.key() == Qt.Key_Right:  # Slow
                    self.record_response("speed", "slow")
                    self.update_arrow_icons(right_selected=True)  # Light up right arrow
                    QTimer.singleShot(500, self.end_trial)  # 0.5-second delay before ending the trial

    def record_response(self, question, answer):
        if len(self.user_data['responses']) < self.current_trial_index:
            self.user_data['responses'].append({
                'frequency': self.current_trial_freq,
                'trial_sound': self.current_trial_sound
            })
        
        self.user_data['responses'][-1][question] = answer

    def end_trial(self):
        self.label.setText('Press Space to start the next trial.')
        self.trial_active = False
        self.question_stage = None
        self.update_arrow_icons(False)  # Hide arrows
        self.update_option_labels()  # Clear options

    def end_experiment(self):
        self.label.setText('Experiment complete!')

    def closeEvent(self, event):
        # Save the collected data when the window is closed
        raw_data_path = os.path.join('psycho', 'raw_data')
        os.makedirs(raw_data_path, exist_ok=True)
        file_path = os.path.join(raw_data_path, f'user_data_{self.user_data["name"]}.json')
        
        organized_data = sorted(self.user_data['responses'], key=lambda x: x['frequency'])
        with open(file_path, 'w') as f:
            json.dump({
                'name': self.user_data['name'],
                'age': self.user_data['age'],
                'gender': self.user_data['gender'],
                'responses': organized_data
            }, f, indent=4)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show the user data collection window first
    user_data_window = UserDataWindow()
    user_data_window.show()

    sys.exit(app.exec_())