# app.py
# Minimal Flask app to upload two images and compare them.

import os
from flask import Flask, request, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename
from ocr_utils import extract_scores_from_image, choose_most_likely_score
from imp import points_to_imps

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

TEMPLATE = """
<!doctype html>
<title>Bridge Score Compare</title>
<h1>Upload two bridge score sheet images</h1>
<form method=post enctype=multipart/form-data>
  <label>Image 1: <input type=file name=image1></label><br><br>
  <label>Image 2: <input type=file name=image2></label><br><br>
  <input type=submit value=Compare>
</form>
{% if result %}
  <h2>Result</h2>
  <p>Image1 chosen score: {{ result.score1 }} (candidates: {{ result.cand1 }})</p>
  <p>Image2 chosen score: {{ result.score2 }} (candidates: {{ result.cand2 }})</p>
  <p>Point difference (img1 - img2): {{ result.diff }}</p>
  <p>IMPs: {{ result.imps }}</p>
{% endif %}
"""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_and_compare():
    result = None
    if request.method == 'POST':
        if 'image1' not in request.files or 'image2' not in request.files:
            return redirect(request.url)
        f1 = request.files['image1']
        f2 = request.files['image2']
        if f1.filename == '' or f2.filename == '':
            return redirect(request.url)
        if f1 and allowed_file(f1.filename) and f2 and allowed_file(f2.filename):
            fn1 = secure_filename(f1.filename)
            fn2 = secure_filename(f2.filename)
            p1 = os.path.join(app.config['UPLOAD_FOLDER'], fn1)
            p2 = os.path.join(app.config['UPLOAD_FOLDER'], fn2)
            f1.save(p1)
            f2.save(p2)

            cand1 = extract_scores_from_image(p1)
            cand2 = extract_scores_from_image(p2)
            score1 = choose_most_likely_score(cand1)
            score2 = choose_most_likely_score(cand2)
            diff = None
            imps = None
            if score1 is not None and score2 is not None:
                diff = score1 - score2
                imps = points_to_imps(abs(diff))
            result = {
                'cand1': cand1,
                'cand2': cand2,
                'score1': score1,
                'score2': score2,
                'diff': diff,
                'imps': imps
            }
    return render_template_string(TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
