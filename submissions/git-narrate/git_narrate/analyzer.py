import git
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from collections import defaultdict

class RepoAnalyzer:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
    
    def analyze(self) -> Dict[str, Any]:
        """Perform complete repository analysis."""
        return {
            "commits": self._get_commits(),
            "branches": self._get_branches(),
            "tags": self._get_tags(),
            "contributors": self._get_contributors(),
            "repo_name": self._get_project_name_from_readme() or self.repo_path.name,
            "readme_content": self._get_readme_content()
        }
    
    def _get_commits(self) -> List[Dict[str, Any]]:
        """Extract commit history."""
        commits = []
        for commit in self.repo.iter_commits("--all"):
            changed_files = list(commit.stats.files.keys())
            
            # Get full content of changed files
            file_contents = {}
            for file_path in changed_files:
                try:
                    file_contents[file_path] = self.repo.git.show(f"{commit.hexsha}:{file_path}")
                except git.exc.GitCommandError:
                    # This can happen for deleted files, etc.
                    file_contents[file_path] = None

            commits.append({
                "sha": commit.hexsha,
                "author": commit.author.name,
                "email": commit.author.email,
                "date": datetime.fromtimestamp(commit.committed_date),
                "message": commit.message.strip(),
                "files_changed": len(changed_files),
                "insertions": commit.stats.total["insertions"],
                "deletions": commit.stats.total["deletions"],
                "is_merge": len(commit.parents) > 1,
                "file_contents": file_contents,
                "category": self._categorize_commit(commit.message.strip())
            })
        return commits

    def _categorize_commit(self, message: str) -> str:
        """Categorize commit based on its message."""
        message = message.lower()
        if message.startswith("feat"):
            return "feature"
        if message.startswith("fix"):
            return "fix"
        if message.startswith("docs"):
            return "documentation"
        if message.startswith("style"):
            return "style"
        if message.startswith("refactor"):
            return "refactor"
        if message.startswith("test"):
            return "test"
        if message.startswith("chore"):
            return "chore"
        return "other"
    
    def _get_branches(self) -> List[Dict[str, Any]]:
        """Get branch information."""
        branches = []
        for branch in self.repo.branches:
            branches.append({
                "name": branch.name,
                "commit": branch.commit.hexsha,
                "is_remote": branch.is_remote
            })
        return branches
    
    def _get_tags(self) -> List[Dict[str, Any]]:
        """Get tag information."""
        tags = []
        for tag in self.repo.tags:
            tags.append({
                "name": tag.name,
                "commit": tag.commit.hexsha,
                "date": datetime.fromtimestamp(tag.tag.tagged_date) if tag.tag else None
            })
        return tags
    
    def _get_contributors(self) -> Dict[str, Dict[str, Any]]:
        """Get contributor statistics."""
        contributors = defaultdict(lambda: {
            "commits": 0,
            "insertions": 0,
            "deletions": 0,
            "first_commit": None,
            "last_commit": None
        })
        
        for commit in self._get_commits():
            author = commit["author"]
            contributors[author]["commits"] += 1
            contributors[author]["insertions"] += commit["insertions"]
            contributors[author]["deletions"] += commit["deletions"]
            
            if not contributors[author]["first_commit"] or commit["date"] < contributors[author]["first_commit"]:
                contributors[author]["first_commit"] = commit["date"]
            if not contributors[author]["last_commit"] or commit["date"] > contributors[author]["last_commit"]:
                contributors[author]["last_commit"] = commit["date"]
        
        return dict(contributors)
    
    def _get_readme_content(self) -> str:
        """Extract content from README file if it exists."""
        readme_paths = [
            self.repo_path / "README.md",
            self.repo_path / "README.rst",
            self.repo_path / "README.txt",
            self.repo_path / "readme.md",
            self.repo_path / "readme.rst",
            self.repo_path / "readme.txt"
        ]
        
        for path in readme_paths:
            if path.exists() and path.is_file():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception:
                    continue
        
        return ""

    def _get_project_name_from_readme(self) -> str:
        """Extract project name from the first H1 heading in README.md."""
        readme = self._get_readme_content()
        if not readme:
            return ""
        
        lines = readme.split('\n')
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('# '):
                return stripped_line.lstrip('# ').strip()
        return ""
