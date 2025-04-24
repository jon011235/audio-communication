def encode_pixmap(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    encoded_string = ""
    for line in lines[1:]:  # Skip the first line (standard number)
        encoded_string += line.strip().replace(" ", "#") + "*"
    
    return encoded_string

def decode_pixmap(encoded_string, output_file_path):
    decoded_lines = encoded_string.replace("*", "\n").replace("#", " ")
    with open(output_file_path, 'w') as file:
        file.write("P3\n")  # Write the standard number
        file.write(decoded_lines)


if __name__ == "__main__":
    import audio_to_phonenumber
    import phonenumber_to_audio
    print("1: Encode, 2: Decode")
    choice = input()
    file = input("Enter the file path: ")
    if choice == '1':
        encoded = encode_pixmap(file)
        audio = phonenumber_to_audio.encode_phone_number(encoded)
        phonenumber_to_audio.save_to_wav(audio, "phone_number.wav")

        
    elif choice == '2':
        phone_number = audio_to_phonenumber.decode_phone(file)
        print(phone_number)
        decoded_message = decode_pixmap(phone_number, "output.pbm")