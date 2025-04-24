import numpy as np
from scipy.io.wavfile import write

# DTMF frequencies
DTMF_FREQS = {
    '1': (697, 1209),
    '2': (697, 1336),
    '3': (697, 1477),
    'A': (697, 1633),
    '4': (770, 1209),
    '5': (770, 1336),
    '6': (770, 1477),
    'B': (770, 1633),
    '7': (852, 1209),
    '8': (852, 1336),
    '9': (852, 1477),
    'C': (852, 1633),
    '*': (941, 1209),
    '0': (941, 1336),
    '#': (941, 1477),
    'D': (941, 1633)
}

def generate_tone(frequencies, duration=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = np.sin(2 * np.pi * frequencies[0] * t) + np.sin(2 * np.pi * frequencies[1] * t)
    return tone

def encode_phone_number(phone_number, sample_rate=44100):
    tones = []
    for digit in phone_number:
        if digit in DTMF_FREQS:
            tone = generate_tone(DTMF_FREQS[digit], sample_rate=sample_rate)
            tones.append(tone)
            # Add a short silence between tones
            tones.append(np.zeros(int(sample_rate * 0.1)))
    return np.concatenate(tones)

def save_to_wav(data, filename, sample_rate=44100):
    # Normalize to 16-bit range
    data = np.int16(data / np.max(np.abs(data)) * 32767)
    write(filename, sample_rate, data)

if __name__ == "__main__":
    phone_number = "123-456-7890"
    audio_data = encode_phone_number(phone_number)
    save_to_wav(audio_data, "phone_number.wav")