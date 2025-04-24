import wave
import struct
import array
import numpy as np
import os

def read_wave_file(file_path):
    with wave.open(file_path, 'rb') as wave_file:
        n_channels = wave_file.getnchannels()
        sample_width = wave_file.getsampwidth()
        frame_rate = wave_file.getframerate() ## TODO Might be double the sample rate (divide by sample_width). Also change mean of the stereo
        n_frames = wave_file.getnframes()
        frames = wave_file.readframes(n_frames)
        
        if sample_width == 1:
            dtype = np.uint8  # 8-bit audio
        elif sample_width == 2:
            dtype = np.int16  # 16-bit audio
        else:
            raise ValueError("Unsupported sample width")
        
        audio_data = np.frombuffer(frames, dtype=dtype)
        if n_channels > 1:
            audio_data = audio_data[::n_channels]  # Use only the first channel
        
        return audio_data, frame_rate, wave_file.getparams()

def detect_onsets(audio_data, threshold=1800):
    onsets = []
    frame_size = 1024
    num_frames = len(audio_data) // frame_size

    for i in range(1, num_frames):
        prev_frame = audio_data[(i - 1) * frame_size:i * frame_size]
        curr_frame = audio_data[i * frame_size:(i + 1) * frame_size]

        prev_energy = sum(abs(x) for x in prev_frame) / frame_size
        curr_energy = sum(abs(x) for x in curr_frame) / frame_size

        if curr_energy - prev_energy > threshold:
            onsets.append(i * frame_size)

    return onsets

def split_notes(filename):
    audio_data, sample_rate, params = read_wave_file(filename)

    onsets = detect_onsets(audio_data)
    note_segments = []

    for i in range(len(onsets) - 1):
        start = onsets[i]
        end = onsets[i + 1]
        note_segments.append(audio_data[start:end])

    return note_segments, sample_rate, params

def save_wave_file(file_path, params, wave_data):
    with wave.open(file_path, 'w') as wav_file:
        wav_file.setparams(params)
        wave_data = np.int16(wave_data)  # Convert to 16-bit integers
        frames = struct.pack('{n}h'.format(n=len(wave_data)), *wave_data)
        wav_file.writeframes(frames)

def check_sine_wave(audio_data, frame_rate, target_freq):
    n = len(audio_data)
    t = np.arange(n) / frame_rate
    sine_wave = np.sin(2 * np.pi * target_freq * t)
    
    correlation = np.correlate(audio_data, sine_wave, mode='valid')
    max_correlation = np.max(correlation)
    
    return max_correlation

# def frequency_to_abc(frequency):
#     # This function converts a frequency to an ABC notation string
#     # For simplicity, we'll assume A4 = 440 Hz and use a basic mapping
#     A4 = 440
#     C0 = A4 * 2**(-4.75)
#     note_names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
#     h = round(12 * np.log2(frequency / C0))
#     octave = h // 12
#     n = h % 12
#     return note_names[n] + str(octave)

def estimate_duration(len_note, frame_rate):
    duration_seconds = len_note / frame_rate
    print(duration_seconds)
    
    # Map duration to ABC notation
    if duration_seconds >= 0.75:
        return "1"  # Whole note
    elif duration_seconds >= 0.375:
        return "/2"  # Half note
    elif duration_seconds >= 0.1875:
        return "/4"  # Quarter note
    elif duration_seconds >= 0.09375:
        return "/8"  # Eighth note
    elif duration_seconds >= 0.046875:
        return "/16"  # Sixteenth note
    else:
        return "/32"  # Shorter note

def frequency_to_abc(frequency):
    # Reference: MIDI note 69 is A4 (440 Hz)
    A4_freq = 440.0
    A4_midi = 69
    
    # Calculate the MIDI note number
    midi_number = round(12 * np.log2(frequency / A4_freq) + A4_midi)
    
    # Define ABC notation note names
    abc_notes = ["C", "^C", "D", "^D", "E", "F", "^F", "G", "^G", "A", "^A", "B"]
    
    # Calculate note name and octave
    note_index = (midi_number - 12) % 12
    octave = (midi_number // 12) - 1  # MIDI octave starts at -1 for C-1
    
    # Convert octave to ABC notation format
    note = abc_notes[note_index]
    if octave >= 5:
        note = note.lower() + "'" * (octave - 4)
    elif octave < 4:
        note = note + "," * (3 - octave)
    
    return note

# Example usage:
filename = 'alle_meine_entchen--heilpaedagogik-info-de.wav'

# TODO
audio_data, frame_rate, params = read_wave_file(filename)
save_wave_file("out.wav", params, audio_data)

notes, sr, params = split_notes(filename)
abc_notation = []
for i, note_data in enumerate(notes):
    output_file = os.path.join("out", f'note_{i+1}.wav')
    save_wave_file(output_file, params, note_data)

    # Find the dominant frequency of the note
    max_correlation = 0
    dominant_freq = 0
    frequencies = np.linspace(300, 600, 100)
    for freq in frequencies:
        correlation = check_sine_wave(note_data, sr, freq)
        if correlation > max_correlation:
            max_correlation = correlation
            dominant_freq = freq
    
    # Convert the dominant frequency to ABC notation
    abc_note = frequency_to_abc(dominant_freq)
    abc_notation.append(abc_note+ estimate_duration(len(note_data), sr))
    

# Print the ABC notation
print("ABC Notation:\nL:1/4\n", " ".join(abc_notation))
print(f'Detected {len(notes)} notes.')
