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



def get_tasks_from_csv(csv_filename):
    df = pd.read_csv(csv_filename)
    df['Name'] = df['Task Name'].str.split('{').str[1].str.removesuffix('}')
    df['Nick'] = df['Task Id'].str.split('_').str[0]
    # Remove columns
    df = df.drop(['Unnamed: 0', 'Unnamed: 5', 'Multi-class? def: Binary', 'Openness of labels set','Multi-label? def: Single-label', 'Soft (probability)? def: Hard', 'Granularity', 'Explained?', 'Type of question wrt Vuls'], axis=1)

    # Boolean columns
    bool_cols = ['Few-Shot', 'ReAct',  'CoT', 'ToT', 'RAG', 'Infiller', 'FeedbackLoop', 'Self-Validation', 'Mult/Openness VulSet']
    for col in bool_cols:
        df[col] = df[col].notna()
    
    return df.to_dict(orient='records')


def get_problems_from_tasks(task_data):

    problems = {}
    for record in task_data:
        if record['SE-Area'] not in problems:
            problems[record['SE-Area']] = {}

        if record['SE-Prob'] not in problems[record['SE-Area']]:
            problems[record['SE-Area']][record['SE-Prob']] = []

        if record['Nick'] not in problems[record['SE-Area']][record['SE-Prob']]:
            problems[record['SE-Area']][record['SE-Prob']].append(record['Nick'])

    return problems

def get_problems_task_from_tasks(task_data):

    problems = {}
    for record in task_data:
        if record['SE-Area'] not in problems:
            problems[record['SE-Area']] = {}

        if record['SE-Prob'] not in problems[record['SE-Area']]:
            problems[record['SE-Area']][record['SE-Prob']] = []

        problems[record['SE-Area']][record['SE-Prob']].append(record['Task Id'])

    return problems


# SOURCES TO DATA
 
# tasks.json
def write_data_files():
    data = get_tasks_from_csv('sources/Tabla de papers para contar con Tasks.csv')
    with open('docs/data/tasks.json', 'w') as file:
        json.dump(data, file, indent=2)

# bib.json
def bibtext_to_json():
    import bibtexparser

    with open("sources/llms.bib") as bibfile:
        bib_database = bibtexparser.load(bibfile)
    data = bib_database.get_entry_list()
    with open('docs/data/bib.json', 'w') as file:
        json.dump(data, file, indent=2)


# problems.json
def write_problems_json():
    with open('docs/data/tasks.json') as file:
        task_data = json.load(file)
    problems = get_problems_from_tasks(task_data)

    with open('docs/data/problems.json', 'w') as file:
        json.dump(problems, file, indent=2)
    
def write_transformations_json():
    with open('docs/data/tasks.json') as file:
        task_data = json.load(file)
    problems = get_problems_task_from_tasks(task_data)

    with open('docs/data/transformations.json', 'w') as file:
        json.dump(problems, file, indent=2)
    


if __name__ == '__main__':
    app.run(debug=True)
