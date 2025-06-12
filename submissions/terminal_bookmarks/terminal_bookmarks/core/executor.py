import os
import sys
import shlex
import subprocess
from datetime import datetime, UTC
from typing import Optional, Dict, List, Tuple
from pathlib import Path
from uuid import UUID
import platform
import re
import time

from ..utils.exceptions import (
    ExecutionError,
    ValidationError,
    SecurityError,
    DependencyError,
    ContextError,
    PlatformError
)
from .models import Bookmark, ExecutionContext, ExecutionResult
from ..utils.platform import Platform, get_platform

class CommandExecutor:
    """Handles secure command execution and environment management."""
    
    DANGEROUS_PATTERNS = [
        "rm -rf", "deltree", "format",
        ">", "2>", 
        "|", 
        "sudo", "su" 
    ]
    
    def __init__(self, sandbox_mode: bool = False):
        self.sandbox_mode = sandbox_mode
        self.platform = get_platform()
        if self.platform == Platform.WINDOWS:
            self.shell = os.environ.get('COMSPEC', r'C:\Windows\System32\cmd.exe')
            self.shell_args = ['/c']
        else:
            self.shell = os.environ.get('SHELL', '/bin/sh')
            self.shell_args = ['-c']

    def execute_bookmark(self, bookmark: Bookmark, context: Optional[ExecutionContext] = None) -> ExecutionResult:
        """Execute a bookmarked command with safety checks."""
        if not context:
            context = ExecutionContext()

        try:
            final_command = self._prepare_command(bookmark)
            if context.command_args:
                final_command = f"{final_command} {' '.join(context.command_args)}"
            bookmark_platform = bookmark.get_platform()
            if bookmark_platform and bookmark_platform != self.platform:
                if not (self.platform == Platform.WINDOWS and 
                       bookmark_platform == Platform.LINUX and 
                       self._is_translatable_command(bookmark.command)):
                    raise PlatformError(
                        f"This bookmark is specific to {bookmark_platform.value} "
                        f"but current platform is {self.platform.value}"
                    )

            if self.sandbox_mode:
                return self._sandbox_execute(final_command)
            try:
                start_time = time.time()
                if not os.path.exists(self.shell):
                    raise ExecutionError(f"Shell not found: {self.shell}")
                if self.platform == Platform.WINDOWS:
                    args = [self.shell, '/c', final_command]
                else:
                    args = [self.shell, '-c', final_command]
                
                process = subprocess.run(
                    args,
                    shell=False,  
                    capture_output=context.capture_output,
                    text=True,
                    timeout=context.timeout,
                    env=context.env_vars or os.environ.copy()
                )
                
                duration = time.time() - start_time
                
                return ExecutionResult(
                    success=(process.returncode == 0),
                    command=final_command,
                    output=process.stdout or '',
                    error=process.stderr or '',
                    return_code=process.returncode,
                    duration=duration,
                    timestamp=datetime.now(UTC)
                )
                
            except FileNotFoundError as e:
                raise ExecutionError(f"Command execution failed: {str(e)}")
            except subprocess.TimeoutExpired as e:
                raise ExecutionError(f"Command timed out after {context.timeout} seconds")
            except Exception as e:
                if isinstance(e, PlatformError):  
                    raise
                raise ExecutionError(f"Failed to execute command: {str(e)}")
                
        except Exception as e:
            if isinstance(e, PlatformError):  
                raise
            raise ExecutionError(f"Execution failed: {str(e)}")
    
    def _prepare_command(self, bookmark: Bookmark) -> str:
        """Prepare command for execution on current platform."""
        command = bookmark.command
        if self.platform == Platform.WINDOWS:
            command = command.replace('/', '\\')
            translations = {
                'ls': 'dir',
                'rm': 'del',
                'cp': 'copy',
                'mv': 'move',
                'cat': 'type',
                'clear': 'cls',
            }
            
            for unix_cmd, win_cmd in translations.items():
                command = re.sub(f"\\b{unix_cmd}\\b", win_cmd, command)
        variables = {
            '{date}': datetime.now().strftime('%Y-%m-%d'),
            '{time}': datetime.now().strftime('%H:%M:%S'),
            '{platform}': self.platform.value,
        }
        
        for var, value in variables.items():
            command = command.replace(var, value)
        
        return command
    
    def _validate_context(self, bookmark: Bookmark, context: Optional[ExecutionContext]):
        """Validate execution context requirements."""
        if not context:
            return
        if bookmark.working_dir:
            if not os.path.isdir(bookmark.working_dir):
                raise ContextError(f"Required directory not found: {bookmark.working_dir}")
        if bookmark.platform != "all" and bookmark.platform != self.platform:
            raise ContextError(
                f"Command is not compatible with {self.platform.value} (requires {bookmark.platform})"
            )
        if context.check_dependencies and bookmark.dependencies:
            missing = self._check_dependencies(bookmark.dependencies)
            if missing:
                raise DependencyError(f"Missing dependencies: {', '.join(missing)}")
    
    def _is_dangerous(self, command: str) -> bool:
        """Check if command contains dangerous patterns."""
        command_lower = command.lower()
        if any(pattern.lower() in command_lower for pattern in self.DANGEROUS_PATTERNS):
            raise SecurityError(
                "This command may be dangerous. Use --force to execute anyway."
            )
        return False
    
    def _check_dependencies(self, dependencies: List[str]) -> List[str]:
        """Check for missing command dependencies."""
        missing = []
        for dep in dependencies:
            if self.platform == Platform.WINDOWS:
                result = subprocess.run(
                    ["where", dep], 
                    capture_output=True, 
                    text=True
                )
            else:
                result = subprocess.run(
                    ["which", dep], 
                    capture_output=True, 
                    text=True
                )
            if result.returncode != 0:
                missing.append(dep)
        return missing
    
    def _sandbox_execute(self, command: str) -> ExecutionResult:
        """Simulate command execution in sandbox mode."""
        return ExecutionResult(
            success=True,
            command=command,
            output=f"[SANDBOX] Would execute: {command}",
            error="",
            return_code=0,
            duration=0,
            timestamp=datetime.now()
        )

    def _is_translatable_command(self, command: str) -> bool:
        """Check if a Linux command can be translated to Windows."""
        translatable_commands = {
            'ls', 'rm', 'cp', 'mv', 'cat', 'clear',
            'pwd', 'touch', 'mkdir', 'rmdir'
        }
        main_command = command.strip().split()[0]
        
        return main_command in translatable_commands 