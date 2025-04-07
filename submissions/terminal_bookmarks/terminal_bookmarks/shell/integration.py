from pathlib import Path
from typing import List, Dict
import platform
from ..utils.exceptions import ShellIntegrationError

class ShellIntegration:
    """Handles shell integration and completion scripts."""
    
    SHELL_TEMPLATES = {
        'bash': """
alias tbm='{executable}'
_tbm_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    case "$prev" in
        "tbm")
            COMPREPLY=( $(compgen -W "add list search run delete" -- "$cur") )
            ;;
        "run"|"delete")
            COMPREPLY=( $(tbm --complete bookmark_ids) )
            ;;
        *)
            COMPREPLY=()
            ;;
    esac
}
complete -F _tbm_completion tbm
""",
        'zsh': """
alias tbm='{executable}'
_tbm() {
    local -a commands
    commands=(
        'add:Add a new bookmark'
        'list:List all bookmarks'
        'search:Search bookmarks'
        'run:Execute a bookmark'
        'delete:Delete a bookmark'
    )
    
    _arguments -C \\
        "1: :->cmds" \\
        "*::arg:->args"
    
    case "$state" in
        cmds)
            _describe "command" commands
            ;;
        args)
            case $line[1] in
                run|delete)
                    local -a bookmark_ids
                    bookmark_ids=($(tbm --complete bookmark_ids))
                    _describe "bookmarks" bookmark_ids
                    ;;
            esac
            ;;
    esac
}
compdef _tbm tbm
""",
        'powershell': """
Set-Alias -Name tbm -Value '{executable}'
Register-ArgumentCompleter -Native -CommandName tbm -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    
    $commands = @('add', 'list', 'search', 'run', 'delete')
    
    if ($commandAst.CommandElements.Count -eq 2) {
        $commands | Where-Object {
            $_ -like "$wordToComplete*"
        } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new(
                $_,
                $_,
                'ParameterValue',
                $_
            )
        }
    }
    elseif ($commandAst.CommandElements.Count -gt 2) {
        $cmd = $commandAst.CommandElements[1].Value
        if ($cmd -in @('run', 'delete')) {
            $bookmarkIds = tbm --complete bookmark_ids
            $bookmarkIds | Where-Object {
                $_ -like "$wordToComplete*"
            } | ForEach-Object {
                [System.Management.Automation.CompletionResult]::new(
                    $_,
                    $_,
                    'ParameterValue',
                    $_
                )
            }
        }
    }
}
"""
    }
    
    def __init__(self):
        self.os_type = platform.system().lower()
        
    def generate_shell_script(self, shell_type: str, executable_path: str) -> str:
        """Generate shell integration script."""
        if shell_type not in self.SHELL_TEMPLATES:
            raise ValueError(f"Unsupported shell: {shell_type}")
            
        return self.SHELL_TEMPLATES[shell_type].format(
            executable=executable_path
        )
    
    def install_shell_integration(self, shell_type: str):
        """Install shell integration for the specified shell."""
        try:
            if shell_type not in self.SHELL_TEMPLATES:
                raise ValueError(f"Unsupported shell: {shell_type}")
            config_file = self._get_shell_config_file(shell_type)
            script = self.generate_shell_script(
                shell_type,
                sys.executable
            )
            if config_file.exists():
                backup_file = config_file.with_suffix('.bak')
                config_file.rename(backup_file)
            with config_file.open('a') as f:
                f.write("\n" + script + "\n")
            
        except Exception as e:
            raise ShellIntegrationError(f"Shell integration failed: {str(e)}")
    
    def _get_shell_config_file(self, shell_type: str) -> Path:
        """Get the appropriate config file path for the shell."""
        home = Path.home()
        
        if shell_type == 'bash':
            return home / '.bashrc'
        elif shell_type == 'zsh':
            return home / '.zshrc'
        elif shell_type == 'powershell':
            if self.os_type == 'windows':
                return home / 'Documents' / 'WindowsPowerShell' / 'Microsoft.PowerShell_profile.ps1'
            return home / '.config' / 'powershell' / 'Microsoft.PowerShell_profile.ps1'
        
        raise ValueError(f"Unsupported shell: {shell_type}") 