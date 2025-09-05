#!/usr/bin/env python3
"""
Privateness Tools Console - Integrated Interface for NESS Network Tools
"""
import os
import sys
import cmd
import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class ToolCategory(Enum):
    KEY_MANAGEMENT = "Key Management"
    FILE_OPERATIONS = "File Operations"
    NETWORK = "Network Operations"
    BACKUP = "Backup & Restore"
    SYSTEM = "System Tools"

@dataclass
class ToolInfo:
    name: str
    description: str
    category: ToolCategory
    command: str
    args: List[str] = None

class PrivatenessConsole(cmd.Cmd):    
    intro = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                     PRIVATENESS TOOLS CONSOLE (v0.1)                         ║
    ║  A unified interface for NESS Network management and operations               ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    
    Type 'help' for available commands or 'help <command>' for command details.
    Type 'exit' to quit.
    """
    
    prompt = 'privateness> '
    
    # Define available tools
    tools = [
        # Key Management
        ToolInfo("key", "Key management utility", ToolCategory.KEY_MANAGEMENT, "key", 
                ["list [dirpath]", "show <keyfile>", "nvs <keyfile>", "worm <keyfile>", 
                 "pack <keyfiles> <encrypted_keyfile>", "unpack <encrypted_keyfile>"]),
        ToolInfo("keygen", "Generate new keys", ToolCategory.KEY_MANAGEMENT, "keygen",
                ["[key_type] [options]"]),
        
        # File Operations
        ToolInfo("ls", "List files in directory", ToolCategory.FILE_OPERATIONS, "ls", 
                ["[path] [options]"]),
        ToolInfo("cd", "Change directory", ToolCategory.FILE_OPERATIONS, "cd", 
                ["[directory]"]),
        ToolInfo("upload", "Upload files", ToolCategory.FILE_OPERATIONS, "upload",
                ["<local_path> [remote_path]"]),
        ToolInfo("download", "Download files", ToolCategory.FILE_OPERATIONS, "download",
                ["<remote_path> [local_path]"]),
        ToolInfo("mkdir", "Create directory", ToolCategory.FILE_OPERATIONS, "mkdir",
                ["<directory_name>"]),
        ToolInfo("rmdir", "Remove directory", ToolCategory.FILE_OPERATIONS, "rmdir",
                ["<directory_name>"]),
        ToolInfo("remove", "Remove files", ToolCategory.FILE_OPERATIONS, "remove",
                ["<file1> [file2 ...]"]),
        ToolInfo("move", "Move/rename files", ToolCategory.FILE_OPERATIONS, "move",
                ["<source> <destination>"]),
        ToolInfo("tree", "Display directory tree", ToolCategory.FILE_OPERATIONS, "tree",
                ["[directory] [depth]"]),
        
        # Backup & Restore
        ToolInfo("backup", "Backup operations", ToolCategory.BACKUP, "backup",
                ["seed", "address", "backup [filename]", "restore [filename]"]),
        
        # Network Operations
        ToolInfo("node", "Node management", ToolCategory.NETWORK, "node",
                ["info", "list", "add <node_url>", "remove <node_id>"]),
        ToolInfo("nodes-update", "Update node list", ToolCategory.NETWORK, "nodes-update",
                []),
        
        # System Tools
        ToolInfo("quota", "Check storage quota", ToolCategory.SYSTEM, "quota", []),
        ToolInfo("jobs", "Background jobs", ToolCategory.SYSTEM, "jobs", 
                ["list", "status <job_id>", "cancel <job_id>"]),
        ToolInfo("prng", "Pseudo-random number generator", ToolCategory.SYSTEM, "prng",
                ["<length> [encoding=hex|base64|int]"]),
    ]

    def __init__(self):
        super().__init__()
        self.categories = {cat.value: [] for cat in ToolCategory}
        for tool in self.tools:
            self.categories[tool.category.value].append(tool)
    
    def do_help(self, arg):
        """List available commands with usage patterns and descriptions."""
        if not arg:
            self.print_main_help()
        else:
            super().do_help(arg)
    
    def print_main_help(self):
        """Display help information in a categorized format."""
        print("\nAVAILABLE COMMANDS BY CATEGORY:")
        print("-" * 80)
        
        for category, tools in self.categories.items():
            if not tools:
                continue
                
            print(f"\n{category.upper()}:")
            print("-" * (len(category) + 1))
            
            for tool in sorted(tools, key=lambda x: x.name):
                args = " | ".join(tool.args) if tool.args else ""
                print(f"  {tool.name:12} {args}")
                print(f"  {'':14}{tool.description}")
        
        print("\nType 'help <command>' for detailed help on a specific command.")
    
    def do_shell(self, line):
        """Execute a shell command."""
        try:
            output = subprocess.check_output(line, shell=True, stderr=subprocess.STDOUT)
            print(output.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.output.decode('utf-8').strip()}")
    
    def do_exit(self, arg):
        """Exit the console."""
        print("Exiting Privateness Tools Console. Goodbye!")
        return True
    
    def emptyline(self):
        """Do nothing on empty input."""
        pass
    
    def default(self, line):
        """Handle unknown commands by trying to execute them as external tools."""
        cmd_parts = line.split()
        if not cmd_parts:
            return
            
        tool_name = cmd_parts[0]
        tool = next((t for t in self.tools if t.name == tool_name), None)
        
        if tool:
            try:
                # Check if the tool is a Python script
                script_path = f"{tool.command}.py"
                if os.path.exists(script_path):
                    # Execute the Python script with the current Python interpreter
                    args = [sys.executable, script_path] + cmd_parts[1:]
                    subprocess.run(args, check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
                else:
                    # Try to execute as a regular command
                    args = [tool.command] + cmd_parts[1:]
                    subprocess.run(args, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error executing {tool_name}: {e}")
                if hasattr(e, 'stderr') and e.stderr:
                    print(e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else e.stderr)
            except FileNotFoundError:
                print(f"Error: Could not find {script_path}")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
        else:
            print(f"Unknown command: {tool_name}. Type 'help' for available commands.")
    
    # Command completions
    def complete(self, text, state):
        """Handle command completion."""
        if not text:
            completions = [t.name for t in self.tools]
        else:
            completions = [t.name for t in self.tools if t.name.startswith(text)]
        
        if state < len(completions):
            return completions[state] + ' '
        return None

if __name__ == '__main__':
    try:
        # Set up the console
        console = PrivatenessConsole()
        
        # Handle command line arguments if provided
        if len(sys.argv) > 1:
            # Join arguments with spaces and process as a single command
            console.onecmd(' '.join(sys.argv[1:]))
        else:
            # Start interactive mode
            console.cmdloop()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
