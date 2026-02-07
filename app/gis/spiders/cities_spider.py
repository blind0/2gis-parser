from typing import Any, Generator

from scrapy import Spider
from scrapy.http import Request, Response
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from gis.items import CityItem


class CitiesSpider(Spider):
    name = "cities"

    version = "2026.02.06"

    allowed_domains = ["2gis.ru"]
    start_urls = [
        "https://catalog.api.2gis.ru/2.0/region/list?format=json&key=rubnkm7490&fields=items.bounds,items.zoom_level,items.time_zone,items.code,items.flags,items.country_code,items.domain,items.default_pos"
    ]

    def __init__(
        self,
        name: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.logger.info("Starting Cities spider v%s", self.version)

        super().__init__(name, **kwargs)

    def parse(self, response: Response) -> Generator[Request, None, None]:
        self.logger.info("Received initial from %s", response.url)

        for entry in response.json()["result"]["items"]:
            yield CityItem(**entry)

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
