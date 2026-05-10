FROM python:3.12-slim
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root
COPY . /app
CMD bash -c "find /app -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"