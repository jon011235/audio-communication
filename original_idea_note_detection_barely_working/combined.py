import numpy as np
import wave
import struct
import os
import matplotlib.pyplot as plt

def read_wave_file(file_path):
    with wave.open(file_path, 'rb') as wave_file:
        n_channels = wave_file.getnchannels()
        sample_width = wave_file.getsampwidth()
        frame_rate = wave_file.getframerate()
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
            audio_data = audio_data.reshape(-1, n_channels)
            audio_data = audio_data.mean(axis=1)  # Average the channels to get a 1D array
        
        return audio_data, frame_rate, wave_file.getparams()

def detect_notes(waveform, frame_size=512, hop_size=256, threshold=1.5):
    mean = np.mean(np.abs(waveform))

    notes = []
    start_index = None

    for i in range(0, len(waveform) - frame_size, hop_size):
        frame = waveform[i:i + frame_size]
        frame_mean = np.mean(np.abs(frame))

        if frame_mean > threshold*mean and start_index is None:
            start_index = i
        elif frame_mean <= threshold*mean and start_index is not None:
            end_index = i
            notes.append((start_index, end_index))
            start_index = None

    if start_index is not None:
        notes.append((start_index, len(waveform)))
    return notes


def detect_notes_with_std(waveform, frame_size=32, hop_size=16, std_factor=2):
    mean = np.mean(np.abs(waveform))
    std = np.std(np.abs(waveform))

    notes = []
    start_index = 0
    flag = False

    for i in range(0, len(waveform) - frame_size, hop_size):
        frame = waveform[i:i + frame_size]
        frame_mean = np.mean(np.abs(frame))

        if frame_mean > mean + std_factor * std and not flag:
            flag = True
            if start_index != 0:
                notes.append((start_index, i-1))
            start_index = i
        elif frame_mean > mean + std_factor * std:
            pass
        else:
            flag = False

    print(notes)
    return notes

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

def correlate(audio_data, frame_rate, audio_file):
    reference_data, ref_frame_rate, _ = read_wave_file(audio_file)
    
    if frame_rate != ref_frame_rate:
        raise ValueError("Frame rates do not match")
    
    correlation = np.correlate(audio_data, reference_data, mode='valid')
    max_correlation = np.max(correlation)
    
    return max_correlation

if __name__ == "__main__":
    input_file = 'alle_meine_entchen--heilpaedagogik-info-de.wav'
    output_dir = 'out/'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    wave_data, frame_rate, params = read_wave_file(input_file)
    # Convert to mono if the audio is stereo
    if params.nchannels > 1:
        wave_data = wave_data[::params.nchannels]
        params = params._replace(nchannels=1)

    abc_notation = []
    i = 0
    for start_index, end_index in detect_notes_with_std(wave_data):
        print(f'Note {i+1}: {start_index} - {end_index}')
        i +=1
        note_data = wave_data[start_index:end_index]
        output_file = os.path.join(output_dir, f'note_{i+1}.wav')
        save_wave_file(output_file, params, note_data)
        
        # Find the dominant frequency of the note
        max_correlation = 0
        dominant_freq = 0
        #frequencies = np.linspace(300, 600, 100)
        frequencies = ["piano/Piano.ff.A1.wav", "piano/Piano.ff.B1.wav", "piano/Piano.ff.C1.wav", "piano/Piano.ff.D1.wav", "piano/Piano.ff.E1.wav", "piano/Piano.ff.F1.wav", "piano/Piano.ff.G1.wav"]
        for freq in frequencies:
            #correlation = check_sine_wave(note_data, frame_rate, freq)
            correlation = correlate(note_data, frame_rate, freq)
            if correlation > max_correlation:
                max_correlation = correlation
                dominant_freq = freq
        
        # Convert the dominant frequency to ABC notation
        abc_note = frequency_to_abc(dominant_freq)
        abc_notation.append(abc_note)
    

    # Print the ABC notation
    print("ABC Notation:", " ".join(abc_notation))
