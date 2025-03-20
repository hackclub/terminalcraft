# git_guardian/hook_manager.py
import platform
from pathlib import Path
from git import Repo
import click


class HookManager:
    @staticmethod
    def install_hook(repo_path: str = ".", hook_type: str = "pre-commit"):
        hook_content = """#!/bin/sh
git-guardian scan --hook
exit $?
        """
        try:
            repo = Repo(repo_path)
            hook_dir = Path(repo.git_dir) / "hooks"
            hook_dir.mkdir(exist_ok=True, parents=True)
            hook_path = hook_dir / hook_type

            # Write hook content
            hook_path.write_text(hook_content)

            # Make hook executable (Unix-like systems)
            if platform.system() != "Windows":
                hook_path.chmod(0o755)

            click.echo(f"✅ {hook_type} hook installed successfully")
        except Exception as e:
            click.echo(f"❌ Failed to install hook: {str(e)}")
            raise
