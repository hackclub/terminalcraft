# Axon - Your Second Brain in the Terminal

Hi! **Axon** is a CLI knowledge management system I built because I was sick of forgetting everything cool I learned.

---

## 🧠 What's This All About?

Ever had an awesome idea at 2 AM and completely forgotten it in the morning? Or spent a whole night figuring something out, only to have to re-figure it out months later? Yeah, me too.

That's why I built **Axon** – it's basically a second brain that lives in your terminal.

Axon lets you:

* 🗂️ Build and tag knowledge nodes (schmancy term for notes)
* 🔗 Link similar ideas together
* 🔍 Search your knowledge base
* 🤖 Ask questions about what you know
* 🧭 Visualize relationships through mindmaps
* ✅ Turn your thoughts into action plans
* 🧠 See what you're thinking most about (Synaptic Heatmap)
* 📝 Export your notes into Notion

---

## 🚀 Getting Started

### 🔧 Installation

1. Clone this repo (most likely, you already did that):

   ```bash
   git clone https://github.com/Malak-Sabry-104/axon.git
   cd axon
   ```

2. Set up a virtual environment (you really want this):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install requirements:

   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables (for AI features):

   ```bash
   cp .env.example ~/Axon/.env
   # Then edit .env with your API keys
   ```

---

## ✍️ Basic Usage

Create a new note:

```bash
python main.py create "My Brilliant Idea"
```

Link related notes:

```bash
python main.py link "My Brilliant Idea" "Related Concept"
```

Search your knowledge:

```bash
python main.py search "python generators"
```

Ask questions:

```bash
python main.py ask "How did I solve that database indexing problem?"
```

Generate a mindmap:

```bash
python main.py mindmap --node "Starting Concept"
```

Turn ideas into action plans:

```bash
python main.py plan "Create a personal website"
```

See what's on your mind the most:

```bash
python main.py heatmap
```

---

## 🗂️ Project Structure

Nothing fancy here, just a standard layout:

```
Axon/
├── main.py              # CLI entry point
├── core/                # Core logic
│   ├── node_manager.py  # Note CRUD operations
│   ├── search.py        # Searching component
│   ├── mindmap.py       # Visualization
│   ├── ask.py           # Question-answering system
│   ├── planner.py       # Action planning generator
│   ├── heatmap.py       # Domain analysis
│   └── export.py        # Notion export
├── utils/               # Helper functions
└── data/                # Where your knowledge lives
    └── nodes/           # Individual knowledge nodes
```

---

## 🐞 Known Issues & Quirks

* 🤷 Sometimes AI is baffled if your notes are just too weird (like mine tend to be)
* 🧶 Mindmap can get messy with too many connections (just like my actual brain)
* 🧊 Occasionally forgets to cache domains for new notes (I'm working on it!)
* 🖥️ Terminal UI is... well, it's a terminal. No unnecessary animations.

---

## 🔮 Future Plans

Stuff I *might* add when procrastinating on other things:

* 📊 Better visualization options
* 🧠 Spaced repetition learning
* 🤝 Suggested automated connections
* 📱 Mobile app (lol, who am I kidding – probably not)

---

## ❤️ Why I Built This

I was tired of having notes strewn everywhere – Notion, Apple Notes, random `.txt` files, and Post-its stuck to my monitor.

I wanted something simple, powerful, and terminal-native – because I’m a nerd and proud.

This is a work in progress and a labor of love. If you find it useful, awesome! If you have ideas to make it better, open an issue or PR!

---

## 📄 License

**MIT** – because sharing is caring.
Use it. Break it. Fix it. Improve it. Send me a PR if you're cool like that.