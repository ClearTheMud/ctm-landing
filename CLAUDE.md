# ctm-landing — clearthemud.org Website

Static landing page for clearthemud.org, hosted on GitHub Pages with Cloudflare DNS.

## Hosting

- **GitHub Pages**: Deployed from `main` branch root (`/`)
- **Custom Domain**: clearthemud.org (CNAME file in repo root)
- **DNS**: Cloudflare — CNAME record pointing to `clearthemud.github.io`
- **SSL**: Enforced via GitHub Pages + Cloudflare (Full strict)

## Structure

```
index.html    -- Single-page landing site
CNAME         -- GitHub Pages custom domain config
```

## Development

Edit `index.html` directly. Push to `main` to deploy. GitHub Pages serves from the repo root.

## Related

- Data pipeline: `~/Local/Projects/github/clearthemud/` (private, ADO civic-tech)
- Dossiers: `~/Local/00-Claude/Clients/Clear_the_Mud_dot_org/Deliverables/dossiers/`
- GitHub org: https://github.com/ClearTheMud
