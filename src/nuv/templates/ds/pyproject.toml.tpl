[project]
name = "{name}"
version = "0.1.0"
description = "A data science project scaffolded by nuv."
readme = "README.md"
requires-python = ">={python_version}"
# ---------------------------------------------------------------------------
# Manifesto: all of what you need or want, but off by default.
#
# The active set below is a deliberately thin core — numpy, pandas, arrow,
# a CLI, and typed config. Everything else lives in the curated, commented
# catalog further down: classical ML, deep learning, neural nets, LLMs,
# experiment tracking, viz, the works. Uncomment a line, run `uv sync`, and
# uv resolves it against everything already locked. Add weight only when you
# reach for it — your environment stays lean until you decide otherwise.
# ---------------------------------------------------------------------------
dependencies = [
    "numpy>=2.4.0",
    "pandas>=2.2.0",
    "pyarrow>=18.0.0",
    "pydantic-settings>=2.14.0",
    "click>=8.3.3",
]

# ---------------------------------------------------------------------------
# The catalog. Uncomment what you need, then `uv sync`.
# Versions are floors for the latest major releases as of mid-2026; bump
# freely. `uv add <pkg>` is the other way in — it edits this list for you.
# ---------------------------------------------------------------------------

# --- Dataframes, formats & local engines ----------------------------------
#   "polars>=1.40.1",          # fast multi-threaded dataframes (Arrow-native)
#   "duckdb>=1.5.2",           # in-process OLAP SQL over Parquet/Arrow/Polars
#   "deltalake>=1.5.1",        # Delta Lake tables without the JVM
#   "fastparquet>=2024.11.0",  # alternative Parquet engine for pandas
#   "openpyxl>=3.1.5",         # read/write .xlsx
#   "xlsxwriter>=3.2.0",       # write richly formatted .xlsx
#   "sqlalchemy>=2.0.36",      # SQL toolkit / ORM
#   "fsspec>=2025.5.0",        # filesystem abstraction (s3, gcs, http, ...)
#   "s3fs>=2025.5.0",          # S3-backed fsspec

# --- Classical / tabular ML ------------------------------------------------
#   "scikit-learn>=1.8.0",     # the workhorse: models, pipelines, metrics
#   "scipy>=1.17.0",           # scientific computing primitives
#   "statsmodels>=0.14.4",     # statistical models & tests
#   "xgboost>=3.0.0",          # gradient-boosted trees
#   "lightgbm>=4.6.0",         # fast gradient boosting
#   "catboost>=1.2.7",         # gradient boosting with native categoricals
#   "imbalanced-learn>=0.13.0",# resampling for imbalanced datasets
#   "optuna>=4.2.0",           # hyperparameter optimization

# --- Deep learning & neural nets -------------------------------------------
#   "torch>=2.11.0",           # PyTorch
#   "torchvision>=0.26.0",     # vision models, transforms, datasets
#   "torchaudio>=2.11.0",      # audio I/O and transforms for PyTorch
#   "lightning>=2.5.0",        # PyTorch Lightning training loops
#   "tensorflow>=2.20.0",      # TensorFlow
#   "keras>=3.11.0",           # multi-backend Keras (TF / JAX / PyTorch)
#   "jax>=0.7.0",              # composable transforms + XLA
#   "flax>=0.10.0",            # neural nets on JAX
#   "optax>=0.2.4",            # gradient processing & optimization for JAX
#   "einops>=0.8.1",           # readable tensor reshaping/rearranging

# --- LLMs, transformers & NLP ----------------------------------------------
#   "transformers>=5.9.0",         # Hugging Face models
#   "datasets>=4.0.0",             # streaming/loading datasets
#   "tokenizers>=0.22.0",          # fast tokenizers
#   "accelerate>=1.10.0",          # device placement & distributed training
#   "peft>=0.18.0",                # parameter-efficient fine-tuning (LoRA, ...)
#   "safetensors>=0.6.0",          # safe, fast tensor serialization
#   "huggingface-hub>=0.36.0",     # pull/push models & datasets
#   "sentence-transformers>=5.1.0",# embeddings & semantic search
#   "bitsandbytes>=0.48.0",        # 8-/4-bit quantization
#   "vllm>=0.11.0",                # high-throughput LLM serving
#   "tiktoken>=0.8.0",             # OpenAI BPE tokenizer
#   "openai>=2.0.0",               # OpenAI API client
#   "anthropic>=0.50.0",           # Anthropic API client
#   "ollama>=0.4.0",               # local model runner client
#   "langchain>=0.4.0",            # LLM application framework
#   "langchain-community>=0.4.0",  # community integrations for LangChain
#   "langgraph>=0.4.0",            # stateful agent/graph orchestration
#   "llama-index>=0.13.0",         # data framework for LLM apps / RAG
#   "spacy>=3.8.0",                # industrial-strength NLP
#   "nltk>=3.9.1",                 # classic NLP toolkit
#   "gensim>=4.3.3",               # topic modelling & word vectors

# --- Vector stores & retrieval ---------------------------------------------
#   "faiss-cpu>=1.9.0",        # similarity search over dense vectors
#   "chromadb>=0.6.0",         # embeddings database
#   "qdrant-client>=1.12.0",   # Qdrant vector DB client

# --- Images, audio & geo ---------------------------------------------------
#   "pillow>=11.0.0",          # image I/O & manipulation
#   "opencv-python>=4.11.0",   # computer vision
#   "scikit-image>=0.25.0",    # image processing
#   "librosa>=0.11.0",         # audio analysis
#   "geopandas>=1.0.1",        # geospatial dataframes

# --- Experiment tracking, orchestration & scaling --------------------------
#   "mlflow>=3.0.0",           # experiment tracking & model registry
#   "wandb>=0.19.0",           # experiment tracking & dashboards
#   "dvc>=3.60.0",             # data & model version control
#   "hydra-core>=1.3.2",       # hierarchical config management
#   "ray[default]>=2.40.0",    # distributed compute / tuning / serving
#   "dask[complete]>=2025.5.0",# parallel & out-of-core computing

# --- Visualization ---------------------------------------------------------
#   "matplotlib>=3.10.0",      # the foundational plotting library
#   "seaborn>=0.13.2",         # statistical visualization
#   "plotly>=6.0.0",           # interactive charts
#   "altair>=5.5.0",           # declarative (Vega-Lite) charts
#   "bokeh>=3.6.0",            # interactive web plots

# --- Utilities -------------------------------------------------------------
#   "tqdm>=4.67.0",            # progress bars
#   "rich>=14.0.0",            # rich terminal output
#   "python-dotenv>=1.0.1",    # load .env files

[project.scripts]
{name} = "{module_name}.main:main"

[dependency-groups]
dev = [
    "pytest>=9.0.3",
    "pytest-cov>=7.1.0",
    "ruff>=0.15.12",
    "ty>=0.0.34",
    "ipython>=9.0.0",
]
# Jupyter / IPython + marimo notebooks. `uv sync --group notebooks` to enable.
notebooks = [
    "jupyterlab>=4.5.7",
    "notebook>=7.5.0",
    "ipykernel>=7.0.0",
    "ipywidgets>=8.1.5",
    "jupytext>=1.17.0",
    "marimo>=0.23.4",
]

[tool.uv]
managed = true

[tool.pytest.ini_options]
addopts = "--cov={module_name} --cov-report=term-missing --cov-fail-under=90"

[tool.ruff]
target-version = "py{python_version_nodot}"
line-length = 180

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.lint.per-file-ignores]
# A bare expression on the last line of a marimo cell is its rendered output.
"notebooks/*.py" = ["B018"]

[tool.ty.src]
# Notebook deps live in the optional `notebooks` group and aren't installed
# by a default `uv sync`, so keep them out of the type-check pass.
exclude = ["notebooks"]

[tool.coverage.run]
branch = true

[tool.coverage.report]
exclude_lines = ["if __name__ == .__main__.:"]

[tool.hatch.build.targets.wheel]
packages = ["src/{module_name}"]
include = ["main.py"]

[build-system]
requires = ["hatchling>=1.29.0"]
build-backend = "hatchling.build"
