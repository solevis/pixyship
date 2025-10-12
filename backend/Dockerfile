FROM python:3.11-alpine

# Install cURL and tzdata
RUN apk --no-cache add curl tzdata

# Set the timezone
ENV TZ=UTC

# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1

# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Install uv for faster dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install app dependencies using uv pip for faster installation
COPY ./requirements.lock /app/requirements.lock
RUN uv pip install --system --no-cache -r /app/requirements.lock

# Copy app source code
COPY . /app

# Expose port
EXPOSE 8000

# Run the app
CMD [ "gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000" ]

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1
