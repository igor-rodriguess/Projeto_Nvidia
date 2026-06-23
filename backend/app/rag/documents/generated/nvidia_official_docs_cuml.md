# cuML

Titulo extraido: Welcome to cuML’s documentation! — cuml 26.06.00 documentation
URL: https://docs.rapids.ai/api/cuml/stable/
Categoria: nvidia_official_docs
Tipo: nvidia_official
Formato: documentation
Prioridade: medium
Coletado em: 2026-06-23T03:11:32.158536+00:00

## Conteudo extraido

Welcome to cuML’s documentation! #

cuML is a suite of fast, GPU-accelerated machine learning algorithms designed for data science and analytical tasks. Our API mirrors scikit-learn, providing practitioners with the familiar fit-predict-transform paradigm without requiring GPU programming expertise. With cuml.accel , cuML can also automatically accelerate existing code with zero code changes.

cuML delivers on average 10-50x faster performance than CPU-based alternatives for realistic workloads and supports 50+ algorithms across all major machine learning categories, including clustering, regression, classification, dimensionality reduction, and time series analysis. With comprehensive multi-GPU and multi-node support via Dask, cuML scales from single workstations to large clusters.

Especially if your scikit-learn, umap-learn, or hdbscan workflows take many minutes to complete, you will likely benefit from using cuML. The equivalent cuML estimators often run in seconds.

Quick Start #

Key Features #

GPU Acceleration : 10-50x faster than CPU-based alternatives

Scikit-learn Compatible : Drop-in replacement for most sklearn algorithms

Multi-GPU Support : Scale across multiple GPUs and nodes with Dask

Comprehensive Coverage : 50+ algorithms across all major ML categories

Flexible Input : Works with NumPy, cuDF, cuPy, and PyTorch tensors

Production Ready : Battle-tested in enterprise environments

Installation #

cuML is available through conda and pip. For detailed installation instructions, visit the RAPIDS Release Selector .

cuML is only supported on Linux operating systems and WSL 2. See the RAPIDS install page for details on system and hardware requirements.

Part of RAPIDS #

cuML is part of the RAPIDS suite of open source libraries that enable end-to-end data science and analytics pipelines entirely on GPUs. It works seamlessly with other RAPIDS libraries like cuDF for data manipulation and cuGraph for graph analytics.

Community & Support #

User Guide - Comprehensive usage documentation

API Reference - Complete API documentation

GitHub Issues - Report bugs and request features

RAPIDS Community - Join our community
