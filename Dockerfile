FROM unclecode/crawl4ai:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates

# Install UV as root
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# On met root et user
RUN useradd -m -u 1000 user

# On expose les deux .local/bin — racine et utilisateur
ENV PATH="/root/.local/bin:/home/user/.local/bin:$PATH"

USER user
WORKDIR /app

COPY --chown=user ./pyproject.toml pyproject.toml
RUN uv sync .

COPY --chown=user . /app

# Run the application
CMD ["uvicorn", "deepengineer.backend.entry_point:app", "--host", "0.0.0.0", "--port", "7860"]
