import os
from svgpathtools import svg2paths, Path
import xml.etree.ElementTree as ET
from math import sqrt

# Define input and output directories
# Replace these with your own folder paths (see README.md for setup instructions)
input_dir = r'C:\Users\YourUsername\Desktop\MultiLeaves\svg mask - INPUT'
output_dir = r'C:\Users\YourUsername\Desktop\MultiLeaves\svg labels - OUTPUT'

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to calculate distance between two points
def distance(p1, p2):
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Function to check if two point lists are nearly identical, translation-invariant
def are_points_similar(points1, points2, threshold=50, size_threshold=50):
    if len(points1) != len(points2):
        return False
    
    # Compute bboxes
    minx1, maxx1 = min(p[0] for p in points1), max(p[0] for p in points1)
    miny1, maxy1 = min(p[1] for p in points1), max(p[1] for p in points1)
    w1 = maxx1 - minx1
    h1 = maxy1 - miny1
    
    minx2, maxx2 = min(p[0] for p in points2), max(p[0] for p in points2)
    miny2, maxy2 = min(p[1] for p in points2), max(p[1] for p in points2)
    w2 = maxx2 - minx2
    h2 = maxy2 - miny2
    
    if abs(w1 - w2) > size_threshold or abs(h1 - h2) > size_threshold:
        return False
    
    # Compute bbox centers
    cx1 = (minx1 + maxx1) / 2
    cy1 = (miny1 + maxy1) / 2
    cx2 = (minx2 + maxx2) / 2
    cy2 = (miny2 + maxy2) / 2
    
    # Check distances after shifting
    mismatches = 0
    for p1, p2 in zip(points1, points2):
        dx = (p1[0] - cx1) - (p2[0] - cx2)
        dy = (p1[1] - cy1) - (p2[1] - cy2)
        if sqrt(dx**2 + dy**2) > threshold:
            mismatches += 1
            if mismatches > 50:  # Allow some mismatches for robustness
                return False
    return True

# Loop through all SVG files
for j in os.listdir(input_dir):
    if not j.lower().endswith('.svg'):
        continue
    
    svg_path = os.path.join(input_dir, j)
    
    try:
        # Parse SVG with ElementTree to extract text labels
        tree = ET.parse(svg_path)
        root = tree.getroot()
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}
        
        texts = []
        for text_elem in root.findall('.//svg:text', namespaces):
            x = float(text_elem.get('x', 0))
            y = float(text_elem.get('y', 0))
            label = ''.join(text_elem.itertext()).strip()
            if label:
                texts.append({'label': label, 'x': x, 'y': y})
        
        # Diagnostic print: number and content of extracted labels
        print(f"--- Diagnostics for {j} ---")
        print(f"Number of extracted text labels: {len(texts)}")
        print(f"Extracted labels: {texts}")
        
        # Get paths using svgpathtools
        paths, attributes = svg2paths(svg_path)
        
        if not paths:
            print(f"No paths found in {j}")
            continue
        
        # Diagnostic print: total number of paths
        print(f"Total number of paths: {len(paths)}")
        
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
            print(f"Warning: Using default A4 dimensions for {j}")
        
        # Determine orientation
        orientation = "landscape" if svg_width > svg_height else "portrait"
        print(f"SVG dimensions: width={svg_width}, height={svg_height}, orientation={orientation}")
        
        # Filter paths: assume leaves are significant paths, ignore very short ones
        min_length_threshold = 100.0
        leaf_paths = [p for p in paths if p.length() > min_length_threshold]
        
        if not leaf_paths:
            print(f"No significant paths found in {j}")
            continue
        
        # Diagnostic print: number of significant paths
        print(f"Number of significant paths (leaves) after filtering: {len(leaf_paths)}")
        
        # Compute centers and bboxes for each path
        path_data = []
        for idx, path in enumerate(leaf_paths):
            bbox = path.bbox()
            center_x = (bbox[0] + bbox[1]) / 2
            center_y = (bbox[2] + bbox[3]) / 2
            path_data.append({
                'path': path,
                'center': (center_x, center_y),
                'bbox': bbox,
                'label': None,
                'points': [],  # To store sampled points for duplication check
                'length': path.length()  # Added for additional similarity check
            })
        
        # Sample points for each path - Increased num_points for better accuracy
        num_points = 2000
        for pd in path_data:
            points = []
            for i in range(num_points):
                t = i / (num_points - 1)
                point = pd['path'].point(t)
                x, y = point.real, point.imag
                pixel_x, pixel_y = int(round(x)), int(round(y))
                points.append((pixel_x, pixel_y))
            pd['points'] = points
        
        # Diagnostic print: path centers and lengths
        print(f"Path centers: {[pd['center'] for pd in path_data]}")
        print(f"Path lengths: {[pd['length'] for pd in path_data]}")  # Added diagnostic
        
        # If this is a vein file, load the corresponding blade file and filter out matching paths
        base_name = j[:-4]  # Remove .svg extension
        is_blade = "blade" in base_name.lower()
        is_vein = "vein" in base_name.lower() or "veins" in base_name.lower()
        
        if is_vein:
            # Find corresponding blade file, handling more variations
            blade_file_candidates = [
                j.replace("_vein.svg", "_blade.svg").replace("_Vein.svg", "_Blade.svg"),
                j.replace("_veins.svg", "_blades.svg").replace("_Veins.svg", "_Blades.svg"),
                j.replace("_vein.svg", "_blade.svg").lower().replace("_veins.svg", "_blades.svg"),
                j.replace("_vein", "_blade").replace(".svg", ".svg")  # Additional variations
            ]
            blade_path = None
            for candidate in blade_file_candidates:
                candidate_path = os.path.join(input_dir, candidate)
                if os.path.exists(candidate_path):
                    blade_path = candidate_path
                    print(f"Found corresponding blade file: {candidate}")
                    break
            
            if blade_path:
                blade_paths, _ = svg2paths(blade_path)
                blade_leaf_paths = [p for p in blade_paths if p.length() > min_length_threshold]
                
                blade_datas = []
                for bp in blade_leaf_paths:
                    points = []
                    for i in range(num_points):
                        t = i / (num_points - 1)
                        point = bp.point(t)
                        x, y = point.real, point.imag
                        pixel_x, pixel_y = int(round(x)), int(round(y))
                        points.append((pixel_x, pixel_y))
                    blade_datas.append({'points': points, 'length': bp.length()})
                
                # Filter out paths that match any blade path - Added length check for better filtering
                new_path_data = []
                for pd in path_data:
                    is_blade_path = False
                    for bd in blade_datas:
                        if abs(pd['length'] - bd['length']) < 100 and are_points_similar(pd['points'], bd['points']):  # Combined length and points
                            is_blade_path = True
                            print(f"Skipping blade-like path at center {pd['center']} in vein file (length match: {pd['length']} vs {bd['length']})")
                            break
                    if not is_blade_path:
                        new_path_data.append(pd)
                path_data = new_path_data
                print(f"After filtering, remaining paths: {len(path_data)}")  # Added diagnostic
            else:
                print(f"No corresponding blade file found for {j}")
        
        # Associate texts to nearest path centers
        for text in texts:
            min_dist = float('inf')
            closest_path = None
            for pd in path_data:
                dist = distance((text['x'], text['y']), pd['center'])
                if dist < min_dist:
                    min_dist = dist
                    closest_path = pd
            if closest_path:
                closest_path['label'] = text['label']
                print(f"Assigned label '{text['label']}' to path at center {closest_path['center']} with distance {min_dist}")
            else:
                print(f"Label '{text['label']}' not assigned to any path (large distance)")
        
        # Assign default labels and handle duplicates based on file name
        path_data.sort(key=lambda pd: pd['center'][0])  # Sort by x-center
        used_points = set()  # To track unique point sets
        
        for idx, pd in enumerate(path_data, start=1):
            if pd['label'] is None:
                # Default labeling based on file type
                if is_vein:
                    pd['label'] = f"vein{idx}"  # Label veins separately if multiple
                elif is_blade:
                    pd['label'] = "blade"
                else:
                    pd['label'] = f"leaf{idx}"
                
                # Check for duplicates with previous paths
                is_duplicate = False
                for prev_pd in path_data[:idx-1]:
                    if are_points_similar(pd['points'], prev_pd['points']):
                        is_duplicate = True
                        pd['label'] = f"{prev_pd['label']}_duplicate"
                        print(f"Detected duplicate path at {pd['center']}, labeled as {pd['label']}")
                        break
                if not is_duplicate:
                    print(f"Assigned default label '{pd['label']}' to unlabeled path at center {pd['center']}")
        
        # Process each path
        output_file = os.path.join(output_dir, base_name + '.txt')
        with open(output_file, 'w') as f:
            for pd in path_data:
                f.write(f"{pd['label']}\n")
                for x, y in pd['points']:
                    f.write(f"{x} {y}\n")
                f.write("\n")  # Separator
        
        print(f"Successfully processed {j}, points saved to {output_file} with {len(path_data)} leaves.")
    
    except Exception as e:
        print(f"Error processing {j}: {str(e)}")