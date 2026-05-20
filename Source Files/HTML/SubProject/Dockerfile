FROM python:3.12-slim

WORKDIR /app

COPY parser.py .

RUN pip install --no-cache-dir \
    pandas \
    selectolax \
    chardet

CMD ["python", "parser.py"] 