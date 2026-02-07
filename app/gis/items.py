from scrapy import Field, Item


class DynamicItem(Item):
    feed_name = "wrapper"

    def __setitem__(self, key, value):
        self.fields.update({key: Field()})
        self._values.update({key: value})

    def __getitem__(self, key):
        return super().__getitem__(key)


class RubricItem(DynamicItem):
    feed_name = "rubrics"


class CityItem(DynamicItem):
    feed_name = "cities"


class OrganizationItem(DynamicItem):
    feed_name = "organizations"


class ReviewItem(DynamicItem):
    feed_name = "reviews"


class MenuItem(DynamicItem):
    feed_name = "menus"


class MediaItem(DynamicItem):
    feed_name = "media"
