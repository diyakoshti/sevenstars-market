After the Render backend is live:
1. Replace REPLACE-WITH-YOUR-RENDER-DOMAIN in vercel.json.
2. Deploy this vercel_proxy folder as the Vercel project root.
3. Add the Vercel URL to ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS on Render.

This gives visitors one Vercel URL while Django serves the complete application.
