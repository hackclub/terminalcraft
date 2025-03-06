# picflip - all in one image tool
an python terminal application that removes background images, and also turns them into pngs

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-0.1.1-brightgreen.svg)

## the brains
This app uses libraries like rembg, PIL, and cairosvg for the image manipulation! rembg is used to remove the background, and PIL and cairosvg is to convert the images into png's

## installation
You can install picflip using pip!
```sh
pip install picflip
```
make sure you have python installed otherwise it wont work.

## usage
once its installed, you can run picflip directly from the terminal. run the **usage** command for a quickstart!
```sh
picflip usage
```

### remove background - usage
to remove the background, just use the *remove* command and then enter the path to your image, and also provide an output image. **(a tip - enter the same information as the input image in the output, and you wont have an extra file)**
```sh
picflip remove shrek.png shrek.png
```

### convert images - usage
if you need to convert webp, jpeg and svg (cairo required), to png's you can use the *convert* command, then enter your image to convert, and then the output image in the .png extension!
```sh
picflip convert shrek.webp shrek.png
```

## example 

[Example Video (will redirect you to another tab)](https://hc-cdn.hel1.your-objectstorage.com/s/v3/f3f569c3833d4b6b711a9478ddda9fae5b6ac3b9_picflip.mp4)
