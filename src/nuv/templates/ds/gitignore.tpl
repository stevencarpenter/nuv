# --- Editors & OS ----------------------------------------------------------
.idea/
*.iml
.vscode/
.DS_Store
.directory
*.swp
*.swo
*~

# --- AI coding agents --------------------------------------------------------
.claude/
.codex/
.copilot/
.amp/
.opencode/
.cursor/
.aider*
.continue/

# --- Python ------------------------------------------------------------------
.venv/
venv/
env/
__pycache__/
*.py[cod]
*$py.class
*.so
build/
dist/
*.egg-info/
.eggs/

# --- Tooling caches ----------------------------------------------------------
.uv/
.uvx/
.ruff_cache/
.pytest_cache/
.mypy_cache/
.dmypy.json
.pyre/
.pytype/
.cache/
.hypothesis/

# --- Coverage & test reports -------------------------------------------------
.coverage
.coverage.*
coverage.xml
htmlcov/
.tox/
.nox/

# --- Environment & secrets ---------------------------------------------------
.env
.env.*
!.env.example
*.pem
*.key
secrets.toml
.secrets/

# --- Notebooks ---------------------------------------------------------------
.ipynb_checkpoints/
*/.ipynb_checkpoints/*
profile_default/
ipython_config.py
.virtual_documents/
__marimo__/

# --- Data: keep the directory tree, ignore its contents ----------------------
# (version actual datasets with DVC/LFS if you must)
data/**
!data/**/
!data/**/.gitkeep
*.csv
*.tsv
*.parquet
*.feather
*.arrow
*.orc
*.avro
*.h5
*.hdf5
*.npy
*.npz
*.pkl
*.pickle
*.db
*.sqlite
*.sqlite3
*.duckdb
warehouse.db
_delta_log/

# --- Models & checkpoints ----------------------------------------------------
models/**
!models/**/
!models/**/.gitkeep
checkpoints/
*.ckpt
*.pt
*.pth
*.bin
*.safetensors
*.onnx
*.pb
*.tflite
*.gguf
*.ggml
*.joblib

# --- Experiment tracking & orchestration -------------------------------------
mlruns/
mlartifacts/
wandb/
.neptune/
lightning_logs/
ray_results/
catboost_info/
.dvc/cache/
outputs/
.hydra/
multirun/

# --- Caches from ML libraries ------------------------------------------------
.keras/
.torch/
.cache/huggingface/
nltk_data/
