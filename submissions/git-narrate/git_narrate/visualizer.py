import markdown2
from pathlib import Path

def create_html_story(markdown_content: str, output_path: Path, project_name: str):
    """Converts a markdown story into a styled HTML file."""
    
    html_body = markdown2.markdown(markdown_content, extras=["fenced-code-blocks", "tables"])
    
    css_style = """
    body {
        font-family: 'Georgia', serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 40px auto;
        padding: 20px;
        background-color: #f9f9f9;
        border-left: 2px solid #ddd;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        color: #2c3e50;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 0.3em;
    }
    h1 {
        font-size: 2.5em;
        text-align: center;
        border-bottom: none;
    }
    h2 {
        font-size: 1.75em;
    }
    p {
        margin-bottom: 1em;
    }
    code {
        background-color: #ecf0f1;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
    }
    pre {
        background-color: #2c3e50;
        color: #ecf0f1;
        padding: 1em;
        border-radius: 5px;
        overflow-x: auto;
    }
    pre code {
        background-color: transparent;
        padding: 0;
    }
    """
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>The Story of {project_name}</title>
        <style>
            {css_style}
        </style>
    </head>
    <body>
        <h1>The Story of {project_name}</h1>
        {html_body}
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
