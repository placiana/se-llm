from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMacroNode, LatexCharsNode, LatexGroupNode

# Abrimos el archivo .tex
with open("sources/AnnotationGeneration.tex", "r", encoding="utf-8") as f:
    latex_code = f.read()

# Creamos el "walker" que genera el árbol de nodos
walker = LatexWalker(latex_code)
nodelist, pos, len_ = walker.get_latex_nodes()

def walk_nodes(nodes, indent=0):
    """Recorrer nodos recursivamente y mostrarlos con sangría."""

    output = []
    for node in nodes:
        prefix = "  " * indent
        if isinstance(node, LatexMacroNode):
            #continue
            #print(f"{prefix}Macro: \\{node.macroname} -> {node.nodeargd}")
            #print(node.macroname)

                #print("caca", node)
            # Si la macro tiene argumentos, recorremos
            res = []
            if node.nodeargd is not None:
                for arg in node.nodeargd.argnlist:
                    if arg is not None:
                        res =  walk_nodes(arg.nodelist, indent+1)
                        output += res
            #print('macro',node.macroname, output)
            if node.macroname == 'phantom':
                print('fantomas', res)
            

        elif isinstance(node, LatexEnvironmentNode):
            #print(f"{prefix}Entorno: {node.envname}")
            walk_nodes(node.nodelist, indent+1)

        elif isinstance(node, LatexCharsNode):
            if node.chars == 'j':
                continue
            if all([x not in node.chars for x in["\n", "node"] ]):
                #print(f"{indent} {prefix}Texto: {node.chars!r}")
                if indent >= 4:
                    output.append( node.chars)
        elif isinstance(node, LatexGroupNode):
            #print('GroupNode:')
            res = walk_nodes(node.nodelist, indent+1)
            output += res
            if res and indent == 4:
                
                print(indent, 'group: ', res)

        else:
            print(f"{prefix}{node!r}")
    return output

# Recorremos el árbol
walk_nodes(nodelist)
