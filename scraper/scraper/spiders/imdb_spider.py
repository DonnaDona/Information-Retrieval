import scrapy
from scrapy.http import Response

from ..items import Movie


class IMDBSpider(scrapy.Spider):
    name = "imdb"
    start_urls = [
        "https://imdb.com/title/tt0100001/",
    ]

    def next_movie_id(self, current_id: str) -> str:
        # in IMDB movie ids are strings of 7 digits
        # e.g. 0000001, 0000002, 0000003, etc.
        print(current_id)
        current_id = int(current_id)
        return str(current_id + 1).zfill(7)

    def next_movie_url(self, current_movie_url: str) -> str:
        # e.g. https://www.imdb.com/title/tt0000001/
        # returns https://www.imdb.com/title/tt0000002/
        current_movie_id = current_movie_url.split("/")[-2]
        next_movie_id = self.next_movie_id(current_movie_id[2:])
        return f"https://www.imdb.com/title/tt{next_movie_id}/"

    def extract_information(self, response: Response) -> Movie:
        pass

    def parse(self, response: Response, **kwargs):
        yield self.extract_information(response)

        next_movie_url = self.next_movie_url(response.url)
        yield scrapy.Request(next_movie_url, callback=self.parse)
