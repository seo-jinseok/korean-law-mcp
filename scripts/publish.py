import os
import sys
import subprocess
import argparse
import shutil
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def sync_readmes(dry_run=False):
    print(">>> Syncing README.md to README_PyPI.md...")
    readme = read_file("README.md")
    
    # Since the new README is designed to be compatible with both GitHub and PyPI,
    # we can just copy it. We might want to append development info.
    
    new_lines = []
    lines = readme.split('\n')
    
    for line in lines:
        new_lines.append(line)

    # Append Developer Info for PyPI specifically if needed, or keeping it identical is also fine.
    # The new README already has a "Developer" section. 
    # Let's add a small note at the bottom for PyPI users to find the repo.
    
    new_lines.append("")
    new_lines.append("---")
    new_lines.append("")
    new_lines.append("> **GitHub 저장소**: 더 자세한 정보나 소스 코드는 [GitHub](https://github.com/seo-jinseok/korean-law-mcp)에서 확인하세요.")

    content = "\n".join(new_lines).strip() + "\n"
    
    if dry_run:
        print("[Dry Run] Content to be written to README_PyPI.md:")
        print(content[:500] + "\n... (truncated)")
    else:
        write_file("README_PyPI.md", content)
        print("Updated README_PyPI.md")

def run_command(cmd, dry_run=False, ignore_errors=False):
    print(f">>> Running: {cmd}")
    if dry_run:
        print("[Dry Run] Command skipped.")
        return
    
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        if ignore_errors:
            print(f"Warning: Command '{cmd}' failed, but continuing.")
        else:
            print(f"Error executing command: {cmd}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Automate release process")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without making changes")
    parser.add_argument("--skip-pypi", action="store_true", help="Skip PyPI publish step")
    parser.add_argument("--prepare-only", action="store_true", help="Only sync READMEs, skip Git and Publish")
    args = parser.parse_args()
    
    # 1. Sync READMEs
    sync_readmes(dry_run=args.dry_run)
    
    if args.prepare_only:
        print(">>> Prepare only mode. Exiting.")
        return
    
    # 2. Git Operations
    run_command("git add README.md README_PyPI.md", dry_run=args.dry_run)
    # Check if there are changes to commit
    if not args.dry_run:
        # Try to commit, but ignore error if nothing to commit
        run_command('git commit -m "docs: sync readme and prepare for release"', dry_run=args.dry_run, ignore_errors=True)
        run_command("git push origin main", dry_run=args.dry_run, ignore_errors=True)
    else:
        print("[Dry Run] git commit and push")

    # 3. PyPI Publish
    if not args.skip_pypi:
        # Check for token
        # Common variable names: UV_PUBLISH_TOKEN, PYPI_TOKEN, or user typo PYPL_TOKEN
        token = os.getenv("UV_PUBLISH_TOKEN") or os.getenv("PYPI_TOKEN") or os.getenv("PYPL_TOKEN")
        
        if not token:
             print("Warning: UV_PUBLISH_TOKEN, PYPI_TOKEN, or PYPL_TOKEN not found in environment. You may need to enter credentials manually.")
             
        # Clean dist directory to avoid uploading old versions
        if os.path.exists("dist"):
            print(">>> Cleaning dist directory...")
            shutil.rmtree("dist")

        # Build
        run_command("uv build", dry_run=args.dry_run)
        
        # Publish
        # Force set UV_PUBLISH_TOKEN if we found a fallback
        if token and not os.getenv("UV_PUBLISH_TOKEN"):
            os.environ["UV_PUBLISH_TOKEN"] = token
            
        run_command("uv publish", dry_run=args.dry_run)

if __name__ == "__main__":
    main()
