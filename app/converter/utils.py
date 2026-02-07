import json
from argparse import ArgumentParser
from typing import Any, Dict, List, Optional, Tuple

try:
    import ijson

    HAS_IJSON = True
except ImportError:
    HAS_IJSON = False

import rv_converter

from converter.constants import (DAYS_ORDER, VALID_CONTACT_TYPES,
                                 WEEKDAYS_MAPPING)


def load_json(file_path: str) -> Dict | List | None:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            if HAS_IJSON:
                data = ijson.items(file, "item")
                return list(data)
            else:

                return json.load(file)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in file: {file_path}")


def parse_arguments() -> Any:
    parser = ArgumentParser(description="Convert JSON data to XLSX format")

    parser.add_argument("filename", help="Path to the input JSON file")
    parser.add_argument("-o", "--output", help="Path to the output XLSX file")

    return parser.parse_args()


def extract_address_part(adm_div: List, part: str):
    try:
        return next(_["name"] for _ in adm_div if _["type"] == part)
    except StopIteration:
        return None


def extract_street_house(entry: Dict) -> Tuple[Optional[str], Optional[str]]:
    street = None
    house = None

    address_components = entry.get("address", {}).get("components", [])
    for component in address_components:
        if component.get("type") != "street_number":
            continue
        street = component.get("street")
        house = component.get("number")
        break

    return street, house


def extract_contacts(contact_groups: List[Dict], contact_type: str) -> List[str]:
    if not contact_groups:
        return []

    contacts = []

    for group in contact_groups:
        for contact in group.get("contacts", []):
            if contact_type in VALID_CONTACT_TYPES:
                if contact["type"] != contact_type:
                    continue

                value = (
                    contact.get("print_text")
                    or contact.get("text")
                    or contact.get("value")
                )
                contacts.append(value)

            else:
                if contact["type"] in {"phone", "email", "website"}:
                    contact_groups
                value = (
                    contact.get("value")
                    if contact_type == "email"
                    else contact.get("url")
                    or contact.get("text")
                    or contact.get("value")
                )
                contacts.append(value)

    return contacts


def format_contacts(contacts: List[str] | str, contact_type: str = None) -> str:
    def format_phone(phone: str) -> str:
        phone = "".join(filter(str.isdigit, phone))
        return "7" + phone[1:] if phone.startswith("8") else phone

    if isinstance(contacts, str):
        if contact_type and contact_type == "phone":
            return format_phone(contacts)

        return contacts

    formatted = []
    seen = set()

    for contact in contacts:
        contact = contact.strip()

        if contact_type and contact_type == "phone":
            contact = format_phone(contact)

        if contact and contact not in seen:
            formatted.append(contact)
            seen.add(contact)

    return ",".join(formatted)


def convert_work_schedule(schedule: Dict) -> Dict:
    res = {
        "schedule": [],
        "is_24x7": schedule.get("is_24x7"),
        "comment": schedule.get("comment"),
    }

    sorted_hours = {}

    formatted_hours = {
        WEEKDAYS_MAPPING.get(day, day): ", ".join(
            [
                f"{hours['from']}-{hours['to']}"
                for hours in details.get("working_hours", [])
            ]
        )
        for day, details in schedule.items()
        if day in list(WEEKDAYS_MAPPING.keys())
    }
    sorted_hours = {
        day: formatted_hours[day] for day in DAYS_ORDER if day in formatted_hours
    }

    for k, v in sorted_hours.items():
        res["schedule"].append(f"{k}: {v}")

    return res
