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

    console.print(f"\n [bold underline bright_white on black] ----------{graph.name}---------- [/bold underline bright_white on black]")

    def draw_n(node):
        l = len(node.label)
        p = node.width - l - 2  
        lp = p // 2
        rp = p - lp
        final = " " * lp + node.label + " " * rp

        if node.shape == "circle":
            return [
                " .---------. ",
                f" (   {final} ) ",
                "  '---------'"
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
            label = f"[bold bright_cyan] {edge.label} [/bold bright_cyan] " if edge.label else ""
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
    console.print(f"[bold green]Creating graph '{name}'[/bold green]")

    try:
        i = 0
        while True:
            console.print(f"\n[bold cyan]Node {i + 1}:[/bold cyan] (type 'exit' to stop)")
            label = typer.prompt("  Label (e.g. Start, User Input)")
            if label.strip().lower() in ["exit", "quit"]:
                break
            shape = typer.prompt("  Shape (process, square, circle, diamond)", default="process")
            ntype = typer.prompt("  Type (e.g. action, decision)", default="")
            g.addn(str(i), label.strip(), shape.strip(), ntype.strip())
            console.print(f"   Node '{i}': '{label}' added.")
            i += 1


    except Exception as e:
        console.print(f"[red] {e}[/red]")
        return

    try:
        i = 0
        while True:
            console.print(f"\n[bold yellow]Edge {i + 1}:[/bold yellow] (type 'exit' to stop)")
            src = typer.prompt(" Source Node ID")
            if src.strip().lower() in ["exit", "done"]:
                break
            tgt = typer.prompt(" Target Node ID")
            elabel = typer.prompt(" Edge Label ", default="")
            g.adde(src.strip(), tgt.strip(), elabel.strip())
            console.print(f"  🔗 Edge {src} -> {tgt} added.")
            i += 1

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
def edit(name: str):
    g = loadpickle(name)
    if g is None:
        return
    console.print(f"[cyan]Editing graph '{name}'[/cyan]")
    while True:
        choice = typer.prompt("What do you want to edit? [node/edge/add node/add edge/delete/show/exit]").strip().lower()

        if choice == "exit":
            break

        elif choice == "node":
            nid = typer.prompt("Node id to edit")
            if nid in g.nodes:
                node = g.nodes[nid]
                label = typer.prompt(f"New Label (current: {node.label})", default=node.label)
                shape = typer.prompt(f"New Shape (current: {node.shape})", default=node.shape)
                ntype = typer.prompt(f"New Type (current: {node.type})", default=node.type)
                node.label = label
                node.shape = shape
                node.type = ntype
                console.print("[green]Node updated[/green]")
            else:
                console.print("[red]Node not found [/red]")
        elif choice == "add node":
            nid = typer.prompt("New Node ID")
            if nid in g.nodes:
                console.print("[red]Node already exists[/red]")
                continue
            label = typer.prompt("  Label (Start, User Input)")
            shape = typer.prompt("  Shape (process, square, circle, diamond)", default="process")
            ntype = typer.prompt("  Type (action, decision)", default="")
            g.addn(nid, label.strip(), shape.strip(), ntype.strip())
            console.print(f"[green]Node '{nid}' added[/green]")

        elif choice == "add edge":
            src = typer.prompt("  Source Node ID")
            tgt = typer.prompt("  Target Node ID")
            elabel = typer.prompt("  Edge Label (can be empty)", default="")
            g.adde(src.strip(), tgt.strip(), elabel.strip())
            console.print(f"[green]Edge '{src}' → '{tgt}' added[/green]")

        elif choice == "edge":
            src = typer.prompt("Source node ID")
            tgt = typer.prompt("Target node ID")
            found = False
            for edge in g.edges:
                if edge.source == src and edge.target == tgt:
                    new_label = typer.prompt(f"New label (current: {edge.label})", default=edge.label)
                    edge.label = new_label
                    found = True
                    console.print("[green]Edge label updated[/green]")
                    break
            if not found:
                console.print("[red]Edge not found[/red]")

        elif choice == "delete":
            to_delete = typer.prompt("Delete [node/edge]?")
            if to_delete == "node":
                nid = typer.prompt("Node ID to delete")
                if nid in g.nodes:
                    del g.nodes[nid]
                    g.edges = [e for e in g.edges if e.source != nid and e.target != nid]
                    console.print(f"[green]Node {nid} and its edges deleted[/green]")
                else:
                    console.print("[red]Node not found[/red]")
            elif to_delete == "edge":
                src = typer.prompt("Source node")
                tgt = typer.prompt("Target node")
                before = len(g.edges)
                g.edges = [e for e in g.edges if not (e.source == src and e.target == tgt)]
                after = len(g.edges)
                if before == after:
                    console.print("[red]Edge not found.[/red]")
                else:
                    console.print("[green]Edge deleted.[/green]")

        elif choice == "show":
            render(g)

    savepickle(name, g)
    console.print(f"[green]Graph '{name}' updated.[/green]")



    
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

