import os
import shutil
import subprocess
from pathlib import Path

MARKETPLACE_ROOT = Path("./.skills-marketplace")

def setup_marketplace():
    """Initialize the marketplace directory and agent-shielding .gitignore."""
    if not MARKETPLACE_ROOT.exists():
        MARKETPLACE_ROOT.mkdir(parents=True, exist_ok=True)
    
    gitignore_path = MARKETPLACE_ROOT / ".gitignore"
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            f.write("*\n")

def parse_github_url(url):
    """Extract owner and repo name from a GitHub URL."""
    url = url.rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    
    parts = url.split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL format. Expected: https://github.com/owner/repo")
    
    owner = parts[-2]
    repo = parts[-1]
    return owner, repo

def add_skill(url, full=False):
    """Retrieve skills from a github repo."""
    try:
        owner, repo = parse_github_url(url)
        target_name = f"{owner}-{repo}"
        target_path = MARKETPLACE_ROOT / target_name
        
        if target_path.exists():
            print(f"Error: {target_name} already exists in marketplace. Use 'sync' to update.")
            return

        print(f"Adding {target_name}...")
        target_path.mkdir(parents=True, exist_ok=True)
        
        subprocess.run(["git", "init"], cwd=target_path, capture_output=True, check=True)
        subprocess.run(["git", "remote", "add", "origin", url], cwd=target_path, capture_output=True, check=True)
        
        if not full:
            subprocess.run(["git", "config", "core.sparseCheckout", "true"], cwd=target_path, capture_output=True, check=True)
            sparse_file = target_path / ".git" / "info" / "sparse-checkout"
            with open(sparse_file, "w") as f:
                f.write("skills/\n")
        
        print("Fetching content...")
        # Get the default branch or common ones
        branch = "main"

        # Query remote for the default branch to avoid trial-and-error
        res = subprocess.run(["git", "ls-remote", "--symref", "origin", "HEAD"], cwd=target_path, capture_output=True, text=True, check=True)
        for line in res.stdout.splitlines():
            if line.startswith("ref: refs/heads/"):
                branch = line.split("\t")[0].replace("ref: refs/heads/", "").strip()
                break

        if branch not in ["main", "master"]:
            print(f"Warning: Default branch is '{branch}' which is neither 'main' nor 'master'.")

        subprocess.run(["git", "fetch", "--depth", "1", "origin", branch], cwd=target_path, check=True, capture_output=True)
        
        # Reset to the fetched branch to establish tracking
        subprocess.run(["git", "reset", "--hard", f"origin/{branch}"], cwd=target_path, check=True, capture_output=True)
        subprocess.run(["git", "branch", "-m", branch], cwd=target_path, capture_output=True)
        subprocess.run(["git", "branch", "--set-upstream-to", f"origin/{branch}", branch], cwd=target_path, capture_output=True)
        
        # Configure git to only fetch this specific branch in the future
        subprocess.run(["git", "config", "remote.origin.fetch", f"+refs/heads/{branch}:refs/remotes/origin/{branch}"], cwd=target_path, capture_output=True)
            
        print(f"Successfully added {target_name} to marketplace.")
        
    except Exception as e:
        print(f"Error: {e}")
        if 'target_path' in locals() and target_path.exists():
            shutil.rmtree(target_path)

def sync_all(target=None):
    """Update all or a specific item in the marketplace."""
    if not MARKETPLACE_ROOT.exists():
        print("Marketplace is empty.")
        return

    if target:
        items = [MARKETPLACE_ROOT / target]
        if not items[0].exists() or not items[0].is_dir():
            print(f"Error: {target} not found in marketplace.")
            return
    else:
        print("Syncing all items in marketplace...")
        items = [item for item in MARKETPLACE_ROOT.iterdir() if item.is_dir() and (item / ".git").exists()]

    for item in items:
        if item.is_dir() and (item / ".git").exists():
            print(f"Updating {item.name}...")
            # Attempt a standard pull
            res = subprocess.run(["git", "pull"], cwd=item, capture_output=True, text=True)
            
            # If tracking is missing, try to find the current branch and pull from origin
            if "no tracking information" in res.stderr.lower() or "specify which branch" in res.stderr.lower():
                branch_res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=item, capture_output=True, text=True)
                branch = branch_res.stdout.strip()
                res = subprocess.run(["git", "pull", "origin", branch], cwd=item, capture_output=True, text=True)

            if res.returncode == 0:
                print(f"  - {item.name}: Done.")
            else:
                print(f"  - {item.name}: Failed. {res.stderr.strip()}")

def list_skills():
    """List all available skill-sets in the marketplace."""
    if not MARKETPLACE_ROOT.exists():
        print("Marketplace is empty.")
        return

    print("Available skill-sets in marketplace:")
    found = False
    for item in sorted(MARKETPLACE_ROOT.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            print(f"  - {item.name}")
            found = True
    
    if not found:
        print("  (No skill-sets found)")

def remove_skill(name):
    """Remove a skill set from the marketplace."""
    target_path = MARKETPLACE_ROOT / name
    if target_path.exists() and target_path.is_dir():
        shutil.rmtree(target_path)
        print(f"Removed {name} from marketplace.")
    else:
        print(f"Error: {name} not found in marketplace.")
