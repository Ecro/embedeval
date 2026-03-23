FROM ghcr.io/zephyrproject-rtos/ci:v0.27.4

ARG ZEPHYR_SDK_VERSION=0.16.8

ENV ZEPHYR_BASE=/opt/zephyrproject/zephyr
ENV ZEPHYR_SDK_INSTALL_DIR=/opt/zephyr-sdk-${ZEPHYR_SDK_VERSION}
ENV BSIM_OUT_PATH=/opt/bsim
ENV PATH="${ZEPHYR_BASE}/scripts:${PATH}"

# Fetch and compile BabbleSim using Zephyr's helper script
RUN mkdir -p ${BSIM_OUT_PATH} && \
    if [ -f ${ZEPHYR_BASE}/scripts/native_simulator/native_sim_utils.sh ]; then \
        echo "Native sim utilities available"; \
    fi && \
    west blobs fetch hal_nordic 2>/dev/null || true

# Install Python tooling
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy dependency files and install (cache-friendly layer)
COPY pyproject.toml .python-version uv.lock ./
RUN if [ -f uv.lock ]; then uv sync --no-dev --frozen; else uv sync --no-dev; fi

# Copy project source and remaining files
COPY . .

ENTRYPOINT ["uv", "run", "embedeval"]
