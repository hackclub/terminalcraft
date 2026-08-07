import os
from PIL import Image, ImageDraw
import numpy as np
import random

def gen_image(width=800,height=600):

    bg_color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
    image= Image.new("RGB", (width,height), bg_color)
    draw= ImageDraw.Draw(image)
    
    for i in range(random.randint(5, 15)):
        shapet =random.choice(["ellipse", "rectangle", "polygon"])
        color =(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        x1, y1 =random.randint(0, width-100), random.randint(0, height-100)
        x2, y2 =x1 + random.randint(50, 200), y1 + random.randint(50, 200)
        
        if shapet=="ellipse":
            draw.ellipse([x1, y1, x2, y2], fill=color)
        elif shapet== "rectangle":
            draw.rectangle([x1, y1, x2, y2], fill=color)
        else:  
            points= []
            for i in range(3,7):
                points.append((random.randint(x1, x2), random.randint(y1, y2)))
            draw.polygon(points, fill=color)
    
    
    for i in range(random.randint(3,8)):
        color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        draw.line(
            [(random.randint(0,width),random.randint(0,height)),
             (random.randint(0,width),random.randint(0,height))],
            fill=color, width=random.randint(1, 5)
        )
    
    return image

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
    if len(msg_bin) > img.size[0] * img.size[1] * 3:
        raise ValueError("Message too large for the image")
    
  
    img_array = np.array(img)
    idx = 0
    
    
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            for k in range(3):  
                if idx < len(msg_bin):
                    img_array[i, j, k] = (img_array[i, j, k] & 0xFE) | int(msg_bin[idx])
                    idx += 1
                else:
                    break
            if idx >= len(msg_bin):
                break
        if idx >= len(msg_bin):
            break
    
    return Image.fromarray(img_array)

def decode_img(img, password=None):
   
    img_array = np.array(img)
    bin_msg = ''
    
  
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            for k in range(3):
                bin_msg += str(img_array[i, j, k] & 1)
    
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


        print("-"*20)
        print("STEGANOGRAPHY TOOL")
        print("-"*20)

        print("1.Hide message in new random image")
        print("2.Hide message in existing image")
        print("3.Unhide message")
        print("4.Exit")
        choice=input("Choose an option (1/2/3/4): ")

        print()
        print("-"*60)
        print()

        if choice == '1':
            
            print("\nGenerating random image...")
            text=input("Enter the text you want to hide: ")

            print()
            print("-"*60)
            print()
            
            use_password = input("Add password protection? (y/n): ").lower()

            print()
            print("-"*60)
            print()

            password = None
            if use_password == 'y':
                password = input("Enter password: ")

                print()
                print("-"*60)
              

                if not password:
                    print("Password cannot be empty. Not using password protection.")
            
            self_dwp = False
            self_daw = False
            
            if use_password == 'y':
                sd_wrong = input("Self-destruct after wrong password attempt? (y/n): ").lower()

                print()
                print("-"*60)
                print()

                self_dwp = sd_wrong == 'y'
            
            sd_view = input("Self-destruct after one successful viewing? (y/n): ").lower()

            print()
            print("-"*60)
       
            
            self_daw = sd_view == 'y'
            
           
            img = gen_image()
            try:
                enc_img = encode_img(img, text, password, self_dwp, self_daw)
                out_path = os.path.join(os.getcwd(), 'encoded_image.png')
                enc_img.save(out_path)
                
                print(f"\nImage with hidden message saved as 'encoded_image.png' at '{os.getcwd()}'")

                print()
                print("-"*60)
                print()

                if self_dwp:
                    print("Warning: Image will self-destruct after wrong password attempt!")
                if self_daw:
                    print("Warning: Image will self-destruct after one successful viewing!")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == '2':
            img_path = input("Enter path to image file: ")

            print()
            print("-"*60)
            print()

            if not os.path.isfile(img_path):
                print("\nFile not found. Please check path and try again!!")
                continue
            
            text = input("Enter the text you want to hide: ")

            print()
            print("-"*60)
            print()
            
            use_password = input("Add password protection? (y/n): ").lower()

            print()
            print("-"*60)
            print()
            
            password = None
            if use_password == 'y':
                password=input("enter password to protect the message: ")

                print()
                print("-"*60)
                print()

                if not password:
                    print("password cannot be empty,not using password protection.")
            
            self_dwp = False
            self_daw = False
            
            if use_password=='y':
                sd_wrong = input("Self-destruct after wrong password attempt? (y/n): ").lower()
                self_dwp = sd_wrong == 'y'
            
            sd_view = input("Self-destruct after one successful viewing? (y/n): ").lower()
            self_daw = sd_view == 'y'
            
            try:
                img = Image.open(img_path)
                enc_img = encode_img(img, text, password, self_dwp, self_daw)
                out_path = os.path.join(os.getcwd(), 'encoded_image.png')
                enc_img.save(out_path)
                
                print(f"\nImage with hidden message saved as 'encoded_image.png' at '{os.getcwd()}'")
                if self_dwp:
                    print("Warning: Image will self-destruct after wrong password attempt!!")
                if self_daw:
                    print("Warning: Image will self-destruct after one successful viewing!!")
            except ValueError as e:
                print(f"Error: Message too large for this image. {e}")
            except Exception as e:
                print(f"Error processing image: {e}")

        elif choice == '3':
            
            img_path = input("Enter path to encoded image: ")

            print()
            print("-"*60)
            print()
            
            if not os.path.isfile(img_path):
                print("\nFile not found. Please check path and try again.")
                continue
            
            password = input("Enter password (if protected, else press enter): ")
            if password == "":
                password = None
            
            try:
                img = Image.open(img_path)
                hidden_msg, should_destruct_wrong, should_destruct_view = decode_img(img, password)
                
                if should_destruct_wrong or should_destruct_view:
                    try:
                        os.remove(img_path)
                        print("\nThe image has self-destructed as per its settings!!")
                    except Exception as e:
                        print(f"\nFailed to self-destruct image: {str(e)}")
                
                print()
                print("-"*60)
                print()

                print("\nHidden message:", hidden_msg)
            except Exception as e:
                print(f"Error decoding image: {e}")

            

        elif choice == '4':
            print("\nExiting program!!!!")
           
            print("-"*60)
            print()
            break

        else:
            print("\nInvalid option. Please try again.")

if __name__ == '__main__':
    main()