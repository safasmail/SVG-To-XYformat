import os
from svgpathtools import svg2paths, Path

# Define input and output directories
input_dir = r'path\to\your\svg mask - INPUT'  # Replace with your input folder path
output_dir = r'path\to\your\svg labels - OUTPUT'  # Replace with your output folder path

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Loop through all SVG files
for j in os.listdir(input_dir):
    if not j.lower().endswith('.svg'):
        continue
    
    svg_path = os.path.join(input_dir, j)
    
    try:
        paths, attributes = svg2paths(svg_path)
        
        if not paths:
            print(f"No paths found in {j}")
            continue
        
        main_path = max(paths, key=lambda p: p.length())
        
        # Get SVG dimensions
        svg_width = None
        svg_height = None
        for attr in attributes:
            if 'viewBox' in attr:
                viewbox = attr['viewBox'].split()
                svg_width = float(viewbox[2]) - float(viewbox[0])
                svg_height = float(viewbox[3]) - float(viewbox[1])
            if 'width' in attr and svg_width is None:
                svg_width = float(attr['width'].strip('px'))
            if 'height' in attr and svg_height is None:
                svg_height = float(attr['height'].strip('px'))
        
        if svg_width is None or svg_height is None:
            svg_width, svg_height = 2480.0, 3508.0  # Default to A4 at 300 DPI
            print(f"Warning: Using A4 default dimensions for {j}")
        
        # Determine orientation
        orientation = "landscape" if svg_width > svg_height else "portrait"
        print(f"SVG dimensions for {j}: width={svg_width}, height={svg_height}, orientation={orientation}")
        
        # Sample more points for smoother curves
        num_points = 1000  # Increased for better curve approximation
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            point = main_path.point(t)
            x, y = point.real, point.imag
            # Save coordinates as pixel values (not normalized)
            pixel_x = int(round(x))  # Round to nearest integer
            pixel_y = int(round(y))
            points.append((pixel_x, pixel_y))
        
        # Check for duplicates or invalid points
        unique_points = []
        for p in points:
            if not unique_points or p != unique_points[-1]:  # Avoid consecutive duplicates
                unique_points.append(p)
        
        # Write to text file
        output_file = os.path.join(output_dir, j[:-4] + '.txt')
        with open(output_file, 'w') as f:
            for x, y in unique_points:
                f.write(f"{x} {y}\n")
        print(f"Successfully processed {j}, points saved to {output_file} with {len(unique_points)} unique points.")
    
    except Exception as e:
        print(f"Error processing {j}: {str(e)}")
