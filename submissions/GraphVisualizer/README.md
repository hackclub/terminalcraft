# CLI Graph Visualizer

A simple command-line tool to create, update, analyze, and visualize graphs using NetworkX and Matplotlib.

---

## Why this was created

Being a competitive programmer, I have often encountered problems relating to graph theory. Sometimes, the process of solving the problem requires testing of various algorithms, and this was made to aid with that. Rather than having to write the entire algorithm again, this serves as a quick solution to gauge whether the algorithm will be useful or not.

---

## Features

- Input and update directed or undirected graphs interactively  
- Visualize graphs and highlight:  
  - Minimum Spanning Tree (Kruskal’s algorithm)  
  - Cycles (directed and undirected)  
- Run common graph algorithms: Bellman-Ford, cycle detection, MST, topological sort  
- Print graph representations: adjacency list, edge list, adjacency matrix  
- Continuous interactive CLI with command support  

---

## Installation

### 1. Clone the repository

```bash
git https://github.com/bluefeng2/GraphVisualizer.git
cd GraphVisualizer
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

Run the main Python script:

```bash
python main.py
```

Follow the prompts to:

* Enter nodes and edges
* Choose graph type (directed or undirected)
* Run commands like `mst`, `cycle`, `bellmanford`, `adjlist`, `edges`, `adjmatrix`, `toposort`, etc.
* Visualize graphs and algorithm results automatically

---

## Available Commands

| Command | Description                                                                                           |
| ------- | ----------------------------------------------------------------------------------------------------- |
| `add`   | Add or update edges in the graph. Input edges line by line as `from to weight`. Empty line to finish. |
| `show`  | Visualize the current graph using matplotlib.                                                         |
| `reset` | Reset the graph and start inputting a new graph from scratch.                                         |
| `exit`  | Exit the program.                                                                                     |
| `tools` | Opens a menu of extra tools:                                                                          |
|         | - `isTree`: Check if the graph is a tree.                                                             |
|         | - `shortestPath`: Find shortest path between two nodes (no negative cycles).                          |
|         | - `pathExists`: Check if a path exists between two nodes.                                             |
|         | - `minimumSpanningTree`: Find the MST of the graph.                                                   |
|         | - `maximumSpanningTree`: Find the maximum spanning tree of the graph.                                 |
|         | - `hasCycle`: Detect if the graph contains a cycle.                                                   |
|         | - `printAdjList`: Print the adjacency list.                                                           |
|         | - `printEdges`: Print the list of edges.                                                              |
|         | - `printAdjMatrix`: Print the adjacency matrix.                                                       |
|         | - `findCentroid`: Find the centroid of the graph (graph must be a tree, direction ignored).           |
|         | - `topologicalSort`: Find the order of a topological sort (graph must be directed and acyclic).       |
| `help`  | Show this help message listing all commands.                                                          |

---

## Requirements

The project requires:

* Python 3.7+
* [NetworkX](https://networkx.org/)
* [Matplotlib](https://matplotlib.org/)

Dependencies are listed in `requirements.txt`.

---

## License

MIT License © Lingfeng Wang
