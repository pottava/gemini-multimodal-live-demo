#!/bin/bash

# Start proxy with output logging
python /app/proxy/proxy.py 2>&1 | tee /var/log/proxy.log &
PROXY_PID=$!

# Give proxy a moment to start
sleep 1

# Check if proxy is still running
if ! kill -0 $PROXY_PID 2>/dev/null; then
    echo "Proxy failed to start. Last few lines of log:"
    tail -n 5 /var/log/proxy.log
    exit 1
fi

echo "listening on port 8080"
nginx -g "daemon off;"
