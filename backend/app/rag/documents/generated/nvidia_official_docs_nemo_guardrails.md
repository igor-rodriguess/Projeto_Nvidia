# NeMo Guardrails

Titulo extraido: GitHub - NVIDIA-NeMo/Guardrails: NeMo Guardrails is an open-source toolkit for easily adding programmable guardrails to LLM-based conversational systems. · GitHub
URL: https://github.com/NVIDIA-NeMo/Guardrails
Categoria: nvidia_official_docs
Tipo: nvidia_official
Formato: github_repository
Prioridade: high
Coletado em: 2026-06-23T03:11:30.068521+00:00

## Conteudo extraido

Notifications You must be signed in to change notification settings

Folders and files

Latest commit

History

Repository files navigation

NVIDIA NeMo Guardrails Library

LATEST RELEASE / DEVELOPMENT VERSION : The develop branch tracks the latest top of tree development. The latest released version is 0.21.0 .

📌 The official NeMo Guardrails library documentation is available at docs.nvidia.com/nemo/guardrails .

NVIDIA NeMo Guardrails library is an open-source toolkit for easily adding programmable guardrails to LLM-based conversational applications. Guardrails (or "rails" for short) are specific ways of controlling the output of a large language model, such as not talking about politics, responding in a particular way to specific user requests, following a predefined dialog path, using a particular language style, extracting structured data, and more.

This paper introduces the NeMo Guardrails library and contains a technical overview of the system and the current evaluation.

Requirements

Python 3.10, 3.11, 3.12 or 3.13.

Installation

For more detailed instructions, see the Installation Guide .

Overview

The NeMo Guardrails library enables developers building LLM-based applications to add programmable guardrails between the application code and the LLM.

Key benefits of adding programmable guardrails include:

Building Trustworthy, Safe, and Secure LLM-based Applications: you can define rails to guide and safeguard conversations; you can choose to define the behavior of your LLM-based application on specific topics and prevent it from engaging in discussions on unwanted topics.

Connecting models, chains, and other services securely: you can connect an LLM to other services (a.k.a. tools) seamlessly and securely.

Controllable dialog : you can steer the LLM to follow pre-defined conversational paths, allowing you to design the interaction following conversation design best practices and enforce standard operating procedures (e.g., authentication, support).

Protecting against LLM Vulnerabilities

The NeMo Guardrails library provides several mechanisms for protecting an LLM-powered chat application against common LLM vulnerabilities, such as jailbreaks and prompt injections. Below is a sample overview of the protection offered by different guardrails configuration for the example ABC Bot included in this repository. For more details, please refer to the LLM Vulnerability Scanning page.

Use Cases

You can use programmable guardrails in different types of use cases:

Question Answering over a set of documents (a.k.a. Retrieval Augmented Generation): Enforce fact-checking and output moderation.

Domain-specific Assistants (a.k.a. chatbots): Ensure the assistant stays on topic and follows the designed conversational flows.

LLM Endpoints : Add guardrails to your custom LLM for safer customer interaction.

LangChain Chains (optional): If you use LangChain for any use case, you can add a guardrails layer around your chains. To enable this integration, set the NEMOGUARDRAILS_LLM_FRAMEWORK=langchain environment variable or call set_default_framework("langchain") .

Usage

To add programmable guardrails to your application you can use the Python API or a guardrails server (see the Server Guide for more details). Using the Python API is similar to using the LLM directly. Calling the guardrails layer instead of the LLM requires only minimal changes to the code base, and it involves two simple steps:

Loading a guardrails configuration and creating an LLMRails instance.

Making the calls to the LLM using the generate / generate_async methods.

The input and output format for the generate method is similar to the Chat Completions API from OpenAI.

The NeMo Guardrails library is an async-first toolkit as the core mechanics are implemented using the Python async model. The public methods have both a sync and an async version. For example: LLMRails.generate and LLMRails.generate_async .

Supported LLMs

You can use NeMo Guardrails with multiple LLMs like OpenAI GPT-3.5, GPT-4, LLaMa-2, Falcon, Vicuna, or Mosaic. For more details, check out the Supported LLM Models section in the Configuration Guide.

Types of Guardrails

The NeMo Guardrails library supports five main types of guardrails:

Input rails : applied to the input from the user; an input rail can reject the input, stopping any additional processing, or alter the input (e.g., to mask potentially sensitive data, to rephrase).

Dialog rails : influence how the LLM is prompted; dialog rails operate on canonical form messages for details see Colang Guide ) and determine if an action should be executed, if the LLM should be invoked to generate the next step or a response, if a predefined response should be used instead, etc.

Retrieval rails : applied to the retrieved chunks in the case of a RAG (Retrieval Augmented Generation) scenario; a retrieval rail can reject a chunk, preventing it from being used to prompt the LLM, or alter the relevant chunks (e.g., to mask potentially sensitive data).

Execution rails : applied to input/output of the custom actions (a.k.a. tools), that need to be called by the LLM.

Output rails : applied to the output generated by the LLM; an output rail can reject the output, preventing it from being returned to the user, or alter it (e.g., removing sensitive data).

Guardrails Configuration

A guardrails configuration defines the LLM(s) to be used and one or more guardrails . A guardrails configuration can include any number of input/dialog/output/retrieval/execution rails. A configuration without any configured rails will essentially forward the requests to the LLM.

The standard structure for a guardrails configuration folder looks like this:

The config.yml contains all the general configuration options, such as LLM models, active rails, and custom configuration data". The config.py file contains any custom initialization code and the actions.py contains any custom python actions. For a complete overview, see the Configuration Guide .

Below is an example config.yml :

The .co files included in a guardrails configuration contain the Colang definitions (see the next section for a quick overview of what Colang is) that define various types of rails. Below is an example greeting.co file which defines the dialog rails for greeting the user.

Below is an additional example of Colang definitions for a dialog rail against insults:

Colang

To configure and implement various types of guardrails, this toolkit introduces Colang , a modeling language specifically created for designing flexible, yet controllable, dialogue flows. Colang has a python-like syntax and is designed to be simple and intuitive, especially for developers.

For a brief introduction to the Colang 1.0 syntax, see the Colang 1.0 Language Syntax Guide .

To get started with Colang 2.0, see the Colang 2.0 Documentation .

Guardrails Library

NeMo Guardrails comes with a set of built-in guardrails .

The library includes guardrails for LLM self-checking (input/output moderation, fact-checking, hallucination detection), NVIDIA safety models (content safety, topic safety), jailbreak and injection detection, and integrations with community models and third-party APIs. For the complete list, see the Guardrails Library documentation .

CLI

The NeMo Guardrails library also comes with a built-in CLI.

Guardrails Server

You can use the NeMo Guardrails library CLI to start a guardrails server. The server can load one or more configurations from the specified folder and expose and HTTP API for using them.

For example, to get a chat completion for a sample config, you can use the /v1/chat/completions endpoint:

To start a guardrails server, you can also use a Docker container. The NeMo Guardrails library provides a Dockerfile that you can use to build a nemoguardrails image. For further information, see the using Docker section.

Integration with LangChain (Optional)

LangChain integration is opt-in. To enable it, set the NEMOGUARDRAILS_LLM_FRAMEWORK=langchain environment variable or call set_default_framework("langchain") . Then install the LangChain packages your configuration requires. After you enable the integration, you can wrap a guardrails configuration around a LangChain chain (or any Runnable ), and you can call a LangChain chain from within a guardrails configuration. For more information, refer to the LangChain Integration Documentation .

Evaluation

Evaluating the safety of a LLM-based conversational application is a complex task and still an open research question. To support proper evaluation, the NeMo Guardrails library provides the following:

An evaluation tool , i.e. nemoguardrails evaluate , with support for topical rails, fact-checking, moderation (jailbreak and output moderation) and hallucination.

Sample LLM Vulnerability Scanning Reports, e.g, ABC Bot - LLM Vulnerability Scan Results

How is this different?

There are many ways guardrails can be added to an LLM-based conversational application. For example: explicit moderation endpoints (e.g., OpenAI, ActiveFence, PolicyAI), critique chains (e.g. constitutional chain), parsing the output (e.g. guardrails.ai), individual guardrails (e.g., LLM-Guard), hallucination detection for RAG applications (e.g., Got It AI, Patronus Lynx).

The NeMo Guardrails library aims to provide a flexible toolkit that can integrate all these complementary approaches into a cohesive LLM guardrails layer. For example, the toolkit provides out-of-the-box integration with ActiveFence, PolicyAI, AlignScore and LangChain chains.

To the best of our knowledge, the NeMo Guardrails library is the only guardrails toolkit that also offers a solution for modeling the dialog between the user and the LLM. This enables on one hand the ability to guide the dialog in a precise way. On the other hand it enables fine-grained control for when certain guardrails should be used, e.g., use fact-checking only for certain types of questions.

Learn More

Telemetry and Privacy

The NVIDIA NeMo Guardrails library collects anonymous telemetry to help NVIDIA understand which deployment patterns and safety features are most used. The library emits one usage event when you instantiate LLMRails , IORails , or Guardrails , then emits periodic heartbeats from a single daemon thread per process. This telemetry is separate from per-request tracing . You configure tracing in your guardrails config and send it to your own observability backend. Telemetry is a minimal anonymous ping to NVIDIA.

Installed library version, Python version, operating system, and platform string

Colang configuration language version (1.0 or 2.x)

Names of configured LLM engine providers, such as openai , nim , or nvidia_ai_endpoints , never model names or credentials

Counts of configured rail flows for input, output, retrieval, tool input, and tool output rails, plus which rail categories are active

Names of built-in library features that are active, such as jailbreak_detection , content_safety , or topic_safety

Count of user-defined Colang flows (count only, never flow names or contents)

Whether tracing, streaming, or a knowledge base is configured

How you deployed guardrails ( library , api , or cli server)

Which runtime rails engine is in use ( LLMRails or IORails )

A random per-process UUID for correlating events from the same instance. The library generates it in memory and does not store it for reuse across restarts, but includes it in audit records and transmitted telemetry events

No user content is collected in the event payload. The payload does not include model names, API keys, endpoints, prompts, completions, token counts, per-request metrics, file paths, usernames, or IP addresses. NVIDIA uses the data in aggregate to prioritize engineering work and will share adoption trends with the community.

The library also attempts to write each event payload to a local audit file at ~/.config/nemoguardrails/usage_stats.json . The audit file stores the event JSONL, not the full NVIDIA telemetry envelope. Audit writes are best effort, and telemetry transmission still proceeds if local audit writing fails.

Set any one of the following options to disable telemetry:

Set the opt-out before the NVIDIA NeMo Guardrails library starts. Changing environment variables or creating do_not_track after telemetry has started does not stop an already-running heartbeat thread.

Refer to docs/telemetry.md for the full schema and field-by-field descriptions.

You may opt out of telemetry collection at any time. Opting out applies only to data collection by the NVIDIA NeMo Guardrails library itself.

Third-party endpoints have separate terms and privacy practices. The NVIDIA NeMo Guardrails library can use inference endpoints such as NVIDIA Build ( build.nvidia.com ). If you use NVIDIA Build or another third-party endpoint, that endpoint's terms of service and privacy practices apply independently of the library. Any telemetry opt-out in the NVIDIA NeMo Guardrails library does not extend to the endpoint you choose. NVIDIA Build is intended for evaluation and testing only and must not be used in production environments. Do not submit confidential information or personal data when using NVIDIA Build.

Inviting the community to contribute

The example rails residing in the repository are excellent starting points. We enthusiastically invite the community to contribute towards making the power of trustworthy, safe, and secure LLMs accessible to everyone. For guidance on setting up a development environment and how to contribute to the NeMo Guardrails library, see the contributing guidelines .

License

The NeMo Guardrails library is licensed under the Apache License, Version 2.0 .

How to cite

If you use the NeMo Guardrails library, cite the EMNLP 2023 paper that introduces it.

About

NeMo Guardrails is an open-source toolkit for easily adding programmable guardrails to LLM-based conversational systems.

Topics

Resources

Contributing

Security policy

Uh oh!

There was an error while loading. Please reload this page .

Stars

Watchers

Forks

Releases 31

Packages 0

Contributors

Languages
