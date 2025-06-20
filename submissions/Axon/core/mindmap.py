from core.node_manager import list_nodes
from utils.file_utils import app_path
from collections import defaultdict, deque
import json
import dotenv
import os
import time  # for debugging slow operations

# load env vars first
dotenv.load_dotenv(os.path.join(app_path, '.env'))

# try to import groq
try:
    from groq import Groq
    ai_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except ImportError:
    print("Warning: Groq not installed. AI features disabled.")
    ai_client = None

# max width for display
MAX_WIDTH = 100
MAX_NODES_SHOWN = 3  # limit nodes shown at each level
DEBUG = False  # set to True for verbose output

# TODO: Add visualization export to graphviz or mermaid
def get_connections():
    """Get all node connections"""
    all_nodes = list_nodes()
    node_links = defaultdict(list)
    name_to_idx = {}
    
    # build connection graph
    for i, n in enumerate(all_nodes):
        title = n.get('title', f'Unnamed_{i}')
        name_to_idx[title] = i
        
        # get outgoing links
        links = n.get('links', [])
        if links:
            for link in links:
                if link:  # skip empty links
                    node_links[title].append(link)
    
    return node_links, name_to_idx, all_nodes

def analyze_network():
    """AI analysis of knowledge network"""
    links, idx_map, nodes = get_connections()
    
    if not links:
        return "No connections found between nodes."
    
    # build network summary
    net_summary = ""
    for src, targets in links.items():
        net_summary += f"{src} → {', '.join(targets)}\n"
    
    # get content snippets
    snippets = ""
    for n in nodes:
        title = n.get('title', 'Untitled')
        path = n.get('path', '')
        try:
            with open(path, 'r') as f:
                raw = f.read()
                # extract content after frontmatter
                parts = raw.split('---', 2)
                content = parts[2].strip()[:200] + "..." if len(parts) > 2 else raw[:200] + "..."
        except:
            content = "Can't read content"
        
        snippets += f"{title}:\n{content}\n\n"
    
    # prepare AI prompt
    msgs = [
        {
            "role": "system",
            "content": "You're analyzing a personal knowledge network. Look for patterns, central concepts, gaps, and insights. Return JSON with: 'central_concepts' (key nodes), 'knowledge_clusters' (related groups), 'gaps' (missing connections), 'recommendations' (improvement ideas), and 'insights' (observations)."
        },
        {
            "role": "user",
            "content": f"Here's my knowledge network:\n{net_summary}\n\nContent snippets:\n{snippets}"
        }
    ]
    
    # call AI
    if not ai_client:
        return "AI analysis unavailable - Groq API key not configured"
    
    try:
        start = time.time()
        resp = ai_client.chat.completions.create(
            messages=msgs,
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        if DEBUG:
            print(f"AI call took {time.time() - start:.2f} seconds")
        
        data = json.loads(resp.choices[0].message.content)
        return pretty_print_analysis(data)
    
    except Exception as e:
        return f"Analysis failed: {str(e)}"

def find_missing_links(focus=None):
    """Find potential missing connections between nodes"""
    links, idx_map, nodes = get_connections()
    
    if not nodes:
        return "No nodes found."
    
    # get all node content
    node_data = ""
    for n in nodes:
        title = n.get('title', 'Untitled')
        path = n.get('path', '')
        existing = n.get('links', [])
        
        try:
            f = open(path, 'r')
            raw = f.read()
            f.close()
            
            # split by frontmatter
            parts = raw.split('---', 2)
            text = parts[2].strip() if len(parts) > 2 else raw
        except:
            text = "Content unavailable"
        
        node_data += f"Title: {title}\nLinks: {existing}\nContent: {text}\n\n---\n\n"
    
    # add focus instruction if needed
    focus_text = ""
    if focus:
        focus_text = f" Focus especially on connections involving '{focus}'."
    
    # prepare AI prompt
    msgs = [
        {
            "role": "system",
            "content": f"You're a knowledge graph expert. Find meaningful missing connections between these nodes.{focus_text} Return JSON with 'suggested_connections' as an array of objects with 'from_node', 'to_node', and 'reason' fields."
        },
        {
            "role": "user",
            "content": f"Here are my knowledge nodes:\n\n{node_data}\n\nWhat connections am I missing?"
        }
    ]
    
    if not ai_client:
        return "Connection suggestions unavailable - Groq API key not configured"
    
    try:
        resp = ai_client.chat.completions.create(
            messages=msgs,
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(resp.choices[0].message.content)
        return pretty_print_suggestions(data)
    
    except Exception as e:
        return f"Failed to generate suggestions: {str(e)}"

def make_learning_path(topic):
    """Generate learning path for a topic"""
    links, idx_map, nodes = get_connections()
    
    # first try to find nodes by title match
    found = []
    for n in nodes:
        title = n.get('title', '')
        if topic.lower() in title.lower():
            found.append(n)
    
    # if no title matches, search content
    if not found:
        for n in nodes:
            path = n.get('path', '')
            try:
                with open(path, 'r') as f:
                    text = f.read().lower()
                    if topic.lower() in text:
                        found.append(n)
            except:
                pass
    
    # still nothing? give up
    if not found:
        some_nodes = list(idx_map.keys())[:5]
        return f"Couldn't find anything about '{topic}'. Try one of these instead: {some_nodes}"
    
    # prepare node info for AI
    info = ""
    for n in nodes:
        title = n.get('title', '')
        outgoing = n.get('links', [])
        path = n.get('path', '')
        
        try:
            with open(path, 'r') as f:
                raw = f.read()
                parts = raw.split('---', 2)
                preview = parts[2].strip()[:300] + "..." if len(parts) > 2 else raw[:300] + "..."
        except:
            preview = "Content unavailable"
        
        info += f"{title} (links: {outgoing}):\n{preview}\n\n"
    
    # prepare AI prompt
    msgs = [
        {
            "role": "system",
            "content": "You're creating a learning path through knowledge nodes. Order them optimally for learning the topic. Return JSON with 'learning_path' as an array of objects with 'node_title', 'why_this_order', and 'key_concepts', plus a 'summary' explaining the approach."
        },
        {
            "role": "user",
            "content": f"Topic: '{topic}'\n\nAvailable nodes:\n{info}\n\nCreate a learning path for '{topic}'."
        }
    ]
    
    if not ai_client:
        return "Learning path unavailable - Groq API key not configured"
    
    try:
        resp = ai_client.chat.completions.create(
            messages=msgs,
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        data = json.loads(resp.choices[0].message.content)
        return pretty_print_learning_path(data, topic)
    
    except Exception as e:
        return f"Couldn't generate learning path: {str(e)}"

def pretty_print_analysis(data):
    """Format network analysis for display"""
    output = []
    output.append("🧠 KNOWLEDGE NETWORK ANALYSIS")
    output.append("=" * 50)
    output.append("")
    
    # sections to display
    sections = [
        ('central_concepts', "🔑 KEY CONCEPTS"),
        ('knowledge_clusters', "🔄 CONCEPT CLUSTERS"),
        ('gaps', "🕳️  KNOWLEDGE GAPS"),
        ('recommendations', "💡 SUGGESTIONS"),
        ('insights', "🔍 INSIGHTS")
    ]
    
    for key, title in sections:
        if key in data:
            output.append(f"{title}:")
            
            # handle both string and list formats
            if isinstance(data[key], list):
                for item in data[key]:
                    output.append(f"  • {item}")
            else:
                output.append(f"  {data[key]}")
                
            output.append("")
    
    output.append("=" * 50)
    return "\n".join(output)

def pretty_print_suggestions(data):
    """Format connection suggestions for display"""
    lines = []
    lines.append("🔗 SUGGESTED CONNECTIONS")
    lines.append("=" * 50)
    lines.append("")
    
    if 'suggested_connections' in data:
        suggestions = data['suggested_connections']
        
        # sort by from_node for easier reading
        try:
            suggestions.sort(key=lambda x: x.get('from_node', ''))
        except:
            # if sorting fails, just use as-is
            pass
            
        for i, item in enumerate(suggestions, 1):
            src = item.get('from_node', 'Unknown')
            dst = item.get('to_node', 'Unknown')
            why = item.get('reason', 'No reason given')
            
            lines.append(f"{i}. {src} → {dst}")
            lines.append(f"   Why: {why}")
            lines.append("")
    
    lines.append("To add these connections: python main.py link \"Source\" \"Target\"")
    lines.append("=" * 50)
    return "\n".join(lines)

def pretty_print_learning_path(data, topic):
    """Format learning path for display"""
    lines = []
    lines.append(f"📚 LEARNING PATH: {topic.upper()}")
    lines.append("=" * 50)
    lines.append("")
    
    if 'summary' in data:
        lines.append("APPROACH:")
        lines.append(f"{data['summary']}")
        lines.append("")
    
    if 'learning_path' in data:
        lines.append("SEQUENCE:")
        for i, step in enumerate(data['learning_path'], 1):
            node = step.get('node_title', 'Unknown')
            why = step.get('why_this_order', '')
            concepts = step.get('key_concepts', [])
            
            lines.append(f"{i}. {node}")
            if why:
                lines.append(f"   Why: {why}")
            if concepts:
                if isinstance(concepts, list):
                    lines.append(f"   Key concepts: {', '.join(concepts)}")
                else:
                    lines.append(f"   Key concepts: {concepts}")
            lines.append("")
    
    lines.append("=" * 50)
    return "\n".join(lines)

def map_node_depths(links, start, max_depth=3):
    """Map nodes by depth from starting node using BFS"""
    if not links or start not in links and not any(start in targets for targets in links.values()):
        # fallback if node isn't in the graph
        return {0: [start]}
    
    seen = set()
    by_depth = defaultdict(list)
    q = deque([(start, 0)])  # (node, depth)
    
    while q:
        node, depth = q.popleft()
        
        # stop if we've seen this or gone too deep
        if node in seen or depth > max_depth:
            continue
            
        seen.add(node)
        by_depth[depth].append(node)
        
        # add connected nodes to queue
        for next_node in links.get(node, []):
            if next_node not in seen:
                q.append((next_node, depth + 1))
    
    return by_depth

def draw_mindmap(root=None, depth=3, width=80):
    """Create ASCII mindmap starting from root node"""
    links, idx_map, nodes = get_connections()
    
    if not links and not idx_map:
        return "No nodes found."
    
    # if no root specified, use most connected node
    if root is None:
        if links:
            # find node with most connections
            root = max(links.keys(), key=lambda x: len(links[x]))
        else:
            # fallback to first node
            root = list(idx_map.keys())[0]
    
    # handle case when root isn't found exactly
    if root not in links and root not in idx_map:
        # try partial match
        matches = [n for n in idx_map.keys() if root.lower() in n.lower()]
        if matches:
            root = matches[0]
        else:
            return f"Can't find node '{root}'. Available nodes: {list(idx_map.keys())[:5]}..."
    
    # get nodes by depth
    levels = map_node_depths(links, root, depth)
    
    # build the map
    output = []
    output.append("-" * min(width, 60))
    output.append(f"MINDMAP: {root}")
    output.append("-" * min(width, 60))
    output.append("")
    
    for level in sorted(levels.keys()):
        nodes_at_level = levels[level]
        
        # root node
        if level == 0:
            output.append(f"● {root}")
            if links.get(root):
                output.append("│")
        else:
            indent = "  " * level
            
            for i, node in enumerate(nodes_at_level):
                is_last = i == len(nodes_at_level) - 1
                branch = "└─" if is_last else "├─"
                
                # truncate long names
                if len(node) > width-len(indent)-5:
                    display = node[:width-len(indent)-8] + "..."
                else:
                    display = node
                
                output.append(f"{indent}{branch}→ {display}")
                
                # show child nodes if any
                children = [c for c in links.get(node, []) if c != root]
                
                if children and level < depth:
                    # limit number shown
                    shown = children[:MAX_NODES_SHOWN]
                    child_indent = indent + ("    " if is_last else "│   ")
                    
                    for j, child in enumerate(shown):
                        is_last_child = j == len(shown) - 1
                        child_branch = "└─" if is_last_child else "├─"
                        
                        # truncate long names
                        if len(child) > width-len(child_indent)-5:
                            child_display = child[:width-len(child_indent)-8] + "..."
                        else:
                            child_display = child
                            
                        output.append(f"{child_indent}{child_branch}→ {child_display}")
                    
                    # show count of hidden children
                    if len(children) > MAX_NODES_SHOWN:
                        hidden = len(children) - MAX_NODES_SHOWN
                        output.append(f"{child_indent}    ... {hidden} more ...")
            
            # add spacing between levels
            if level < max(levels.keys()):
                output.append("│")
    
    output.append("")
    output.append("● Root | → Connection")
    output.append("-" * min(width, 60))
    
    return "\n".join(output)

def show_connections():
    """Display all connections between nodes"""
    links, idx_map, nodes = get_connections()
    
    if not links:
        return "No connections found."
    
    output = []
    output.append("-" * 50)
    output.append("NODE CONNECTIONS")
    output.append("-" * 50)
    output.append("")
    
    # sort by number of connections (most first)
    sorted_nodes = sorted(links.items(), key=lambda x: len(x[1]), reverse=True)
    
    for node, targets in sorted_nodes:
        output.append(f"● {node} ({len(targets)} links)")
        for target in sorted(targets):
            output.append(f"  └→ {target}")
        output.append("")
    
    # find orphaned nodes (no outgoing links)
    all_nodes = set(idx_map.keys())
    linked = set(links.keys())
    orphans = all_nodes - linked
    
    if orphans:
        output.append("ORPHANED NODES:")
        for orphan in sorted(orphans):
            output.append(f"  ● {orphan}")
        output.append("")
    
    output.append("-" * 50)
    return "\n".join(output)

def generate_mindmap(node_name=None, show_all=False, max_depth=3, ai_analysis=False, suggest_connections=False, learning_path=None):
    """Main entry point for mindmap functionality"""
    # handle different modes
    if ai_analysis:
        return analyze_network()
    elif suggest_connections:
        return find_missing_links(node_name)
    elif learning_path:
        return make_learning_path(learning_path)
    elif show_all:
        return show_connections()
    else:
        return draw_mindmap(node_name, max_depth)