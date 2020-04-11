# Install packages
FROM python:3.8-alpine as packages

RUN apk add g++ libc-dev libffi-dev libpng libpng-dev freetype freetype-dev libgfortran
RUN pip install pipenv

WORKDIR /pipfile
COPY Pipfile Pipfile.lock ./

ENV PIP_USER=1
ENV PIP_IGNORE_INSTALLED=1
ENV PYROOT /pyroot
ENV PYTHONUSERBASE $PYROOT

RUN pipenv install --system --deploy


# Build
FROM python:3.8-alpine

ENV PYTHONUNBUFFERED=1
ENV TZ=Africa/Johannesburg

RUN apk add tzdata freetype libpng libgfortran g++

WORKDIR /app

COPY --from=packages /pyroot/ /usr/local/

COPY . .

EXPOSE 8080

CMD ["python", "discord_main.py"]
