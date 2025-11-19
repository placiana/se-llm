from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMacroNode, LatexCharsNode, LatexGroupNode





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
        for node in nodes:
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
                #if node.chars == 'j' or node.chars == 'Ag':
                #    continue
                if all([x not in node.chars for x in["\n", "node"] ]):
                    #print(f"{indent} {prefix}Texto: {node.chars!r}")
                    #if indent in [4, 5,6]:
                    #    print(indent, prefix, node.chars)
                    if indent >= 4:
                        #print(indent, "dddddd ategoría:", node.chars)
                        output.append( node.chars)
                        
                    else:
                        print(indent, "Texto ignorado:", node.chars)
                #print(indent, node.chars)
            elif isinstance(node, LatexGroupNode):
                #print(indent, "GroupNode:")
                #for n in node.nodelist:
                #    print(indent, " Group child node:", n)
                res = self.walk_nodes(node.nodelist, indent+1)
                #print(indent, 'Grupo res:', res)
                res = self.parse_phantom(res)
                output += res
                if res and indent in [3]:
                    #print("Indent 3 res:", res )
                    if len(res) == 1: #if ':' not in res[0]: #
                        #print("Categoría encontrada:", res)
                        category = res[0].split(':')[0].strip()
                        self.categories[category] = {}
                        
                    if len(res) > 1: #else: #
                        
                        subcat = res[0].split(':')[0].strip()
                        #print("Subcategorías encontradas:", res, subcat)
                        #category = res[0].split(':')[0].strip()
                        #print('Posta:', res[1:])
                        if subcat in self.categories[category]:
                            print('A')
                            self.categories[category][subcat].extend(res[1:])
                        else:
                            #print('B')
                            self.categories[category][subcat] = self.parse_nodelist(res[1:])

                        output.append(self.categories[category][subcat])

                    #print(indent, prefix, res)

            else:
                print(f"{prefix}{node!r}")
        
        return output
        #return categories

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
            print("Parsing section:", sec)
            #result.extend(self.parse_nodelist(sec))
            if ':' in sec[0]:
                print('Se pico:', sec)
                result.append({
                    sec[0].split(':')[0].strip(): self.parse_nodelist(sec[1:])
                })
            

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
            print("Parsed categories:", categories)
            result.extend(categories)

            
        return result



    def parse_phantom(self, nodelist):
        """Elimina nodos phantom (y el siguiente nodo) de una lista de nodos."""
        output = []
        skip_next = False
        for i, item in enumerate(nodelist):
            if skip_next:
                skip_next = False
                continue
            if item == '\\phantom':
                skip_next = True
                continue
            output.append(item)
        return output
        

# Recorremos el árbol


# main
if __name__ == "__main__":
    # walk over .tex files in sources/ recursively and extract categories
    import glob

    result = {}

    walker = CategoriesWalker()
    for tex_file in glob.glob("sources/test/**/*.tex", recursive=True):
        print("Processing file:", tex_file)
        walker.walk(tex_file)
        categories = walker.get_categories()
        print(f"Categories in {tex_file}:")

        # extact last directory name as topic
        import os
        topic = os.path.basename(os.path.dirname(tex_file))

        #extract filename without extension
        filename = os.path.splitext(os.path.basename(tex_file))[0]

        result_key = f"{topic}/{filename}"
        result[result_key] = categories

    # Save result to JSON
    import json
    import pprint
    with open('docs/data/categories_from_tex.json', 'w') as file:
        json.dump(result, file, indent=2)



    # Print the final result
    print("Final result:")
    pprint.pp(result)
