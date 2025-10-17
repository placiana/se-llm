function sort_str(string_arr) {
  return string_arr.sort((a, b) => {
    if (typeof a === 'object' || typeof b === 'object') return 0; // no ordenar objetos
    return String(a).localeCompare(String(b));
  })
}


async function renderTree(file_url = 'tree.json', container_id = 'treeview') {
  const response = await fetch(file_url);
  const treeData = await response.json();

  const container = document.getElementById(container_id);

  tasks = sort_str(Object.keys(treeData));

  function createTree(data) {
    if (data === null || data === undefined) {
      return '';
    }

    // caso primitivo (string, número, booleano)
    if (typeof data !== 'object') {
      return `<li data-tooltip="nick-${data}" class="tooltipable">${data}</li>`;
    }

    let html = '<ul class="tree">';

    if (Array.isArray(data)) {
      // ordenar array (si los elementos son primitivos)
      const sortedArray = [...data].sort((a, b) => {
        if (typeof a === 'object' || typeof b === 'object') return 0; // no ordenar objetos
        return String(a).localeCompare(String(b));
      });

      for (const item of sortedArray) {
        html += createTree(item);
      }
    } else {
      // es diccionario → ordenar claves
      const keys = Object.keys(data).sort((a, b) => a.localeCompare(b));

      for (const key of keys) {
        const value = data[key];
        if (typeof value === 'object' && value !== null) {
          html += `<li>
            <details>
              <summary>${key}</summary>
              ${createTree(value)}
            </details>
          </li>`;
        } else {
          html += `<li data-tooltip="nick-${value}">${key}: ${value}</li>`;
        }
      }
    }

    html += '</ul>';
    return html;
  }


  container.innerHTML = createTree(treeData);

  setEventHandlers();
}



async function renderTreeAlt(file_url = 'tree.json', container_id = 'treeview') {
  const response = await fetch(file_url);
  const treeData = await response.json();

  const container = document.getElementById(container_id);

  function createTree(data) {
    if (data === null || data === undefined) {
      return '';
    }

    // caso primitivo (string, número, booleano)
    if (typeof data !== 'object') {
      return `<li>${data}</li>`;
    }

    let html = '<ul class="tree">';

    if (Array.isArray(data)) {
      // ordenar array (si los elementos son primitivos)
      const sortedArray = [...data].sort((a, b) => {
        if (typeof a === 'object' || typeof b === 'object') return 0; // no ordenar objetos
        return String(a).localeCompare(String(b));
      });

      for (const item of sortedArray) {
        html += createTree(item);
      }
    } else {
      // es diccionario → ordenar claves
      const keys = Object.keys(data).sort((a, b) => a.localeCompare(b));

      for (const key of keys) {
        const value = data[key];
        if (typeof value === 'object' && value !== null) {
          html += `<li>
      <details>
        <summary>${key}</summary>
        ${createTree(value)}
      </details>
    </li>`;
        } else {
          html += `<li>${key}: ${value}</li>`;
        }
      }
    }

    html += '</ul>';
    return html;
  }


  container.innerHTML = createTree(treeData);
}

    function textDataToClassName(text) {
        return '_' + text.replace(/ /g, '-');
    }

    var category_colors = {
      "1 - Generative": "#c1e1f3",
      "2 - Evaluative": "#e6ecbc",
      "3 - Extractive": "#f3d8c1",
      "4 - Abstractive": "#efc6d7",
      "5 - Executive": "#ceb7d4",
      "6 - Consultative": "#acc0b8"
    };

    async function renderTaskTable(file_url = 'tasks.json', container_id = 'task-table') {
      const response = await fetch(file_url);
      const tableData = await response.json();
      /*
      table data looks like a list of:
      {
        "SE-Area": "5 - Program Verification",
        "SE-Prob": "29 - Program Verification",
        "Task Id": "Clover_1",
        "Task Name": "\\gen{VerifierAware-AnnotationCorresponding-Code-InFilling}",
        "Mult/Openness VulSet": false,
        "Few-Shot": false,
        "ReAct": false,
        "CoT": false,
        "ToT": false,
        "RAG": false,
        "Infiller": false,
        "FeedbackLoop": false,
        "Self-Validation": false,
        "LLM-Downstream Task Class": "01 - General-Code Generation",
        "LLM-Task Category": "1 - Generative",
        "Name": "VerifierAware-AnnotationCorresponding-Code-InFilling"
      },

      */

      // load headers
      const container = document.getElementById(container_id);
      const thead = container.querySelector('thead');
      const tbody = container.querySelector('tbody');
      var headers = Object.keys(tableData[0]);
      // remove Task Name from headers
      headers.splice(headers.indexOf("Task Name"), 1);

      // manually define headers
      headers = ["Task Id", "Name","LLM-Task Category", "LLM-Downstream Task Class", "SE-Area", "SE-Prob"];

      headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        thead.appendChild(th);
      });

      // load rows
      tableData.forEach(row => {
        const tr = document.createElement('tr');
        
        tr.id = textDataToClassName(row["Task Id"]);  // Assign an ID to the target row

        // add class to tr, prepend underscore and replace spaces with dashes
        tr.classList.add(textDataToClassName(row["SE-Prob"]));
        tr.classList.add(textDataToClassName(row["SE-Area"]));
        headers.forEach(header => {
          const td = document.createElement('td');
          if (header == "Task Name") {
            td.innerHTML = row[header].replace(/\\gen\{(.*)\}/, '<code>$1</code>');
          } else if (header == "Name") {
            td.textContent = row[header];
            //td.style.color = category_colors[row["LLM-Task Category"]] || 'black';
            td.style.backgroundColor = category_colors[row["LLM-Task Category"]] || 'white';
          } else if (typeof row[header] === "boolean") {
            td.innerHTML = row[header] ? '✅' : '❌';
            td.style.textAlign = 'center';
          } else {
            td.textContent = row[header];
          }
          
          if (header === "LLM-Task Category" && category_colors[row[header]]) {
            td.style.backgroundColor = category_colors[row[header]];
          }


          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });

      // make table sortable
      const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;
      const compare = (idx, asc) => (a, b) => {
        const v1 = getCellValue(asc ? a : b, idx);
        const v2 = getCellValue(asc ? b : a, idx);
        return v1.localeCompare(v2, undefined, { numeric: true });
      };
      thead.querySelectorAll('th').forEach((th, idx) => {
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
          const asc = !th.classList.contains('asc');
          thead.querySelectorAll('th').forEach(th => th.classList.remove('asc', 'desc'));
          th.classList.toggle('asc', asc);
          th.classList.toggle('desc', !asc);
          const rowsArray = Array.from(tbody.querySelectorAll('tr'));
          rowsArray.sort(compare(idx, asc));
          rowsArray.forEach(tr => tbody.appendChild(tr));
        });
      });

    }    
    
async function renderHTMLTaskTable(file_url = 'tasks.json', container_id = 'task-table') {
  const response = await fetch(file_url);
  const tableData = await response.json();
  /*
  table data looks like a list of:

  [
  {
    "description": "Table 1: SE task: Testing.",
    "rows": [
      {
        "SE Problem": "Unit-Test Generation",
        "LLM Downstream Tasks": [
          {
            "task": "TestGen-LLM",
            "text": "[4] : existing unit test class (UTC) + tested class id \u2192 \u27e8CoverageAugmenting-Test-Extension\u27e9 \u2192 extended UTC."
          },
          {
            "task": "FSML",
            "text": "[6] : list helper meths + meth under test \u2192 \u27e8Test-Generation\u27e9 \u2192 (test) + [Few-Shot]."
          },
          ...

  */

  tableData.forEach(table => {
    const container = document.getElementById(container_id);

    // add description
    const p = document.createElement('p');
    p.innerHTML = table.description;
    container.appendChild(p);

    // create table
    const htmlTable = document.createElement('table');
    htmlTable.classList.add('task-table');
    container.appendChild(htmlTable);

    // create header
    const thead = document.createElement('thead');
    htmlTable.appendChild(thead);
    const headerRow = document.createElement('tr');
    thead.appendChild(headerRow);
    const headers = ["SE Problem", "LLM Downstream Tasks", "Architectural Notes"];
    headers.forEach(headerText => {
      const th = document.createElement('th');
      th.textContent = headerText;
      headerRow.appendChild(th);
    });
    // create body
    const tbody = document.createElement('tbody');
    htmlTable.appendChild(tbody);

    // add rows
    table.rows.forEach(row => {
      const tr = document.createElement('tr');

      // add class to tr, prepend underscore and replace spaces with dashes
      tr.classList.add(textDataToClassName(row["SE Problem"]));
      tbody.appendChild(tr);

      // SE Problem cell
      const seProblemCell = document.createElement('td');
      seProblemCell.textContent = row["SE Problem"];
      tr.appendChild(seProblemCell);

      // LLM Downstream Tasks cell
      const llmTasksCell = document.createElement('td');
      if (Array.isArray(row["LLM Downstream Tasks"])) {
        const ul = document.createElement('ul');
        row["LLM Downstream Tasks"].forEach(task => {
          const li = document.createElement('li');
          
          task_text_colored = task.text;

          task.color.forEach(color_tag => {
            // task color is a 2 elment array [color, text]
            inner_text = color_tag[1];
            color = color_tag[0];
            // replace inner text in task.text with span with background color
            task_text_colored = task_text_colored.replace(inner_text, `<span style="background-color:${color}">${inner_text}</span>`);
          });

          task_text_colored = task_text_colored.replace(task.task, `<strong>${task.task}</strong>`);
          li.innerHTML = task_text_colored;

          ul.appendChild(li);
        });
        llmTasksCell.appendChild(ul);
      } else {
        llmTasksCell.textContent = row["LLM Downstream Tasks"];
      }
      tr.appendChild(llmTasksCell);

      // Architectural Notes cell
      const notesCell = document.createElement('td');
      if (Array.isArray(row["Architectural Notes"])) {
        const ul = document.createElement('ul');
        row["Architectural Notes"].forEach(note => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${note.task}</strong>: ${note.text}`;
            ul.appendChild(li);
          });
        notesCell.appendChild(ul);
      } else {
        notesCell.textContent = row["Architectural Notes"];
      }
      tr.appendChild(notesCell);
    });
  });
}