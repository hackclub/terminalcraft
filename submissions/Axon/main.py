#!/usr/bin/env python3
import argparse
import sys
import os
from core import node_manager, linker, search, trail, ask, mindmap, export, planner, heatmap
from utils.file_utils import app_path

# TODO: Add config file support
# TODO: Add color output option

VERSION = "0.0.1"  # bump this when making significant changes

def setup_parsers():
    # main parser
    parser = argparse.ArgumentParser(
        description="SynapNode CLI - Personal knowledge management system",
        epilog="Use 'python main.py <command> --help' for more info on a command"
    )
    
    # add version info
    parser.add_argument('--version', action='version', version=f'SynapNode v{VERSION}')
    
    # setup subcommands
    cmd_parsers = parser.add_subparsers(dest="cmd")
    
    # create command
    new_parser = cmd_parsers.add_parser("create", help="Create a new knowledge node")
    new_parser.add_argument("title", help="Title for the new node")
    
    # link command
    link_parser = cmd_parsers.add_parser("link", help="Link two knowledge nodes")
    link_parser.add_argument("source", help="Source node title")
    link_parser.add_argument("target", help="Target node title")
    
    # ask command
    ask_parser = cmd_parsers.add_parser("ask", help="Ask questions about your knowledge")
    ask_parser.add_argument("question", help="Your question")
    
    # search command
    search_parser = cmd_parsers.add_parser("search", help="Search your knowledge nodes")
    search_parser.add_argument("query", help="Search query")
    
    # trail command
    trail_parser = cmd_parsers.add_parser("trail", help="Show connection trail for a node")
    trail_parser.add_argument("node_title", help="Node to start from")
    
    # mindmap command
    map_parser = cmd_parsers.add_parser("mindmap", help="Visualize knowledge connections")
    map_parser.add_argument("--node", help="Starting node (default: most connected node)")
    map_parser.add_argument("--all", action="store_true", help="Show all connections")
    map_parser.add_argument("--depth", type=int, default=3, help="Max depth (default: 3)")
    map_parser.add_argument("--analyze", action="store_true", help="AI analysis of network")
    map_parser.add_argument("--suggest", action="store_true", help="Get AI connection suggestions")
    map_parser.add_argument("--learn", metavar="TOPIC", help="Generate learning path for topic")
    
    # heatmap command
    heatmap_parser = cmd_parsers.add_parser("heatmap", help="Show knowledge domain distribution")
    heatmap_parser.add_argument("--update", action="store_true", help="Force update all domains")
    
    # export command
    exp_parser = cmd_parsers.add_parser("export", help="Export notes to Notion")
    exp_parser.add_argument("--note", type=int, help="Export specific note by index")
    exp_parser.add_argument("--all", action="store_true", help="Export all notes")
    exp_parser.add_argument("--indices", nargs='+', type=int, help="Export specific notes by indices")
    exp_parser.add_argument("--database", metavar="DB_ID", help="Custom Notion database ID")
    exp_parser.add_argument("--check", action="store_true", help="Check Notion setup")
    exp_parser.add_argument("--create-db", metavar="TITLE", help="Create new Notion database")
    exp_parser.add_argument("--parent-page", metavar="PAGE_ID", help="Parent page ID for new database")
    
    save_ctx_parser = cmd_parsers.add_parser("save-context", help="Save what you are currently working on")
    save_ctx_parser.add_argument("note", help="Describe your current context briefly")

    cmd_parsers.add_parser("restore-context", help="Load your last saved context")
    
    # plan command
    plan_parser = cmd_parsers.add_parser("plan", help="Generate an action plan from your idea")
    plan_parser.add_argument("topic", help="Topic or idea to plan")
    plan_parser.add_argument("--save", action="store_true", help="Save the plan as a knowledge node")
    plan_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    return parser

def handle_create(args):
    node_manager.create_node(args.title)

def handle_link(args):
    linker.link_nodes(args.source, args.target)

def handle_ask(args):
    answer = ask.ask(args.question)
    print(answer)

def handle_search(args):
    search.semantic_search(args.query)

def handle_trail(args):
    trail.show_trail(args.node_title)

def handle_mindmap(args):
    # build params
    params = {
        "node_name": args.node,
        "show_all": args.all,
        "max_depth": args.depth,
        "ai_analysis": args.analyze,
        "suggest_connections": args.suggest,
        "learning_path": args.learn
    }
    
    # generate and display
    output = mindmap.generate_mindmap(**params)
    print(output)

def handle_heatmap(args):
    """Generate and display a knowledge domain heatmap"""
    # Force update all domains if requested
    if args.update:
        from core.heatmap import update_all_domains
        updated = update_all_domains(force=True)
        print(f"Updated domains for {updated} nodes")
    
    # Generate the heatmap
    output = heatmap.make_heatmap()
    print(output)
    
    return 0

def handle_export(args):
    if args.check:
        # verify configuration
        status = export.check_setup()
        
        print("\n--- Notion Configuration ---")
        print(f"Status: {'OK' if status['configured'] else 'Not Configured'}")
        print(f"API Token: {'✓ Set' if status['token_set'] else '✗ Missing'}")
        print(f"Database: {'✓ Set' if status['database_set'] else '✗ Missing'}")
        
        if status['issues']:
            print("\nIssues Found:")
            for problem in status['issues']:
                print(f"  • {problem}")
        else:
            print("\nEverything looks good!")
    
    elif args.create_db:
        # need parent page ID
        if not args.parent_page:
            print("Error: Missing --parent-page parameter")
            print("Hint: You need to provide a Notion parent page ID")
            return 1
            
        # create database
        result = export.make_db(args.create_db, args.parent_page)
        
        if result['success']:
            print(f"\nDatabase created: {result['title']}")
            print(f"ID: {result['database_id']}")
            print(f"URL: {result['url']}")
            print("\nAdd this to your .env file:")
            print(f"NOTION_DATABASE_ID={result['database_id']}")
        else:
            print(f"\nFailed: {result['error']}")
            return 1
    
    elif args.note is not None:
        # get nodes
        nodes = node_manager.list_nodes()
        
        # check index
        if not nodes:
            print("No nodes found")
            return 1
            
        if args.note < 0 or args.note >= len(nodes):
            print(f"Error: Invalid note index {args.note}")
            print(f"Valid range: 0-{len(nodes)-1}")
            return 1
            
        # get the node and export
        node = nodes[args.note]
        result = export.send_to_notion(node['path'], args.database)
        
        if result['success']:
            print(f"\nExported: {result['title']}")
            print(f"URL: {result['url']}")
        else:
            print(f"\nExport failed: {result['error']}")
            return 1
    
    elif args.all:
        # export everything
        result = export.batch_export(database_id=args.database)
        
        # show results
        print(f"\n--- Export Results ---")
        print(f"Total: {result['total']}")
        print(f"Success: {result['successful']}")
        print(f"Failed: {result['failed']}")
        
        if result['results']:
            print("\nDetails:")
            for item in result['results']:
                icon = "✓" if item['success'] else "✗"
                print(f"  {icon} {item['title']}")
                if not item['success']:
                    print(f"    Error: {item['error']}")
    
    elif args.indices:
        # export specific indices
        result = export.batch_export(args.indices, args.database)
        
        # show results
        print(f"\n--- Export Results ---")
        print(f"Total: {result['total']}")
        print(f"Success: {result['successful']}")
        print(f"Failed: {result['failed']}")
        
        if result['results']:
            print("\nDetails:")
            for item in result['results']:
                icon = "✓" if item['success'] else "✗"
                print(f"  {icon} {item['title']}")
                if not item['success']:
                    print(f"    Error: {item['error']}")
    
    else:
        # show available notes
        nodes = node_manager.list_nodes()
        
        if not nodes:
            print("No notes found")
            return 1
            
        print("\n--- Available Notes ---")
        for i, node in enumerate(nodes):
            title = node.get('title', 'Untitled')
            date = node.get('created', 'Unknown date')
            
            # just show date part
            if len(date) > 10:
                date = date[:10]
                
            print(f"{i}: {title} ({date})")
            
        print("\nTip: Use --note INDEX to export a specific note")
        print("     Use --all to export everything")
    
    return 0

def handle_save_context(args):
    if args.note:
        with open(os.path.join(app_path, 'ctx.save'), 'w') as f:
            f.write(args.note)
        print("Current context saved successfully, Come back soon!")

def handle_load_context(_):
    with open(os.path.join(app_path, 'ctx.save'), 'r') as f:
        print(f.read())

def handle_plan(args):
    """Generate and display an action plan"""
    # Generate the plan
    plan_output = planner.create_plan(args.topic)
    
    # Display the plan
    print(plan_output)
    
    # Save the plan if requested
    if args.save:
        file_path = planner.save_as_node(args.topic, plan_output)
        print(f"\nPlan saved to: {file_path}")
    
    return 0

def main():
    # setup argument parser
    parser = setup_parsers()
    
    # parse arguments
    args = parser.parse_args()
    
    # no command specified?
    if not args.cmd:
        parser.print_help()
        return 0
    
    # command handlers - using a dict is cleaner than a big if/elif chain
    handlers = {
        "create": handle_create,
        "link": handle_link,
        "ask": handle_ask,
        "search": handle_search,
        "trail": handle_trail,
        "mindmap": handle_mindmap,
        "export": handle_export,
        "save-context": handle_save_context,
        "restore-context": handle_load_context,
        "plan": handle_plan,
        "heatmap": handle_heatmap,
    }
    
    # dispatch to appropriate handler
    if args.cmd in handlers:
        try:
            return handlers[args.cmd](args) or 0
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return 130  # standard exit code for SIGINT
        except Exception as e:
            print(f"Error: {str(e)}")
            return 1
    else:
        # shouldn't happen with argparse, but just in case
        print(f"Unknown command: {args.cmd}")
        parser.print_help()
        return 1

# script entry point
if __name__ == "__main__":
    sys.exit(main())
