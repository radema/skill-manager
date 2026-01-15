import argparse
from skm.logic import setup_marketplace, add_skill, sync_all, remove_skill, list_skills

def main():
    setup_marketplace()
    
    parser = argparse.ArgumentParser(description="SKM: Your Agentic Skills Marketplace Manager.")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add
    add_parser = subparsers.add_parser("add", help="Add a new skill-set from GitHub")
    add_parser.add_argument("url", help="GitHub repository URL")
    add_parser.add_argument("--full", action="store_true", help="Clone the full repository instead of just 'skills/' folder")
    
    # Sync
    sync_parser = subparsers.add_parser("sync", help="Sync skills in the marketplace")
    sync_parser.add_argument("name", nargs="?", help="Optional: Specific folder name to sync")
    
    # List
    subparsers.add_parser("list", help="List all available skill-sets in the marketplace")

    # Remove
    remove_parser = subparsers.add_parser("remove", help="Remove a skill-set from the marketplace")
    remove_parser.add_argument("name", help="Folder name of the skill-set to remove (e.g. owner-repo)")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_skill(args.url, args.full)
    elif args.command == "sync":
        sync_all(args.name)
    elif args.command == "list":
        list_skills()
    elif args.command == "remove":
        remove_skill(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
