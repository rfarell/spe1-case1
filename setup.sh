#!/usr/bin/env bash
# Generic project-local Conda bootstrap
# ------------------------------------
set -euo pipefail

# Load Conda's shell helpers into *this* subshell
eval "$(conda shell.bash hook)"

PROJECT_NAME=$(basename "$PWD")
echo "🚀  setting up $PROJECT_NAME …"

# ------------------------------------------------------------------
# 1. ensure we start from the base env (avoids nesting inside dev/…)
# ------------------------------------------------------------------
while [[ ${CONDA_DEFAULT_ENV:-base} != "base" ]]; do
  conda deactivate
done

# ------------------------------------------------------------------
# 2. wipe any existing env with the same name (interactive confirm)
# ------------------------------------------------------------------
if conda env list | grep -E "^\**\s*$PROJECT_NAME\s" >/dev/null; then
  read -rp "⚠️  env '$PROJECT_NAME' exists – delete? [y/N] " ans
  [[ $ans =~ ^[Yy]$ ]] || { echo "abort"; exit 1; }
  conda env remove -n "$PROJECT_NAME" -y
  echo "🗑️  removed old env"
fi

# ------------------------------------------------------------------
# 3. create & activate a *named* env (name ⇒ portable activation)
# ------------------------------------------------------------------
conda create -n "$PROJECT_NAME" python=3.11 -y
conda activate "$PROJECT_NAME"
echo "✅  created and activated $PROJECT_NAME"

# ------------------------------------------------------------------
# 4. install dependencies
#    • prefer environment.yml for reproducible builds
#    • fall back to requirements.txt (pip)
# ------------------------------------------------------------------
if [[ -f environment.yml ]]; then
  echo "📦 installing from environment.yml …"
  conda env update -n "$PROJECT_NAME" -f environment.yml -y
elif [[ -f requirements.txt ]]; then
  echo "📦 installing from requirements.txt …"
  pip install -r requirements.txt
else
  echo "⚠️  no environment.yml or requirements.txt found – empty env created"
fi

# ------------------------------------------------------------------
# 5. create necessary directories
# ------------------------------------------------------------------
echo "📁 creating project directories …"
mkdir -p data patched outputs

# ------------------------------------------------------------------
# 6. make scripts executable
# ------------------------------------------------------------------
echo "🔧 making scripts executable …"
chmod +x scripts/*.py

echo -e "\n✨  done!  next steps:\n  conda activate $PROJECT_NAME\n  cp /path/to/SPE1CASE1.DATA data/\n  python scripts/patch_summary.py data/SPE1CASE1.DATA patched/SPE1CASE1_patched.DATA\n"