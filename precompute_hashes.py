from PIL import Image
import imagehash
import os
import json
import zipfile
import shutil

BASE_DIR = os.path.dirname(__file__)
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
OUT_FILE = os.path.join(BASE_DIR, 'hashes.json')
ZIP_NAMES = ['vagusnervedataset.zip']

def is_image_file(name):
    name = name.lower()
    return name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff'))

def ensure_dataset_extracted():
    """If a known zip is present (in project root or inside `dataset/`), extract it into `DATASET_DIR`.
    Returns True if dataset dir exists and contains at least one image file after extraction.
    """
    # Create dataset dir if missing
    if not os.path.isdir(DATASET_DIR):
        os.makedirs(DATASET_DIR, exist_ok=True)

    # look for zip files in BASE_DIR and DATASET_DIR
    candidates = []
    for name in ZIP_NAMES:
        p1 = os.path.join(BASE_DIR, name)
        p2 = os.path.join(DATASET_DIR, name)
        if os.path.isfile(p1):
            candidates.append(p1)
        if os.path.isfile(p2):
            candidates.append(p2)

    for zpath in candidates:
        try:
            print('Extracting', zpath, '->', DATASET_DIR)
            with zipfile.ZipFile(zpath, 'r') as z:
                z.extractall(DATASET_DIR)
        except Exception as e:
            print('Failed to extract', zpath, e)

    # Also check for reference images in project root (e.g. reference.jpg, dataset_image_2.jpg)
    # If present, copy them into DATASET_DIR so they become dataset images.
    for name in ('reference.jpg', 'reference.png', 'dataset_image.jpg', 'dataset_image.png', 'dataset_image_2.jpg', 'dataset_image_2.png'):
        src = os.path.join(BASE_DIR, name)
        if os.path.isfile(src):
            dst = os.path.join(DATASET_DIR, name)
            try:
                print('Copying reference image', src, '->', dst)
                shutil.copy(src, dst)
            except Exception as e:
                print('Failed to copy reference image', src, e)

    # check for any images recursively
    for root, dirs, files in os.walk(DATASET_DIR):
        for f in files:
            if is_image_file(f):
                return True
    return False

def main():
    ok = ensure_dataset_extracted()
    if not ok:
        print('No images found in', DATASET_DIR)
        print('Place images directly in the `dataset/` folder or provide', ZIP_NAMES[0])
        return

    hashes = {}
    # walk recursively so we pick images in subfolders too
    for root, dirs, files in os.walk(DATASET_DIR):
        for fn in sorted(files):
            if not is_image_file(fn):
                continue
            path = os.path.join(root, fn)
            # store filename relative to DATASET_DIR so app can serve it
            rel = os.path.relpath(path, DATASET_DIR).replace('\\', '/')
            try:
                with Image.open(path) as img:
                    h = imagehash.phash(img)
                    hashes[rel] = str(h)
                    print('Hashed', rel, '->', str(h))
            except Exception as e:
                print('Failed to hash', rel, e)

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(hashes, f, indent=2)

    print('Saved', OUT_FILE)

if __name__ == '__main__':
    main()
