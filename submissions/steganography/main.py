import os
from PIL import Image

def str_to_bin(s):
    return ''.join(format(ord(c), '08b') for c in s)

def bin_to_str(b):
    chars = []
    for i in range(0, len(b), 8):
        byte = b[i:i + 8]
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

def encode_img(img, msg):
    msg += "|||"
    msg_bin = str_to_bin(msg)
    idx = 0
    img_data = list(img.getdata())
    
    for i in range(len(img_data)):
        px = list(img_data[i])
        if idx < len(msg_bin):
            px[0] = (px[0] & 0xFE) | int(msg_bin[idx])
            idx += 1
        img_data[i] = tuple(px)

    img.putdata(img_data)
    return img

def decode_img(img):
    bin_msg = ''
    img_data = list(img.getdata())

    for px in img_data:
        bin_msg += str(px[0] & 1)

    msg = bin_to_str(bin_msg)
    return msg.split('|||')[0]


def main():
    while True:
        print()
        print("-"*60)
        print()
        
        print("-"*20)
        print("STEGANOGRAPHY TOOL")
        print("-"*20)
        print("1. Hide message")
        print("2. Unhide message")
        print("3. Exit")
        choice = input("Choose an option (1/2/3): ")

        print()
        print("-"*60)
        print()

        if choice == '1':
            img_path = input("Enter the path to the image file: ")
            if not os.path.isfile(img_path):

                print()
                print("-"*60)
                print()

                print("File not found, Please check path and try again!!")
                continue

            print()
            print("-"*60)
            print()

            text = input("Enter the text you want to hide: ")
            img = Image.open(img_path)
            enc_img = encode_img(img, text)

            out_path = os.path.join(os.getcwd(), 'encoded_image.png')
            enc_img.save(out_path)

            print()
            print("-"*60)
            print()

            print(f"Message hidden in file 'encoded_image.png' saved at '{os.getcwd()}'")

        elif choice == '2':
            img_path = input("Enter the path to the encoded image file: ")
            if not os.path.isfile(img_path):

                print()
                print("-"*60)
                print()

                print("File not found, Please check path and try again!!")
                continue

            img = Image.open(img_path)
            hidden_msg = decode_img(img)

            print()
            print("-"*60)
            print()

            print("Decoded message:", hidden_msg)

        elif choice == '3':
            print("Exiting the program!!!")

            print()
            print("-"*60)
            print()

            break

        else:
            print("Invalid option, Please try again!!")

if __name__ == '__main__':
    main()
