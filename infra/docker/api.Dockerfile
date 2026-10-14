FROM python:3.11-slim-bookworm AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 UV_NO_PROGRESS=1
WORKDIR /opt/dermalens
RUN pip install --no-cache-dir uv==0.9.5
COPY pyproject.toml uv.lock requirements-persistence.txt requirements-cv.txt requirements-rag.txt ./
RUN uv sync --frozen --no-dev --no-install-project --python 3.11 \
    && uv pip install --python .venv/bin/python --no-cache \
        -r requirements-persistence.txt -r requirements-cv.txt -r requirements-rag.txt
COPY apps/api/ apps/api/
COPY apps/__init__.py apps/__init__.py
COPY packages/ packages/
COPY services/ services/
COPY infra/database/ infra/database/
COPY alembic.ini ./
COPY README.md ./
COPY docs/ docs/
RUN groupadd -g 10001 dermalens && useradd --no-log-init -u 10001 -g dermalens -d /tmp dermalens \
    && chown -R dermalens:dermalens /opt/dermalens
USER 10001:10001
EXPOSE 8000
CMD ["/opt/dermalens/.venv/bin/uvicorn", "apps.api.dermalens_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
