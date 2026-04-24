server {
    listen 443 ssl;
    server_name mcp.finapi.upvaly.com;

    ssl_certificate /etc/letsencrypt/live/mcp.finapi.upvaly.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.finapi.upvaly.com/privkey.pem;

    # MCP Server Endpoint
    location /mcp {

        proxy_pass http://127.0.0.1:8004/mcp;
        proxy_http_version 1.1;

        # REQUIRED HEADERS
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header Accept $http_accept;
        proxy_set_header X-API-Key $http_x_api_key;

        # REQUIRED FOR SSE
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }
    
    # Health Check Endpoint (optional, no auth needed)
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8004/health;
        proxy_http_version 1.1;
    }

    # Root redirect (optional)
    location / {
        return 404;
    }

}
