FROM ghcr.io/zephyrproject-rtos/ci:v0.27.4

ARG ZEPHYR_SDK_VERSION=0.16.8
ARG ZEPHYR_VERSION=v4.1.0

ENV ZEPHYR_SDK_INSTALL_DIR=/opt/zephyr-sdk-${ZEPHYR_SDK_VERSION}
ENV BSIM_OUT_PATH=/opt/bsim

# Initialize Zephyr workspace (CI image has toolchain but no source)
RUN mkdir -p /opt/zephyrproject && \
    cd /opt/zephyrproject && \
    west init -m https://github.com/zephyrproject-rtos/zephyr --mr ${ZEPHYR_VERSION} && \
    west update --narrow -o=--depth=1 && \
    west blobs fetch hal_nordic 2>/dev/null || true

ENV ZEPHYR_BASE=/opt/zephyrproject/zephyr
ENV PATH="${ZEPHYR_BASE}/scripts:${PATH}"

# Install Python tooling
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy dependency files and source for install
COPY pyproject.toml .python-version uv.lock README.md ./
COPY src/ ./src/
ENV PATH="/root/.local/bin:${PATH}"
RUN uv python install 3.12 && \
    uv sync --no-dev --frozen 2>/dev/null || uv sync --no-dev

# Copy remaining project files
COPY . .

ENV EMBEDEVAL_ENABLE_BUILD=1

ENTRYPOINT ["uv", "run", "embedeval"]
