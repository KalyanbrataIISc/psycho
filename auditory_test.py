# auditory_experiment.py

from psychopy import visual, sound, event, core, gui
import numpy as np
import random
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# -------------------------------
# Participant Information Dialog
# -------------------------------

def get_participant_info():
    info = {'Username': '', 'Age': '', 'Gender': ['Male', 'Female', 'Other']}
    dlg = gui.DlgFromDict(dictionary=info, title='Participant Information')
    if dlg.OK:
        return info
    else:
        core.quit()

participant_info = get_participant_info()

# -------------------------------
# Experiment Parameters
# -------------------------------

# Stimulus settings
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

# -------------------------------
# Prepare Stimuli
# -------------------------------

def generate_tone(frequency, duration, sample_rate, amplitude_left, amplitude_right, phase_diff):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    phase_rad = np.deg2rad(phase_diff)
    tone_left = amplitude_left * np.sin(2 * np.pi * frequency * t)
    tone_right = amplitude_right * np.sin(2 * np.pi * frequency * t + phase_rad)
    stereo_tone = np.array([tone_left, tone_right]).T
    return stereo_tone

# -------------------------------
# Generate Trials
# -------------------------------

def create_trials():
    trials = []

    # Amplitude difference trials
    for amp_diff in AMPLITUDE_DIFFS:
        for _ in range(TRIALS_PER_LEVEL):
            amplitude_left = 1.0
            amplitude_right = 1.0 * (10 ** (-amp_diff / 20))
            label = 'Left' if amp_diff > 0 else 'Center'
            trials.append({'type': 'Amplitude', 'amp_diff': amp_diff, 'phase_diff': 0,
                           'amplitude_left': amplitude_left, 'amplitude_right': amplitude_right,
                           'label': label})

    # Phase difference trials
    for phase_diff in PHASE_DIFFS:
        for _ in range(TRIALS_PER_LEVEL):
            amplitude_left = 1.0
            amplitude_right = 1.0
            label = 'Left' if phase_diff > 0 else 'Center'
            trials.append({'type': 'Phase', 'amp_diff': 0, 'phase_diff': phase_diff,
                           'amplitude_left': amplitude_left, 'amplitude_right': amplitude_right,
                           'label': label})

    # Catch trials (no difference)
    for _ in range(CATCH_TRIALS):
        trials.append({'type': 'Catch', 'amp_diff': 0, 'phase_diff': 0,
                       'amplitude_left': 1.0, 'amplitude_right': 1.0, 'label': 'Center'})

    random.shuffle(trials)
    return trials

trials = create_trials()

# -------------------------------
# Experiment Execution
# -------------------------------

def run_experiment(trials):
    win = visual.Window(fullscr=True, color=[0, 0, 0], units='pix')
    instruction_text = visual.TextStim(win, text="Press 'J' for Left, 'K' for Center, 'L' for Right.\nPress any key to start.", color='white')
    instruction_text.draw()
    win.flip()
    event.waitKeys()

    results = []

    for trial_num, trial in enumerate(trials):
        # Generate stimulus
        tone = generate_tone(FREQUENCY, DURATION, SAMPLE_RATE,
                             trial['amplitude_left'], trial['amplitude_right'], trial['phase_diff'])
        stimulus = sound.Sound(value=tone, sampleRate=SAMPLE_RATE, stereo=True)

        # Play stimulus
        stimulus.play()
        core.wait(DURATION)

        # Collect response
        response = None
        timer = core.Clock()
        while timer.getTime() < 2.0:  # 2-second response window
            keys = event.getKeys(keyList=list(RESPONSE_KEYS.keys()))
            if keys:
                response = RESPONSE_KEYS[keys[0]]
                break

        # Default response if none
        if response is None:
            response = 'No Response'

        # Store result
        results.append({'Trial': trial_num + 1, 'Type': trial['type'],
                        'Amplitude Difference': trial['amp_diff'],
                        'Phase Difference': trial['phase_diff'],
                        'Label': trial['label'], 'Response': response})

        # Clear events
        event.clearEvents()

        # Inter-trial interval
        core.wait(1.0)

    win.close()
    return results

results = run_experiment(trials)

# -------------------------------
# Data Analysis
# -------------------------------

def analyze_results(results):
    import pandas as pd
    from scipy.optimize import curve_fit

    df = pd.DataFrame(results)

    # Filter out 'No Response'
    df = df[df['Response'] != 'No Response']

    # Define sigmoid function
    def sigmoid(x, L ,x0, k, b):
        y = L / (1 + np.exp(-k*(x-x0))) + b
        return y

    analysis_results = {}

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

    analysis_results['Amplitude'] = {'x': amp_x, 'y': amp_y, 'fit_x': amp_fit_x, 'fit_y': amp_fit_y, 'threshold': amp_threshold}

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

    analysis_results['Phase'] = {'x': phase_x, 'y': phase_y, 'fit_x': phase_fit_x, 'fit_y': phase_fit_y, 'threshold': phase_threshold}

    return analysis_results

analysis_results = analyze_results(results)

# -------------------------------
# Generate PDF Report
# -------------------------------

def generate_pdf(participant_info, analysis_results):
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

generate_pdf(participant_info, analysis_results)

# -------------------------------
# End of Experiment
# -------------------------------

print("Experiment completed. Results have been saved.")