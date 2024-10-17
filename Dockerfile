ARG PYTHON_VERSION=3.12-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV DJANGO_SETTINGS_MODULE "config.settings.production"
ENV DJANGO_SECRET_KEY "this is a secret key for building purposes"
ENV DJANGO_ADMIN_URL "admin/"
ENV DATABASE_URL "sqlite:///db.sqlite3"
ENV BREVO_API_KEY "some api key"

RUN mkdir -p /code

WORKDIR /code

COPY requirements/base.txt /tmp/base.txt
COPY requirements/production.txt /tmp/production.txt

# install psycopg2 dependencies
# RUN apt-get update && apt-get install -y \
#     libpq-dev \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*  # <-- Updated!

RUN apt-get update && apt-get install -y \
    bzip2 git \
    && rm -rf /var/lib/apt/lists/

# --mount=type=cache,target=/root/.cache

RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/production.txt && \
    rm -rf /root/.cache/
COPY . /code

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--timeout", "20", "--workers", "4", "config.wsgi"]
