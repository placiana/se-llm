import os
import json
from flask import render_template
from flask import Flask
import pandas as pd

from parsing import bib_to_obj

app = Flask(__name__, template_folder='templates', static_folder='static')

# Path to a sample data file (optional)
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data.json')
bib_file = 'sources/llms.bib'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data')
def data():
    # Serve JSON data for the tree.
    # You can either load from a file or return a Python dict.
    if os.path.exists(bib_file):
        payload = bib_to_obj(bib_file)
        payload = {"name": "References", "children": payload[:30]}
    else:
        # fallback sample tree
        payload = {
            "name": "Root",
            "children": [
                {"name": "Branch A", "children": [{"name": "Leaf A1"}, {"name": "Leaf A2"}]},
                {"name": "Branch B", "children": [{"name": "Leaf B1"}]}
            ]
        }
    # ECharts `tree` series expects an *array* of root nodes
    return json.dumps([payload])


@app.route('/data/categories')
def data_categories():
    df = pd.read_csv('sources/Tabla de papers para contar con Tasks.csv')
    category_column = 'LLM-Task Category'
    task_column = 'Task Id'

    # return a nested object with categories as top-level nodes then tasks as children
    categories = []
    for category, group in df.groupby(category_column):
        tasks = [{"name": task_id} for task_id in group[task_column].unique()]
        categories.append({"name": category, "children": tasks})
    return json.dumps(categories)


if __name__ == '__main__':
    app.run(debug=True)
