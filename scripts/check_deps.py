#!/usr/bin/env python3
"""
Shared dependency checker for all skills.
Import this at the top of any script that needs external packages.

Usage in scripts:
    from check_deps import require
    require("google.genai", "google-genai")  # module_name, package_name
    require("matplotlib")  # same name for both
"""

import sys
import os

def get_install_command():
    """Get the appropriate install command based on environment."""
    # Try to find the skills root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skills_root = os.path.dirname(script_dir)
    
    # Check for requirements.txt
    requirements_path = os.path.join(skills_root, "requirements.txt")
    install_script = os.path.join(skills_root, "scripts", "install.sh")
    
    if os.path.exists(install_script):
        return f"./scripts/install.sh\n   Or: pip install -r requirements.txt"
    elif os.path.exists(requirements_path):
        return f"pip install -r {requirements_path}"
    else:
        return "pip install -r requirements.txt"

def require(module_name: str, package_name: str = None):
    """
    Check if a module is available, exit with helpful error if not.
    
    Args:
        module_name: The import name (e.g., "google.genai")
        package_name: The pip package name (e.g., "google-genai"). 
                      If None, uses module_name.
    """
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
    except ImportError:
        print(f"""
╭─────────────────────────────────────────────────────────────────╮
│  Missing Dependency: {package_name:<40} │
╰─────────────────────────────────────────────────────────────────╯

The package '{package_name}' is required but not installed.

To install all dependencies, run:

   {get_install_command()}

Or install just this package:

   pip install {package_name}

Note: Requires Python 3.10+ for google-genai package.
""", file=sys.stderr)
        sys.exit(1)

def require_all(dependencies: list):
    """
    Check multiple dependencies at once.
    
    Args:
        dependencies: List of tuples (module_name, package_name) or strings
    """
    missing = []
    
    for dep in dependencies:
        if isinstance(dep, tuple):
            module_name, package_name = dep
        else:
            module_name = package_name = dep
        
        try:
            __import__(module_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"""
╭─────────────────────────────────────────────────────────────────╮
│  Missing Dependencies                                           │
╰─────────────────────────────────────────────────────────────────╯

The following packages are required but not installed:
{chr(10).join(f'  • {pkg}' for pkg in missing)}

To install all dependencies, run:

   {get_install_command()}

Or install missing packages:

   pip install {' '.join(missing)}

Note: Requires Python 3.10+ for google-genai package.
""", file=sys.stderr)
        sys.exit(1)

# Quick check function for single imports
def check(module_name: str, package_name: str = None) -> bool:
    """
    Check if a module is available without exiting.
    Returns True if available, False otherwise.
    """
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

if __name__ == "__main__":
    # Test the dependency checker
    print("Testing dependency checker...")
    print(f"Install command: {get_install_command()}")
    print()
    
    # Test some common dependencies
    deps = [
        ("google.genai", "google-genai"),
        ("matplotlib", "matplotlib"),
        ("PIL", "Pillow"),
    ]
    
    for module, package in deps:
        status = "✓" if check(module) else "✗"
        print(f"  {status} {package}")
