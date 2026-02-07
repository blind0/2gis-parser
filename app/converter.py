from parsel import Selector
from rv_converter import converter

from converter.constants import CONTACTS_MAP
from converter.utils import (convert_work_schedule, extract_address_part,
                             extract_contacts, extract_street_house,
                             format_contacts, load_json, parse_arguments)


def convert_entry(entry: dict) -> dict:
    item = {}

    item["ID"] = entry["id"].split("_")[0]
    item["Ссылка"] = f"https://2gis.ru/firm/{item['ID']}"

    rubrics_names = [r["name"] for r in entry.get("rubrics", [])]
    rubrics_names.sort()

    primary_rubrics = [
        r["name"] for r in entry.get("rubrics", []) if r.get("kind", "") == "primary"
    ]

    item["Рубрики"] = ", ".join(rubrics_names)
    item["Основные рубрики"] = ", ".join(primary_rubrics)

    stop_factors = (entry.get("context", {}) or {}).get("stop_factors", []) or []
    item["Стоп-факторы"] = ", ".join([factor["name"] for factor in stop_factors])

    item["Название"] = entry.get("name") or entry.get("full_name")

    try:
        ads_legal_name = entry["ads"]["options"]["legal_name"]
    except (KeyError, TypeError, AttributeError):
        ads_legal_name = None

    legal_name = entry.get("name_ex").get("legal_name") if entry.get("name_ex") else ""
    legal_name_parts = [
        part.strip() for part in [ads_legal_name, legal_name] if part and part.strip()
    ]

    item["Юр.лицо"] = "/".join(legal_name_parts)

    adm_div = entry.get("adm_div", []) or []

    item["Адрес"] = entry.get("full_address_name")

    item["Страна"] = extract_address_part(adm_div, "country")
    item["Регион"] = extract_address_part(adm_div, "region")
    item["Округ"] = extract_address_part(adm_div, "district_area")

    city = extract_address_part(adm_div, "city")
    settlement = extract_address_part(adm_div, "settlement")
    city_settlement_parts = [part for part in [city, settlement] if part]

    item["Нас. пункт"] = "/".join(city_settlement_parts)
    item["Район"] = extract_address_part(adm_div, "district")
    item["Микрорайон"] = extract_address_part(adm_div, "living_area")

    item["Улица"], item["Дом"] = extract_street_house(entry)

    item["Этаж/Офис"] = entry.get("address_comment")
    item["Почтовый индекс"] = entry.get("address", {}).get("postcode")

    point = entry.get("point", {}) or {}
    item["Широта"] = point.get("lat")
    item["Долгота"] = point.get("lon")

    contacts_groups = entry.get("contact_groups", []) or []
    for ru_key, contact_group in CONTACTS_MAP.items():
        contacts = extract_contacts(contacts_groups, contact_group)
        item[ru_key] = format_contacts(contacts, contact_group)

    schedule = convert_work_schedule(entry.get("schedule", {}) or {})
    item["Режим работы"] = ", ".join(schedule["schedule"])
    item["Режим работы (комментарий)"] = schedule["comment"]
    item["24x7?"] = (
        "Да"
        if schedule["is_24x7"]
        else "Нет" if schedule["is_24x7"] is not None else None
    )

    item["Рейтинг"] = entry["reviews"].get("general_rating")
    item["Кол-во оценок"] = entry["reviews"].get("general_review_count")

    ads = entry.get("ads", {}) or {}
    item["Инфо"] = ads.get("article")
    if item["Инфо"]:
        item["Инфо"] = "\n".join(
            [
                _.strip()
                for _ in Selector(text=item["Инфо"]).xpath("//text()").getall()
                if _.strip()
            ]
        )

    return item


def main(filename: str, output_filename: str) -> None:
    stats = {
        "total_orgs": 0,
        "orgs_with_phones": 0,
        "orgs_with_emails": 0,
        "stats_per_contact_type": {
            contact_name: {"seen": set(), "count": 0}
            for contact_name in CONTACTS_MAP.keys()
        },
    }

    data = load_json(filename)
    items = []
    for entry in data:
        items.append(convert_entry(entry))

    for item in items:
        stats["total_orgs"] += 1

        for contact_name in CONTACTS_MAP.keys():
            contacts = item.get(contact_name) or ""
            if not contacts:
                continue

            if contact_name == "Телефон":
                stats["orgs_with_phones"] += 1
            if contact_name == "Эл.почта":
                stats["orgs_with_emails"] += 1

            contacts = contacts.split(",")
            stats["stats_per_contact_type"][contact_name]["count"] += len(contacts)
            stats["stats_per_contact_type"][contact_name]["seen"].update(set(contacts))

    print(f"Всего организаций: {stats['total_orgs']}")
    print(f"Организаций с телефонами: {stats['orgs_with_phones']}")
    print(f"Организаций с email: {stats['orgs_with_emails']}")
    for contact_name, contact_stats in stats["stats_per_contact_type"].items():
        print(f"Столбец: {contact_name}")
        print(f"  Кол-во всего: {contact_stats['count']}")
        print(f"  Кол-во уникальных: {len(contact_stats['seen'])}")

    def del_column(contact_name: str):
        for item in items:
            if contact_name in item:
                del item[contact_name]

    for contact_name, contact_stats in stats["stats_per_contact_type"].items():
        if contact_stats["count"] == 0:
            print(f"Столбец {contact_name} удален, так как в нем нет значений")
            del_column(contact_name)

    converter.save_file(items, output_filename)


if __name__ == "__main__":
    args = parse_arguments()

    main(
        filename=args.filename,
        output_filename=args.output,
    )
