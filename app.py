from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os

from AppCode.main import gridExtraction, stepSolver, initialize

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the PDF and extract the grid
        grid = gridExtraction(file_path)
        print(grid)


        return jsonify({'grid': grid})


@app.route('/solve', methods=['POST'])
def solve():
    # This would need the grid to be sent in the request, for simplicity, just returning a dummy grid here
    initialize()
    solved_grid = stepSolver()
    solved_grid_list = solved_grid.tolist()
    print(solved_grid_list)
    return jsonify({'grid': solved_grid_list})

if __name__ == '__name__':
    app.run(debug=True)