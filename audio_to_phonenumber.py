import numpy as np
import wave


# DTMF frequencies
DTMF_FREQS = {
    (697, 1209): '1',
    (697, 1336): '2',
    (697, 1477): '3',
    (697, 1633): 'A',
    (770, 1209): '4',
    (770, 1336): '5',
    (770, 1477): '6',
    (770, 1633): 'B',
    (852, 1209): '7',
    (852, 1336): '8',
    (852, 1477): '9',
    (852, 1633): 'C',
    (941, 1209): '*',
    (941, 1336): '0',
    (941, 1477): '#',
    (941, 1633): 'D'
}

def read_wave_file(file_path):
    with wave.open(file_path, 'r') as wav_file:
        frames = wav_file.readframes(-1)
        frame_rate = wav_file.getframerate()
        audio_data = np.frombuffer(frames, dtype=np.int16)
    return audio_data, frame_rate

def split_audio_on_silence(audio_file, chunk_size=128):
    audio_data, frame_rate = read_wave_file(audio_file)

    silence_threshold = np.mean(np.abs(audio_data)) * 0.5
    chunks = []
    start = 0
    end = 0
    silent_chunks = 0

    for i in range(0, len(audio_data)- chunk_size, chunk_size):
        if np.mean(np.abs(audio_data[i:i+chunk_size])) < silence_threshold:
            silent_chunks += 1
            end = i if silent_chunks == 1 else end
        else:
            if silent_chunks * chunk_size > frame_rate * 0.02:
                chunks.append(audio_data[start:end])
                start = i
            silent_chunks = 0
    
    chunks.append(audio_data[start:end])
    
    return chunks, frame_rate

def check_sine_wave(audio_data, frame_rate, target_freq):
    n = len(audio_data)
    t = np.arange(n) / frame_rate
    sine_wave = np.sin(2 * np.pi * target_freq * t)
    
    correlation = np.correlate(audio_data, sine_wave, mode='valid')
    max_correlation = np.max(correlation)
    
    return max_correlation


import matplotlib.pyplot as plt

def plot_audio_chunks(chunks, frame_rate):
    num_chunks = len(chunks)
    plt.plot
    fig, axs = plt.subplots(num_chunks, 1, figsize=(10, 2 * num_chunks))
    
    if num_chunks == 1:
        axs = [axs]
    
    for i, chunk in enumerate(chunks):
        t = np.arange(len(chunk)) / frame_rate
        axs[i].plot(t, chunk)
        axs[i].set_title(f'Chunk {i+1}')
        axs[i].set_xlabel('Time [s]')
        axs[i].set_ylabel('Amplitude')
    
    plt.tight_layout()
    plt.show()

def decode_phone(audio_file):
    number_notes, frame_rate = split_audio_on_silence(audio_file)
    phone_number = ''

    # plot_audio_chunks(number_notes, frame_rate)
    for note in number_notes:
        max1 = 0
        max2 = 0
        freq1 = 0
        freq2 = 0
        for freqs1, freqs2 in DTMF_FREQS.keys():
            correlation = abs(check_sine_wave(note, frame_rate, freqs1))
            if correlation > max1:
                max1 = correlation
                freq1 = freqs1
            correlation = abs(check_sine_wave(note, frame_rate, freqs2))
            if correlation > max2:
                max2 = correlation
                freq2 = freqs2
        phone_number += DTMF_FREQS[(freq1, freq2)]
    return phone_number

if __name__ == "__main__":
    audio_file = 'phone_number.wav'
    phone_number = decode_phone(audio_file)
    print(f"Decoded phone number: {phone_number}")