import os
import glob
import cv2
import numpy as np

def load_polygons(txt_path):
    print(f"Loading polygons from: {txt_path}")
    polygons = []
    if not os.path.exists(txt_path):
        print(f"Error: File {txt_path} does not exist!")
        return polygons
    
    with open(txt_path, 'r') as f:
        lines = f.readlines()
    print(f"File opened successfully. Total lines: {len(lines)}")
    
    i = 0
    current_poly = []
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            if current_poly:
                polygons.append(np.array(current_poly, dtype=np.int32).reshape((-1, 1, 2)))
                current_poly = []
            continue
        try:
            parts = line.split()
            if len(parts) != 2:
                raise ValueError
            x, y = map(float, parts)
            current_poly.append([int(round(x)), int(round(y))])
        except ValueError:
            if current_poly:
                polygons.append(np.array(current_poly, dtype=np.int32).reshape((-1, 1, 2)))
                current_poly = []
    if current_poly:
        polygons.append(np.array(current_poly, dtype=np.int32).reshape((-1, 1, 2)))
    
    print(f"Loaded {len(polygons)} polygons.")
    return polygons

def rescale_and_center_polygons(polygons, width, height, base_name):
    if not polygons:
        return polygons
    
    all_points = np.concatenate(polygons, axis=0)
    min_x = all_points[:, 0, 0].min()
    min_y = all_points[:, 0, 1].min()
    max_x = all_points[:, 0, 0].max()
    max_y = all_points[:, 0, 1].max()
    
    orig_width = max_x - min_x
    orig_height = max_y - min_y
    
    if max_x < width * 0.5 or max_y < height * 0.5:
        scale_x = width / orig_width if orig_width > 0 else 1
        scale_y = height / orig_height if orig_height > 0 else 1
        scale = min(scale_x, scale_y)
        new_width = orig_width * scale
        new_height = orig_height * scale
        offset_x = (width - new_width) / 2
        offset_y = (height - new_height) / 2
        
        if base_name == '588640a':
            offset_x += 50
            offset_y += 50
        
        for i in range(len(polygons)):
            polygons[i][:, 0, 0] = (polygons[i][:, 0, 0] - min_x) * scale + offset_x
            polygons[i][:, 0, 1] = (polygons[i][:, 0, 1] - min_y) * scale + offset_y
    
    return polygons

def get_total_area(polygons):
    return sum(cv2.contourArea(poly) for poly in polygons if len(poly) >= 3)

def overlay_polygons():
    print("Starting execution...")
    # Replace these with your own folder paths (see README.md for setup instructions)
    data_dir = r"C:\Users\YourUsername\Desktop\MultiLeaves\Test Leaf DATA\data"
    outputs_dir = r"C:\Users\YourUsername\Desktop\MultiLeaves\Test Leaf DATA\outputs"

    if not os.path.exists(data_dir):
        print(f"Error: Data directory {data_dir} does not exist!")
        return

    os.makedirs(outputs_dir, exist_ok=True)

    image_extensions = ['jpg', 'jpeg', 'png', 'tif', 'tiff']
    image_files = set()
    for ext in image_extensions:
        image_files.update(glob.glob(os.path.join(data_dir, f'*.{ext}')))
        image_files.update(glob.glob(os.path.join(data_dir, f'*.{ext.upper()}')))    
    image_files = list(image_files)
    print(f"Found {len(image_files)} images: {image_files}")

    if not image_files:
        print("No images found in the data directory.")
        return

    for img_path in image_files:
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        print(f"Processing image: {base_name}...")
        
        img = cv2.imread(img_path)
        if img is None:
            print(f"Error: Could not read image {img_path}")
            continue

        height, width = img.shape[:2]
        print(f"Image dimensions: {width}x{height}")

        blank_canvas = np.zeros_like(img, dtype=np.uint8)
        
        blade_path = os.path.join(data_dir, f'{base_name}_blade.txt')
        print(f"Looking for blade file: {blade_path}")
        blade_polys = load_polygons(blade_path)
        blade_polys = rescale_and_center_polygons(blade_polys, width, height, base_name)
        
        veins_path = os.path.join(data_dir, f'{base_name}_vein.txt')
        veins_path_alt = os.path.join(data_dir, f'{base_name}_veins.txt')
        if os.path.exists(veins_path):
            veins_polys = load_polygons(veins_path)
        elif os.path.exists(veins_path_alt):
            veins_polys = load_polygons(veins_path_alt)
        else:
            veins_polys = []
        veins_polys = rescale_and_center_polygons(veins_polys, width, height, base_name)
        
        # Optional: Skip drawing veins if they seem too large (uncomment if needed)
        # if blade_polys and veins_polys:
        #     blade_area = get_total_area(blade_polys)
        #     veins_area = get_total_area(veins_polys)
        #     print(f"Blade area: {blade_area}, Veins area: {veins_area}")
        #     if veins_area > blade_area * 0.5:
        #         print(f"Warning: Veins area too large for {base_name}, skipping veins drawing.")
        #         veins_polys = []

        if blade_polys:
            cv2.fillPoly(blank_canvas, blade_polys, color=(255, 127, 0))

        if veins_polys:
            cv2.fillPoly(blank_canvas, veins_polys, color=(255, 0, 255))

        final_img = img.copy()
        
        alpha_blade = 0.5
        alpha_veins = 0.8
        
        blade_mask = np.all(blank_canvas == [255, 127, 0], axis=-1)
        if np.any(blade_mask):
            final_img[blade_mask] = (
                final_img[blade_mask] * (1 - alpha_blade) +
                np.array([255, 127, 0]) * alpha_blade
            ).astype(np.uint8)
        
        veins_mask = np.all(blank_canvas == [255, 0, 255], axis=-1)
        if np.any(veins_mask):
            final_img[veins_mask] = (
                final_img[veins_mask] * (1 - alpha_veins) +
                np.array([255, 0, 255]) * alpha_veins
            ).astype(np.uint8)

        output_filename = f'{base_name}.jpg'
        output_path = os.path.join(outputs_dir, output_filename)
        cv2.imwrite(output_path, final_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"Saved output to: {output_path}")

if __name__ == '__main__':
    overlay_polygons()