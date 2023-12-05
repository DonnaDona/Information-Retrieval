import json
from typing import Any, Generator
from urllib.parse import urlparse, parse_qs

import scrapy
from scrapy.http import Response, Request

from .utils import parse_duration, datestr_to_iso
from ..items import Movie, Review


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

    def get_movie_id(self, url: str) -> str:
        """
        Given a movie URL, return the movie id.
        For example, given https://www.metacritic.com/movie/the-godfather/, return "the-godfather".

        :param url: the URL of the movie
        :return: the movie id
        """
        return url.split("/")[4]

    def next_page(self, response: Response) -> Request:
        """
        Given a browse page, return a `Request` for the next page.
        """
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)
        current_page = int(query_params["page"][0])
        return response.follow(f"{self.BASE_BROWSE_URL}?page={current_page + 1}", callback=self.parse_browse_page,
                               priority=0)

    def parse_browse_page(self, response: Response) -> Generator[Request, None, None]:
        """
        Parse a browse page, yielding a `Request` for each movie in the page and a `Request` for the next page.
        """
        for movie_url in response.xpath("//div[@class='c-productListings']//a/@href").extract():
            yield response.follow(f"{self.DOMAIN}{movie_url}", callback=self.parse_movie, priority=1)
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
            yield self.parse_movie(response)
        elif page_type == "browse":
            yield from self.parse_browse_page(response)

    def parse_metadata(self, response: Response) -> Movie.Metadata:
        url = response.xpath("//link[@rel='canonical']/@href").get()
        image_url = response.xpath("//meta[@property='og:image']/@content").get()
        page_title = response.xpath("//title/text()").get()
        return Movie.Metadata(url=url, image_url=image_url, page_title=page_title)

    def parse_movie(self, response: Response):
        """
        Parse the movie details, returning a tuple with the release date, the duration, the rating and the genres.

        :param response: the response of the movie page
        :return: a tuple with the release date, the duration, the rating and the genres
        """

        movie_id = self.get_movie_id(response.url)
        title = response.css("div.c-productHero_title").xpath("./div/text()").get().strip()

        description = response.xpath("//meta[@name='description']/@content").get()
        plot = description

        release_date_str = response.xpath(
            "//div[contains(@class, 'c-movieDetails')]//div[contains(span, 'Release Date')]/span[2]/text()") \
            .get()
        release_date = datestr_to_iso(release_date_str, "%b %d, %Y")

        duration_str = response.xpath("//div[contains(@class, 'c-heroMetadata')]//li[4]/span/text()").get().strip()
        duration = parse_duration(duration_str)

        genres = response.xpath("//ul[contains(@class, 'c-genreList')]//span/text()")
        genres = list(set(genres.get().strip() for genres in genres))

        critic_score = float(response.xpath(
            "//div[contains(@class, 'c-siteReviewScore_background-critic_medium')]//span/text()").get()) / 10 \
            or float('nan')

        user_score = float(
            response.xpath("//div[contains(@class, 'c-siteReviewScore_background-user')]//span/text()").get() or float(
                'nan'))

        director = response.xpath("//div[contains(@class, 'c-productDetails_staff_directors')]//a/text()").get().strip()

        actors = response.xpath("//div[contains(@data-cy, 'cast-')]//h3/text()")
        actors = list(set(actors.get().strip() for actors in actors))

        metadata = self.parse_metadata(response)

        yield Movie(movie_id=movie_id, title=title, description=description, release=release_date, duration=duration,
                    genres=genres, score=user_score, critic_score=critic_score, director=director, actors=actors,
                    metadata=metadata, plot=plot)
