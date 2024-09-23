import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QRadioButton, QPushButton, QSlider, QButtonGroup
from PyQt5.QtCore import Qt
import shift as sft  # Assuming this is your custom sound-shifting library

# Sound shifting functions based on your library
fl = lambda x: sft.sound_shift(x, 'phase', 'left', 'short')
fr = lambda x: sft.sound_shift(x, 'phase', 'right', 'short')
sl = lambda x: sft.sound_shift(x, 'phase', 'left', 'long')
sr = lambda x: sft.sound_shift(x, 'phase', 'right', 'long')
cnst = lambda x: sft.sound_shift(x, 'flat')

class LearnWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Learn Sound Shifting')
        self.setGeometry(200, 200, 400, 300)

        # Frequency selection
        self.freq_label = QLabel('Select Frequency (Hz):')
        self.freq_slider = QSlider(Qt.Horizontal, self)
        self.freq_slider.setMinimum(0)
        self.freq_slider.setMaximum(7)  # Corresponds to 8 fixed values
        self.freq_slider.setTickPosition(QSlider.TicksBelow)
        self.freq_slider.setTickInterval(1)
        self.freq_slider.valueChanged.connect(self.update_freq_label)

        self.freq_values = [50, 200, 440, 700, 1000, 1400, 1600, 2000]
        self.freq_display = QLabel(f"Frequency: {self.freq_values[0]} Hz")

        # Direction selection with radio buttons
        self.direction_label = QLabel('Select Direction:')
        self.left_radio = QRadioButton('Left')
        self.right_radio = QRadioButton('Right')
        self.flat_radio = QRadioButton('Flat')
        self.direction_group = QButtonGroup(self)
        self.direction_group.addButton(self.left_radio)
        self.direction_group.addButton(self.right_radio)
        self.direction_group.addButton(self.flat_radio)
        self.left_radio.setChecked(True)  # Set 'Left' as default

        direction_layout = QHBoxLayout()
        direction_layout.addWidget(self.left_radio)
        direction_layout.addWidget(self.right_radio)
        direction_layout.addWidget(self.flat_radio)

        # Speed selection with radio buttons
        self.speed_label = QLabel('Select Speed:')
        self.short_radio = QRadioButton('Short')
        self.long_radio = QRadioButton('Long')
        self.speed_group = QButtonGroup(self)
        self.speed_group.addButton(self.short_radio)
        self.speed_group.addButton(self.long_radio)
        self.short_radio.setChecked(True)  # Set 'Short' as default

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(self.short_radio)
        speed_layout.addWidget(self.long_radio)

        # Play button
        self.play_button = QPushButton('Play Sound', self)
        self.play_button.clicked.connect(self.play_sound)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.freq_label)
        layout.addWidget(self.freq_slider)
        layout.addWidget(self.freq_display)
        layout.addWidget(self.direction_label)
        layout.addLayout(direction_layout)
        layout.addWidget(self.speed_label)
        layout.addLayout(speed_layout)
        layout.addWidget(self.play_button)

        self.setLayout(layout)

    def update_freq_label(self):
        # Update the label to show the currently selected frequency
        current_freq = self.freq_values[self.freq_slider.value()]
        self.freq_display.setText(f"Frequency: {current_freq} Hz")

    def play_sound(self):
        # Get the selected frequency, direction, and speed
        freq = self.freq_values[self.freq_slider.value()]
        direction = self.get_selected_direction()
        speed = self.get_selected_speed()

        # Play the sound based on user selection
        if direction == 'Left' and speed == 'Short':
            fl(freq)
        elif direction == 'Left' and speed == 'Long':
            sl(freq)
        elif direction == 'Right' and speed == 'Short':
            fr(freq)
        elif direction == 'Right' and speed == 'Long':
            sr(freq)
        elif direction == 'Flat':
            cnst(freq)

    def get_selected_direction(self):
        if self.left_radio.isChecked():
            return 'Left'
        elif self.right_radio.isChecked():
            return 'Right'
        elif self.flat_radio.isChecked():
            return 'Flat'

    def get_selected_speed(self):
        if self.short_radio.isChecked():
            return 'Short'
        elif self.long_radio.isChecked():
            return 'Long'

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LearnWindow()
    window.show()
    sys.exit(app.exec_())