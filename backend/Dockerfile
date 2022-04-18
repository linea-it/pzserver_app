FROM python:3.10-slim as builder

WORKDIR /app

# If this is set to a non-empty string, Python won’t try
# to write .pyc files on the import of source modules
ENV PYTHONDONTWRITEBYTECODE=1

# Force the stdout and stderr streams to be unbuffered.
# This option has no effect on the stdin stream.
ENV PYTHONUNBUFFERED=1

# TODO: Instalar as dependencias do LDAP e do Shibboleth.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    libpcre3 \
    libpcre3-dev

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --upgrade pip wheel  && \
    pip install -r requirements.txt


FROM python:3.10-slim

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"

COPY ./entrypoint.sh /app/entrypoint.sh
# ENTRYPOINT ./entrypoint.sh

COPY . /app

