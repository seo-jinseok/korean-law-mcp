import os
import sys
import subprocess
import argparse

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def sync_readmes(dry_run=False):
    print(">>> Syncing README.md to README_PyPI.md...")
    readme = read_file("README.md")
    
    # Transformation Logic
    lines = readme.split('\n')
    new_lines = []
    
    skip_mode = False
    
    for line in lines:
        # Stop skipping if we hit the next section
        if skip_mode and line.startswith("## "):
            skip_mode = False
            
        # 1. Transform Installation to Quick Start
        if "## 🛠️ 설치 및 설정" in line:
            new_lines.append("## 🚀 빠른 시작 (Quick Start)")
            new_lines.append("")
            new_lines.append("이 패키지는 `uvx`를 사용하여 설치 없이 즉시 실행할 수 있습니다.")
            new_lines.append("")
            new_lines.append("```bash")
            new_lines.append("uvx korean-law-mcp")
            new_lines.append("```")
            new_lines.append("")
            new_lines.append("또는 `pip`로 설치할 수 있습니다:")
            new_lines.append("")
            new_lines.append("```bash")
            new_lines.append("pip install korean-law-mcp")
            new_lines.append("```")
            new_lines.append("")
            new_lines.append("### 필수 조건")
            new_lines.append("* **국가법령정보센터 Open API ID**가 필요합니다. ([회원가입 및 신청](https://www.law.go.kr/))")
            new_lines.append("* 실행 시 환경 변수 `OPEN_LAW_ID`를 설정해야 합니다.")
            new_lines.append("")
            skip_mode = True # Skip the original installation section
            continue
            
        # 2. Skip "배포 및 쉬운 사용 방법" as it's redundant for PyPI
        if "## 📦 배포 및 쉬운 사용 방법" in line:
            skip_mode = True
            continue

        # 3. Add link to GitHub at the end
        if not skip_mode:
            new_lines.append(line)

    # Append Developer Info
    new_lines.append("")
    new_lines.append("---")
    new_lines.append("")
    new_lines.append("> **개발자 정보**: 소스 코드 확인 및 기여는 [GitHub 저장소](https://github.com/seo-jinseok/korean-law-mcp)를 참고하세요.")

    content = "\n".join(new_lines).strip() + "\n"
    
    if dry_run:
        print("[Dry Run] Content to be written to README_PyPI.md:")
        print(content[:500] + "\n... (truncated)")
    else:
        write_file("README_PyPI.md", content)
        print("Updated README_PyPI.md")

def run_command(cmd, dry_run=False):
    print(f">>> Running: {cmd}")
    if dry_run:
        print("[Dry Run] Command skipped.")
        return
    
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Error executing command: {cmd}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Automate release process")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without making changes")
    parser.add_argument("--skip-pypi", action="store_true", help="Skip PyPI publish step")
    args = parser.parse_args()
    
    # 1. Sync READMEs
    sync_readmes(dry_run=args.dry_run)
    
    # 2. Git Operations
    run_command("git add README.md README_PyPI.md", dry_run=args.dry_run)
    # Check if there are changes to commit
    if not args.dry_run:
        status = subprocess.getoutput("git status --porcelain")
        if status:
            run_command('git commit -m "docs: sync readme and prepare for release"', dry_run=args.dry_run)
            run_command("git push origin main", dry_run=args.dry_run)
        else:
            print("No changes to commit.")
    else:
        print("[Dry Run] git commit and push")

    # 3. PyPI Publish
    if not args.skip_pypi:
        # Build
        run_command("uv build", dry_run=args.dry_run)
        # Publish
        run_command("uv publish", dry_run=args.dry_run)

if __name__ == "__main__":
    main()
