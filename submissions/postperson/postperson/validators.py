from textual.validation import Validator, ValidationResult

from pathlib import Path
from urllib.parse import urlparse


class FilePathValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value:
            return self.failure("File path is required")
        if not value.endswith(".json"):
            return self.failure("File path must end with .json")

        path = Path(value)
        parent = path.parent

        if not parent.exists():
            return self.failure(f"Directory {parent} does not exist")

        return self.success()

def url_validator(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
