#!/bin/bash
set -euo pipefail

# Download and install uv (Linux x86_64, change URL if needed for other platforms)
echo "Installing uv..."
curl -sSfL https://astral.sh/uv/install.sh | sh

# Make sure ~/.cargo/bin is in PATH for this session
export PATH="$HOME/.cargo/bin:$PATH"

# Use uv to install pre-commit
echo "Installing pre-commit..."
uv pip install pre-commit

# Install pre-commit hooks
echo "Installing hooks..."
uv run pre-commit install

# Install project
uv pip install -e .