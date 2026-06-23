# NVIDIA RAPIDS

Titulo extraido: RAPIDS | GPU Accelerated Data Science
URL: https://rapids.ai/
Categoria: nvidia_official_docs
Tipo: nvidia_official
Formato: product_page
Prioridade: high
Coletado em: 2026-06-23T03:11:31.783367+00:00

## Conteudo extraido

What is RAPIDS

RAPIDS provides unmatched speed with familiar APIs that match the most popular PyData libraries. Built on state-of-the-art foundations like NVIDIA CUDA and Apache Arrow , it unlocks the speed of GPUs with code you already know. Jump to About Section

Why Use RAPIDS

RAPIDS allows fluid, creative interaction with data for everyone from BI users to AI researchers on the cutting edge. GPU acceleration means less time and less cost moving data and training models. Jump to RAPIDS Use Cases

Open Source Ecosystem

RAPIDS is Open Source and available on GitHub . Our mission is to empower and advance the open-source GPU data science data engineering ecosystem. Jump to RAPIDS GitHub

Pandas Accelerator Mode for cuDF

Use cuDF pandas Accelerator Mode to speed up pandas workflows with zero code change. Learn More on the Accelerator Mode Page

Polars GPU Engine powered by cuDF

Accelerate Polars by enabling the GPU engine with zero code change. Learn More on the Launch Page

Accelerated scikit-learn with cuML

Run machine learning models faster with zero code change. Learn More on the Accelerated ML Page

NetworkX Supercharged by cuGraph

Speed up your large-scale graph workflows with zero code change. Learn More on the nx-cugraph Page

Faster Pandas with cuDF

cuDF accelerates pandas with zero code changes and brings greatly improved performance.

* Benchmark on AMD EPYC 7642 (using 1x 2.3GHz CPU core) w/ 512GB and NVIDIA A100 80GB (1x GPU) w/ pandas v1.5 and cuDF v23.02

Faster scikit-learn with cuML

cuML brings huge speedups to ML modeling with an API that matches scikit-learn.

* Benchmark on AMD EPYC 7642 (using 1x 2.3GHz CPU core) w/ 512GB and NVIDIA A100 80GB (1x GPU) w/ scikit-learn v1.2 and cuML v23.02

Faster NetworkX with cuGraph

cuGraph accelerates NetworkX with zero code changes for much greater performance at scale.

* Benchmark on Intel(R) Xeon(R) w9-3495X w/ 250 GB and NVIDIA A100 80GB (1x GPU) w/ NetworkX v3.4.1 and cuGraph/nx-cugraph v24.10; WCC = Weakly Connected Components; Betweenness = Betweenness Centrality with k=100

Quick Start

Quick Local Install

RAPIDS offers several installation methods, the quickest is shown below.

For more information, refer to the RAPIDS Installation Guide

Requirements

A. NVIDIA Volta™ or higher GPU with compute capability 7.0+

B. Compatible Linux distribution or WSL2 on Windows 11

C. Recent CUDA version and NVIDIA driver pairs . Check yours with: nvidia-smi See System Requirements for details. Install with Conda 1. If not installed, download and run the install script. This will install the latest miniforge: wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh" bash Miniforge3-$(uname)-$(uname -m).sh 2. Then quick install RAPIDS with: conda create -n rapids-26.06 -c rapidsai -c conda-forge rapids=26.06 python=3.14 cuda-version=13.1 Install with pip Install via the NVIDIA PyPI index: pip install \ --extra-index-url=https://pypi.nvidia.com \ cudf-cu13==26.6.* \ dask-cudf-cu13==26.6.* \ cuml-cu13==26.6.* \ cugraph-cu13==26.6.* Install with Docker Check that you have the required environment and then use the install selector Install on Windows Use the Windows WSL2 installation instructions RAPIDS Release Selector Please see the RAPIDS Installation Guide for the interactive release selector with more options, detailed installation steps, and information about supported platforms.

See System Requirements for details.

Install with Conda

1. If not installed, download and run the install script. This will install the latest miniforge:

2. Then quick install RAPIDS with:

Install with pip

Install via the NVIDIA PyPI index:

Install with Docker

Check that you have the required environment and then use the install selector

Install on Windows

Use the Windows WSL2 installation instructions

RAPIDS Release Selector

Please see the RAPIDS Installation Guide for the interactive release selector with more options, detailed installation steps, and information about supported platforms.

Test Drive cuDF

Try out cuDF pandas Accelerator Mode, with a free required account, right now by launching Google Colab

Try RAPIDS Online

Don't have access to a GPU system right now? Try out all of the RAPIDS libraries with cloud based hardware from one of these featured channels:

Google CoLab

Jump right into a GPU enabled RAPIDS notebook environment with a free required account.

Studio Lab

Enables Amazon Sagemaker notebook based environments in a free trial with required account.

Paperspace

Use Quick Start Instances through a limited free account.

NVIDIA Launchpad

Free short term use to try and learn with hands-on lab environment.

Microsoft Azure

Microsoft Azure Cloud infrastructure and services are available with RAPIDS.

Oracle Cloud

Oracle Cloud infrastructure and services are available with RAPIDS.

IBM Cloud

IBM Cloud infrastructure and services are available with RAPIDS.

User Guides and Tutorials

After installing, the best place to start is by looking through our more detailed tutorials and guides on the User Guides Page

Ecosystem

Hardware

NVIDIA's industry leading hardware provides the platform for RAPIDS high performance. Get details on the newest GPUs, server architectures, and cloud offerings in our Ecosystem Hardware Section

Software

Find out details on featured RAPIDS projects like cuDF, cuML, cuGraph, and more. Also learn about those using our integrated with RAPIDS in our Ecosystem Software Section

Developers

Get involved with RAPIDS projects, reach out to its developers, find maintainer and contribution guides in our Ecosystem Developers Section

Open Source

RAPIDS would not be possible without the collaboration of these important open source projects. Click on a logo to learn more:

Adopters and Contributors

RAPIDS has a strong ecosystem of adopters and contributors in a variety of industries and communities. Click on a logo to learn more:

Learn More

About RAPIDS

Learn more about RAPIDS' start with Apache Arrow and GoAi. Also find an overview of the capabilities of RAPIDS, as well as featured projects in our About Section

Use Cases

Hear about success stories, resources for integrating RAPIDS workflows in your business, and deployment strategies in our Use Cases Section

Get Involved

Use RAPIDS directly or through NVIDIA AI Enterprise , which provides extensive optimization, certified hardware profiles, and direct IT support. Find additional business resources, community resources, and guides for RAPIDS evangelism in our Get Involved Section

Latest News

RAPIDS X/Twitter

Follow the latest from the RAPIDS X/Twitter community with @RAPIDSai

RAPIDS Support Notices

Get the full list of developer updates and notices (RSN) that may affect your projects on the RSN Docs Page

RAPIDS News

Find our highlighted content, including talks, posts, guides and more on the NVIDIA Dev Blog and RAPIDS Blog

Latest Posts

Reducing CUDA Binary Size to Distribute cuML on PyPI

Starting with the 25.10 release, pip-installable cuML wheels can now be downloaded directly from PyPI. No more complex installation steps or managing Conda... Post by Divye Gala · Dec 15, 2025

How to GPU-Accelerate Model Training with CUDA-X Data Science

In previous posts on AI in manufacturing and operations, we covered the unique data challenges in the supply chain and how smart feature engineering can... Post by Divyansh Jain · Sep 25, 2025

How to Accelerate Community Detection in Python Using GPU-Powered Leiden

Community detection algorithms play an important role in understanding data by identifying hidden groups of related entities in networks. Social network... Post by Rick Ratzel · Sep 23, 2025

The Kaggle Grandmasters Playbook: 7 Battle-Tested Modeling Techniques for Tabular Data

Over hundreds of Kaggle competitions, we've refined a playbook that consistently lands us near the top of the leaderboard—no matter if we’re working with... Post by Kazuki Onodera · Sep 18, 2025

NVIDIA RAPIDS 25.08 Adds New Profiler for cuML, Updates to the Polars GPU Engine, Additional Algorithm Support, and More

The 25.08 release of RAPIDS continues to push the boundaries toward making accelerated data science more accessible and scalable with the addition of several... Post by Brian Tepera · Sep 17, 2025

How to Spot (and Fix) 5 Common Performance Bottlenecks in pandas Workflows

Slow data loads, memory-intensive joins, and long-running operations—these are problems every Python practitioner has faced. They waste valuable time and make... Post by Jamil Semaan · Aug 22, 2025
