# Multi-stage build: rust-builder → python-builder → runtime

# ─── Stage 1: Rust extension builder ────────────────────────────────────────
FROM rust:1.76-slim AS rust-builder

RUN apt-get update && apt-get install -y \
    python3-dev python3-pip curl \
    && pip3 install maturin \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY rust_ext/ rust_ext/
COPY Cargo.toml .

RUN maturin build --release --manifest-path rust_ext/Cargo.toml \
    --out /wheels --interpreter python3


# ─── Stage 2: Python builder ─────────────────────────────────────────────────
FROM python:3.11-slim AS python-builder

RUN pip install uv

WORKDIR /app
COPY pyproject.toml .
COPY src/ src/

# Install Rust wheel + all Python dependencies
COPY --from=rust-builder /wheels/ /wheels/
RUN uv pip install --system /wheels/*.whl ".[postgres]"
RUN uv pip install --system -e .


# ─── Stage 3: Runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Non-root user
RUN useradd -m -s /bin/bash agentuser

# Copy installed packages from builder
COPY --from=python-builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=python-builder /usr/local/bin/agent /usr/local/bin/agent
COPY --from=python-builder /app/src /app/src

WORKDIR /app

# Persistent data volume (SQLite + credential store)
RUN mkdir -p /app/data && chown agentuser:agentuser /app/data
VOLUME ["/app/data"]

USER agentuser

ENV PYTHONPATH=/app/src
ENV AGENT_HEADLESS=1
ENV DATA_DIR=/app/data

EXPOSE 7890

CMD ["agent", "run", "--foreground"]
