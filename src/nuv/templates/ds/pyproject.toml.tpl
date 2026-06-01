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
    "numpy>=2.4.6",
    "pandas>=3.0.3",
    "pyarrow>=24.0.0",
    "pydantic-settings>=2.14.1",
    "click>=8.4.1",
]

# ---------------------------------------------------------------------------
# The catalog. Uncomment what you need, then `uv sync`.
# Versions are floors for the latest stable PyPI releases as of June 1, 2026.
# `uv add <pkg>` is the other way in — it edits this list for you.
# ---------------------------------------------------------------------------

# --- Dataframes, formats & local engines ----------------------------------
#   "polars>=1.41.2",          # fast multi-threaded dataframes (Arrow-native)
#   "duckdb>=1.5.3",           # in-process OLAP SQL over Parquet/Arrow/Polars
#   "deltalake>=1.6.0",        # Delta Lake tables without the JVM
#   "fastparquet>=2026.5.0",   # alternative Parquet engine for pandas
#   "openpyxl>=3.1.5",         # read/write .xlsx
#   "xlsxwriter>=3.2.9",       # write richly formatted .xlsx
#   "sqlalchemy>=2.0.50",      # SQL toolkit / ORM
#   "fsspec>=2026.4.0",        # filesystem abstraction (s3, gcs, http, ...)
#   "s3fs>=2026.4.0",          # S3-backed fsspec

# --- Classical / tabular ML ------------------------------------------------
#   "scikit-learn>=1.8.0",     # the workhorse: models, pipelines, metrics
#   "scipy>=1.17.1",           # scientific computing primitives
#   "statsmodels>=0.14.6",     # statistical models & tests
#   "xgboost>=3.2.0",          # gradient-boosted trees
#   "lightgbm>=4.6.0",         # fast gradient boosting
#   "catboost>=1.2.10",        # gradient boosting with native categoricals
#   "imbalanced-learn>=0.14.1",# resampling for imbalanced datasets
#   "optuna>=4.9.0",           # hyperparameter optimization

# --- Deep learning & neural nets -------------------------------------------
#   "torch>=2.12.0",           # PyTorch
#   "torchvision>=0.27.0",     # vision models, transforms, datasets
#   "torchaudio>=2.11.0",      # audio I/O and transforms for PyTorch
#   "lightning>=2.6.5",        # PyTorch Lightning training loops
#   "tensorflow>=2.21.0",      # TensorFlow
#   "keras>=3.14.1",           # multi-backend Keras (TF / JAX / PyTorch)
#   "jax>=0.10.1",             # composable transforms + XLA
#   "flax>=0.12.7",            # neural nets on JAX
#   "optax>=0.2.8",            # gradient processing & optimization for JAX
#   "einops>=0.8.2",           # readable tensor reshaping/rearranging

# --- LLMs, transformers & NLP ----------------------------------------------
#   "transformers>=5.9.0",         # Hugging Face models
#   "datasets>=4.8.5",             # streaming/loading datasets
#   "tokenizers>=0.23.1",          # fast tokenizers
#   "accelerate>=1.13.0",          # device placement & distributed training
#   "peft>=0.19.1",                # parameter-efficient fine-tuning (LoRA, ...)
#   "safetensors>=0.7.0",          # safe, fast tensor serialization
#   "huggingface-hub>=1.17.0",     # pull/push models & datasets
#   "sentence-transformers>=5.5.1",# embeddings & semantic search
#   "bitsandbytes>=0.49.2",        # 8-/4-bit quantization
#   "vllm>=0.22.0",                # high-throughput LLM serving
#   "tiktoken>=0.13.0",            # OpenAI BPE tokenizer
#   "openai>=2.38.0",              # OpenAI API client
#   "anthropic>=0.105.2",          # Anthropic API client
#   "ollama>=0.6.2",               # local model runner client
#   "langchain>=1.3.2",            # LLM application framework
#   "langchain-community>=0.4.2",  # community integrations for LangChain
#   "langgraph>=1.2.2",            # stateful agent/graph orchestration
#   "llama-index>=0.14.22",        # data framework for LLM apps / RAG
#   "spacy>=3.8.14",               # industrial-strength NLP
#   "nltk>=3.9.4",                 # classic NLP toolkit
#   "gensim>=4.4.0",               # topic modelling & word vectors

# --- Vector stores & retrieval ---------------------------------------------
#   "faiss-cpu>=1.14.2",       # similarity search over dense vectors
#   "chromadb>=1.5.9",         # embeddings database
#   "qdrant-client>=1.18.0",   # Qdrant vector DB client

# --- Images, audio & geo ---------------------------------------------------
#   "pillow>=12.2.0",          # image I/O & manipulation
#   "opencv-python>=4.13.0.92",# computer vision
#   "scikit-image>=0.26.0",    # image processing
#   "librosa>=0.11.0",         # audio analysis
#   "geopandas>=1.1.3",        # geospatial dataframes

# --- Experiment tracking, orchestration & scaling --------------------------
#   "mlflow>=3.13.0",          # experiment tracking & model registry
#   "wandb>=0.27.0",           # experiment tracking & dashboards
#   "dvc>=3.67.1",             # data & model version control
#   "hydra-core>=1.3.2",       # hierarchical config management
#   "ray[default]>=2.55.1",    # distributed compute / tuning / serving
#   "dask[complete]>=2026.3.0",# parallel & out-of-core computing

# --- Visualization ---------------------------------------------------------
#   "matplotlib>=3.10.9",      # the foundational plotting library
#   "seaborn>=0.13.2",         # statistical visualization
#   "plotly>=6.7.0",           # interactive charts
#   "altair>=6.1.0",           # declarative (Vega-Lite) charts
#   "bokeh>=3.9.0",            # interactive web plots

# --- Utilities -------------------------------------------------------------
#   "tqdm>=4.67.3",            # progress bars
#   "rich>=15.0.0",            # rich terminal output
#   "python-dotenv>=1.2.2",    # load .env files

[project.scripts]
{name} = "{module_name}.main:main"

[dependency-groups]
dev = [
    "pytest>=9.0.3",
    "pytest-cov>=7.1.0",
    "ruff>=0.15.15",
    "ty>=0.0.40",
    "ipython>=9.14.0",
]
# Jupyter / IPython + marimo notebooks. `uv sync --group notebooks` to enable.
notebooks = [
    "jupyterlab>=4.5.7",
    "notebook>=7.5.6",
    "ipykernel>=7.2.0",
    "ipywidgets>=8.1.8",
    "jupytext>=1.19.3",
    "marimo>=0.23.8",
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
