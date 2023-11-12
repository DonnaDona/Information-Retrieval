# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.http import Response


class Review(scrapy.Item):
    url = scrapy.Field()
    score = scrapy.Field()
    text = scrapy.Field()


class Movie(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    release = scrapy.Field()
    duration = scrapy.Field()
    genres = scrapy.Field()
    rating = scrapy.Field()
    score = scrapy.Field()
    actors = scrapy.Field()
    reviews = list[Review]
