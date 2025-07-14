FROM unclecode/crawl4ai:latest

USER root

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . /app
RUN pip install -e .

CMD ["uvicorn", "deepengineer.backend.entry_point:app", "--host", "0.0.0.0", "--port", "7860"]
