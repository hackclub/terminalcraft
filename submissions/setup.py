from setuptools import setup, find_packages

setup(
    name="picflip",
    version="0.1.1",
    description="Picflip - fix your images by removing backgrounds and converting to PNG!",
    long_description="""picflip is a terminal application that does everything you would want to do with a image, remove their bg's and convert them to png!

remove backgrounds or convert JPG, WEBP, and even SVG images to PNG's with just a couple of commands!

Usage:
  picflip remove <input_image> <output_image>
  picflip convert <input_image> <output_image>
  picflip usage
""",
    long_description_content_type="text/markdown",
    author="Divpreet Singh",
    author_email="divpreetsingh68@gmail.com",
    url="https://github.com/divpreeet/picflip",
    packages=find_packages(),
    install_requires=[
        "rembg",
        "Pillow",
        "cairosvg",
        "onnxruntime"
    ],
    entry_points={
        "console_scripts": [
            "picflip=picflip.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
