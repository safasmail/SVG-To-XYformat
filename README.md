# SVG-To-XYformat
SVG to XY Converter
This Python script converts SVG files to XY coordinate .txt files, streamlining the drawing workflow by allowing editable drawings in Adobe Illustrator (15-day trial) or Inkscape (free), avoiding the need to restart 35-minute drawings in ImageJ/Fiji.
Requirements

Python 3.6+ (download).
svgpathtools: Install via:pip install svgpathtools



Setup

**Create Folders**

Input folder (e.g., svg mask - INPUT) for SVG files.
Output folder (e.g., svg labels - OUTPUT) for .txt files.


**Update File Paths**

Open svg_to_xy_converter.py in a text editor.
Modify input_dir and output_dir to match your system. Example:input_dir = r'C:\Users\YourUsername\Desktop\svg mask - INPUT'  # Replace with your input folder
output_dir = r'C:\Users\YourUsername\Desktop\svg labels - OUTPUT'  # Replace with your output folder


For macOS/Linux: /Users/YourUsername/Desktop/svg mask - INPUT.


Save the Script:

Save as svg_to_xy_converter.py.


**Usage**

Place SVG files in the input folder.
Run in terminal:python svg_to_xy_converter.py
Or:python3 svg_to_xy_converter.py
Check .txt files in the output folder with XY coordinates.


**Troubleshooting**

Module not found: Verify svgpathtools installation (pip show svgpathtools).
Contact [Your Name] for issues.


This project is licensed under the MIT License - see the LICENSE file for details.
Feedback
Please test and share feedback. If effective, consider sharing with the team.
