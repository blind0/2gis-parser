from math import ceil
from typing import Any, Generator, Iterable

from scrapy import Spider
from scrapy.http import Request, Response
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.utils.project import get_project_settings
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from gis import utils
from gis.constants import RUBRICS_WITH_MENU_TAB, RUBRICS_WITH_PRICE_TAB
from gis.items import MediaItem, MenuItem, OrganizationItem, ReviewItem


class OrganizationsSpider(Spider):
    name = "organizations"

    version = "2026.02.07"

    allowed_domains = ["2gis.ru", "2gis.com"]

    seen_organizations = set()
    per_page = 50
    media_per_page = 100

    max_items = 15_000

    def __init__(
        self,
        name: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.logger.info("Starting Organizations spider v%s", self.version)

        super().__init__(name, **kwargs)

        self.settings = get_project_settings()
        (
            self.rubrics,
            self.cities,
            self.parse_reviews,
            self.parse_menus,
            self.parse_media,
        ) = utils.parse_list_kwargs_config(kwargs)

    def start_requests(self) -> Iterable[Request]:
        for city in self.cities:
            for rubric in self.rubrics:
                yield utils.create_search_pagination_request(
                    city=city,
                    rubric=rubric,
                    page=1,
                    per_page=self.per_page,
                    callback=self.parse,
                    errback=self.handle_error,
                )

    def parse(self, response: Response) -> Iterable[Request]:
        self.logger.info(
            "Received initial response for city %s, rubric %s",
            response.meta["city"]["name"],
            response.meta["rubric"]["label"],
        )

        data = response.json()
        if data["meta"]["code"] >= 400 and data["meta"]["code"] < 600:
            self.logger.warning(
                "Received error code %s for city %s, rubric %s. URL - %s",
                data["meta"]["code"],
                response.meta["city"]["name"],
                response.meta["rubric"]["label"],
                response.url,
            )
            return

        total = data["result"]["total"]
        if total > self.max_items:
            self.logger.info(
                "Total items %s exceed max_items %s, limiting to max_items",
                total,
                self.max_items,
            )
            total = self.max_items

        total_pages = ceil(total / self.per_page)

        self.logger.info(
            "Found %s total items on %s total pages for city %s, rubric %s. URL - %s",
            total,
            total_pages,
            response.meta["city"]["name"],
            response.meta["rubric"]["label"],
            response.url,
        )

        yield from self.parse_page(response)
        for page in range(2, total_pages + 1):
            yield utils.create_search_pagination_request(
                city=response.meta["city"],
                rubric=response.meta["rubric"],
                page=page,
                per_page=self.per_page,
                callback=self.parse_page,
                errback=self.handle_error,
            )

    def parse_page(self, response: Response) -> Generator[OrganizationItem, None, None]:
        self.logger.info(
            "Parsing page %s for city %s, rubric %s",
            response.meta.get("page", 1),
            response.meta["city"]["name"],
            response.meta["rubric"]["label"],
        )

        data = response.json()
        if data["meta"]["code"] >= 400 and data["meta"]["code"] < 600:
            self.logger.warning(
                "Received error code %s for city %s, rubric %s. URL - %s",
                data["meta"]["code"],
                response.meta["city"]["name"],
                response.meta["rubric"]["label"],
                response.url,
            )
            return

        for entry in data["result"]["items"]:
            id_ = entry["id"].split("_")[0]
            rubrics = entry.get("rubrics", [])
            rubrics_ids = [r["id"] for r in rubrics]

            key = f"{id_}_{rubrics_ids}"

            if key in self.seen_organizations:
                continue

            yield OrganizationItem(
                **entry,
                meta={
                    "city": response.meta["city"],
                    "rubric": response.meta["rubric"],
                },
            )
            self.seen_organizations.add(key)
            total_reviews = entry["reviews"].get("review_count") or entry[
                "reviews"
            ].get("org_review_count", 0)
            if self.parse_reviews and total_reviews > 0:
                total_pages = ceil(total_reviews / self.per_page)

                self.logger.info(
                    "Found %d reviews on %d total pages for organization %s",
                    total_reviews,
                    total_pages,
                    id_,
                )

                for page in range(1, total_pages + 1):
                    yield utils.create_reviews_request(
                        org_id=id_,
                        page=page,
                        callback=self.parse_reviews_page,
                        errback=self.handle_error,
                    )

            rubrics_ids = [r["id"] for r in entry.get("rubrics", [])]
            if self.parse_menus and (
                any(rubric_id in RUBRICS_WITH_MENU_TAB for rubric_id in rubrics_ids)
                or any(rubric_id in RUBRICS_WITH_PRICE_TAB for rubric_id in rubrics_ids)
            ):
                yield utils.create_menus_pagination_request(
                    org_id=id_,
                    page=1,
                    per_page=self.per_page,
                    callback=self.parse_menu,
                    errback=self.handle_error,
                )

            if self.parse_media:
                yield utils.create_media_pagination_request(
                    org_id=id_,
                    album_type="all",
                    page=1,
                    per_page=self.media_per_page,
                    callback=self.parse_media_by_type,
                    errback=self.handle_error,
                )

    def parse_reviews_page(
        self, response: Response
    ) -> Generator[ReviewItem, None, None]:
        self.logger.info(
            "Parsing reviews page %s for organization %s. URL - %s",
            response.meta["page"],
            response.meta["org_id"],
            response.url,
        )

        for index, review in enumerate(response.json()["reviews"]):
            yield ReviewItem(
                **review,
                meta={
                    "org_id": response.meta["org_id"],
                    "page": response.meta["page"],
                    "index": index + 1,
                },
            )

    def parse_menu(self, response: Response) -> Iterable[Request]:
        self.logger.info(
            "Parsing menu for organization %s. URL - %s",
            response.meta["org_id"],
            response.url,
        )

        data = response.json()
        if data["meta"]["code"] >= 400 and data["meta"]["code"] < 600:
            self.logger.warning(
                "Received error code %s for organization %s. URL - %s",
                data["meta"]["code"],
                response.meta["org_id"],
                response.url,
            )
            return

        data = data["result"]
        total = data["total"]
        total_pages = ceil(total / self.per_page)

        self.logger.info(
            "Found %s total menu items on %s total pages for organization %s. URL - %s",
            total,
            total_pages,
            response.meta["org_id"],
            response.url,
        )

        yield from self.parse_menu_page(response)
        for page in range(2, total_pages + 1):
            yield utils.create_menus_pagination_request(
                org_id=response.meta["org_id"],
                page=page,
                callback=self.parse_menu_page,
            )

    def parse_menu_page(self, response: Response) -> Generator[MenuItem, None, None]:
        self.logger.info(
            "Parsing menu page %s for organization %s. URL - %s",
            response.meta["page"],
            response.meta["org_id"],
            response.url,
        )

        data = response.json()
        if data["meta"]["code"] >= 400 and data["meta"]["code"] < 600:
            self.logger.warning(
                "Received error code %s for organization %s. URL - %s",
                data["meta"]["code"],
                response.meta["org_id"],
                response.url,
            )
            return

        for index, entry in enumerate(data["result"]["items"]):
            yield MenuItem(
                **entry,
                meta={
                    "org_id": response.meta["org_id"],
                    "album_type": response.meta.get("album_type"),
                    "page": response.meta["page"],
                    "index": index + 1,
                },
            )

    def parse_media_by_type(self, response: Response) -> Iterable[Request]:
        self.logger.info(
            "Parsing media for organization %s, album type %s. URL - %s",
            response.meta["org_id"],
            response.meta["album_type"],
            response.url,
        )

        data = response.json()

        albums = data.get("albums", [])
        all_album = next(
            (album for album in data.get("albums", []) if album["id"] == "all"), None
        )
        albums = [album for album in albums if album["id"] != "all"]
        if response.meta["album_type"] == "all":
            if albums:
                for album in albums:
                    yield utils.create_media_pagination_request(
                        org_id=response.meta["org_id"],
                        album_type=album["id"],
                        page=1,
                        per_page=self.media_per_page,
                        callback=self.parse_media_by_type,
                        errback=self.handle_error,
                        #
                        total_count=album.get("count", 0),
                    )
            else:
                response.meta["total_count"] = (
                    all_album.get("count", 0) if all_album else 0
                )
                yield from self.parse_media_page(response)
        else:
            yield from self.parse_media_page(response)

    def parse_media_page(
        self, response: Response
    ) -> Generator[MediaItem | Request, None, None]:
        self.logger.info(
            "Parsing media page %s for organization %s, album type %s. URL - %s",
            response.meta["page"],
            response.meta["org_id"],
            response.meta["album_type"],
            response.url,
        )

        data = response.json()
        items = data.get("items", [])

        for index, entry in enumerate(items):
            yield MediaItem(
                **entry,
                meta={
                    "org_id": response.meta["org_id"],
                    "album_type": response.meta["album_type"],
                    "page": response.meta["page"],
                    "index": index + 1,
                },
            )

        next_page_token = data.get("next_page_token")
        total_count = response.meta["total_count"]
        collected = response.meta["collected"] + len(items)

        if next_page_token and collected < total_count:
            yield utils.create_media_pagination_request(
                org_id=response.meta["org_id"],
                album_type=response.meta["album_type"],
                next_page_token=next_page_token,
                page=response.meta["page"] + 1,
                per_page=self.media_per_page,
                callback=self.parse_media_page,
                errback=self.handle_error,
                #
                total_count=total_count,
                collected=collected,
            )

    def handle_error(self, failure) -> None:
        if failure.check(HttpError):
            self.logger.error(
                "HttpError on %s. Status code: %s",
                failure.value.response.url,
                failure.value.response.status,
            )
        elif failure.check(DNSLookupError):
            self.logger.error("DNSLookupError on %s", failure.request.url)
        elif failure.check((TimeoutError, TCPTimedOutError)):
            self.logger.error("TimeoutError on %s", failure.request.url)
