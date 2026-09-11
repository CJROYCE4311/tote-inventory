export type InventoryItem = {
  name: string;
  quantity: number;
  category: string;
  condition: string;
  notes?: string;
  photo?: string;
};

import inventoryData from "./inventory-data.json";

export type BoxRecord = {
  id: string;
  slug: string;
  owner: string;
  label: string;
  status: "Test inventory" | "Cataloged" | "Awaiting inventory";
  location: string;
  category: string;
  summary: string;
  packedBy: string;
  updated: string;
  handling: string[];
  items: InventoryItem[];
  photos?: string[];
};

export const boxes = inventoryData as BoxRecord[];

export function isPrimaryBox(box: BoxRecord) {
  const match = String(box.id).match(/\d+/);
  if (!match) return true;
  const number = Number(match[0]);
  return Number.isFinite(number) ? number > 2 : true;
}

export function findBox(slug: string) {
  return boxes.find((box) => box.slug === slug.toLowerCase());
}
