FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Install spacy model (fixed)
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.5.0/en_core_web_sm-3.5.0-py3-none-any.whl

EXPOSE 5000

ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
