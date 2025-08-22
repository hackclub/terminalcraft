import pathlib
import flightdeck.files.picture as picture
import flightdeck.files.markdown as markdown

def read_file(file):
    print(f"Reading file: {file}")
    extension = pathlib.Path(file).suffix.lower()
    print("Extension:", extension)

    image = [".jpg", ".jpeg", ".png"]
    
    try:
        if extension in image:
            picture.print_image(file)
        elif extension == ".md":
            markdown.print_markdown_fancy(file)
    except:
        print("Error reading. Please try again or make sure the file exists.")

