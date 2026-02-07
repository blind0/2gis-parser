# Scrapy settings for gis project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import inspect
import os
import platform
import sys
from datetime import datetime

from dotenv import load_dotenv

from gis.items import *

load_dotenv()

SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"

BOT_NAME = "gis"

# Proxy Configuration
PROXY_ENABLED = False

# Logging Configuration
LOG_LEVEL = "INFO"
os.makedirs("logs", exist_ok=True)
LOG_FILE = f"./logs/{datetime.now().strftime('%Y.%m.%d')}.log"

SPIDER_MODULES = ["gis.spiders"]
NEWSPIDER_MODULE = "gis.spiders"

DEFAULT_HEADERS = {}

# User Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36"

# Robots.txt
ROBOTSTXT_OBEY = False

# Concurrency Settings
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 16

DOWNLOAD_DELAY = 0.25 / 128

# Cookies
COOKIES_ENABLED = True
COOKIES_DEBUG = False

# Headers
DEFAULT_REQUEST_HEADERS = {}

# Pipelines
ITEM_PIPELINES = {
    "gis.pipelines.CitiesRubricsPipeline": 300,
}


# Downloader Middlewares
DOWNLOADER_MIDDLEWARES = {}
# Extensions
EXTENSIONS = {}

# Reactor and Encoding
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Base Feed Template
BASE_FEED_TEMPLATE = {
    "encoding": "utf-8",
    "store_empty": False,
    "fields": None,
    "overwrite": True,
}

# Format-specific templates
FEED_FORMATS = {
    "json": {**BASE_FEED_TEMPLATE, "format": "json"},
}

ITEM_CLASSES = [
    cls
    for _, cls in inspect.getmembers(sys.modules[f"{BOT_NAME}.items"], inspect.isclass)
    if hasattr(cls, "feed_name") and cls != DynamicItem and cls.feed_name != "wrapper"
]

FEEDS = {
    f"./data/{item_class.feed_name}_{datetime.now().strftime('%Y.%m.%d')}.{fmt}": {
        **template,
        "item_classes": [item_class],
    }
    for item_class in ITEM_CLASSES
    for fmt, template in FEED_FORMATS.items()
}


# Proxy Configuration
if PROXY_ENABLED:
    DOWNLOADER_MIDDLEWARES.update(
        {
            "rotating_proxies.middlewares.RotatingProxyMiddleware": 610,
            "rotating_proxies.middlewares.BanDetectionMiddleware": 620,
        }
    )

    ROTATING_PROXY_LIST_PATH = os.getenv("ROTATING_PROXY_LIST_PATH")
    ROTATING_PROXY_LIST_X_KEY = os.getenv("ROTATING_PROXY_LIST_X_KEY")


# Variables

URLLENGTH_LIMIT = 50_000

CITIES_FILE = os.getenv("CITIES_FILE", "cities_full.json")
RUBRICS_FILE = os.getenv("RUBRICS_FILE", "rubrics_full.json")
