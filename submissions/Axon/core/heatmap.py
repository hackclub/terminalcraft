import os
import json
import re
from collections import Counter, defaultdict
import dotenv
from core.node_manager import list_nodes
from utils.file_utils import app_path, load_node
import random  # for some randomness in the heatmap display

# TODO: Add option to export heatmap as image
# TODO: Add time-based heatmap to show activity over time

dotenv.load_dotenv(os.path.join(app_path, '.env'))

# Define domain keywords for both AI and fallback classification
DOMAIN_KEYWORDS = {
    "Programming": ["code", "programming", "function", "algorithm", "variable", "python", "javascript", "class", "method", "compiler", "rust", "golang", "java", "coding"],
    "Web Development": ["html", "css", "javascript", "web", "frontend", "backend", "react", "angular", "vue", "node", "express", "api", "website", "responsive", "dom"],
    "Data Science": ["data", "analysis", "statistics", "pandas", "numpy", "visualization", "dataset", "correlation", "regression", "analytics", "tableau", "matplotlib"],
    "Machine Learning": ["ml", "ai", "model", "training", "neural", "prediction", "classification", "clustering", "tensorflow", "pytorch", "deep learning", "nlp", "computer vision"],
    "Databases": ["sql", "database", "query", "table", "schema", "nosql", "mongodb", "postgresql", "mysql", "redis", "orm", "acid", "index", "primary key"],
    "Project Management": ["project", "management", "agile", "scrum", "sprint", "milestone", "kanban", "jira", "deadline", "stakeholder", "requirement", "deliverable"],
    "Philosophy": ["philosophy", "ethics", "moral", "existence", "consciousness", "metaphysics", "epistemology", "logic", "meaning", "ontology", "phenomenology"],
    "Health": ["health", "fitness", "exercise", "diet", "nutrition", "workout", "wellness", "meditation", "mindfulness", "yoga", "mental health", "physical"],
    "Finance": ["finance", "money", "investment", "stock", "budget", "saving", "expense", "income", "asset", "liability", "wealth", "portfolio", "retirement"],
    "Writing": ["writing", "blog", "article", "essay", "story", "novel", "character", "plot", "narrative", "grammar", "prose", "fiction", "nonfiction"],
    "Cooking": ["recipe", "cooking", "baking", "ingredient", "meal", "food", "dish", "cuisine", "kitchen", "flavor", "taste", "culinary", "chef"],
    "Personal Development": ["habit", "productivity", "goal", "motivation", "discipline", "routine", "mindset", "growth", "improvement", "self-help", "learning"],
    "Technology": ["hardware", "software", "device", "gadget", "tech", "innovation", "digital", "computer", "mobile", "app", "iot", "cloud", "saas"],
    "Business": ["business", "startup", "entrepreneur", "marketing", "strategy", "customer", "product", "service", "market", "revenue", "profit", "sales"]
}

# Try to import Groq for AI domain classification
try:
    from groq import Groq
    brain = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    AI_WORKS = True
except ImportError:
    print("Warning: Groq not installed. Domain classification will be limited.")
    AI_WORKS = False
except Exception as e:
    print(f"Error initializing Groq: {e}")
    AI_WORKS = False

# Common domains to help avoid duplicates
COMMON_DOMAINS = list(DOMAIN_KEYWORDS.keys())

def get_note_content(path):
    """Get the actual content from a note file"""
    try:
        with open(path, 'r') as f:
            raw = f.read()
        
        # split by frontmatter markers
        chunks = raw.split('---', 2)
        if len(chunks) >= 3:
            return chunks[2].strip()
        return raw
    except Exception as e:
        print(f"Couldn't read {path}: {e}")
        return "Content unavailable"

def get_domain(title, content, existing=None):
    """Figure out what domain a note belongs to"""
    if not AI_WORKS:
        # fallback to keyword matching
        return guess_domain(title, content, existing)
    
    # Format domain keywords for AI
    domain_info = "\n".join([f"- {domain}: {', '.join(keywords[:5])}" for domain, keywords in DOMAIN_KEYWORDS.items()])
    
    # build context with existing domains to avoid duplication
    context = ""
    if existing:
        context = f"Here are the domains already in use: {', '.join(existing)}. Try to use one of these if it fits."
    
    # build prompt for AI
    prompt = [
        {
            "role": "system",
            "content": (
                "You're a knowledge domain classifier. Analyze the note title and content "
                "and determine which single domain or category it belongs to. "
                "Return ONLY the domain name as a single word or short phrase, nothing else. "
                "Choose the most specific domain that accurately represents the content. "
                f"{context}\n\n"
                f"Here are the available domains with their related keywords:\n{domain_info}"
            )
        },
        {
            "role": "user",
            "content": f"Note title: {title}\n\nContent: {content[:1000]}..."
        }
    ]
    
    try:
        # ask AI for domain
        resp = brain.chat.completions.create(
            messages=prompt,
            model="llama-3.3-70b-versatile",
            max_tokens=20
        )
        
        # clean up the response
        domain = resp.choices[0].message.content.strip()
        
        # remove quotes and punctuation
        domain = re.sub(r'[^\w\s]', '', domain)
        
        # check for similar domains to avoid duplicates
        if existing:
            for e in existing:
                # if they're similar enough, use the existing one
                if domain.lower() in e.lower() or e.lower() in domain.lower():
                    return e
        
        # Check if response matches one of our predefined domains
        for known_domain in COMMON_DOMAINS:
            if domain.lower() == known_domain.lower() or domain.lower() in known_domain.lower():
                return known_domain
        
        return domain
    except Exception as e:
        print(f"AI domain classification failed: {e}")
        return guess_domain(title, content, existing)

def guess_domain(title, content, existing=None):
    """Guess domain based on keywords when AI isn't available"""
    text = (title + " " + content).lower()
    
    # Count keyword matches for each domain
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = 0
        for word in keywords:
            if word.lower() in text:
                score += 1
        if score > 0:
            scores[domain] = score
    
    # If we have existing domains, check for matches in title
    if existing and title:
        for domain in existing:
            if domain.lower() in title.lower():
                return domain
    
    # Return domain with highest score or default
    if scores:
        best_domain = max(scores, key=scores.get)
        # If we have existing domains and a similar one exists, use that instead
        if existing:
            for e in existing:
                if best_domain.lower() in e.lower() or e.lower() in best_domain.lower():
                    return e
        return best_domain
    
    # Last resort - check if any common domain appears in the title
    for domain in COMMON_DOMAINS:
        if domain.lower() in title.lower():
            return domain
            
    return "Uncategorized"

def save_domain_to_note(path, domain):
    """Save domain to a note's metadata"""
    try:
        # read the file
        with open(path, 'r') as f:
            content = f.read()
        
        # find metadata section
        match = re.search(r"---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return False
        
        # get metadata
        meta_str = match.group(1)
        meta = json.loads(meta_str)
        
        # only update if domain changed
        if meta.get('domain') != domain:
            meta['domain'] = domain
            
            # replace metadata in file
            new_content = content.replace(
                f"---\n{meta_str}\n---",
                f"---\n{json.dumps(meta, indent=2)}\n---"
            )
            
            # write back to file
            with open(path, 'w') as f:
                f.write(new_content)
            
            return True
    except Exception as e:
        print(f"Error updating note domain: {e}")
    
    return False

def update_all_domains(force=False):
    """Make sure all notes have domains assigned"""
    notes = list_nodes()
    if not notes:
        return 0
    
    # get existing domains
    domains = set()
    for note in notes:
        if 'domain' in note:
            domains.add(note['domain'])
    
    # count how many we update
    updated = 0
    
    # process notes
    for note in notes:
        # Update if no domain or force update is requested
        if 'domain' not in note or force:
            path = note.get('path', '')
            title = note.get('title', '')
            
            if path and title:
                content = get_note_content(path)
                domain = get_domain(title, content, list(domains))
                
                if domain and save_domain_to_note(path, domain):
                    domains.add(domain)
                    updated += 1
    
    return updated

def make_heatmap():
    """Generate an ASCII heatmap of knowledge domains"""
    # First, make sure all notes have domains
    updated = update_all_domains()
    if updated > 0:
        print(f"Added domains to {updated} notes")
    
    # Get all notes
    notes = list_nodes()
    if not notes:
        return "No notes found in your knowledge base"
    
    # Count domains and track which notes belong to each
    counts = Counter()
    domain_notes = defaultdict(list)
    
    for note in notes:
        domain = note.get('domain', 'Uncategorized')
        counts[domain] += 1
        domain_notes[domain].append(note.get('title', 'Untitled'))
    
    # Sort domains by count
    sorted_domains = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    # Start building output
    output = []
    output.append("🧠 SYNAPTIC HEATMAP")
    output.append("=" * 50)
    output.append("")
    
    # Get max count for scaling
    max_count = max(counts.values()) if counts else 0
    
    # Generate bars with a bit of randomness in the character choice
    bar_chars = ['█', '▓', '▒', '░']  # different fill characters for variety
    
    for domain, count in sorted_domains:
        # Calculate bar length (max 40 chars)
        bar_len = int((count / max_count) * 40) if max_count > 0 else 0
        
        # Pick a character for this bar
        char = random.choice(bar_chars) if random.random() > 0.7 else '█'
        bar = char * bar_len
        
        # Add the domain bar
        output.append(f"{domain.ljust(20)} | {bar} ({count})")
    
    output.append("")
    output.append("=" * 50)
    
    # Add domain details section
    output.append("\n📊 DOMAIN BREAKDOWN")
    output.append("-" * 50)
    
    for domain, note_titles in domain_notes.items():
        output.append(f"\n📌 {domain} ({len(note_titles)} notes)")
        for i, title in enumerate(note_titles, 1):
            if i <= 5:  # Show only top 5 notes per domain
                output.append(f"  • {title}")
        if len(note_titles) > 5:
            output.append(f"  • ... and {len(note_titles) - 5} more")
    
    return "\n".join(output)

def add_domain_to_new_note(path):
    """Add domain to a newly created note"""
    try:
        # Get note info
        meta = load_node(path)
        title = meta.get('title', '')
        
        # Get content
        content = get_note_content(path)
        
        # Get existing domains
        notes = list_nodes()
        domains = set()
        for note in notes:
            if 'domain' in note:
                domains.add(note['domain'])
        
        # Get domain for this note
        domain = get_domain(title, content, list(domains))
        
        # Save it
        save_domain_to_note(path, domain)
        
        return domain
    except Exception as e:
        print(f"Error adding domain to new note: {e}")
        return None

# Aliases for compatibility with imported code
process_nodes_for_domains = update_all_domains
generate_heatmap = make_heatmap
assign_domain_to_new_node = add_domain_to_new_note
extract_content = get_note_content
classify_domain = get_domain
update_node_with_domain = save_domain_to_note