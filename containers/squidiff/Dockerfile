# Squidiff container based on pinned commit abdfc27
# Docker not available on evaluation machine; this is a reference Dockerfile
# for reproducibility only.

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

RUN pip install squidiff==1.0.8 anndata scanpy

WORKDIR /workspace

COPY external_runners/squidiff/ /workspace/runners/

ENTRYPOINT ["python", "-m", "runners.smoke"]
