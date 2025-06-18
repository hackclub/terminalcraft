# CodePlotter - A Command Line Tool

## Why?

I recently spent a couple of weeks converting an old 3D printer into a pen-plotter, and with that, I noticed several issues. I was using a tool to generate handwriting as G-Code using RNNs but it was difficult to get that GCode to be exactly where I wanted it on the build plate of my printer. That's where CodePlotter comes in, CodePlotter allows you to manipulate GCode as if its an image file. You can scale, merge, move, rotate, and much more. Additionally, as I used CodePlotter, I added features such as a pen offset (Because of how the conversion from 3D printer to pen plotter worked, I needed an easy way of measuring where exactly I wanted the pen to draw), which saves you from doing complex calculations.

## Features

- **Single File Transformations**: Scale, rotate, translate, and apply pen offsets to individual G-code files
- **Multi-File Merging**: Combine multiple G-code files with individual transformations
- **Rotation Support**: Rotate G-code around the origin with precise angle control
- **Pen Offset Compensation**: Account for pen/tool offsets in plotter operations
- **Bounds Calculation**: Display file dimensions and coordinate ranges
- **Bed Boundary Cropping**: Automatically crop coordinates to stay within bed limits
- **Auto-Centering**: Automatically center files on the print bed
- **Legacy Mode**: Simple scale and offset operations for backward compatibility

## Example Usage & Images

Original GCode (Visualized)
![OriginalGCodeExample](https://github.com/user-attachments/assets/82814f8c-d90e-4210-a068-e898a32c47fc)

GCode With Transformations Applied Using CodePlotter (Visualized)
![ModifiedGCodeExample](https://github.com/user-attachments/assets/a9c43cc7-767c-4828-b6b9-faf77a5ca2f6)

CodePlotter Terminal Usage Example
![CodePlotterUsageExample](https://github.com/user-attachments/assets/52f905f0-5cb4-4f6b-8c10-14ef8971c106)

## Requirements

- Python 3.6 or higher
- No additional dependencies required (uses only standard library)

## Usage

Run the script and choose from three operation modes:
On Unix, run:
```bash
./CodePlotter_Unix
```
On Windows, run CodePlotter.exe

OR

Just run the Python file, you shouldn't need any dependencies :)

### Mode 1: Single File Transform

Transform a single G-code file with comprehensive parameter control:

- **Scaling**: Independent X, Y, Z scaling factors
- **Rotation**: Rotate around origin (in degrees)
- **Translation**: X, Y, Z coordinate offsets
- **Pen Offsets**: Compensation for plotter pen positioning
- **Bed Cropping**: Optional coordinate clipping to bed boundaries

**Example workflow:**
1. Enter file path to your G-code
2. Set transformation parameters (scale, rotation, offsets)
3. Configure bed dimensions and cropping options
4. Save the transformed file

### Mode 2: Multi-File Merge

Combine multiple G-code files with individual transformations:

- Load multiple files with different transformations
- Auto-center option for each file
- Individual parameter control per file
- Unified output with proper headers and comments

**Example workflow:**
1. Set bed dimensions
2. Add files one by one with their transformations
3. Option to auto-center each file on the bed
4. Generate merged output file

### Mode 3: Legacy Mode

Simple scale and offset operations for backward compatibility:

- Basic X, Y, Z scaling
- Basic X, Y, Z translation
- Compatible with original legacy.py behavior

## Transformation Parameters

### Scaling
- **X Scale**: Horizontal scaling factor (1.0 = no change, 2.0 = double size)
- **Y Scale**: Vertical scaling factor
- **Z Scale**: Height scaling factor

### Rotation
- **Rotation Angle**: Degrees to rotate around origin (positive = counterclockwise)

### Translation
- **X Offset**: Horizontal movement in mm
- **Y Offset**: Vertical movement in mm
- **Z Offset**: Height adjustment in mm

### Pen Offsets (for Plotters)
- **Pen X Offset**: Horizontal offset between pen and carriage
- **Pen Y Offset**: Vertical offset between pen and carriage

*Note: Pen offsets are subtracted from final coordinates to compensate for physical pen positioning*

## Bounds and Validation

The tool automatically calculates and displays:
- Original file dimensions and coordinate ranges
- Transformed file dimensions
- Warnings if coordinates exceed bed boundaries
- Usable space after pen offset compensation

## Output Files

All output files include:
- Transformation parameter comments
- Original file identification
- Bed dimension information
- Coordinate clipping notifications (if applicable)

## Example Transformations

### Scale a file to 50% size:
```
X scale: 0.5
Y scale: 0.5
Z scale: 0.5
```

### Rotate 45 degrees and move to corner:
```
Rotation: 45
X offset: 10
Y offset: 10
```

### Compensate for pen offset:
```
Pen X offset: 5.0
Pen Y offset: 2.5
```

### Center and scale for smaller bed:
```
X scale: 0.8
Y scale: 0.8
Auto-center: Yes
```

## File Formats

- **Input**: Standard G-code files (.gcode, .nc, .g)
- **Output**: G-code with transformation comments and headers
- **Encoding**: UTF-8 with error handling for various file encodings

## Error Handling

The tool includes comprehensive error handling for:
- File not found errors
- Invalid numeric inputs
- Empty or corrupted G-code files
- Coordinate parsing errors
- File write permissions

## Tips and Best Practices

1. **Always check bounds** after transformation to ensure coordinates fit your bed
2. **Use auto-center** when combining files of different sizes
3. **Set pen offsets** accurately for plotter operations
4. **Enable cropping** when working near bed boundaries
5. **Save intermediate files** when doing complex multi-step transformations
6. **Test with small files** first when learning the tool

## Troubleshooting

### Common Issues:

**"File not found"**: Check file path and ensure file exists
**"Invalid input"**: Ensure numeric values are entered for parameters
**"Coordinates exceed bed"**: Reduce scaling or adjust offsets
**"Empty file"**: Check that input file contains valid G-code

### Performance:

- Large files (>100k lines) may take several seconds to process
- Rotation and cropping operations are more computationally intensive
- Memory usage scales with file size and number of files in merge mode

## Version History

- **v2.0**: Added rotation, pen offsets, multi-file support, bounds calculation
- **v1.0**: Original simple scale and offset functionality

## License

Created by Aditya Mendiratta

---
