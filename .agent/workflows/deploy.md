---
description: Deploy the project by committing changes and triggering GitHub Actions
---

This workflow automates the deployment process. It prepares the documentation, commits all changes, and pushes to the main branch.
The push will trigger the `.github/workflows/release_pipeline.yml` on GitHub, which handles:
1.  Creating a GitHub Release/Tag (if version changed).
2.  Publishing to PyPI.
3.  Building and uploading Windows executable.

### Steps

1.  **Bump Version**: Increment the patch version in `pyproject.toml`.
    ```bash
    uv run python scripts/bump_version.py
    ```

2.  **Sync Documentation**: Ensure `README_PyPI.md` is up to date (this MUST happen after version bump so docs reflect new version if needed, though mostly for content).
    ```bash
    uv run python scripts/publish.py --prepare-only
    ```

3.  **Git Add**: Stage all changes (pyproject.toml + READMEs).
    ```bash
    git add .
    ```

4.  **Git Commit**: Commit the changes.
    ```bash
    git commit -m "chore: bump version and update docs for release"
    ```

5.  **Git Push**: Push to origin to trigger the pipeline (which listens for pyproject.toml changes).
    // turbo
    ```bash
    git push origin main
    ```


5.  **Completion**: The GitHub Actions will now take over. You can check the progress on the GitHub Actions tab.
