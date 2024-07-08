FROM python:3.10-slim

# If this is set to a non-empty string, Python won’t try
# to write .pyc files on the import of source modules
ENV PYTHONDONTWRITEBYTECODE=1

# Force the stdout and stderr streams to be unbuffered.
# This option has no effect on the stdin stream.
ENV PYTHONUNBUFFERED=1

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    libpcre3 \
    libpcre3-dev \
    iputils-ping \
    && apt-get clean \
    && apt-get autoclean \
    && apt-get autoremove --purge  -y \
    && rm -rf /var/lib/apt/lists/*

# Install python packages
COPY ./requirements.txt /tmp/pip-tmp/
RUN pip install --upgrade pip wheel setuptools \
    && pip --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

# add user so we can run things as non-root
# https://code.visualstudio.com/remote/advancedcontainers/add-nonroot-user
ARG USERNAME=pzapp
ARG USERID=1000
ARG GROUPID=1000

RUN groupadd --gid ${GROUPID} $USERNAME \
    && useradd --uid ${USERID} --gid ${GROUPID} -m ${USERNAME} \
    && mkdir -p /app /archive/data /archive/logs \
    && chown -R ${USERID}:${GROUPID} /app \
    && chown -R ${USERID}:${GROUPID} /archive

# Copy app files into container
WORKDIR /app
COPY . /app

COPY --chmod=0775 ./entrypoint.sh /entrypoint.sh
COPY --chmod=0775 ./start.sh /start.sh

# Switch to non-priviliged user and run app
USER $USERNAME

ENTRYPOINT [ "/entrypoint.sh" ]