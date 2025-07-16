FROM unclecode/crawl4ai:latest

# 1) go back to root so we can apt‑install and modify users
USER root

# 2) install procps (for ps, needed by VS Code server) and git‑lfs
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      procps \
      git-lfs \
 && rm -rf /var/lib/apt/lists/* \
 && git lfs install --system

# 3) re‑map appuser → uid 1000 (and gid 1000)
RUN groupmod -g 1000 appuser \
 && usermod  -u 1000 appuser \
 && chown -R appuser:appuser /home/appuser /app

# 4) switch back to the non‑root user
USER appuser

WORKDIR /app

# your existing pip/COPY/CMD steps…
COPY  ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app
RUN pip install -e .

CMD ["python", "gradio_app.py"]
