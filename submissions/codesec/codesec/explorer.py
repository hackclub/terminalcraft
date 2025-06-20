from pathlib import Path
import ast
from typing import Dict, List, Set
from tree_sitter import Language, Parser
import networkx as nx

class CodeExplorer:
    """Code exploration and analysis functionality."""
    
    def __init__(self):
        self.parser = self._setup_parser()
        self.call_graph = nx.DiGraph()
        
    def _setup_parser(self) -> Parser:
        """Set up the tree-sitter parser."""
        # TODO: Build and load language support
        parser = Parser()
        # parser.set_language(Language('build/my-languages.so', 'python'))
        return parser
        
    def explore_directory(self, path: Path) -> Dict:
        """Explore a directory and generate code insights."""
        files = list(path.rglob('*'))
        insights = {
            'total_files': len(files),
            'file_types': self._count_file_types(files),
            'call_graph': self._generate_call_graph(files),
            'function_index': self._index_functions(files)
        }
        return insights
        
    def _count_file_types(self, files: List[Path]) -> Dict[str, int]:
        """Count files by their extension."""
        counts = {}
        for file in files:
            if file.is_file():
                ext = file.suffix
                counts[ext] = counts.get(ext, 0) + 1
        return counts
        
    def _generate_call_graph(self, files: List[Path]) -> nx.DiGraph:
        """Generate a call graph of the codebase."""
        self.call_graph.clear()
        
        for file in files:
            if file.suffix == '.py':
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                        self._analyze_calls(tree, str(file))
                except:
                    continue
                    
        return self.call_graph
        
    def _analyze_calls(self, tree: ast.AST, filename: str):
        """Analyze function calls in an AST."""
        class CallVisitor(ast.NodeVisitor):
            def __init__(self, explorer):
                self.current_function = None
                self.explorer = explorer
                
            def visit_FunctionDef(self, node):
                prev_function = self.current_function
                self.current_function = f"{filename}:{node.name}"
                self.explorer.call_graph.add_node(self.current_function)
                self.generic_visit(node)
                self.current_function = prev_function
                
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name) and self.current_function:
                    called = node.func.id
                    self.explorer.call_graph.add_edge(
                        self.current_function,
                        f"{filename}:{called}"
                    )
                self.generic_visit(node)
                
        visitor = CallVisitor(self)
        visitor.visit(tree)
        
    def _index_functions(self, files: List[Path]) -> Dict[str, List[Dict]]:
        """Create an index of functions in the codebase."""
        index = {}
        
        for file in files:
            if file.suffix == '.py':
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                        functions = self._extract_functions(tree)
                        if functions:
                            index[str(file)] = functions
                except:
                    continue
                    
        return index
        
    def _extract_functions(self, tree: ast.AST) -> List[Dict]:
        """Extract function definitions from an AST."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func = {
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'docstring': ast.get_docstring(node)
                }
                functions.append(func)
                
        return functions
        
    def fuzzy_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Perform fuzzy search across the codebase."""
        # TODO: Implement fuzzy search using rapidfuzz or similar
        pass
        
    def generate_ascii_graph(self) -> str:
        """Generate an ASCII representation of the call graph."""
        # TODO: Implement ASCII graph generation
        pass
