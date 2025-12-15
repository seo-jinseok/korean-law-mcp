import re
import sys

def bump_version(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find version = "x.y.z"
    pattern = r'(version\s*=\s*")(\d+)\.(\d+)\.(\d+)(")'
    match = re.search(pattern, content)
    
    if not match:
        print("Error: Could not find version string in pyproject.toml")
        sys.exit(1)
        
    prefix = match.group(1)
    major = int(match.group(2))
    minor = int(match.group(3))
    patch = int(match.group(4))
    suffix = match.group(5)
    
    new_patch = patch + 1
    new_version_str = f"{major}.{minor}.{new_patch}"
    
    print(f"Bumping version: {major}.{minor}.{patch} -> {new_version_str}")
    
    new_content = re.sub(pattern, f"{prefix}{new_version_str}{suffix}", content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    return new_version_str

if __name__ == "__main__":
    bump_version("pyproject.toml")
