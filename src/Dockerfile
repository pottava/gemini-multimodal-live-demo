FROM python:3.12-slim

WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y nginx gettext-base procps tini \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
ARG SRC_DIR=src/
COPY ${SRC_DIR}index.html /app/
COPY proxy/proxy.py /app/proxy/
COPY shared /app/shared

# Install Python dependencies
RUN pip install --no-cache-dir \
    websockets \
    google-auth \
    certifi \
    requests

# Configure nginx
RUN echo 'events { worker_connections 1024; } http { include /etc/nginx/mime.types; map $http_upgrade $connection_upgrade { default upgrade; "" close; } server { listen 8080; location / { root /app; try_files $uri $uri/ =404; } location /ws { proxy_pass http://localhost:8081; proxy_http_version 1.1; proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade"; proxy_set_header Host $host; } } }' > /etc/nginx/nginx.conf

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

CMD ["/usr/bin/tini", "--", "/app/entrypoint.sh"]
