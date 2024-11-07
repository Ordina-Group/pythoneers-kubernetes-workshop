ARG PYTHON_VERSION="3.12.7-alpine3.20"
# Poetry Builder part of this image is responsible for building the application dependencies into wheels. 
# Which will be used in the application image to install the dependencies. 
# By doing this the final image does not need to have the build tools installed. 
FROM python:${PYTHON_VERSION} AS builder

ARG POETRY_VERSION="1.8.4"
ARG POETRY_PLUGIN_EXPORT_VERSION="1.8.0"

RUN apk add --no-cache \
        curl \
        gcc \
        libressl-dev \
        musl-dev \
        libffi-dev \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile=minimal \
    && source "$HOME/.cargo/env" \
    && python -m venv /venvs/poetry \
    && /venvs/poetry/bin/pip install "poetry~=${POETRY_VERSION}" "poetry-plugin-export~=${POETRY_PLUGIN_EXPORT_VERSION}" \
    && mkdir -p "/builder/wheelhouse"

COPY ["pyproject.toml", "poetry.lock", "/builder/"]

WORKDIR /builder

RUN /venvs/poetry/bin/poetry export -f requirements.txt --output requirements.txt \
    && python -m venv /venvs/builder \
    && /venvs/builder/bin/pip install --upgrade wheel \
    && /venvs/builder/bin/pip wheel --wheel-dir "/builder/wheelhouse" -r requirements.txt

# Application image
FROM python:${PYTHON_VERSION} AS application

# Upgrade all alpine packages
RUN apk upgrade --ignore alpine-baselayout

# Create a non-root user
RUN adduser --disabled-password --uid 1000 pythonuser

# Set the working directory
WORKDIR /src

# Create and Activate Python Virtual Environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install application dependencies from wheelhouse into the python virtual environment
COPY --from=builder ["/builder/wheelhouse", "/builder/wheelhouse"]

RUN pip install -U pip \
    && pip install --no-index --no-deps /builder/wheelhouse/*.whl

# Copy the application code into the container
COPY app app

# Expose the correct port
EXPOSE 8000

# Switch to non-root user
USER pythonuser

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
