# Image Matching Prototype (Flask + pHash)

Quick prototype that accepts an uploaded image, compares it against a local `dataset/` using perceptual hashing (pHash), and shows exact matches. If no exact match is found the app shows `image is not relevant`.

Setup (PowerShell):

```powershell
cd 'c:/Users/ADMIN/Desktop/prototype'
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Prepare dataset:

1. Unzip `vagusnervedataset.zip` into `c:/Users/ADMIN/Desktop/prototype/dataset` so images are directly inside the `dataset` folder.
2. Run the precompute step to build `hashes.json`:

```powershell
python precompute_hashes.py
```

Run the app:

```powershell
python app.py
```

Open `http://127.0.0.1:5000/` in your browser, upload an image, and the app will display dataset images that match exactly (pHash distance 0). If none match you will see "image is not relevant".

Notes:
- This uses perceptual hashing and requires that the uploaded image is the same image as one in `dataset/` (or visually identical such that pHash equals). To allow relaxed matching, edit `MATCH_DISTANCE` in `app.py` (e.g., use 1-10 for more tolerant matching).
