FROM python:3.12-slim

# uv from the official multi-arch image (multi-stage copy keeps final image small).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Build deps:
#   build-essential, libpcre2-dev — required to compile uWSGI from sdist
#                                   (PCRE3 was dropped in Debian Trixie)
#   libpq-dev                     — runtime headers for psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpcre2-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copy lockfile + manifest first so dependency layer caches across source changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy source and entrypoint
COPY ./server /code/server
COPY ./.env /code/.env
COPY ./docker-entrypoint.sh /code/docker-entrypoint.sh

# Put the venv on PATH so `uwsgi`, `python`, etc. resolve without `uv run`
ENV PATH="/code/.venv/bin:${PATH}" \
    VIRTUAL_ENV="/code/.venv"

ENTRYPOINT ["/code/docker-entrypoint.sh"]
EXPOSE 6000
CMD ["run_server"]
