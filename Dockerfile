FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser --home /home/appuser appuser

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev && \
    chown -R appuser:appuser /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=appuser:appuser . .

COPY run.sh /run.sh
RUN chmod +x /run.sh

USER appuser

ENV HOME=/home/appuser
ENV UV_NO_CACHE=1

EXPOSE 8000

CMD ["/run.sh"]