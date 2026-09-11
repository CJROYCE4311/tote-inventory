import { boxes, findBox } from "../../data";

function photosFromItem(raw?: string) {
  return (raw || "")
    .split(/[,;|]/)
    .map((value) => value.trim())
    .filter((value) => value.length > 0);
}

function photoSource(photo: string) {
  return /^https?:\/\//i.test(photo) ? photo : `/box-photos/${photo}`;
}

export function generateStaticParams() {
  return boxes.map((box) => ({ boxId: box.slug }));
}

export default async function BoxPage({ params }: { params: Promise<{ boxId: string }> }) {
  const { boxId } = await params;
  const box = findBox(boxId);

  if (!box) {
    return (
      <main className="detail-shell">
        <a className="back-link" href="/">← Tote directory</a>
        <section className="missing-card">
          <span className="eyebrow eyebrow-light">Tote not found</span>
          <h1>This QR code is not in the published tote list.</h1>
          <p>Check the printed ID or return to the directory.</p>
        </section>
      </main>
    );
  }

  const photos = [...new Set([...(box.photos || []), ...box.items.flatMap((item) => photosFromItem(item.photo))])];

  return (
    <main className="detail-shell">
      <header className="detail-header">
        <a className="wordmark" href="/" aria-label="Tote Inventory home">
          <span className="wordmark-main">Tote</span>
          <span className="wordmark-sub">Jean&apos;s Inventory</span>
        </a>
        <a className="back-link" href="/">← Tote directory</a>
      </header>

      <section className="box-detail-hero">
        <div>
          <span className="eyebrow">{box.owner}&apos;s tote inventory</span>
          <p className="detail-kicker">{box.label}</p>
          <h1>{box.id}</h1>
          <p><a href={`/qr/${box.slug}.png`} download>Download QR label</a></p>
          <p>{box.summary || "Contents list will be added as photos are processed."}</p>
        </div>
        <div className="detail-status-card">
          <span>Status</span>
          <strong>{box.status}</strong>
          <small>Last updated: {box.updated}</small>
        </div>
      </section>

      {photos.length ? (
        <section className="photo-gallery" aria-label={`${box.id} photos`}>
          <div className="photo-gallery-heading">
            <span className="eyebrow eyebrow-light">Packing photos</span>
            <p>Reference photos for this tote&apos;s listed contents.</p>
          </div>
          <div className="photo-grid">
            {photos.map((photo) => (
              <img key={photo} src={photoSource(photo)} alt={`Items packed in ${box.id}`} loading="lazy" />
            ))}
          </div>
        </section>
      ) : null}

      <section className="fact-grid" aria-label="Tote details">
        <div><span>Owner</span><strong>{box.owner}</strong></div>
        <div><span>Category</span><strong>{box.category}</strong></div>
        <div><span>Current location</span><strong>{box.location}</strong></div>
        <div><span>Cataloged by</span><strong>{box.packedBy}</strong></div>
      </section>

      {box.handling.length ? (
        <section className="handling-strip" aria-label="Handling notes">
          <span>Handling</span>
          <div>{box.handling.map((note) => <strong key={note}>{note}</strong>)}</div>
        </section>
      ) : null}

      <section className="contents-panel">
        <div className="contents-heading">
          <div>
            <span className="eyebrow eyebrow-light">Contents</span>
            <h2>{box.items.length ? `${box.items.length} item groups` : "Awaiting catalog"}</h2>
          </div>
          <span className="quantity-total">
            {box.items.length ? `${box.items.reduce((sum, item) => sum + item.quantity, 0)} recorded pieces/groups` : "Not yet cataloged"}
          </span>
        </div>

        {box.items.length ? (
          <div className="contents-table-wrap">
            <table>
              <thead><tr><th>Item</th><th>Qty</th><th>Category</th><th>Condition</th><th>Notes</th></tr></thead>
              <tbody>
                {box.items.map((item) => (
                  <tr key={`${item.category}-${item.name}`}>
                    <td data-label="Item"><strong>{item.name}</strong></td>
                    <td data-label="Qty">{item.quantity}</td>
                    <td data-label="Category">{item.category}</td>
                    <td data-label="Condition">{item.condition}</td>
                    <td data-label="Notes">{item.notes ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-box-message">
            <strong>Inventory for this tote is not yet cataloged.</strong>
            <p>This page remains permanent; add contents in Google Drive when cataloging is complete.</p>
          </div>
        )}
      </section>

      <footer>
        <span>Jean&apos;s Tote Inventory</span>
        <span>{box.id} · Public tote record</span>
      </footer>
    </main>
  );
}
