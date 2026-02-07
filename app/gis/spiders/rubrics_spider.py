from typing import Any, Generator

from scrapy import Spider
from scrapy.http import Request, Response
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from gis.items import RubricItem


class RubricsSpider(Spider):
    name = "rubrics"

    version = "2026.02.06"

    allowed_domains = ["2gis.ru"]
    start_urls = ["https://hermes.2gis.ru/api/data/availableParameters"]

    def __init__(
        self,
        name: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.logger.info("Starting Rubrics spider v%s", self.version)

        super().__init__(name, **kwargs)

    def parse(self, response: Response) -> Generator[Request, None, None]:
        self.logger.info("Received initial from %s", response.url)

        for _, entry in response.json()["rubrics"].items():
            yield RubricItem(**entry)

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
