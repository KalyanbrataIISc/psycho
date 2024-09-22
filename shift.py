from sound import SoundGenerator
import numpy as np
import time

def phase_shift_sound(frequency, start_deg, stop_deg, time_interval, total_time):
    """
    Generates a sound with a given frequency, starting at start_deg phase and linearly
    shifting to stop_deg phase over time_interval seconds, within the total_time duration,
    with the volume reduced to 50%.
    
    Parameters:
    frequency: Frequency of the sound in Hz.
    start_deg: Initial phase in degrees.
    stop_deg: Final phase in degrees.
    time_interval: Duration of the phase shift in seconds.
    total_time: Total time for the sound to play (must be greater than time_interval).
    """
    if total_time <= time_interval:
        raise ValueError("total_time must be greater than time_interval")

    # Create the sound generator
    sound_gen = SoundGenerator()

    # Convert degrees to radians for starting and stopping phase
    start_phase_rad = np.deg2rad(start_deg)
    stop_phase_rad = np.deg2rad(stop_deg)

    # Calculate the time before and after the phase change
    pre_phase_time = (total_time - time_interval) / 2
    post_phase_time = total_time - pre_phase_time - time_interval

    # Number of frames for the entire sound duration
    total_frames = int(sound_gen.sample_rate * total_time)

    # Frames where the phase shift should occur
    start_phase_frame = int(sound_gen.sample_rate * pre_phase_time)
    stop_phase_frame = start_phase_frame + int(sound_gen.sample_rate * time_interval)

    # Phase difference step per frame
    phase_step = (stop_phase_rad - start_phase_rad) / (stop_phase_frame - start_phase_frame)

    # Initialize phase difference
    current_phase = start_phase_rad

    # Start sound generation
    sound_gen.update_sound_properties(frequency, 0.5, 0.5, np.rad2deg(current_phase))  # 50% volume initially
    sound_gen.start_sound()

    # Get the start time
    start_time = time.time()

    for frame in range(total_frames):
        # Determine the phase for this frame
        if frame < start_phase_frame:
            # Before phase shift, use start phase, 50% volume
            current_phase = start_phase_rad
        elif start_phase_frame <= frame <= stop_phase_frame:
            # During phase shift, update the phase linearly, 50% volume
            current_phase = start_phase_rad + (frame - start_phase_frame) * phase_step
        else:
            # After phase shift, use stop phase, 50% volume
            current_phase = stop_phase_rad

        # Update the sound properties with the current phase and reduced volume (50%)
        sound_gen.update_sound_properties(frequency, 0.5, 0.5, np.rad2deg(current_phase))

        # Calculate how long we need to wait to maintain real-time playback
        elapsed_time = time.time() - start_time
        target_time = (frame + 1) / sound_gen.sample_rate
        sleep_time = target_time - elapsed_time

        if sleep_time > 0:
            time.sleep(sleep_time)

    # Ensure the sound stops after the total time
    sound_gen.stop_sound()

def volume_shift_sound_precise(frequency, start_left_vol, stop_left_vol, start_right_vol, stop_right_vol, time_interval, total_time):
    """
    Generates a sound with a given frequency, changing the left and right volumes over time_interval seconds,
    within the total_time duration.

    Parameters:
    frequency: Frequency of the sound in Hz.
    start_left_vol: Initial left volume (0.0 to 1.0).
    stop_left_vol: Final left volume (0.0 to 1.0).
    start_right_vol: Initial right volume (0.0 to 1.0).
    stop_right_vol: Final right volume (0.0 to 1.0).
    time_interval: Duration of the volume change in seconds.
    total_time: Total time for the sound to play (must be greater than time_interval).
    """
    if total_time <= time_interval:
        raise ValueError("total_time must be greater than time_interval")

    # Create the sound generator
    sound_gen = SoundGenerator()

    # Number of frames for the entire sound duration
    total_frames = int(sound_gen.sample_rate * total_time)

    # Frames where the volume shift should occur
    start_vol_frame = int(sound_gen.sample_rate * (total_time - time_interval) / 2)
    stop_vol_frame = start_vol_frame + int(sound_gen.sample_rate * time_interval)

    # Volume step per frame for left and right channels
    left_vol_step = (stop_left_vol - start_left_vol) / (stop_vol_frame - start_vol_frame)
    right_vol_step = (stop_right_vol - start_right_vol) / (stop_vol_frame - start_vol_frame)

    # Initialize left and right volumes
    left_vol = start_left_vol
    right_vol = start_right_vol

    # Start sound generation
    sound_gen.update_sound_properties(frequency, left_vol, right_vol, 0)  # Start with initial volumes
    sound_gen.start_sound()

    # Get the start time
    start_time = time.time()

    for frame in range(total_frames):
        # Determine the volumes for this frame
        if frame < start_vol_frame:
            # Before volume shift, use start volumes
            left_vol = start_left_vol
            right_vol = start_right_vol
        elif start_vol_frame <= frame <= stop_vol_frame:
            # During volume shift, update the volumes linearly
            left_vol = start_left_vol + (frame - start_vol_frame) * left_vol_step
            right_vol = start_right_vol + (frame - start_vol_frame) * right_vol_step
        else:
            # After volume shift, use stop volumes
            left_vol = stop_left_vol
            right_vol = stop_right_vol

        # Update the sound properties with the current volumes
        sound_gen.update_sound_properties(frequency, left_vol, right_vol, 0)

        # Calculate how long we need to wait to maintain real-time playback
        elapsed_time = time.time() - start_time
        target_time = (frame + 1) / sound_gen.sample_rate
        sleep_time = target_time - elapsed_time

        if sleep_time > 0:
            time.sleep(sleep_time)

    # Ensure the sound stops after the total time
    sound_gen.stop_sound()

def volume_shift_sound(frequency, start_vol, stop_vol, time_interval, total_time):
    """
    Generates a sound with a given frequency, changing the volume over time_interval seconds,
    within the total_time duration.

    Parameters:
    frequency: Frequency of the sound in Hz.
    start_vol: Initial volume (-100 to 100).
    stop_vol: Final volume (-100 to 100).
    time_interval: Duration of the volume change in seconds.
    total_time: Total time for the sound to play (must be greater than time_interval).
    """

    start_vol = 0 - start_vol
    stop_vol = 0 - stop_vol
    start_left_vol = (start_vol + 100) / 200
    stop_left_vol = (stop_vol + 100) / 200
    start_right_vol = 1 - start_left_vol
    stop_right_vol = 1 - stop_left_vol

    volume_shift_sound_precise(frequency, start_left_vol, stop_left_vol, start_right_vol, stop_right_vol, time_interval, total_time)

max_deg = 150 # Don't change this value
max_vol = 35 # Don't change this value
short_time = 3 # Don't change this value
long_time = 9 # Don't change this value
full_time = 10 # Don't change this value


def short_left_phase_shift(freq):
    """
    Generates a short sound with a phase shift from left to right.
    """
    phase_shift_sound(freq, 0, -max_deg, short_time, full_time)

def short_right_phase_shift(freq):
    """
    Generates a short sound with a phase shift from right to left.
    """
    phase_shift_sound(freq, 0, max_deg, short_time, full_time)

def short_left_volume_shift(freq):
    """
    Generates a short sound with a volume shift from left to right.
    """
    volume_shift_sound(freq, 0, -max_vol, short_time, full_time)

def short_right_volume_shift(freq):
    """
    Generates a short sound with a volume shift from right to left.
    """
    volume_shift_sound(freq, 0, max_vol, short_time, full_time)

def long_left_phase_shift(freq):
    """
    Generates a long sound with a phase shift from left to right.
    """
    phase_shift_sound(freq, 0, -max_deg, long_time, full_time)

def long_right_phase_shift(freq):
    """
    Generates a long sound with a phase shift from right to left.
    """
    phase_shift_sound(freq, 0, max_deg, long_time, full_time)

def long_left_volume_shift(freq):
    """
    Generates a long sound with a volume shift from left to right.
    """
    volume_shift_sound(freq, 0, -max_vol, long_time, full_time)

def long_right_volume_shift(freq):
    """
    Generates a long sound with a volume shift from right to left.
    """
    volume_shift_sound(freq, 0, max_vol, long_time, full_time)

def sound_shift(freq=440, mode='phase', direction='left', shift='short'):
    """
    Generates a sound with a given frequency and shift type.
    
    Parameters:
    freq: Frequency of the sound in Hz.
    mode: Shift mode ('phase' or 'volume').
    direction: Shift direction ('left' or 'right').
    shift: Shift duration ('short' or 'long').
    """

    if mode == 'phase':
        if direction == 'left':
            if shift == 'short':
                short_left_phase_shift(freq)
            elif shift == 'long':
                long_left_phase_shift(freq)
            else:
                raise ValueError("Invalid shift duration")
        elif direction == 'right':
            if shift == 'short':
                short_right_phase_shift(freq)
            elif shift == 'long':
                long_right_phase_shift(freq)
            else:
                raise ValueError("Invalid shift duration")
        else:
            raise ValueError("Invalid shift direction")
    elif mode == 'volume':
        if direction == 'left':
            if shift == 'short':
                short_left_volume_shift(freq)
            elif shift == 'long':
                long_left_volume_shift(freq)
            else:
                raise ValueError("Invalid shift duration")
        elif direction == 'right':
            if shift == 'short':
                short_right_volume_shift(freq)
            elif shift == 'long':
                long_right_volume_shift(freq)
            else:
                raise ValueError("Invalid shift duration")
        else:
            raise ValueError("Invalid shift direction")
    elif mode == 'flat':
        phase_shift_sound(freq, 0, 0, long_time, full_time)
    else:
        raise ValueError("Invalid shift mode")
    
    ans = [direction, shift]
    return ans
    

