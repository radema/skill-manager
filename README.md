# SKM: Agentic Skills Marketplace Manager

A lightweight tool to manage a local marketplace of agentic skills retrieved from GitHub.

## Installation

This project is managed by `uv`.

### From GitHub

To install the latest version directly from GitHub:

**Using uv:**

```bash
uv pip install git+https://github.com/radema/skill-manager.git
```

**Using pip:**

```bash
pip install git+https://github.com/radema/skill-manager.git
```

### For Local Development

To install the current folder in editable mode:

```bash
uv pip install -e .
```

## Features

- **Sparse Checkout**: By default, only the `skills/` folder is pulled from the remote repository.
- **Flat Organization**: Repositories are stored as `provider-repo` in `/root/.skills-marketplace/`.
- **Agent Shielding**: The marketplace is automatically ignored by AI agents via a `.gitignore` containing `*`.
- **Sync & Remove**: Easy commands to update or delete skill sets.

## Usage

### Add a skill set (folder `skills/` only)

```bash
skm add <repo-url>
```

### Add a full repository

```bash
skm add <repo-url> --full
```

### Sync all items

```bash
skm sync
```

### Sync a specific item

```bash
skm sync anthropics-skills
```

### List all items

```bash
skm list
```

### Remove an item

```bash
skm remove <repo-skill-name>
```

## Marketplace Location

All skills are stored in: `./.skills-marketplace/`
