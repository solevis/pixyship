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

# Upgrading pip version
RUN pip install --no-cache-dir --upgrade pip

# Install app dependencies
COPY ./requirements.lock /app/requirements.lock
RUN pip install --no-cache-dir --upgrade -r /app/requirements.lock

# Copy app source code
COPY . /app

# Expose port
EXPOSE 8000

# Run the app
CMD [ "gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000" ]

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1
