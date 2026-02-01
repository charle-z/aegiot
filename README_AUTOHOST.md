# Autohost (Nginx + Cloudflare Tunnel)

Prereqs:
- Docker + Docker Compose
- Cloudflare Tunnel token

Steps:
1. Create a tunnel in Cloudflare Zero Trust and copy the token.
2. Set the token in your shell:
   - PowerShell: $env:CLOUDFLARE_TUNNEL_TOKEN="<token>"
   - Bash: export CLOUDFLARE_TUNNEL_TOKEN="<token>"
3. Start the stack:
   - docker compose up -d
4. Stop the stack:
   - docker compose down

Notes:
- No ports are exposed to the host. Access is through the tunnel.
- The static site is served from ./docs.