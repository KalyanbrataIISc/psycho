import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from sound import SoundGenerator
import math

class SoundControlApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the sound generator
        self.sound_generator = SoundGenerator()
        self.is_playing = False

        # Initialize current frequency
        self.current_frequency = 440  # Default frequency

        # Create UI components
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Sound Control')
        layout = QVBoxLayout()

        # Start/Stop button
        self.toggle_button = QPushButton('Start', self)
        self.toggle_button.clicked.connect(self.toggle_sound)
        layout.addWidget(self.toggle_button)

        # Frequency control (slider and textbox)
        freq_layout = QHBoxLayout()

        # Frequency slider
        self.freq_slider = QSlider(Qt.Horizontal, self)
        self.freq_slider.setMinimum(0)  # Min value for exponential calculation
        self.freq_slider.setMaximum(1000)  # Adjust the range for exponential scaling
        self.freq_slider.setValue(500)  # Default value for initial frequency
        self.freq_slider.valueChanged.connect(self.update_frequency_from_slider)
        freq_layout.addWidget(QLabel('Frequency'))
        freq_layout.addWidget(self.freq_slider)

        # Frequency textbox
        self.freq_textbox = QLineEdit(self)
        self.freq_textbox.setText('440')
        self.freq_textbox.setValidator(QIntValidator(20, 20000, self))  # Limit input to valid frequency range
        self.freq_textbox.editingFinished.connect(self.update_frequency_from_textbox)
        freq_layout.addWidget(self.freq_textbox)

        layout.addLayout(freq_layout)

        # Balance slider (replacing left and right sliders)
        self.balance_slider = QSlider(Qt.Horizontal, self)
        self.balance_slider.setMinimum(-100)
        self.balance_slider.setMaximum(100)
        self.balance_slider.setValue(0)  # Default to 50-50 balance
        self.balance_slider.valueChanged.connect(self.update_sound)
        self.balance_label = QLabel('Balance: L 50% - R 50%', self)
        layout.addWidget(self.balance_label)
        layout.addWidget(self.balance_slider)

        # Phase difference slider
        self.phase_diff_slider = QSlider(Qt.Horizontal, self)
        self.phase_diff_slider.setMinimum(-180)
        self.phase_diff_slider.setMaximum(180)
        self.phase_diff_slider.setValue(0)
        self.phase_diff_slider.valueChanged.connect(self.update_sound)
        self.phase_label = QLabel('Phase Difference: 0°', self)
        layout.addWidget(self.phase_label)
        layout.addWidget(self.phase_diff_slider)

        # Set layout and show
        self.setLayout(layout)
        self.show()

    def toggle_sound(self):
        if not self.is_playing:
            # Start sound
            self.start_sound()
            self.toggle_button.setText('Stop')
        else:
            # Stop sound
            self.stop_sound()
            self.toggle_button.setText('Start')

    def start_sound(self):
        self.is_playing = True
        self.update_sound()  # Update properties before starting
        self.sound_generator.start_sound()

    def stop_sound(self):
        self.is_playing = False
        self.sound_generator.stop_sound()

    def update_sound(self):
        if self.is_playing:
            # Calculate the balance
            balance = self.balance_slider.value()
            left_amp = max(0, (100 - balance) / 100.0)  # Left amplitude
            right_amp = max(0, (100 + balance) / 100.0)  # Right amplitude
            # Update balance label
            self.balance_label.setText(f'Balance: L {int(left_amp * 100)}% - R {int(right_amp * 100)}%')

            # Get phase difference
            phase_diff = self.phase_diff_slider.value()
            # Update phase label
            self.phase_label.setText(f'Phase Difference: {phase_diff}°')

            # Update the sound properties for real-time adjustment
            self.sound_generator.update_sound_properties(self.current_frequency, left_amp, right_amp, phase_diff)

    def update_frequency_from_slider(self):
        # Apply exponential scaling
        slider_value = self.freq_slider.value()
        self.current_frequency = int(20 * (10 ** (slider_value / 250)))  # Base 10 exponential scaling

        # Update frequency textbox
        self.freq_textbox.setText(str(self.current_frequency))
        self.update_sound()

    def update_frequency_from_textbox(self):
        # Update frequency slider when textbox changes
        try:
            frequency = int(self.freq_textbox.text())
            self.current_frequency = frequency

            # Convert the frequency to slider value for consistency
            slider_value = int(250 * math.log10(frequency / 20))
            self.freq_slider.setValue(slider_value)

            self.update_sound()
        except ValueError:
            pass  # Ignore invalid input

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SoundControlApp()
    sys.exit(app.exec_())