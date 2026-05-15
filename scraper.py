import json
import random
from datetime import date
import os

from funda import Funda


def scrape_houses(n: int = 10) -> dict:
    houses = []

    with Funda() as client:
        # Fetch a broader pool so we can filter to valid entries
        results = list(client.search(category="buy", sort="newest"))
        random.shuffle(results)

        for item in results:
            if len(houses) >= n:
                break
            try:
                listing = client.listing(item.id)

                # Skip if missing critical fields
                if not listing.price or not listing.price.amount:
                    continue

                # Pick first thumbnail photo
                photo_url = None
                if listing.media and listing.media.photos:
                    photo_url = listing.media.photos[0].thumbnail_url

                if not photo_url:
                    continue

                # Surface area — try common attribute names
                surface = (
                    getattr(listing, "living_area", None)
                    or getattr(listing, "surface_area", None)
                    or getattr(listing, "floor_area", None)
                )

                house = {
                    "id": str(getattr(listing, "id", item.id)),
                    "address": listing.title or "",
                    "city": listing.city or "",
                    "price": int(listing.price.amount),
                    "photo": photo_url,
                    "bedrooms": listing.rooms.bedrooms if listing.rooms else None,
                    "energy_label": listing.energy_label or "?",
                    "surface": int(surface) if surface else None,
                    "url": item.url or "",
                }
                houses.append(house)
                print(f"  ✓ {house['address']} ({house['city']}) — €{house['price']:,}")

            except Exception as exc:
                print(f"  ✗ Skipping {getattr(item, 'id', '?')}: {exc}")
                continue

    return {
        "date": date.today().isoformat(),
        "houses": houses[:n],
    }


if __name__ == "__main__":
    print(f"Scraping {10} houses from Funda…")
    data = scrape_houses(10)

    os.makedirs("data", exist_ok=True)
    out_path = "data/houses.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(data['houses'])} houses for {data['date']} → {out_path}")
