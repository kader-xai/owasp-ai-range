FROM python:3.12-slim
WORKDIR /app
COPY app.py scenarios.py vision.py index.html disclosure.html scenario.html vision.html ./
COPY support.html ./
COPY range_core ./range_core
COPY labs ./labs
USER 65532:65532
ENV BIND=0.0.0.0 PORT=8088 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8088
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8088/health')"
CMD ["python", "app.py"]
