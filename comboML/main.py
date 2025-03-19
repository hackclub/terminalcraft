import sys
from .app import ComboMLApp

def main():
    if len(sys.argv) != 2:
        print("Usage: comboML <filepath>")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    app = ComboMLApp(dataset_path)
    app.run()
