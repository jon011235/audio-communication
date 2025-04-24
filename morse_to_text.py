import numpy as np
import wave

# Morse code dictionary
MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
    '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
    '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
    '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
    '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
    '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9'
}

def read_wave_file(file_path):
    with wave.open(file_path, 'r') as wav_file:
        frames = wav_file.readframes(-1)
        frame_rate = wav_file.getframerate()
        audio_data = np.frombuffer(frames, dtype=np.int16)
    return audio_data, frame_rate

def decode_morse(audio_data, frame_rate):
    threshold = np.max(audio_data) * 0.5
    frame_size = int(frame_rate/500)
    morse_code = ''
    counter = 0
    silence = True

    for i in range(0, len(audio_data)-frame_size, frame_size):
        sample = np.mean(np.abs(audio_data[i:i+frame_size]))
        if sample < threshold and silence:
            counter += frame_size
        elif sample < threshold:
            silence = True
            if counter > frame_rate * 0.2:
                morse_code += "-"
            elif counter > frame_rate *0.05:
                morse_code += "."
            else:
                print("unrecognized tone")
            counter = frame_size
        elif sample >= threshold and not silence:
            counter += frame_size
        else:
            silence = False
            if counter > frame_rate * 1.5: # word break
                morse_code += "   "
            elif counter > frame_rate *0.4: # char finished
                morse_code += " "
            else:
                pass
                #print("unrecognized silence")
            counter = frame_size

    return morse_code

def morse_to_text(morse_code):
    words = morse_code.split('   ')
    decoded_message = ''
    for word in words:
        for char in word.split():
            decoded_message += MORSE_CODE_DICT.get(char, '')
        decoded_message += ' '
    return decoded_message.strip()

if __name__ == "__main__":
    audio_data, frame_rate = read_wave_file('morse_code.wav')
    morse_code = decode_morse(audio_data, frame_rate)
    decoded_message = morse_to_text(morse_code)
    print(decoded_message)