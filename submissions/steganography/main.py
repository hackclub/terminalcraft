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

def encode_img(img, msg, password=None, self_dwp=False, self_daw=False):
   
    metadata = []
    if password:
        metadata.append(f"PWD{password}")
    else:
        metadata.append("NPW")
    
    if self_dwp:
        metadata.append("SDWP1")
    else:
        metadata.append("SDWP0")
        
    if self_daw:
        metadata.append("SDAV1")
    else:
        metadata.append("SDAV0")
    
    msg = '|||'.join(metadata) + '|||' + msg + "|||"
    
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

def decode_img(img, password=None):
    bin_msg = ''
    img_data = list(img.getdata())

    for px in img_data:
        bin_msg += str(px[0] & 1)

    msg = bin_to_str(bin_msg)
    
    parts = msg.split('|||')
    if len(parts) < 5:  
        return "No hidden message found or corrupted data.", False, False
    
 
    password_flag = parts[0]
    self_dwp = parts[1] == "SDWP1"
    self_daw = parts[2] == "SDAV1"
    hidden_msg = parts[3]
    
  
    if password_flag.startswith('PWD'):
        stored_password = password_flag[3:]
        if password is None:
            return "This message is password protected. Please provide the correct password.", False, False
        elif password != stored_password:
            if self_dwp:
                return "Wrong password. The image has self-destructed.", True, False
            return "Wrong password.", False, False
        else:
            if self_daw:
                return hidden_msg, False, True
            return hidden_msg, False, False
    else:
        if self_daw:
            return hidden_msg, False, True
        return hidden_msg, False, False

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

            text = input("Enter the text you want to hide:")
            
            
            use_password = input("Do you want to add password protection? (y/n): ").lower()
            password = None
            if use_password == 'y':
                password = input("enter password to protect the message: ")
                if not password:
                    print("password cannot be empty,not using password protection.")
            
            
            self_dwp = False
            self_daw = False
            
            if use_password == 'y':
                sd_wrong = input("Self-destruct after wrong password attempt? (y/n): ").lower()
                self_dwp = sd_wrong == 'y'
            
            sd_view = input("Self-destruct after one successful viewing? (y/n): ").lower()
            self_daw = sd_view == 'y'
            
            img = Image.open(img_path)
            enc_img = encode_img(img, text, password, self_dwp, self_daw)

            out_path = os.path.join(os.getcwd(), 'encoded_image.png')
            enc_img.save(out_path)

            print()
            print("-"*60)
            print()

            print(f"Message hidden in file 'encoded_image.png' saved at '{os.getcwd()}'")
            if self_dwp:
                print("Warning: Image will self-destruct after wrong password attempt!")
            if self_daw:
                print("Warning: Image will self-destruct after one successful viewing!")

        elif choice == '2':
            img_path = input("Enter the path to the encoded image file: ")
            if not os.path.isfile(img_path):
                print()
                print("-"*60)
                print()
                print("File not found, Please check path and tryr again!!")
                continue

            img = Image.open(img_path)
            
            password = input("Enter password (if message is protected, press enter if none): ")
            if password == "":
                password = None
                
            hidden_msg, should_destruct_wrong, should_destruct_view = decode_img(img, password)
            
            
            if should_destruct_wrong or should_destruct_view:
                try:
                    os.remove(img_path)
                    print("\nThe image is self-destructed as per its settings.")
                except Exception as e:
                    print(f"\nFailed to self-destruct image: {str(e)}")

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