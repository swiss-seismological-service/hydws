FROM python:3.9-slim-bullseye AS app

LABEL maintainer="Nicolas Schmid <nicolas.schmid@sed.ethz.ch>"

WORKDIR /hydws

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl libpq-dev git\
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean \
    && useradd --create-home python \
    && chown python:python -R /hydws

USER python

COPY --chown=python:python requirements*.txt ./
RUN pip3 install -U --no-cache-dir --user wheel setuptools
RUN pip3 install --no-cache-dir --user -r requirements.txt

ENV PYTHONUNBUFFERED="true" \
    PYTHONPATH="." \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python"

COPY --chown=python:python . .

EXPOSE 8000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "python:config.gunicorn", "hydws.main:app"]
