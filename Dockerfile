FROM mcr.microsoft.com/playwright/python:v1.55.0-noble

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install chromium

COPY . .

ENV ICEBERG_MODO_LOCAL=false
ENV ICEBERG_ENTORNO=docker
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUTF8=1

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
