import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator  # Import QIntValidator
from sound import SoundGenerator

class SoundControlApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the sound generator
        self.sound_generator = SoundGenerator()
        self.is_playing = False

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
        self.freq_slider.setMinimum(20)   # Min frequency
        self.freq_slider.setMaximum(20000)  # Max frequency
        self.freq_slider.setValue(440)   # Default frequency
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

        # Left amplitude slider
        self.left_amp_slider = QSlider(Qt.Horizontal, self)
        self.left_amp_slider.setMinimum(0)
        self.left_amp_slider.setMaximum(100)
        self.left_amp_slider.setValue(50)
        self.left_amp_slider.valueChanged.connect(self.update_sound)
        layout.addWidget(QLabel('Left Amplitude'))
        layout.addWidget(self.left_amp_slider)

        # Right amplitude slider
        self.right_amp_slider = QSlider(Qt.Horizontal, self)
        self.right_amp_slider.setMinimum(0)
        self.right_amp_slider.setMaximum(100)
        self.right_amp_slider.setValue(50)
        self.right_amp_slider.valueChanged.connect(self.update_sound)
        layout.addWidget(QLabel('Right Amplitude'))
        layout.addWidget(self.right_amp_slider)

        # Phase difference slider
        self.phase_diff_slider = QSlider(Qt.Horizontal, self)
        self.phase_diff_slider.setMinimum(-180)
        self.phase_diff_slider.setMaximum(180)
        self.phase_diff_slider.setValue(0)
        self.phase_diff_slider.valueChanged.connect(self.update_sound)
        layout.addWidget(QLabel('Phase Difference'))
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
            frequency = int(self.freq_textbox.text())  # Get frequency from textbox
            left_amp = self.left_amp_slider.value() / 100.0
            right_amp = self.right_amp_slider.value() / 100.0
            phase_diff = self.phase_diff_slider.value()

            # Update the sound properties for real-time adjustment
            self.sound_generator.update_sound_properties(frequency, left_amp, right_amp, phase_diff)

    def update_frequency_from_slider(self):
        # Update frequency textbox when slider changes
        frequency = self.freq_slider.value()
        self.freq_textbox.setText(str(frequency))
        self.update_sound()

    def update_frequency_from_textbox(self):
        # Update frequency slider when textbox changes
        try:
            frequency = int(self.freq_textbox.text())
            self.freq_slider.setValue(frequency)
            self.update_sound()
        except ValueError:
            pass  # Ignore invalid input

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SoundControlApp()
    sys.exit(app.exec_())