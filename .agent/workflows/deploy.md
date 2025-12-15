---
description: Deploy the project by committing changes and triggering GitHub Actions
---

This workflow automates the deployment process. It prepares the documentation, commits all changes, and pushes to the main branch.
The push will trigger the `.github/workflows/release_pipeline.yml` on GitHub, which handles:
1.  Creating a GitHub Release/Tag (if version changed).
2.  Publishing to PyPI.
3.  Building and uploading Windows executable.

### Steps

1.  **Sync Documentation**: Ensure `README_PyPI.md` is up to date.
    ```bash
    uv run python scripts/publish.py --prepare-only
    ```

2.  **Git Add**: Stage all changes.
    ```bash
    git add .
    ```

3.  **Git Commit**: Commit the changes.
    - If you are just updating docs, use: `git commit -m "docs: update README"`
    - If you are releasing a new version, use: `git commit -m "chore: release v(version)"`
    ```bash
    git commit -m "chore: update documentation and prepare for deployment"
    ```

4.  **Git Push**: Push to origin to trigger the pipeline.
    // turbo
    ```bash
    git push origin main
    ```

5.  **Completion**: The GitHub Actions will now take over. You can check the progress on the GitHub Actions tab.
