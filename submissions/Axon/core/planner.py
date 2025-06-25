import os
import json
import re
from datetime import datetime
import dotenv
from core.node_manager import list_nodes
from utils.file_utils import slugify, load_node, app_path
import time  # for debugging

# TODO: Add support for exporting plans to PDF
# TODO: Add plan templates feature

dotenv.load_dotenv(os.path.join(app_path, '.env'))

# max number of nodes to include
MAX_NODES = 5
DEBUG = False  # set to True to see timing info

# try loading groq - might fail if not installed
try:
    from groq import Groq
    llm = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    if DEBUG:
        print("Groq loaded successfully")
except ImportError:
    print("Warning: Couldn't load Groq. Planning features won't work.")
    llm = None
except Exception as e:
    print(f"Something went wrong with Groq: {e}")
    llm = None

def get_node_text(path):
    try:
        f = open(path, 'r')
        raw = f.read()
        f.close()
        
        # split by frontmatter markers
        chunks = raw.split('---', 2)
        if len(chunks) >= 3:
            return chunks[2].strip()
        return raw
    except Exception as e:
        if DEBUG:
            print(f"Couldn't read {path}: {e}")
        return "Can't read this node"

def find_matching_nodes(query):
    all_nodes = list_nodes()
    if not all_nodes:
        return []
    
    # we'll track matches here
    hits = []
    
    # first pass - check titles for matches
    for n in all_nodes:
        node_title = n.get('title', '').lower()
        # check if any word from query is in title
        for word in query.lower().split():
            if word in node_title and len(word) > 2:  # ignore short words
                hits.append(n)
                break
    
    # second pass - if we need more, check content
    if len(hits) < 3:
        for n in all_nodes:
            # skip if already matched
            if n in hits:
                continue
                
            # check content
            node_path = n.get('path', '')
            if not node_path:
                continue
                
            try:
                content = get_node_text(node_path).lower()
                # look for meaningful words from query in content
                important_words = [w for w in query.lower().split() if len(w) > 3]
                
                # if any important word appears in content
                if any(w in content for w in important_words):
                    hits.append(n)
                    # stop if we have enough
                    if len(hits) >= MAX_NODES:
                        break
            except:
                # just skip problematic files
                pass
    
    # might be empty, that's fine
    return hits

def create_plan(topic):
    # need AI for this
    if not llm:
        return "Can't create plans - Groq API not available"
    
    start_time = time.time()
    
    # find nodes that might help
    print("Finding relevant nodes...")
    nodes = find_matching_nodes(topic)
    
    # build context from nodes
    context = ""
    for i, n in enumerate(nodes):
        name = n.get('title', f'Node-{i}')
        path = n.get('path', '')
        
        # get content
        text = get_node_text(path)
        
        # truncate if too long - we just need a preview
        if len(text) > 500:
            text = text[:500] + "..."
            
        # add to context
        context += f"--- {name} ---\n{text}\n\n"
    
    # fallback if no context
    if not context:
        context = "No relevant nodes found in your knowledge base."
    
    # build the prompt
    system_msg = "You're a planning assistant that creates actionable plans based on ideas. Make a practical plan using any relevant knowledge. Return JSON with: plan_title (string), overview (string), steps (array of objects with step, details, resources, estimated_time), dependencies (array), and estimated_completion (string)."
    
    prompt = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"Create a plan for: {topic}\n\nHere's relevant info from my notes:\n{context}"}
    ]
    
    # call the AI
    print("Generating plan...")
    try:
        resp = llm.chat.completions.create(
            messages=prompt,
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        # parse JSON response
        plan_data = json.loads(resp.choices[0].message.content)
        
        if DEBUG:
            print(f"Plan generated in {time.time() - start_time:.2f} seconds")
            
        # format the plan nicely
        return pretty_print_plan(plan_data, topic)
        
    except Exception as e:
        return f"Failed to create plan: {str(e)}"

def pretty_print_plan(data, topic):
    lines = []
    
    # header stuff
    lines.append("🔄 MINDCHAIN AUTOPILOT")
    lines.append("-" * 50)
    
    # title - use provided or fallback
    title = data.get("plan_title") or f"Plan for: {topic}"
    lines.append(f"📝 {title.upper()}")
    lines.append("")
    
    # overview section
    overview = data.get("overview", "No overview provided")
    lines.append("🎯 OVERVIEW:")
    lines.append(f"  {overview}")
    lines.append("")
    
    # steps section
    steps = data.get("steps", [])
    if steps:
        lines.append("🛠️  STEPS:")
        
        # process each step
        for i, step in enumerate(steps, 1):
            # get step info with fallbacks
            name = step.get("step", f"Step {i}")
            details = step.get("details", "")
            resources = step.get("resources", "")
            time_est = step.get("estimated_time", "")
            
            # format step
            lines.append(f"  {i}. {name}")
            
            # add details if any
            if details:
                lines.append(f"     → {details}")
                
            # add resources if any
            if resources:
                lines.append(f"     📚 Resources: {resources}")
                
            # add time estimate if any
            if time_est:
                lines.append(f"     ⏱️ Time: {time_est}")
                
            # space between steps
            lines.append("")
    
    # dependencies section
    deps = data.get("dependencies", [])
    if deps and len(deps) > 0:
        lines.append("⚠️  PREREQUISITES:")
        for d in deps:
            lines.append(f"  • {d}")
        lines.append("")
    
    # completion time
    est_time = data.get("estimated_completion", "Unknown")
    lines.append(f"⏳ TOTAL TIME: {est_time}")
    lines.append("")
    
    # footer
    lines.append("-" * 50)
    lines.append(f"To save this plan: python main.py plan \"{topic}\" --save")
    
    # join with newlines
    return "\n".join(lines)

def save_as_node(topic, content):
    # make a title
    node_title = f"Plan: {topic}"
    
    # create filename from title
    fname = slugify(node_title)
    
    # make sure directory exists
    data_dir = os.path.join(app_path, "data/nodes")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    # full path to file
    fpath = os.path.join(data_dir, f"{fname}.md")
    
    # check if file exists already
    if os.path.exists(fpath):
        # add timestamp to make unique
        ts = datetime.now().strftime("%Y%m%d-%H%M")
        fpath = os.path.join(data_dir, f"{fname}-{ts}.md")
    
    # create node metadata
    meta = {
        "title": node_title,
        "created": datetime.now().isoformat(),
        "type": "plan",
        "topic": topic,
        "links": []
    }
    
    # write the file
    try:
        with open(fpath, "w") as f:
            # write frontmatter
            f.write("---\n")
            f.write(json.dumps(meta, indent=2))
            f.write("\n---\n\n")
            # write content
            f.write(content)
        return fpath
    except Exception as e:
        if DEBUG:
            print(f"Failed to save plan: {e}")
        return None