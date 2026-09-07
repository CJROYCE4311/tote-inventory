import { InventoryHome } from "./InventoryHome";
import { boxes } from "./data";

export default function Home() {
  return <InventoryHome boxes={boxes} />;
}
