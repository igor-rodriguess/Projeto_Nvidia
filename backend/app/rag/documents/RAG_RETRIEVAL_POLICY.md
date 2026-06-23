# RAG Retrieval Policy

This project should prefer structured knowledge-base entries over raw webpage text.

Rules for the future NVIDIA RAG Agent:

- Always return citations from `sources` metadata.
- If no retrieved chunk contains a matching startup signal, return "insufficient evidence" instead of guessing.
- Use official NVIDIA sources for NVIDIA product claims.
- Use case materials only for strategic framing, such as AI-native services or AI infrastructure layers.
- Do not claim eligibility, acceptance, pricing, credits, regulatory approval, clinical validation, or production readiness unless present in retrieved evidence.
- Prefer a short ranked recommendation with confidence and evidence gaps over a long speculative answer.
- If multiple NVIDIA technologies match, explain the layer: model exploration, model customization, model serving, inference optimization, data acceleration, domain platform, enterprise deployment, or startup program.
