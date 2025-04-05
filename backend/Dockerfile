# Use a larger image with GTK and cairo pre-installed
FROM python:3.10-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system-level dependencies needed by manim
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    pkg-config \
    ffmpeg \
    git \
    python3-pyqt5 \
    texlive-full \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy your app code
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 5000

# Set the startup command
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "600"]
