import matplotlib.pyplot as plt
import networkx as nx
import sys

def bellman_ford(G, start):
    dist = {node: float('inf') for node in G.nodes()}
    prev = {node: None for node in G.nodes()}
    dist[start] = 0

    for _ in range(len(G.nodes()) - 1):
        for u, v, data in G.edges(data=True):
            weight = data.get('weight', 1)
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                prev[v] = u
            if not G.is_directed() and dist[v] + weight < dist[u]:
                dist[u] = dist[v] + weight
                prev[u] = v

    # Check for negative weight cycles
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 1)
        if dist[u] + weight < dist[v]:
            print("Graph contains a negative weight cycle.")
            return None, None

    # Draw the graph
    pos = nx.spring_layout(G, k=50)
    edge_labels = nx.get_edge_attributes(G, 'weight')

    # Highlight shortest-path tree edges
    shortest_tree_edges = []
    for v, u in prev.items():
        if u is not None:
            shortest_tree_edges.append((u, v))
    
    print("Shortest distances from node", start)
    for node in sorted(G.nodes()):
        print(f"Node {node}: Distance = {dist[node]}")

    node_colors = ['gold' if node == start else 'skyblue' for node in G.nodes()]
    edge_colors = ['green' if (u, v) in shortest_tree_edges or (not G.is_directed() and (v, u) in shortest_tree_edges) else 'gray' for u, v in G.edges()]

    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color=edge_colors,
            node_size=400, font_weight='bold', arrows=G.is_directed())
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title(f"Shortest Paths from Node {start} (Bellman-Ford)")
    plt.axis('off')
    plt.show()

    return dist, prev

def kruskal_mst(G):
    if G.is_directed():
        print("MST is only defined for undirected graphs.")
        return None

    parent = {}
    rank = {}

    def find(u):
        if parent[u] != u:
            parent[u] = find(parent[u])  # path compression
        return parent[u]

    def union(u, v):
        root_u = find(u)
        root_v = find(v)
        if root_u == root_v:
            return False
        if rank[root_u] < rank[root_v]:
            parent[root_u] = root_v
        else:
            parent[root_v] = root_u
            if rank[root_u] == rank[root_v]:
                rank[root_u] += 1
        return True

    # Initialize disjoint sets
    for node in G.nodes():
        parent[node] = node
        rank[node] = 0

    edges = sorted(G.edges(data=True), key=lambda x: x[2].get('weight', 1))

    mst_edges = []
    total_weight = 0

    for u, v, data in edges:
        weight = data.get('weight', 1)
        if union(u, v):
            mst_edges.append((u, v))
            total_weight += weight

    print("MST edges (u, v, weight):")
    for u, v in mst_edges:
        w = G[u][v].get('weight', 1)
        print(f"{u} - {v} (weight {w})")

    print(f"Total weight of MST: {total_weight}")

    # Visualization
    pos = nx.spring_layout(G, k=50)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=400, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw_networkx_edges(G, pos, edgelist=mst_edges, edge_color='green', width=2)

    plt.title("Minimum Spanning Tree (Kruskal's Algorithm)")
    plt.axis('off')
    plt.show()

    return mst_edges

def kruskal_mast(G):
    if G.is_directed():
        print("MST is only defined for undirected graphs.")
        return None

    parent = {}
    rank = {}

    def find(u):
        if parent[u] != u:
            parent[u] = find(parent[u])  # path compression
        return parent[u]

    def union(u, v):
        root_u = find(u)
        root_v = find(v)
        if root_u == root_v:
            return False
        if rank[root_u] < rank[root_v]:
            parent[root_u] = root_v
        else:
            parent[root_v] = root_u
            if rank[root_u] == rank[root_v]:
                rank[root_u] += 1
        return True

    # Initialize disjoint sets
    for node in G.nodes():
        parent[node] = node
        rank[node] = 0

    edges = sorted(G.edges(data=True), key=lambda x: x[2].get('weight', 1), reverse=True)

    mst_edges = []
    total_weight = 0

    for u, v, data in edges:
        weight = data.get('weight', 1)
        if union(u, v):
            mst_edges.append((u, v))
            total_weight += weight

    print("MST edges (u, v, weight):")
    for u, v in mst_edges:
        w = G[u][v].get('weight', 1)
        print(f"{u} - {v} (weight {w})")

    print(f"Total weight of MST: {total_weight}")

    # Visualization
    pos = nx.spring_layout(G, k=50)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=400, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    nx.draw_networkx_edges(G, pos, edgelist=mst_edges, edge_color='green', width=2)

    plt.title("Maximum Spanning Tree (Kruskal's Algorithm)")
    plt.axis('off')
    plt.show()

    return mst_edges


def find_cycle(G):
    visited = set()
    cycle_nodes = []
    cycle_edges = []

    def draw_cycle():
        pos = nx.spring_layout(G, k=50)
        node_colors = []
        for node in G.nodes():
            node_colors.append('red' if node in cycle_nodes else 'skyblue')

        edge_colors = []
        for u, v in G.edges():
            if (u, v) in cycle_edges or (v, u) in cycle_edges:
                edge_colors.append('red')
            else:
                edge_colors.append('gray')

        nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=400, font_weight='bold', edge_color=edge_colors, width=[3 if c=='red' else 1 for c in edge_colors], arrows=G.is_directed())
        plt.title("Graph Cycle Visualization")
        plt.axis('off')
        plt.show()

    if G.is_directed():
        rec_stack = set()
        parent = {}

        def dfs(node):
            nonlocal cycle_nodes, cycle_edges
            visited.add(node)
            rec_stack.add(node)

            for neighbor in G.neighbors(node):
                if neighbor not in visited:
                    parent[neighbor] = node
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle, reconstruct path
                    cycle_nodes = [neighbor]
                    current = node
                    while current != neighbor:
                        cycle_nodes.append(current)
                        current = parent[current]
                    cycle_nodes.append(neighbor)
                    cycle_nodes.reverse()

                    # Build cycle edges
                    cycle_edges = []
                    for i in range(len(cycle_nodes) - 1):
                        cycle_edges.append((cycle_nodes[i], cycle_nodes[i+1]))
                    print("Cycle found:", " -> ".join(map(str, cycle_nodes)))
                    draw_cycle()
                    return True

            rec_stack.remove(node)
            return False

        for node in G.nodes():
            if node not in visited:
                parent[node] = None
                if dfs(node):
                    return True
        print("No cycle found.")
        draw_cycle()
        return False

    else:
        parent = {}

        def dfs(node, prev):
            nonlocal cycle_nodes, cycle_edges
            visited.add(node)
            for neighbor in G.neighbors(node):
                if neighbor not in visited:
                    parent[neighbor] = node
                    if dfs(neighbor, node):
                        return True
                elif neighbor != prev:
                    # Found cycle, reconstruct path
                    cycle_nodes = [neighbor]
                    current = node
                    while current != neighbor:
                        cycle_nodes.append(current)
                        current = parent[current]
                    cycle_nodes.append(neighbor)
                    cycle_nodes.reverse()

                    # Build cycle edges
                    cycle_edges = []
                    for i in range(len(cycle_nodes) - 1):
                        cycle_edges.append((cycle_nodes[i], cycle_nodes[i+1]))
                    print("Cycle found:", " - ".join(map(str, cycle_nodes)))
                    draw_cycle()
                    return True
            return False

        for node in G.nodes():
            if node not in visited:
                parent[node] = None
                if dfs(node, None):
                    return True
        print("No cycle found.")
        draw_cycle()
        return False

def has_cycle(G):
    visited = set()

    if G.is_directed():
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in G.neighbors(node):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in G.nodes():
            if node not in visited:
                if dfs(node):
                    return True
        return False
    else:
        def dfs(node, parent):
            visited.add(node)
            for neighbor in G.neighbors(node):
                if neighbor not in visited:
                    if dfs(neighbor, node):
                        return True
                elif neighbor != parent:
                    return True
            return False

        for node in G.nodes():
            if node not in visited:
                if dfs(node, -1):
                    return True
        return False

def topological_sort(G):
    import collections
    
    if not G.is_directed():
        print("Topological sort only applies to directed graphs.")
        return None

    in_degree = {u: 0 for u in G.nodes()}
    for u, v in G.edges():
        in_degree[v] += 1

    queue = collections.deque([u for u in G.nodes() if in_degree[u] == 0])
    topo_order = []

    while queue:
        u = queue.popleft()
        topo_order.append(u)
        for v in G.successors(u):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(topo_order) != len(G.nodes()):
        print("The graph contains a cycle. Topological sort is not possible.")
        return None

    print("Topological Order:")
    print(" -> ".join(map(str, topo_order)))
    return topo_order

def find_tree_centroid(G):
    if not nx.is_tree(G):
        print("The graph is not a tree.")
        return []

    n = len(G.nodes())
    centroid = []
    subtree_size = {}

    def dfs(u, parent):
        size = 1
        is_centroid = True
        for v in G.neighbors(u):
            if v == parent:
                continue
            child_size = dfs(v, u)
            if child_size > n // 2:
                is_centroid = False
            size += child_size
        subtree_size[u] = size
        if n - size > n // 2:
            is_centroid = False
        if is_centroid:
            centroid.append(u)
        return size

    dfs(next(iter(G.nodes())), -1)

    print(f"Centroid node(s): {centroid}")

    # Draw graph
    pos = nx.spring_layout(G, k=50)
    node_colors = ['lightgreen' if node in centroid else 'skyblue' for node in G.nodes()]

    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=400, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
    plt.title("Tree with Centroid(s) Highlighted")
    plt.show()

    return centroid

def print_adj_list(G):
    print("Adjacency List:")
    for node in sorted(G.nodes()):
        neighbors = list(G.neighbors(node))
        print(f"{node}: {neighbors}")
        
def print_edges(G):
    print("Edges:")
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 1)
        print(f"{u} -- {v} (weight {weight})")
        
import numpy as np

def print_adj_matrix(G):
    nodes = sorted(G.nodes())
    index = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)

    matrix = np.zeros((n, n))

    for u, v, data in G.edges(data=True):
        w = data.get('weight', 1)
        i, j = index[u], index[v]
        matrix[i][j] = w
        if not G.is_directed():
            matrix[j][i] = w

    print("Adjacency Matrix:")
    print("    " + "  ".join(map(str, nodes)))
    for i, row in enumerate(matrix):
        print(f"{nodes[i]:>3} { '  '.join(f'{val:.1f}' for val in row) }")


def parse_initial_graph():
    print("Enter number of nodes and edges (e.g. `4 5`):")
    n, m = map(int, sys.stdin.readline().strip().split())
    
    print("Is this graph directed or undirected? (Directed, Undirected)")
    answer = sys.stdin.readline().strip().lower()
    if answer == "directed":
        G = nx.DiGraph()
        directed = True
    elif answer == "undirected":
        G = nx.Graph()
        directed = False
    else:
        print("Invalid input. Defaulting to undirected graph.")
        G = nx.Graph()
        directed = False
    
    print("Now enter each edge as `from to weight` (e.g. `1 4 6`). For unweighted, use weight=1")
    for _ in range(m):
        line = sys.stdin.readline().strip()
        if not line:
            continue
        u, v, w = line.split()
        G.add_edge(int(u), int(v), weight=float(w))
    
    return G, directed

def visualize_graph(G, directed=True):
    from math import sqrt
    pos = nx.spring_layout(G, k=50)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=400, font_weight='bold', arrows=directed)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    plt.title("Graph Visualization")
    plt.axis('off')
    plt.show()

def print_help():
    help_text = """
Available commands:

  add      - Add or update edges in the graph.
             Enter edges line by line in the format: from to weight
             Example: 1 3 5
             Enter an empty line to finish adding edges.

  show     - Visualize the current graph with matplotlib.

  reset    - Reset the graph and start inputting a new graph from scratch.

  exit     - Exit the program.
  
  tools    - Opens up a menu of extra tools
             isTree: checks if the graph is a tree
             shortestPath: finds the shortest path between two nodes (cannot have negative cycles)
             pathExists: checks if a path exists between two nodes
             minimumSpanningTree: finds the minimum spanning tree of the graph
             maximumSpanningTree: finds the maximum spanning tree of the graph
             hasCycle: detects whether there is a cycle in the graph
             printAdjList: prints out the adjacency list
             printEdges: prints out the list of edges
             printAdjMatrix: prints out the adjacency matrix
             findCentroid: finds the centroid of the graph (graph must be a tree and direction will not be taken into consideration)
             topologicalSort: finds the order of the topological sort (graph must be directed and acyclic)

  help     - Show this help message.
"""
    print(help_text)

def main():
    print("=== CLI Graph Visualizer ===")
    G, directed = parse_initial_graph()

    while True:
        print("\nEnter a command: add, show, reset, exit, tools, help")
        cmd = sys.stdin.readline().strip().lower()

        if cmd == "tools":
            print("\nEnter a command: isTree, shortestPath, pathExists, minimumSpanningTree, maximumSpanningTree, hasCycle, printAdjList, printEdges, printAdjMatrix, findCentroid, topologicalSort")
            choice = sys.stdin.readline().strip()
            if choice == "isTree":
                if has_cycle(G):
                    print("The graph **is not** a tree.")
                else:
                    print("The graph **is** a tree.")
            elif choice == "shortestPath":
                print("Enter the starting node:")
                start = int(sys.stdin.readline().strip())
                dist, prev = bellman_ford(G, start)
            elif choice == "pathExists":
                print("Enter the starting node:")
                start = int(sys.stdin.readline().strip())
                print("Enter the ending node:")
                end = int(sys.stdin.readline().strip())
                dist, prev = bellman_ford(G, start)
                if dist[end] == float('inf'):
                    print("This path **does not** exist.")
                else:
                    print("This path **does** exist")
            elif choice == "minimumSpanningTree":
                kruskal_mst(G)
            elif choice == "maximumSpanningTree":
                kruskal_mast(G)
            elif choice == "hasCycle":
                find_cycle(G)
            elif choice == "printAdjList":
                print_adj_list(G)
            elif choice == "printEdges":
                print_edges(G)
            elif choice == "printAdjMatrix":
                print_adj_matrix(G)
            elif choice == "findCentroid":
                find_tree_centroid(G)
            elif choice == "topologicalSort":
                topological_sort(G)
            else:
                print("Unknown choice")
        elif cmd == "help":
            print_help()
        elif cmd == "add":
            print("Enter edges to add/update in format `from to weight`. Empty line to stop.")
            while True:
                line = sys.stdin.readline().strip()
                if line == "":
                    break
                try:
                    u, v, w = line.split()
                    G.add_edge(int(u), int(v), weight=float(w))
                    print(f"Added/Updated edge {u} -> {v} with weight {w}")
                except ValueError:
                    print("Invalid format, please enter `from to weight`")
        elif cmd == "show":
            visualize_graph(G, directed)
        elif cmd == "reset":
            print("Resetting graph...")
            G, directed = parse_initial_graph()
        elif cmd == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command. Available commands: add, show, reset, exit")

if __name__ == "__main__":
    main()
