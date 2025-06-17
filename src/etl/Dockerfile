FROM python:3.12-slim-bookworm

WORKDIR /opt/banking-project

COPY src src
COPY scripts scripts
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "sh", "scripts/run_etl.sh" ]
