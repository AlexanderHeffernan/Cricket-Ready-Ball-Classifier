FROM rust:1.99-bookworm AS build
WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release --locked

FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends libssl3 libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 cricket && useradd --uid 10001 --gid cricket --no-create-home cricket \
    && mkdir -p /data/pending && chown -R cricket:cricket /data
WORKDIR /app
# CPU wheels avoid installing CUDA runtimes on CPU-only hosts.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.14.1 torchvision==0.29.1
COPY nn-classifier/requirements-inference.txt /app/nn-classifier/requirements-inference.txt
RUN pip install --no-cache-dir -r nn-classifier/requirements-inference.txt
COPY --from=build /build/target/release/Cricket-Ready-Backend ./Cricket-Ready-Backend
COPY nn-classifier/predict.py ./nn-classifier/predict.py
COPY nn-classifier/models ./nn-classifier/models
ENV PYTHON_EXECUTABLE=python3 TRAINING_PENDING_DIR=/data/pending PYTHONDONTWRITEBYTECODE=1
USER 10001:10001
EXPOSE 49161
CMD ["./Cricket-Ready-Backend"]
