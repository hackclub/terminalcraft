import os
import json
import re
from datetime import datetime
import dotenv
from notion_client import Client
from notion_client.errors import APIResponseError
from core.node_manager import list_nodes
from utils.file_utils import load_node, app_path

dotenv.load_dotenv(os.path.join(app_path, '.env'))

# grab tokens from env
token = os.environ.get("NOTION_TOKEN")
db_id = os.environ.get("NOTION_DATABASE_ID")

# init client if we can
client = None
if token:
    client = Client(auth=token)
else:
    print("Warning: NOTION_TOKEN not set in environment")
if not db_id:
    print("Warning: NOTION_DATABASE_ID not set in environment")

# max retries for API calls
MAX_RETRIES = 2

# TODO: Add support for tables and images
def convert_md_to_blocks(md_text):
    # convert markdown to notion blocks
    result = []
    lines = md_text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # skip empty lines
        if not line:
            i += 1
            continue
        
        # handle headings
        if line.startswith('#'):
            # count number of # symbols
            count = 0
            for char in line:
                if char == '#':
                    count += 1
                else:
                    break
                    
            txt = line[count:].strip()
            
            # h1, h2, or h3+
            if count == 1:
                type = "heading_1"
            elif count == 2:
                type = "heading_2" 
            else:
                type = "heading_3"
                
            result.append({
                "object": "block",
                "type": type,
                type: {
                    "rich_text": [{"type": "text", "text": {"content": txt}}]
                }
            })
        
        # code blocks - bit tricky
        elif line.startswith('```'):
            code = []
            i += 1
            lang = line[3:].strip() or "plain text"
            
            # collect all lines until closing ```
            while i < len(lines):
                if lines[i].strip().startswith('```'):
                    break
                code.append(lines[i])
                i += 1
                
            # join code lines
            code_text = '\n'.join(code)
            
            # only add if we have content
            if code_text.strip():
                result.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": code_text}}],
                        "language": lang
                    }
                })
        
        # bullet lists
        elif line.startswith('- ') or line.startswith('* '):
            txt = line[2:].strip()
            result.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": txt}}]
                }
            })
        
        # numbered lists - use regex to match
        elif re.match(r'^\d+\.', line):
            # strip the number and period
            txt = re.sub(r'^\d+\.\s*', '', line)
            result.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": txt}}]
                }
            })
        
        # blockquotes
        elif line.startswith('>'):
            txt = line[1:].strip()
            result.append({
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [{"type": "text", "text": {"content": txt}}]
                }
            })
        
        # just regular text
        else:
            result.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line}}]
                }
            })
        
        i += 1
    
    return result

def send_to_notion(file_path, target_db=None):
    # sanity checks
    if not client:
        return {"success": False, "error": "No Notion token found"}
    
    # use provided db or fallback to env var
    target = target_db if target_db else db_id
    if not target:
        return {"success": False, "error": "No database ID provided"}
    
    try:
        # load the node
        node = load_node(file_path)
        if not node:
            return {"success": False, "error": f"Failed loading node: {file_path}"}
        
        # get full content
        f = open(file_path, 'r')
        raw = f.read()
        f.close()
            
        # split by frontmatter markers
        chunks = raw.split('---', 2)
        content = chunks[2].strip() if len(chunks) >= 3 else raw
        
        # convert markdown to notion format
        blocks = convert_md_to_blocks(content)
        
        # grab metadata
        title = node.get('title') or "Untitled"
        date = node.get('created') or datetime.now().isoformat()
        tags = node.get('links', [])
        
        # build properties object
        props = {
            "Name": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        }
        
        # add date if valid
        try:
            # just get the date part
            date_str = date.split('T')[0]
            props["Created"] = {
                "date": {"start": date_str}
            }
        except:
            # bad date format, just skip it
            pass
        
        # add tags if we have them
        if tags and len(tags) > 0:
            try:
                # notion has a limit of 10 multi-select items
                tag_list = tags[:10] if len(tags) > 10 else tags
                props["Tags"] = {
                    "multi_select": [{"name": t} for t in tag_list]
                }
            except Exception as e:
                print(f"Warning: Couldn't add tags: {e}")
        
        # finally create the page
        for attempt in range(MAX_RETRIES):
            try:
                page = client.pages.create(
                    parent={"database_id": target},
                    properties=props,
                    children=blocks
                )
                
                # success!
                return {
                    "success": True, 
                    "page_id": page["id"], 
                    "url": page["url"],
                    "title": title
                }
            except APIResponseError as e:
                if attempt == MAX_RETRIES - 1:
                    raise e
                # wait before retry
                import time
                time.sleep(1)
                
    except APIResponseError as e:
        return {"success": False, "error": f"API error: {e.code} - {e.message}"}
    except Exception as e:
        return {"success": False, "error": f"Failed: {str(e)}"}

def batch_export(indices=None, target_db=None):
    # get all nodes
    all_nodes = list_nodes()
    if not all_nodes:
        return {"success": False, "error": "No nodes found"}
    
    # if no indices provided, export everything
    if indices is None:
        indices = range(len(all_nodes))
    
    # track results
    results = []
    success = 0
    
    # export each node
    for idx in indices:
        # bounds check
        if idx < 0 or idx >= len(all_nodes):
            results.append({
                "index": idx,
                "success": False,
                "error": "Index out of bounds"
            })
            continue
            
        # get the node and export it
        node = all_nodes[idx]
        res = send_to_notion(node['path'], target_db)
        
        # track success
        if res.get('success'):
            success += 1
            
        # store result
        results.append({
            "index": idx,
            "title": node.get('title', 'Unknown'),
            **res
        })
    
    # return summary
    return {
        "success": success > 0,
        "total": len(results),
        "successful": success,
        "failed": len(results) - success,
        "results": results
    }

def make_db(title="My Knowledge Base", parent_id=None):
    # need client and parent page
    if not client:
        return {"success": False, "error": "No Notion token found"}
    
    if not parent_id:
        return {"success": False, "error": "Need parent page ID"}
    
    try:
        # define db structure
        props = {
            "Name": {"title": {}},  # required
            "Created": {"date": {}},
            "Tags": {"multi_select": {"options": []}},
            # maybe add status field for workflow
            "Status": {
                "select": {
                    "options": [
                        {"name": "Draft", "color": "yellow"},
                        {"name": "In Progress", "color": "orange"},
                        {"name": "Complete", "color": "green"}
                    ]
                }
            }
        }
        
        # create it!
        db = client.databases.create(
            parent={"type": "page_id", "page_id": parent_id},
            title=[{"type": "text", "text": {"content": title}}],
            properties=props
        )
        
        return {
            "success": True,
            "database_id": db["id"],
            "url": db["url"],
            "title": title
        }
        
    except APIResponseError as e:
        return {"success": False, "error": f"API error: {e.code} - {e.message}"}
    except Exception as e:
        return {"success": False, "error": f"Failed: {str(e)}"}

def check_setup():
    # list of issues found
    problems = []
    
    # check env vars
    if not token:
        problems.append("NOTION_TOKEN not set")
    
    if not db_id:
        problems.append("NOTION_DATABASE_ID not set")
    
    # test connection if possible
    if token and client:
        try:
            # simple API call to verify token works
            client.users.me()
        except APIResponseError as e:
            problems.append(f"Auth failed: {e.message}")
        except Exception as e:
            problems.append(f"Connection error: {str(e)}")
    
    # quick status report
    return {
        "configured": len(problems) == 0,
        "issues": problems,
        "token_set": bool(token),
        "database_set": bool(db_id)
    }
