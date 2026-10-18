# SVG-To-XYformat

Python tools for converting hand-traced leaf SVG files into XY coordinate `.txt` files, as part of the grapevine leaf vein and lobe segmentation project. These scripts let tracing be done in Adobe Illustrator (15-day trial) or Inkscape (free), avoiding the need to re-trace leaves in ImageJ/Fiji.

Two versions are provided:

- **`MULTIsvg2point.py`** (current version) — converts SVG files containing **multiple leaves per file**, with automatic text-label reading and duplicate/overlap filtering between blade and vein paths.
- **`legacy/svg-to-XY.py`** (original version, Sept 2025) — converts SVG files containing a **single leaf per file**. Kept here for reference and for compatibility with any older traced data that still uses this format.

A companion quality-control script, **`MULTItest_leaf_data.py`**, overlays the converted coordinates back onto the original scan image so the conversion can be checked visually before the data is used for training.

## What's new in `MULTIsvg2point.py`

Compared to the original `legacy/svg-to-XY.py`:

- Supports **any number of leaf paths in one SVG file**, instead of exactly one.
- Reads the **text labels placed on the SVG** (e.g. `blade`, `vein1`, `vein2`) and assigns each label to its nearest path automatically; paths with no label get an automatic default name.
- Detects and removes **duplicate or overlapping paths between a vein file and its matching blade file**, so a blade-shaped path that was accidentally included in a vein tracing is filtered out before it reaches the training data.
- Increased the number of sampled points per path from 1,000 to 2,000 for smoother coordinate curves.
- Writes all leaves from one SVG into a **single combined `.txt` file**, with each leaf's section starting with its label and separated from the next by a blank line (instead of one `.txt` file per leaf).
- Falls back to A4 page dimensions (2480×3508 px) only if the SVG's width/height truly cannot be read from its `viewBox` or `width`/`height` attributes, same as the original.

## Requirements

- Python 3.6+
- `svgpathtools` — install with:
  ```
  pip install svgpathtools
  ```
- For the QC overlay script (`MULTItest_leaf_data.py`) only:
  ```
  pip install opencv-python numpy
  ```

## Setup

### 1. Create folders

For `MULTIsvg2point.py`:
- An input folder (e.g. `svg mask - INPUT`) containing your traced SVG files.
- An output folder (e.g. `svg labels - OUTPUT`) where the converted `.txt` files will be written.

For `MULTItest_leaf_data.py`:
- A `data` folder containing the original scan images together with the `.txt` files produced above (matched by file name, e.g. `leaf01_blade.txt`, `leaf01_vein.txt`).
- An `outputs` folder where the overlay check images will be saved.

### 2. Update file paths

Open the script in a text editor and change the folder paths near the top to match your own system. For example, in `MULTIsvg2point.py`:
```python
input_dir = r'C:\Users\YourUsername\Desktop\MultiLeaves\svg mask - INPUT'
output_dir = r'C:\Users\YourUsername\Desktop\MultiLeaves\svg labels - OUTPUT'
```
On macOS/Linux, use a forward-slash path instead, e.g. `/Users/YourUsername/Desktop/MultiLeaves/svg mask - INPUT`.

The same applies to `data_dir` and `outputs_dir` inside `MULTItest_leaf_data.py`.

## Usage

1. Place your traced SVG files in the input folder.
2. Run:
   ```
   python MULTIsvg2point.py
   ```
3. Check the resulting `.txt` files in the output folder.
4. (Optional, recommended) Run the quality-control overlay to visually confirm the conversion is correct:
   ```
   python MULTItest_leaf_data.py
   ```
   This draws the blade (orange) and vein (magenta) coordinates on top of the original scan image so any misalignment can be caught before the data is used for model training.

## File naming convention

- `*_blade.txt` — blade (lamina) outline points.
- `*_vein.txt` or `*_veins.txt` — vein outline points.
- Within a combined output file, each leaf's block starts with its label (`blade`, `vein1`, `vein2`, `leaf1`, etc.) followed by its sampled `x y` coordinate pairs, with a blank line separating leaves.

## Using the legacy version

`legacy/svg-to-XY.py` is kept unchanged for reference. It expects exactly one leaf path per SVG file and writes one `.txt` file per SVG. See the comments at the top of that script for its own input/output path variables. New tracing work should use `MULTIsvg2point.py` instead.

## Troubleshooting

- **Module not found**: verify the required package is installed (`pip show svgpathtools`, `pip show opencv-python`).
- **Wrong or missing labels**: check that text labels in the SVG are close to their intended path; labels are assigned to the nearest path center.
- **Unexpected image size / A4 fallback warning**: the SVG's `viewBox`/`width`/`height` attributes could not be read; check the SVG export settings from Illustrator/Inkscape.

## License

This project is licensed under the MIT License — see the `LICENSE` file for details.

## Feedback

Please test and share feedback with the project team. Issues and suggested improvements are welcome via GitHub issues or pull requests.
