# tests/test_git_guardian.py
import pytest
import os
import re
import json
from pathlib import Path
from git import Repo
from unittest.mock import patch
from click.testing import CliRunner

from git_guardian import GitGuardianScanner, HookManager, Reporter, cli


@pytest.fixture
def temp_repo(tmp_path):
    # Create a temporary Git repository
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    repo = Repo.init(repo_path)

    # Create sample files
    safe_file = repo_path / "safe.txt"
    safe_file.write_text("This is a safe file")

    secret_file = repo_path / ".env"
    secret_file.write_text("API_KEY=1234567890abcdef")

    # Commit initial files
    repo.index.add([str(safe_file), str(secret_file)])
    repo.index.commit("Initial commit")
    return repo_path


@pytest.fixture
def runner():
    return CliRunner()


def test_scan_file_with_secret(tmp_path):
    # Setup
    test_file = tmp_path / "test.env"
    test_file.write_text("AWS_SECRET_ACCESS_KEY=AKIAEXAMPLEKEY")

    # Test
    scanner = GitGuardianScanner()
    results = scanner.scan_file(test_file)

    # Assert
    assert len(results) > 0
    assert any("AWS Secret Key" in result[0] for result in results)


def test_scan_file_without_secret(tmp_path):
    # Setup
    test_file = tmp_path / "safe.txt"
    test_file.write_text("Just normal text")

    # Test
    scanner = GitGuardianScanner()
    results = scanner.scan_file(test_file)

    # Assert
    assert len(results) == 0


def test_repo_scanning(temp_repo):
    # Setup
    scanner = GitGuardianScanner()

    # Test
    results = scanner.scan_repo(temp_repo)

    # Asert
    assert ".env" in results  # Use relative path
    assert "API Key" in [f[0] for f in results[".env"]]


def test_hook_installation(temp_repo):
    # Setup
    hook_manager = HookManager()

    # Test
    hook_manager.install_hook(repo_path=str(temp_repo))
    hook_file = Path(temp_repo) / ".git" / "hooks" / "pre-commit"

    # Assert
    assert hook_file.exists()
    assert "git-guardian scan --hook" in hook_file.read_text()


def test_cli_scan_command(temp_repo, runner):
    # Create uncommitted change
    (Path(temp_repo) / ".env").write_text("API_KEY=NEW_SECRET")

    # Test
    result = runner.invoke(cli, ["scan", str(temp_repo)])

    # Assert
    assert result.exit_code == 1
    assert "API Key" in result.output


def test_cli_clean_scan(tmp_path, runner):
    # Setup
    clean_repo = tmp_path / "clean_repo"
    clean_repo.mkdir()
    repo = Repo.init(clean_repo)
    (clean_repo / "README.md").write_text("No secrets here")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")

    # Tet
    result = runner.invoke(cli, ["scan", str(clean_repo)])

    # Assert
    assert result.exit_code == 0
    assert "No secrets found" in result.output


def test_custom_rules(tmp_path):
    # Setup
    custom_rule = {"name": "Test Pattern", "pattern": r"TEST-\d+"}
    config_file = tmp_path / ".gitguardianrc"
    config_file.write_text(json.dumps({"custom_rules": [custom_rule]}))

    # Create scanner with config path
    scanner = GitGuardianScanner()
    scanner.ignored_dirs = []
    scanner.config_path = config_file
    scanner.load_custom_rules()

    test_file = tmp_path / "test.txt"
    test_file.write_text("TEST-1234")

    # Test
    results = scanner.scan_file(test_file)

    # Assert
    assert any("Test Pattern" in result[0] for result in results)


def test_report_generation():
    # Setup
    test_data = {"file1.txt": [("API Key", "file1.txt", ["apikey=12345"])]}

    # Test CLI output
    cli_output = Reporter.generate_report(test_data, "cli")

    # Test JSON output
    with patch("builtins.print") as mock_print:
        Reporter.generate_report(test_data, "json")
        mock_print.assert_called_with(json.dumps(test_data, indent=2))


def test_ignored_directories(temp_repo):
    # Setup
    scanner = GitGuardianScanner()
    node_modules = temp_repo / "node_modules"
    node_modules.mkdir()
    (node_modules / "ignored.js").write_text("SECRET=123")

    # Test
    results = scanner.scan_repo(temp_repo)

    # Assert
    assert str(node_modules / "ignored.js") not in results


def test_large_file_handling(tmp_path):
    # Setup
    large_file = tmp_path / "large.bin"
    with open(large_file, "wb") as f:
        f.write(os.urandom(1024 * 1024))  # 1MB random file

    # Test
    scanner = GitGuardianScanner()
    results = scanner.scan_file(large_file)

    # Assert
    assert len(results) == 0, f"Found unexpected matches in binary file: {results}"


def test_binary_file_handling(tmp_path):
    # Setup
    binary_file = tmp_path / "binary"
    binary_file.write_bytes(b"\x00\x01\x02\x03")

    # Test
    scanner = GitGuardianScanner()
    results = scanner.scan_file(binary_file)

    # Assert
    assert len(results) == 0


if __name__ == "__main__":
    pytest.main()
