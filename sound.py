import numpy as np
import sounddevice as sd
import threading

class SoundGenerator:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.stream = None
        self.is_playing = False
        self.current_frequency = 440
        self.target_frequency = 440
        self.left_amp = 1.0
        self.right_amp = 1.0
        self.phase_diff = 0.0
        self.stop_event = threading.Event()
        self.phase = 0.0  # To ensure continuous waveform

    def generate_stereo_wave(self, frames):
        """
        Generate a short stereo wave of a given frequency with specified amplitudes and phase difference.
        """
        # Smoothly transition to the target frequency
        freq_step = (self.target_frequency - self.current_frequency) / frames
        t = np.linspace(0, frames / self.sample_rate, frames, False)

        # Generate the sine wave for both channels
        stereo_wave = np.zeros((frames, 2))
        for i in range(frames):
            # Update frequency smoothly
            self.current_frequency += freq_step

            # Generate the next sample, maintaining phase continuity
            self.phase += 2 * np.pi * self.current_frequency / self.sample_rate
            self.phase %= 2 * np.pi  # Keep phase within 0 to 2*pi
            phase_diff_rad = np.deg2rad(self.phase_diff)

            # Calculate the sample for each channel
            stereo_wave[i, 0] = np.sin(self.phase) * self.left_amp  # Left channel
            stereo_wave[i, 1] = np.sin(self.phase + phase_diff_rad) * self.right_amp  # Right channel

        # Convert to float32 for sounddevice compatibility
        return stereo_wave.astype(np.float32)

    def start_sound(self):
        """
        Start playing the sound in a continuous loop.
        """
        self.is_playing = True
        self.stop_event.clear()
        self.stream = sd.OutputStream(samplerate=self.sample_rate, channels=2, callback=self.callback, blocksize=1024)
        self.stream.start()

    def stop_sound(self):
        """
        Stop playing the sound.
        """
        self.is_playing = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.stop_event.set()

    def callback(self, outdata, frames, time, status):
        """
        Callback function for the output stream.
        """
        if not self.is_playing or self.stop_event.is_set():
            outdata[:] = np.zeros((frames, 2), dtype=np.float32)
            return

        # Generate the stereo wave for the number of frames needed
        stereo_wave = self.generate_stereo_wave(frames)

        # Fill the output buffer with the generated stereo wave
        outdata[:] = stereo_wave

    def update_sound_properties(self, frequency, left_amp, right_amp, phase_diff):
        """
        Update sound properties for real-time adjustment.
        """
        self.target_frequency = frequency  # Update target frequency
        self.left_amp = left_amp
        self.right_amp = right_amp
        self.phase_diff = phase_diff