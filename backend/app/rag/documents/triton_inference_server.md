# NVIDIA Dynamo-Triton / Triton Inference Server

Fontes oficiais:

- Produto: https://developer.nvidia.com/dynamo-triton
- Documentacao: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html

NVIDIA Triton Inference Server e um servidor open source para deploy e serving de modelos de machine learning e deep learning em producao.

Quando recomendar:

- Startup precisa servir varios modelos em producao.
- Ha modelos em frameworks diferentes, como PyTorch, ONNX, TensorRT ou Python.
- O time precisa de observabilidade, escalabilidade e padronizacao de inferencia.

Sinais em uma startup:

- Produto tem APIs de predicao, recomendacao, classificacao, deteccao ou modelos de visao.
- Ha necessidade de reduzir latencia e organizar serving em cloud, edge ou data center.
