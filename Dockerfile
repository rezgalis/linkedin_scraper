FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install Chromium + dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    gnupg \
    libnss3 \
    libxi6 \
    libxcursor1 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libgbm1 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    ca-certificates \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn

EXPOSE 3008

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3008"]
