FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 REB_REMOTE_DATA=/data REB_HOST=0.0.0.0 REB_PORT=8787
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . && useradd -m -u 10001 reb && mkdir /data && chown reb:reb /data
USER reb
EXPOSE 8787
CMD ["reb-remote", "serve", "--host", "0.0.0.0", "--port", "8787"]
