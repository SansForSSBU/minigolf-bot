# Minigolf (Name TBC)

A toy minigolf game and level editor built with **Pygame**, employing a lightweight ECS-style architecture.

Designed as a small game architecture exercise and a sandbox for experimenting with reinforcement learning.

---

## Installation

1. Script

Run [scripts/install.sh](scripts/install.sh)

2. Manual

```bash
uv sync
```

## Usage

```bash
# Game
uv run minigolf
# Level editor
uv run minigolf-editor
```

## Dev

```bash
uv sync --group dev
# Lint & type check
make check
# Run tests with coverage
make test
# Auto-fix lint/format
make fix
```
