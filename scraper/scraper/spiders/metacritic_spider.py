import json
from typing import Any, Generator
from urllib.parse import urlparse, parse_qs

import scrapy
from scrapy.http import Response

from .utils import parse_duration, datestr_to_iso
from ..items import Movie, Review


def parse_movie_details(response: Response):
    """
    Parse the movie details, returning a tuple with the release date, the duration, the rating and the genres.

    :param response: the response of the movie page
    :return: a tuple with the release date, the duration, the rating and the genres
    """
    get_detail = lambda idx: response.css("div.c-movieDetails_sectionContainer")[idx].xpath("(./span)[2]/text()").get()

    release = datestr_to_iso(get_detail(1))
    duration = parse_duration(get_detail(2))
    genres = response.css("div.c-movieDetails_sectionContainer")[4].xpath("./ul/li//span/text()").getall()
    genres = list(map(str.strip, genres))

    return release, duration, rating, genres


def parse_movie(response: Response) -> Movie:
    """
    Parse a movie page, returning a `Movie` object. The `Movie` class is defined in `scraper/items.py`.

    :param response: the response of the movie page
    :return: a `Movie` object describing the movie
    """
    title: str = response.css("div.c-productHero_title").xpath("./div/text()").get().strip()
    description: str = response.css("meta[name=description]::attr(content)").get().strip()
    release, duration, rating, genres = parse_movie_details(response)
    return Movie(title=title, description=description, release=release, duration=duration, rating=rating, genres=genres)


def parse_reviews(response: Response):
    """
    Parse the reviews page, yielding a `Review` for each review in the page.
    There is no need to follow the pagination, since the API returns REVIEWS_LIMIT reviews.

    :param response: the response of the reviews page
    :return: a `Review` for each review in the page
    """
    content = json.loads(response.body)
    reviews = content["data"]["items"]
    for review in reviews:
        yield Review(score=review["score"], text=review["quote"])


class MetacriticSpider(scrapy.Spider):
    name = "metacritic"

    DOMAIN = "https://www.metacritic.com"
    BASE_BROWSE_URL = f"{DOMAIN}/browse/movie/"
    REVIEWS_LIMIT = 1000  # The API returns at most 1000 reviews

    start_urls = [f"{BASE_BROWSE_URL}?page=1"]

    def reviews_api_url(self, movie_slug):
        """
        Generate the URL for the API that returns the reviews of a movie.

        :param movie_slug: the slug of the movie, i.e. the part of the URL that identifies the movie
        :return: the URL of the API
        """
        return f"https://fandom-prod.apigee.net/v1/xapi/reviews/metacritic/user/movies/{movie_slug}/web?limit={self.REVIEWS_LIMIT}"

    def reviews_url(self, movie_slug):
        """
        Generate the URL for the reviews page of a movie.

        :param movie_slug: the slug of the movie, i.e. the part of the URL that identifies the movie
        :return: the URL of the reviews page
        """
        return f"{self.DOMAIN}/movie/{movie_slug}/user-reviews"

    def next_page(self, response: Response) -> scrapy.Request:
        """
        Given a browse page, return a `Request` for the next page.
        """
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)
        current_page = int(query_params["page"][0])
        return response.follow(f"{self.BASE_BROWSE_URL}?page={current_page + 1}", callback=self.parse_browse_page)

    def parse_browse_page(self, response: Response) -> Generator[scrapy.Request, None, None]:
        """
        Parse a browse page, yielding a `Request` for each movie in the page and a `Request` for the next page.
        """
        for movie_url in response.xpath("//div[@class='c-productListings']//a/@href").extract():
            yield response.follow(f"{self.DOMAIN}{movie_url}", callback=parse_movie)
        yield self.next_page(response)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        """
        Entry point, call the right parser based on the page type.

        This function should be called only the first time; the other `Request`s have the callback set to the right
        parser function.
        """
        page_url = response.url
        page_type = page_url.split("/")[3]

        if page_type == "movie":
            yield parse_movie(response)
        elif page_type == "browse":
            yield from self.parse_browse_page(response)
