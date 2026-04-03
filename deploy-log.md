# ContextBudget - Deploy Log

## Live URLs
- **Frontend:** https://contextbudget.dev (primary), https://contextbudget.pages.dev (fallback)
- **API:** https://cb-api.brkn.ai
- **API Health:** https://cb-api.brkn.ai/api/health
- **GitHub:** https://github.com/drewbeyersdorf/contextbudget

## Custom Domains
- **contextbudget.dev** -- LIVE (Cloudflare Pages custom domain, configured 2026-04-02)
- DNS: 172.67.162.97, 104.21.74.192 (Cloudflare CDN)
- NS: kurt.ns.cloudflare.com, mckinley.ns.cloudflare.com

## Infrastructure
- **Frontend hosting:** Cloudflare Pages (project: contextbudget)
- **API hosting:** Docker on charlie (container: contextbudget-api, port 8091)
- **Tunnel:** brkn tunnel (332df5d8) via cb-api.brkn.ai
- **Tunnel config:** charlie:~/.cloudflared/config.yml

## Stripe
- **Product:** prod_UGQmvrHR90OjPj (ContextBudget Pro)
- **Pro price:** price_1THtvCPMQUb4AkDpKcaDG19Z ($9/mo)
- **Team price:** price_1THtvCPMQUb4AkDpcrZNrANX ($29/mo)

## AdSense
- Placeholder in index.html head (ca-pub-PLACEHOLDER)
- Apply at: https://adsense.google.com after 2 weeks of traffic

## Monitoring
- API health: `curl https://cb-api.brkn.ai/api/health`
- Docker: `ssh charlie "docker logs contextbudget-api --tail 20"`
- Tunnel: `ssh charlie "tail -20 /tmp/brkn-tunnel.log"`

## Deployed
- 2026-04-02T15:51:00-07:00
