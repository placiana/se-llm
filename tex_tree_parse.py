from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMacroNode, LatexCharsNode, LatexGroupNode
import json




class CategoriesWalker():
    """Clase para recorrer nodos y extraer categorías."""

    def __init__(self):
        self.categories = {}

    def get_categories(self):
        return self.categories

    def walk(self, filename):
        # Abrimos el archivo .tex
        with open(filename, "r", encoding="utf-8") as f:
            latex_code = f.read()

        # Creamos el "walker" que genera el árbol de nodos
        walker = LatexWalker(latex_code)
        nodelist, pos, len_ = walker.get_latex_nodes()

        self.categories = {}
        self.walk_nodes(nodelist)

    def walk_nodes(self, nodes, indent=0):
        """Recorrer nodos recursivamente y mostrarlos con sangría."""

        output = []
        subcat = ''
        self.current_cats = []
        for node in nodes:
            #print(indent, "Node type:", type(node), node)
            prefix = "  " * indent
            if isinstance(node, LatexMacroNode):
                #continue
                #print(f"{prefix}Macro: \\{node.macroname} -> {node.nodeargd}")
                #print(node.macroname)

                #print("node", node)
                # Si la macro tiene argumentos, recorremos
                res = []
                if node.nodeargd is not None:
                    for arg in node.nodeargd.argnlist:
                        if arg is not None:
                            res =  self.walk_nodes(arg.nodelist, indent+1)
                            #print(node.macroname, "res:", res)
                            output += res
                if node.macroname not in []:#['phantom']:
                    output.append(f'\\{node.macroname}')
                #print(indent, "Macro result:", node.macroname, res)

            elif isinstance(node, LatexEnvironmentNode):
                #print(f"{prefix}Entorno: {node.envname}")
                self.walk_nodes(node.nodelist, indent+1)

            elif isinstance(node, LatexCharsNode):
                #print(indent, "Chars node:", node.chars)
                if node.chars == 'j': #or node.chars == 'Ag':
                    continue
                if all([x not in node.chars for x in["\n", "node"] ]):
                    #print(f"{indent} {prefix}Texto: {node.chars!r}")
                    #if indent in [4, 5,6]:
                    #    print(indent, prefix, node.chars)
                    if indent >= 4:
                        #print(indent, "dddddd ategoría:", node.chars)
                        output.append(node.chars)
                        
                    else:
                        print(indent, "Texto ignorado:", node.chars)
                else:
                    #print(indent, "Texto con salto o node ignorado:", node.chars)
                    pass
                #print(indent, node.chars)
            elif isinstance(node, LatexGroupNode):
                #print(indent, "GroupNode:", node.nodelist)
                #for n in node.nodelist:
                #    print(indent, " Group child node:", n)
                res = self.walk_nodes(node.nodelist, indent+1)
                print(indent, 'Grupo res:', res)
                res = self.parse_phantom(res)
               
                output += res
                if res and indent in [3]:
                    #print(indent, 'Grupo post-phantom res:', res)
                    #print("Indent 3 res:", res )
                    if len(res) == 1: #if ':' not in res[0]: #
                        print("Categoría encontrada:", res)
                        category = res[0].split(':')[0].strip()
                        self.categories[category] = {}
                        self.subcat = ''
                        
                    if len(res) > 1: #else: #
                        print('Handle:', self.handle_nodegroup(res))
                        if ':' in res[0]:
                            self.subcat = res[0].split(':')[0].strip()
                            
                            #category = res[0].split(':')[0].strip()
                            #print('Posta:', res[1:])
                            if self.subcat in self.categories[category]:
                                parsed = self.parse_nodelist(res[1:])
                                print('A', category, subcat, parsed)
                                self.categories[category][self.subcat].extend(parsed)
                            else:
                                parsed = self.parse_nodelist(res[1:])
                                self.categories[category][self.subcat] = parsed
                                print('B', category, self.subcat, parsed)
                        else:
                            parsed = self.parse_nodelist(res)
                            
                            if len(parsed) > 1 and len(parsed[0]) == 1:
                                self.subcat = parsed[0][0]
                                parsed = parsed[1:]
                                self.categories[category][self.subcat] = []
                                print('D', category, self.subcat, parsed)
                            print('C', category, self.subcat, parsed)
                            if self.subcat:
                                self.categories[category][self.subcat].extend( parsed )
                            else:
                                print('E', category, self.subcat, parsed)
                                self.categories[category]['undefined'] = parsed

                        #output.append(self.categories[category][self.subcat])

                    #print(indent, prefix, res)

            else:
                print(f"{prefix}{node!r}")
        
        return output
        #return categories

    def handle_nodegroup(self, res):
        print('handle:', res)
        if ':' in res[0]:
            # define una nueva subcategoría
            subcat = res[0].split(':')[0].strip()
            self.current_cats.append(subcat)
            
            #category = res[0].split(':')[0].strip()
            #print('Posta:', res[1:])
            if subcat :
                parsed = self.parse_nodelist(res[1:])
                return {subcat: parsed}
            else:
                parsed = self.parse_nodelist(res[1:])
                return [parsed]
        else:
            parsed = self.parse_nodelist(res)
            
            if len(parsed) > 1 and len(parsed[0]) == 1:
                subcat = parsed[0][0]
                parsed = parsed[1:]
                return {subcat: parsed}
            return [parsed]
        return None

        output.append(self.categories[category][self.subcat])
    def parse_nodelist(self, nodelist):
        #print("Parsing nodelist:", nodelist)
        """Parsea una lista de nodos para extraer categorías."""

        sections = []
        section = []
        for item in nodelist:
            if ':' in item:
                sections.append(section)
                section = [item]
            else:
                section.append(item)
        if section:
            sections.append(section)

        #print("Sections:", sections)
        result = []
        for sec in sections:
            if sec:
                #print("Parsing section:", sec)
                #result.extend(self.parse_nodelist(sec))
                if ':' in sec[0]:
                    #print('Se pico:', sec)
                    result.append({
                        sec[0].split(':')[0].strip(): self.parse_nodelist(sec[1:])
                    })
                else:

                    # Split list in many lists if there are commas
                    categories = []
                    current_cat = []
                    for item in sec:
                        if item == ', ':
                            if current_cat:
                                categories.append(current_cat)
                                current_cat = []
                        else:
                            current_cat.append(item)
                    if current_cat:
                        categories.append(current_cat)
                    #print("Parsed categories:", categories)
                    result.extend(categories)

            
        return result



    def parse_phantom(self, nodelist):
        """Elimina nodos phantom (y el siguiente nodo) de una lista de nodos."""
        output = []
        skip_next = False
        for i, item in enumerate(nodelist):
            if skip_next:
                skip_next = False
                #print("Not Adding item:", item)
                continue
            if item == '\\phantom':
                skip_next = True
                continue
            if item == ' ':
                continue
            output.append(item)
        return output
        

# Recorremos el árbol


# main
class PatternWaker():
    current_pattern = ''
    patterns = {}
    description_section = False
    tools_section = False

    def walk_nodes(self, nodes, indent=0):
        """Recorrer nodos recursivamente y mostrarlos con sangría."""
        output = []
        
        if indent == 2:
            print(indent, "Nodes:", nodes)
        for node in nodes:
            
            if isinstance(node, LatexMacroNode):
                print(indent, 'macro:', node.macroname)
                if node.macroname == 'SetCell':
                    self.tools_section = False


                # Si la macro tiene argumentos, recorremos
                res = []

                if node.nodeargd is not None:
                    for arg in node.nodeargd.argnlist:
                        if arg is not None:
                            if hasattr(arg, 'nodelist'):
                                res = self.walk_nodes(arg.nodelist, indent+1)
                            #print(indent, node.macroname, res)
                            output += res
                if node.macroname not in []:#['phantom']:
                    output.append(f'\\{node.macroname}')

                if node.macroname == 'texttt':
                    print("================================================", res)
                    
                    self.current_pattern = ''.join(res)
                    self.patterns[self.current_pattern] = {}

                if node.macroname == 'textbf' and res[0].startswith('Description'):
                    #print("Description found:", res)
                    self.description_section = True
                if node.macroname == 'textbf' and res[0].startswith('Tools'):
                    self.tools_section = True


            elif isinstance(node, LatexEnvironmentNode):
                self.walk_nodes(node.nodelist, indent+1)

            elif isinstance(node, LatexCharsNode):
                print(indent, "Chars node:", node.chars)
                if node.chars in ['\\\\']:
                    continue

                if indent == 3 and self.description_section and self.current_pattern:
                    self.patterns[self.current_pattern]['description'] = node.chars
                    print("Pattern description:", node.chars)
                    self.description_section = False

                if indent >= 4:
                    output.append(node.chars)
                elif indent == 3:
                    output.append(node.chars)

            elif isinstance(node, LatexGroupNode):
                res = self.walk_nodes(node.nodelist, indent+1)
                if indent == 4:
                    # tools?
                    if self.current_pattern and self.tools_section:
                        if 'tools' in self.patterns[self.current_pattern]:
                            self.patterns[self.current_pattern]['tools'].append(res[0])
                        else:
                            self.patterns[self.current_pattern]['tools'] = [res[0]]

                        tools = res
                        print('Tools', tools)
                print(indent, 'GroupNode', res)
                
                output += res

        print(indent, 'Output', output)
        return output
        #return categories

if __name__ == "__main__":
    filename = 'sources/table-patterns (1).tex'
    with open(filename, "r", encoding="utf-8") as f:
        latex_code = f.read()

    # Creamos el "walker" que genera el árbol de nodos
    walker = LatexWalker(latex_code)
    nodelist, pos, len_ = walker.get_latex_nodes()
    nodelist, pos, len_ = walker.get_latex_nodes()

    pw = PatternWaker() 
    pw.walk_nodes(nodelist)
    import pprint
    pprint.pprint(pw.patterns)
    with open('docs/data/patterns.json', 'w') as file:
        json.dump(pw.patterns, file, indent=2)

if __name__ == "__main__vak":
    # walk over .tex files in sources/ recursively and extract categories
    import glob

    result = {}

    walker = CategoriesWalker()
    for tex_file in glob.glob("sources/tex/**/*.tex", recursive=True):
        print("Processing file:", tex_file)
        walker.walk(tex_file)
        categories = walker.get_categories()
        print(f"Categories in {tex_file}:")

        # extact last directory name as topic
        import os
        topic = os.path.basename(os.path.dirname(tex_file))
        print(topic)
        if '-' in topic:
            # keep string after first '-'
            topic = topic.split('-', 1)[1]

        #extract filename without extension
        filename = os.path.splitext(os.path.basename(tex_file))[0]

        result_key = f"{topic}/{filename}"
        result[result_key] = categories

    # Save result to JSON
    import json
    import pprint
    with open('docs/data/categories_from_tex.json-draft', 'w') as file:
        json.dump(result, file, indent=2)



    # Print the final result
    print("Final result:")
    #pprint.pp(result)
