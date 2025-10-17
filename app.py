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
    

def parse_html():
    from bs4 import BeautifulSoup
    import re

    with open('sources/tabla4.html') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    tables = soup.find_all('table')

    data = []

    for table in tables:
        table_data = {}
        # Find the closest preceding <p> that looks like "Table X:"
        desc_p = None
        for prev in table.find_all_previous("p"):
            text = prev.get_text(strip=True)
            if re.match(r"^Table\s*\d+[:.]", text, re.IGNORECASE):
                desc_p = prev
                break

        description = desc_p.get_text(" ", strip=True) if desc_p else None

        print("----")
        print("Table description:", description)
        table_data['description'] = description
        table_data['rows'] = []

        rows = table.find_all('tr')
        #drop the header row
        rows = rows[1:]

        for row in rows:
            cols = row.find_all("td")

            # Define column names
            column_names = ["SE Problem", "LLM Downstream Tasks", "Architectural Notes"]
            result = {}
            

            for i, td in enumerate(cols):
                tasks = []
                if i == 0:
                    # First column, no special parsing
                    text = td.get_text(" ", strip=True)
                    if text:
                        tasks = text
                else:

                    ps = td.find_all("p")
                    current_task = {}
                    for p in ps:

                        # if there is a span with class sBold, start a new task
                        # else, append to the current task text
                        # in any way if there is a span with background style, add it annotated


                        sbold_spans = p.find_all("span", class_="sBold")
                        if sbold_spans:
                            if current_task:
                                tasks.append(current_task)
                            current_task = {
                                'task': sbold_spans[0].get_text(" ", strip=True),
                                'text': sbold_spans[0].get_text(" ", strip=True),
                                'color': []
                            }
                            # add the rest of the p text
                            rest_text = p.get_text(" ", strip=True).replace(sbold_spans[0].get_text(" ", strip=True), "").strip()
                            if rest_text:
                                current_task['text'] += " " + rest_text
                        else:
                            if current_task:
                                current_task['text'] += " " + p.get_text(" ", strip=True)
                            else:
                                current_task = {'text': p.get_text(" ", strip=True), 'color': []}

                        bg_spans = p.find_all("span", style=re.compile("background-color"))
                        for bg in bg_spans:
                            if current_task:
                                #current_task['text'] += bg.get_text(" ", strip=True)
                                try:
                                    current_task['color'].append((bg.get('style').split(':')[1].strip(), bg.get_text(strip=True)))

                                except:
                                    print("Error parsing style:", bg, current_task)


                    if current_task:
                        tasks.append(current_task)


                # Use column name as key
                if i < len(column_names):
                    result[column_names[i]] = tasks
                else:
                    result[f"Column_{i+1}"] = tasks
            if result:
                table_data['rows'].append(result)
        data.append(table_data)

    with open('docs/data/tasks_from_html.json', 'w') as file:
        json.dump(data, file, indent=2)


if __name__ == '__main__':
    #app.run(debug=True)
    parse_html()
