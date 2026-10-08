FROM python:3.11-slim

RUN pip install --no-cache-dir mlflow

RUN mkdir -p /mlflow-data

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0", "--port", "5000", \
     "--backend-store-uri", "sqlite:////mlflow-data/mlflow.db", \
     "--artifacts-destination", "/mlflow-data/mlruns", \
     "--serve-artifacts", \
     "--disable-security-middleware"]