# Jean moving box inventory

Canonical data: [Google Sheet](https://docs.google.com/spreadsheets/d/1fJXY3XIhmydEnoq8Czlc_mQfXPKtWsQ_JK3tsRE4mu4/edit), in the existing Jean box inventory folder. Boxes, Items and Photos are the only editable inventory. The superseded CSVs were moved to Google Drive Trash at Chris’s request after migration; do not restore them as active records.

Website: https://jean-inventory.netlify.app/ . Permanent routes `/box/jean-###` remain stable. The legacy Sites origin redirects to this origin for printed QR compatibility. Each box page offers a QR PNG.

## Publishing

`tools/publish_inventory.py --publish` reads the Sheet and authorized Drive photo folder, validates IDs and relationships, creates resized photos without EXIF, generates QR PNGs, builds in a private temporary directory, and deploys a complete static export through the Netlify API. It verifies the production revision before recording success. No private credentials or new inventory snapshots are committed to this public repository.

The Mac Mini LaunchAgent `com.christopherroyce.jean-inventory-publisher` checks every 300 seconds. Git-triggered Netlify builds are skipped to avoid replacing the Sheet with stale checked-in example data. Use `--force` after source-only changes. Without `--publish`, the command validates and builds without deployment.

Runtime: `~/.local/share/caddie-backup/venv/bin/python`; dependencies listed in tools/publisher-requirements.txt. Google authorization: existing `~/.config/caddie-mirror/google-drive/token.json`. Netlify authorization: existing CLI config in `~/Library/Preferences/netlify/config.json`. Neither secret is copied into the repository or website.

State, build log, last-error record, photo cache and successful source snapshots: `~/.local/share/jean-inventory-publisher/`. Only public resized photo copies go to Netlify. Google originals retain their permissions. Stop on invalid rows or missing photos; the prior deployed site remains online.

## Adding content

- Boxes: unique permanent `JEAN ###` ID; Publish Yes or No. New IDs must never reuse an earlier box. Website URL, if supplied, must match the ID.
- Items: unique Item ID and existing Box ID, description and positive quantity.
- Photos: upload into the registered box-photos folder (subfolders allowed), add unique Photo ID and Box ID, optional Item ID, Drive ID or URL, and Publish Yes. Do not change Drive sharing.
- Test boxes JEAN 001 and JEAN 002 remain excluded from the public directory, preserving prior behavior; their QR routes remain available.

`python -m unittest discover -s tests` tests malformed IDs, relationships, quantities, private photo exclusion and new-box/box-photo support. Full isolated builds and production revision/route/photo readback were also checked during migration.

## Recovery

The Sheet and original photos in Drive are authoritative. Git backs up publisher source. Google revision history and local successful source snapshots provide recovery evidence; encrypted independent iCloud recovery remains part of the separate unfinished Mac backup work. This folder stays yellow until that recovery is verified.
