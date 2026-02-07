import json
import os
from typing import Any, Callable, Dict, Generator, Iterable, Tuple

from scrapy.http import Request, Response

from gis.constants import (CITIES_FILE_POSSIBLE_KEYS, CITIES_IDS_POSSIBLE_KEYS,
                           CONFLICTING_KEYS, MEDIA_URL_TEMPLATE,
                           MENUS_URL_TEMPLATE, PARSE_MEDIA_POSSIBLE_KEYS,
                           PARSE_MENUS_POSSIBLE_KEYS,
                           PARSE_REVIEWS_POSSIBLE_KEYS, REVIEWS_URL_TEMPLATE,
                           RUBRICS_CODES_POSSIBLE_KEYS,
                           RUBRICS_FILE_POSSIBLE_KEYS, TRUE_VARIATIONS,
                           URL_TEMPLATE)
from gis.items import MediaItem, MenuItem, OrganizationItem, ReviewItem
from gis.settings import CITIES_FILE, RUBRICS_FILE


def _load_json_file(filepath: str) -> list:
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found at {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_by_codes_ids(data: list, codes: list, key: str = "code") -> list:
    return [item for item in data if item[key] in codes]


def _filter_by_country(data: list, country_code: str) -> list:
    return [item for item in data if item["country_code"] == country_code]


def parse_kwargs_config(kwargs: Dict[str, Any]) -> Tuple[list, list, bool, bool, bool]:
    for conflict_key, conflicting_keys in CONFLICTING_KEYS.items():
        if sum(1 for key in conflicting_keys if key in kwargs) > 1:
            raise ValueError(
                f"Conflicting keys for {conflict_key} found in kwargs: "
                f"{', '.join(conflicting_keys)}. Provide only one."
            )

    rubrics: list = []
    cities: list = []

    parse_reviews = False
    parse_menus = False
    parse_media = False

    if rubrics_file := next(
        (kwargs.get(key) for key in RUBRICS_FILE_POSSIBLE_KEYS if key in kwargs), None
    ):
        rubrics = _load_json_file(rubrics_file)
    elif rubrics_codes := next(
        (kwargs.get(key) for key in RUBRICS_CODES_POSSIBLE_KEYS if key in kwargs),
        None,
    ):
        rubrics_codes = [
            str(code).strip() for code in rubrics_codes.split(",") if code.strip()
        ]
        rubrics_full = _load_json_file(RUBRICS_FILE)
        rubrics = filter_by_codes_ids(rubrics_full, rubrics_codes)
    elif parse_all_rubrics := kwargs.get("parse_all_rubrics"):
        if str(parse_all_rubrics).lower() in TRUE_VARIATIONS:
            rubrics = _load_json_file(RUBRICS_FILE)

    if cities_file := next(
        (kwargs.get(key) for key in CITIES_FILE_POSSIBLE_KEYS if key in kwargs), None
    ):
        cities = _load_json_file(cities_file)
    elif cities_ids := next(
        (kwargs.get(key) for key in CITIES_IDS_POSSIBLE_KEYS if key in kwargs), None
    ):
        cities_ids = [
            str(city_id).strip() for city_id in cities_ids.split(",") if city_id.strip()
        ]
        cities_full = _load_json_file(CITIES_FILE)
        cities = filter_by_codes_ids(cities_full, cities_ids, key="id")
    elif country := kwargs.get("country"):
        cities_full = _load_json_file(CITIES_FILE)
        cities = _filter_by_country(cities_full, country)
    elif parse_all_cities := kwargs.get("parse_all_cities"):
        if str(parse_all_cities).lower() in TRUE_VARIATIONS:
            cities = _load_json_file(CITIES_FILE)

    if parse_reviews := next(
        (kwargs.get(key) for key in PARSE_REVIEWS_POSSIBLE_KEYS if key in kwargs),
        None,
    ):
        parse_reviews = str(parse_reviews).lower() in TRUE_VARIATIONS

    if parse_menus := next(
        (kwargs.get(key) for key in PARSE_MENUS_POSSIBLE_KEYS if key in kwargs),
        None,
    ):
        parse_menus = str(parse_menus).lower() in TRUE_VARIATIONS

    if parse_media := next(
        (kwargs.get(key) for key in PARSE_MEDIA_POSSIBLE_KEYS if key in kwargs),
        None,
    ):
        parse_media = str(parse_media).lower() in TRUE_VARIATIONS

    return rubrics, cities, parse_reviews, parse_menus, parse_media


def create_pagination_request(
    city: dict,
    rubric: dict,
    page: int = 1,
    per_page: int = 50,
    callback: Callable[
        [Response], Iterable[Request] | Generator[OrganizationItem, None, None]
    ] = None,
    errback: Callable[[Response], None] = None,
) -> Request:
    return Request(
        url=URL_TEMPLATE.format(
            page=page,
            rubric_id=rubric["code"],
            city_id=city["id"],
            per_page=per_page,
        ),
        method="GET",
        callback=callback,
        errback=errback,
        meta={
            "city": city,
            "rubric": rubric,
            "page": page,
        },
    )


def create_reviews_request(
    org_id: str,
    page: int = 1,
    per_page: int = 50,
    callback: Callable[[Response], Generator[ReviewItem, None, None]] = None,
    errback: Callable[[Response], None] = None,
) -> Request:
    return Request(
        url=REVIEWS_URL_TEMPLATE.format(
            org_id=org_id,
            per_page=per_page,
            offset=(page - 1) * per_page,
        ),
        method="GET",
        callback=callback,
        errback=errback,
        meta={
            "org_id": org_id,
            "page": page,
        },
    )


def create_menus_pagination_request(
    org_id: str,
    page: int = 1,
    per_page: int = 50,
    callback: Callable[
        [Response], Iterable[Request] | Generator[MenuItem, None, None]
    ] = None,
    errback: Callable[[Response], None] = None,
) -> Request:
    return Request(
        url=MENUS_URL_TEMPLATE.format(
            org_id=org_id,
            page=page,
            per_page=errback,
        ),
        method="GET",
        callback=callback,
        errback=errback,
        meta={
            "org_id": org_id,
            "page": page,
        },
    )


def create_media_pagination_request(
    org_id: str,
    album_type: str,
    next_page_token: str = None,
    page: int = 1,
    per_page: int = 100,
    callback: Callable[
        [Response], Iterable[Request] | Generator[MediaItem, None, None]
    ] = None,
    errback: Callable[[Response], None] = None,
    #
    total_count: int = 0,
    collected: int = 0,
) -> Request:
    url = MEDIA_URL_TEMPLATE.format(
        org_id=org_id,
        album_type=album_type,
        per_page=per_page,
    )
    if next_page_token:
        url += f"&next_page_token={next_page_token}"

    return Request(
        url=url,
        method="GET",
        callback=callback,
        errback=errback,
        meta={
            "org_id": org_id,
            "album_type": album_type,
            "page": page,
            "total_count": total_count,
            "collected": collected,
        },
    )
