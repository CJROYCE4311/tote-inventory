"use client";

import { useMemo, useState } from "react";
import { isPrimaryBox, type BoxRecord } from "./data";

function isExcludedFromLanding(box: BoxRecord) {
  return !isPrimaryBox(box);
}

export function InventoryHome({ boxes }: { boxes: BoxRecord[] }) {
  const [query, setQuery] = useState("");
  const normalizedQuery = query.trim().toLowerCase();
  const publicBoxes = useMemo(() => boxes.filter((box) => !isExcludedFromLanding(box)), [boxes]);
  const inventoriedCount = publicBoxes.filter((box) => box.items.length > 0).length;
  const awaitingCount = publicBoxes.length - inventoriedCount;

  const filteredBoxes = useMemo(
    () =>
      publicBoxes.filter((box) =>
        [box.id, box.label, box.category, box.summary, box.status]
          .join(" ")
          .toLowerCase()
          .includes(normalizedQuery),
      ),
    [publicBoxes, normalizedQuery],
  );

  const featuredBoxes = filteredBoxes.slice(0, 4);

  return (
    <main>
      <header className="site-header">
        <a className="wordmark" href="/" aria-label="Tote Inventory home">
          <span className="wordmark-main">Tote</span>
          <span className="wordmark-sub">Jean&apos;s Inventory</span>
        </a>
        <span className="header-label">Mobile-ready • QR-first</span>
      </header>

      <section className="hero" aria-labelledby="hero-title">
        <img
          className="hero-image"
          src="/hero-tote-rack.svg"
          alt="Garage rack with totes and QR labels"
          loading="eager"
        />
        <div className="hero-shade" />
        <div className="hero-copy">
          <span className="eyebrow">Jean&apos;s storage totes</span>
          <h1 id="hero-title">Scan a tote. Open its full contents instantly.</h1>
          <p>
            Every tote in Jean&apos;s garage has a QR sticker that opens its page with what&apos;s inside,
            photos, and handling notes.
          </p>
          <a className="primary-button" href="#boxes">Open the tote directory</a>
        </div>
      </section>

      <section className="summary-strip" aria-label="Inventory summary">
        <div><strong>{publicBoxes.length}</strong><span>Totes cataloged</span></div>
        <div><strong>{inventoriedCount}</strong><span>Inventories listed</span></div>
        <div><strong>{awaitingCount}</strong><span>Waiting for catalog</span></div>
      </section>

      <section className="inventory-section featured" aria-label="Featured totes">
        <div className="section-heading">
          <div>
            <span className="eyebrow eyebrow-light">Featured</span>
            <h2>Start with these totes</h2>
            <p>These are the first available tote pages.</p>
          </div>
        </div>
        <div className="box-grid featured-grid">
          {featuredBoxes.map((box) => (
            <a className={`box-card ${box.items.length ? "box-card-ready" : ""}`} href={`/box/${box.slug}`} key={`${box.id}-featured`}>
              <div className="box-card-topline">
                <span className="box-id">{box.id}</span>
                <span className={`status-pill ${box.items.length ? "status-ready" : ""}`}>{box.status}</span>
              </div>
              <h3>{box.label}</h3>
              <p>{box.summary}</p>
            </a>
          ))}
        </div>
      </section>

      <section className="inventory-section" id="boxes">
        <div className="section-heading">
          <div>
            <span className="eyebrow eyebrow-light">Tote directory</span>
            <h2>Browse Jean&apos;s totes</h2>
            <p>Search by number, category, status, or contents summary.</p>
          </div>
          <label className="search-box">
            <span>Search inventory</span>
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Try JEAN 014, kitchen, or photo albums"
            />
          </label>
        </div>

        <div className="box-grid">
          {filteredBoxes.map((box) => (
            <a className={`box-card ${box.items.length ? "box-card-ready" : ""}`} href={`/box/${box.slug}`} key={box.id}>
              <div className="box-card-topline">
                <span className="box-id">{box.id}</span>
                <span className={`status-pill ${box.items.length ? "status-ready" : ""}`}>{box.status}</span>
              </div>
              <h3>{box.label}</h3>
              <p>{box.summary}</p>
              <div className="box-card-footer">
                <span>{box.category}</span>
                <span>{box.items.length ? `${box.items.length} item groups` : "Add contents"} →</span>
              </div>
            </a>
          ))}
        </div>

        {filteredBoxes.length === 0 ? (
          <div className="empty-state">No boxes match “{query}”. Try a box number or category.</div>
        ) : null}
      </section>

      <footer>
        <span>Tote Inventory</span>
        <span>Public inventory for Jean&apos;s move. No sensitive details.</span>
      </footer>
    </main>
  );
}
