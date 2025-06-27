from rich.console import Console
from rich.text import Text
import typer
import json
import os
from pathlib import Path
import pickle


GRAPH = Path("graphs.json")
app = typer.Typer()
console = Console(record=True)

class Node:
    def __init__(self, id, label="",  shape="", type=""):
        self.id = id
        self.label = label
        self.type = type
        self.shape = shape
        self.height = 3
        self.width = 5 + len(label)
        self.x = 0                  
        self.y = 0 


class Edge:
    def __init__(self, source, target, label=""):
        self.source = source
        self.target = target
        self.label = label


class Graph:
    def __init__(self, name=""):
        self.nodes = {}
        self.edges = []
        self.name = name

    def addn(self, id, label,  shape, type):
        if id in self.nodes:
            return
        self.nodes[id] = Node(id, label,  shape,type)
    
    def adde(self, source, target, label=""):
        if source not in self.nodes:
            return
        if target not in self.nodes:
            return
        self.edges.append(Edge(source, target, label))

    def connect(self, source, target):
        if source not in self.nodes or target not in self.nodes:
            return
        self.edges.append(Edge(source, target))


def render(graph):
    if not graph.nodes:
        return

    console.print(f"\n----------{graph.name}----------")

    def draw_n(node):
        l = len(node.label)
        p = node.width - l - 2  
        lp = p // 2
        rp = p - lp
        final = " " * lp + node.label + " " * rp

        if node.shape == "circle":
            return [
                " .---. ",
                f" ( {final})",
                "  '---'"
            ]
        elif node.shape == "square":
            return [
                "+" + "-" * (node.width - 2) + "+",
                "|" + final + "|",
                "+" + "-" * (node.width - 2) + "+"
            ]
        elif node.shape == "diamond":
            return [
                f"/{'-' * (node.width - 6)}\\",
                f"< {node.label} >",
                f" \\{'-' * (node.width - 6)}/"
            ]
        else:
            return [
                "+" + "-" * (node.width - 2) + "+",
                "|" + final + "|",
                "+" + "-" * (node.width - 2) + "+"
            ]

    all = {edge.target for edge in graph.edges}
    rnode = [node_id for node_id in graph.nodes if node_id not in all]

    if not rnode:
        rnode = list(graph.nodes.keys())
    
    def r_dfs(node_id, prefix="", is_last=True):
        node = graph.nodes[node_id]
        nodeascii = draw_n(node)
        connector = "└──▶" if is_last else "├──▶"
        el = f"{prefix}{connector} "
        np = prefix + ("    " if is_last else "│   ")

        for i, line in enumerate(nodeascii):
            if i == 0:
                console.print(el + line, style="bold green")
            else:
                console.print(np + line, style="bold green")

        outedge = [e for e in graph.edges if e.source == node_id]

        for idx, edge in enumerate(outedge):
            child = edge.target
            lastc = idx == len(outedge) - 1
            label = f"{edge.label} " if edge.label else ""
            edgel = f"{np}{'└──▶' if lastc else '├──▶'} {label}".rstrip()
            console.print(edgel, style="bold cyan")
            r_dfs(child, np, lastc)


    for root_id in rnode:
        r_dfs(root_id)
        if len(rnode) > 1:
            console.print("\n" + "=" * 40 + "\n") 

GRAPH_DIR = Path("graphs")

def savepickle(graphname: str, graph_obj: Graph):
    GRAPH_DIR.mkdir(exist_ok=True)
    path = GRAPH_DIR / f"{graphname}.pkl"
    with open(path, "wb") as f:
        pickle.dump(graph_obj, f)
    console.print(f"[green]Graph object saved as: {path}[/green]")

def loadpickle(graphname: str) -> Graph:
    path = GRAPH_DIR / f"{graphname}.pkl"
    if not path.exists():
        console.print(f"[red]Pickled graph '{graphname}' not found.[/red]")
        return None
    with open(path, "rb") as f:
        graph = pickle.load(f)
    return graph


def load():
    if not GRAPH.exists() or GRAPH.stat().st_size == 0:
        with open(GRAPH, "w") as f:
            json.dump([], f, indent=2)
    with open(GRAPH, "r") as f:
        return json.load(f)

def save(name):
    if not GRAPH.exists() or GRAPH.stat().st_size == 0:
        with open(GRAPH, "w") as f:
            json.dump([], f, indent=2)
    with open(GRAPH, "w") as f:
        existing = load()
        existing.append(name)
        json.dump(existing, f, indent=2)

@app.command()
def create(name: str):
    if name in load():
        console.print(f"[red]Graph '{name}' already exists.[/red]")
        return

    g = Graph(name)
    console.print(f"[green]Creating graph '{name}'[/green]")

    try:
        num_nodes = int(typer.prompt("How many nodes do you want to add?"))
        for i in range(num_nodes):
            console.print(f"\n[bold cyan]Node {i + 1}:[/bold cyan]")
            label = typer.prompt("  Label (e.g. Start, User Input)")
            shape = typer.prompt("  Shape (process, square, circle, diamond)", default="process")
            ntype = typer.prompt("  Type (e.g. action, decision)", default="")
            g.addn(str(i), label.strip(), shape.strip(), ntype.strip())
            console.print(f"   Node '{i}': '{label}' added.")

    except Exception as e:
        console.print(f"[red] {e}[/red]")
        return

    try:
        e = int(typer.prompt("How many edges do you want to add?"))
        for i in range(e):
            console.print(f"\n[bold yellow]Edge {i + 1}:[/bold yellow]")
            src = typer.prompt("  Source Node ID")
            tgt = typer.prompt("  Target Node ID")
            elabel = typer.prompt("  Edge Label (can be empty)", default="")
            g.adde(src.strip(), tgt.strip(), elabel.strip())
            console.print(f"  🔗 Edge {src} -> {tgt} added.")
    except Exception as e:
        console.print(f"[red]Error while adding edges: {e}[/red]")
        return
    save(name)

    savepickle(name, g)

    console.print(f"\n[bold green]Graph '{name}' created successfully![/bold green]")
    render(g)

@app.command()
def show(name: str):
    g = loadpickle(name)
    if g is None:
        return
    render(g)



    
@app.command()
def export(graphname: str):
    if graphname not in load():
        console.print(f"[red]Graph '{graphname}' not found[/red]")
        return

    g = loadpickle(graphname)
    if g is None:
        return

    GRAPH_DIR.mkdir(exist_ok=True)
    export_path = GRAPH_DIR / f"{graphname}.txt"

    render(g) 
    console.save_text(str(export_path), clear=True, styles=False)

    console.print(f"[green]Exported clean flowchart to: {export_path}[/green]")


if __name__ == "__main__":
    app()


# example
# g = Graph()

# g.addn("A", "Start", "process", "circle")
# g.addn("B", "User Input", "action", "square")
# g.addn("C", "Process Data", "process", "cloud")
# g.addn("D", "Decision Point", "decision", "diamond")
# g.addn("E", "Output Result", "action", "square")
# g.addn("F", "End", "process", "circle")
# g.addn("G", "Error", "process", "cloud")

# g.adde("A", "B", "Starting")
# g.adde("B", "C", "Data Received")
# g.adde("C", "D", "Data Processed")
# g.adde("D", "E", "Yes")
# g.adde("D", "G", "No")
# g.adde("D", "G", "maybe")
# g.adde("D", "F", "maybe2")
# g.adde("D", "G", "maybe3")
# # g.adde("E", "F")
# g.adde("G", "F", "Handle Error")

# render(g)

# g3 = Graph()
# render(g3)

