FROM python:3.12.1-slim-bookworm

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "-m", "tagbiljett"]
