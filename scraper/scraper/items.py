# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Review(scrapy.Item):
    movie_id = scrapy.Field()
    url = scrapy.Field()
    score = scrapy.Field()
    tite = scrapy.Field()
    text = scrapy.Field()


class Movie(scrapy.Item):
    class Metadata(scrapy.Item):
        url = scrapy.Field()
        image_url = scrapy.Field()
        page_title = scrapy.Field()

    movie_id = scrapy.Field()

    title = scrapy.Field()
    description = scrapy.Field()
    release = scrapy.Field()
    duration = scrapy.Field()
    genres = scrapy.Field()
    score = scrapy.Field()
    
    director = scrapy.Field()
    actors = scrapy.Field()  # type: List[str]
    
    plot = scrapy.Field()
    metadata = scrapy.Field()  # type: Metadata
