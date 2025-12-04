from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image
import imagehash
import os
import json

BASE_DIR = os.path.dirname(__file__)
DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
HASH_FILE = os.path.join(BASE_DIR, 'hashes.json')

MATCH_DISTANCE = 0  # 0 = exact pHash match; increase (e.g. 5-10) for more tolerant matching

app = Flask(__name__)

def load_hashes():
    if not os.path.exists(HASH_FILE):
        return {}
    with open(HASH_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

hashes = load_hashes()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'message': 'no file provided'}), 400
    file = request.files['file']
    try:
        img = Image.open(file.stream)
    except Exception:
        return jsonify({'message': 'invalid image'}), 400

    ph = imagehash.phash(img)

    # compute Hamming distance to every dataset image
    distances = []
    for fn, hexhash in hashes.items():
        try:
            other = imagehash.hex_to_hash(hexhash)
            dist = int(ph - other)
            distances.append((fn, dist))
        except Exception:
            continue

    # sort by distance (lower is better) and return top-5 for inspection
    distances.sort(key=lambda x: x[1])
    topk = distances[:5]

    # select those within threshold as matches
    matches = [{'filename': fn, 'distance': d} for fn, d in topk if d <= MATCH_DISTANCE]

    if not matches:
        nearest = topk[0] if topk else None
        resp = {'message': 'image is not relevant', 'matches': []}
        if nearest:
            resp['nearest'] = {'filename': nearest[0], 'distance': int(nearest[1])}
        return jsonify(resp)

    # image matches: include diagnostic message
    diagnostic = "No signs of vagal disease. Sagittal ultrasound (15 MHz) clearly shows internal structure made of some hypoechoic parallel fascicles separated by hyperechoic envelope (arrowheads)."
    return jsonify({'matches': matches, 'diagnostic': diagnostic})

@app.route('/dataset/<path:filename>')
def dataset_file(filename):
    return send_from_directory(DATASET_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
