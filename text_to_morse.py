import numpy as np
import wave

# Morse code dictionary
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ' ': '/'
}

# Parameters for the audio
SAMPLE_RATE = 44100
DOT_DURATION = 0.1  # seconds
DASH_DURATION = 0.3  # seconds
FREQUENCY = 1000  # Hz

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(char.upper(), '') for char in text)

def generate_tone(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * frequency * t)

def generate_morse_audio(morse_code):
    audio = np.array([], dtype=np.float32)
    for symbol in morse_code:
        if symbol == '.':
            audio = np.concatenate((audio, generate_tone(FREQUENCY, DOT_DURATION, SAMPLE_RATE)))
        elif symbol == '-':
            audio = np.concatenate((audio, generate_tone(FREQUENCY, DASH_DURATION, SAMPLE_RATE)))
        elif symbol == ' ':
            audio = np.concatenate((audio, np.zeros(int(SAMPLE_RATE * DOT_DURATION))))
        elif symbol == '/':
            audio = np.concatenate((audio, np.zeros(int(SAMPLE_RATE * DASH_DURATION))))
        audio = np.concatenate((audio, np.zeros(int(SAMPLE_RATE * DOT_DURATION))))  # Space between symbols
    return audio

def save_wave(filename, audio, sample_rate):
    audio = np.int16(audio * 32767)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

if __name__ == "__main__":
    text = "HELLO WORLD"
    morse_code = text_to_morse(text)
    audio = generate_morse_audio(morse_code)
    save_wave("morse_code.wav", audio, SAMPLE_RATE)