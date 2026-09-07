# Tote Inventory

QR-linked tote inventory for Jean, optimized for mobile scanning.

- Production target: Netlify
- Framework: Next.js
- Primary URL pattern: `/box/{slug}` (example: `/box/jean-003`)
- Test totes excluded from directory: `JEAN 001` and `JEAN 002`

## Development

- Install dependencies: `npm install`
- Start local server: `npm run dev`
- Build: `npm run build`

## Data sync from Google Drive

The public site reads from `app/inventory-data.json`, and photos are served from `public/box-photos`.

```bash
cd /Users/christopherroyce/tote-inventory
node /Users/christopherroyce/local-apps/scripts/storage-labels/sync_inventory_site.mjs \
  "/Users/christopherroyce/Library/CloudStorage/GoogleDrive-christopher.royce@gmail.com/My Drive/Caddie_OS/People/Jean/box inventory" \
  "./app/inventory-data.json" \
  "./public/box-photos"
```

## Netlify settings

- Build command: `npm run build`
- Publish directory: `.next`
- Plugin: `@netlify/plugin-nextjs`

## Notes

- Keep QR labels pointed to the permanent route slug (`/box/jean-###`) for each tote.
- Update this repo when Google Drive CSVs are refreshed to keep URLs and photos current.
