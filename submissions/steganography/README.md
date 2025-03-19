# Steganography Tool

This is a simple steganography tool that allows users to hide and extract messages from images using the Least Significant Bit (LSB) method.


## Requirements
First install dependencies with :

```bash
pip install -r requirements.txt
```

## How to Run

1. Clone the repository or download the script.
2. Ensure you have Python installed (preferably Python 3.x).
3. Navigate to the script location and run the following command (first install dependencies):

```bash
python main.py
```


## Note
Currently working on hiding text in video, there are lots of errors. So will upload that feature in feature-branch.


## Notes
- The tool does not handle very large messages or images efficiently due to the nature of the LSB method
- Ensure the image file is a valid format (e.g., PNG, JPEG).
- The tool modifies the least significant bit of pixels to store the message.
- Messages are terminated with `|||` to mark the end of the hidden text.

