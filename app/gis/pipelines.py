import json
from pathlib import Path
from typing import Dict, List

from itemadapter import ItemAdapter
from scrapy import Item, Spider
from scrapy.utils.project import get_project_settings

from gis.items import CityItem, RubricItem


class CitiesRubricsPipeline:
    filenames = {
        "cities": "cities_full.json",
        "rubrics": "rubrics_full.json",
    }

    def __init__(self):
        self._collected_items: Dict[str, List] = {"cities": [], "rubrics": []}

        self._seen_cities = set()
        self._seen_rubrics = set()

        settings = get_project_settings()
        self.cities_filename = settings.get("CITIES_FILE")
        self.rubrics_filename = settings.get("RUBRICS_FILE")

        self.filenames.update(
            {
                "cities": self.cities_filename,
                "rubrics": self.rubrics_filename,
            }
        )

    def open_spider(self, spider: Spider) -> None:
        pass

    def process_item(self, item: Item, spider: Spider) -> Item:
        if not isinstance(item, (CityItem, RubricItem)):
            return item

        adapter = ItemAdapter(item)

        if isinstance(item, CityItem):
            if adapter["id"] in self._seen_cities:
                return item

            self._collected_items["cities"].append(adapter.asdict())
            self._seen_cities.add(adapter["id"])

        elif isinstance(item, RubricItem):
            if adapter["code"] in self._seen_rubrics:
                return item

            self._collected_items["rubrics"].append(adapter.asdict())
            self._seen_rubrics.add(adapter["code"])

        return item

    def close_spider(self, spider: Spider) -> None:
        for key in ["cities", "rubrics"]:
            path = Path(self.filenames[key])

            if not self._collected_items[key]:
                continue

            path.write_text(
                json.dumps(self._collected_items[key], ensure_ascii=False, indent=4),
                encoding="utf-8",
            )
