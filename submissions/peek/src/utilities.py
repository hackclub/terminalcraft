from referenceVariables import BINARY_FILE_EXTENSIONS, TEXT_FILE_EXTENSIONS

from charset_normalizer import from_bytes, is_binary
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound

def getLanguageForFilename(filename: str, false_return="text"):
    try:
        return get_lexer_for_filename(filename)
    except ClassNotFound:
        return false_return

def stripEmptyTrailingLines(string):
    lines = str.splitlines(string, keepends=True)
    while lines and lines[-1].strip() == "":
        lines.pop()
    return "".join(lines)

def getLines(string: str, max_lines: int):
    lines = string.splitlines(keepends=True)
    i = 0
    result = ""
    while i < max_lines:
        try:
            result += lines[i]
        except IndexError:
            break
        i += 1
    return result

def readChunk(path, max_bytes: int=8192):
    try:
        with path.open('rb') as file:
            return file.read(max_bytes)
    except Exception:
        return b''

def stringChunk(chunk):
    # never had an issue happen but just in case yk
    try:
        string = str(from_bytes(chunk).best())
        if not string:
            raise ValueError("Chunk seems not to be readable")
        return string
    except Exception:
        return "[Binary or unreadable file]"

def isBinary(chunk, path, accuracy: str = "high"):
    filename = path.name
    file_extension = path.suffix.lower().lstrip('.')

    if file_extension in BINARY_FILE_EXTENSIONS:
        return True
    if file_extension in TEXT_FILE_EXTENSIONS:
        return False
    
    if accuracy == "high":
        if (getLanguageForFilename(filename, false_return="_fail") != "_fail"):
            return False
        else: return is_binary(chunk)
    
    return True