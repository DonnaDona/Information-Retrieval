from typing import Generator

import scrapy
from scrapy.http import Response

from .utils import parse_duration, datestr_to_iso
from ..items import Review, Movie


class IMDBSpider(scrapy.Spider):
    name = "imdb"
    domain = "https://www.imdb.com"

    def reviews_api_url(self, movie_slug, datakey=None):
        """
        Generate the URL for the API that returns the reviews of a movie.

        :param movie_slug: the slug of the movie, i.e. the part of the URL that identifies the movie
        :param datakey: the offset of the reviews to return, expressed as a string found in the HTML of reviews page
        :return: the URL of the API
        """
        url = f"{self.domain}/title/{movie_slug}/reviews/_ajax?sort=reviewVolume&dir=desc&ratingFilter=0"
        if datakey:
            url = f"{url}&dataKey={datakey}"
        return url

    start_urls = ["https://www.imdb.com/chart/top/?ref_=nv_mv_250"]

    REVIEWS_LIMIT = 1000  # The API returns at most 1000 reviews

    def get_movie_id(self, url: str) -> str:
        """
        Given a movie URL, return the movie id.
        For example, given https://www.imdb.com/title/tt0000001/, return "0000001".

        :param url: the URL of the movie
        :return: the movie id
        """
        return url.split("/")[4][2:]

    def next_movie_id(self, current_id: str) -> str:
        """
        Given a movie id, return the next movie id.
        :param current_id: the current movie id, e.g. "0000001"
        :return: the next movie id, e.g. "0000002"
        """
        current_id = int(current_id)
        return str(current_id + 1).zfill(7)

    def next_movie_url(self, current_movie_url: str) -> str:
        """
        Given a movie URL, return the URL of the next movie.
        For example, given https://www.imdb.com/title/tt0000001/, return https://www.imdb.com/title/tt0000002/.

        :param current_movie_url: the URL of the current movie
        :return: the URL of the next movie
        """
        current_movie_id = self.get_movie_id(current_movie_url)
        next_movie_id = self.next_movie_id(current_movie_id[2:])
        rest_url = current_movie_url.split("/")[5:]
        return f"{self.domain}/title/tt{next_movie_id}/{'/'.join(rest_url)}"

    def extract_reviews(self, response: Response, movie: Movie, extracted: int = 0) -> Generator[Review, None, None]:
        """
        Extract the reviews from a movie page.

        :param response: the response of the movie page
        :param extracted: the number of reviews extracted so far for the current movie
        :return: a `Movie` with the reviews of the movie
        """
        reviews = response.xpath("//div[@class='lister-item-content']")
        for review in reviews:
            score = review.xpath(
                ".//div[@class='ipl-ratings-bar']//span[@class='rating-other-user-rating']//span//text()").get()
            text = '\n'.join(review.xpath(".//div[@class='text show-more__control']/text()").getall())
            permalink = review.xpath(".//div[@class='actions text-muted']/a/@href").get()
            if score and text and permalink:
                extracted += 1
                yield Review(url=f"{self.domain}{permalink}", movie_id=self.get_movie_id(response.url), score=score,
                             text=text)
        next_datakey = response.xpath("//div[@class='load-more-data']/@data-key")

        current_movie_id = self.get_movie_id(response.url)
        if extracted < self.REVIEWS_LIMIT and next_datakey:
            next_datakey = next_datakey.get()
            next_url = self.reviews_api_url(f"tt{current_movie_id}", next_datakey)
            yield response.follow(next_url, callback=self.extract_reviews,
                                  cb_kwargs={"movie": movie, "extracted": extracted})

    def parse_metadata(self, response: Response) -> Movie.Metadata:
        url = response.xpath("//link[@rel='canonical']/@href")
        image_url = response.xpath("//meta[@property='og:image']/@content")
        page_title = response.xpath("//title/text()")
        return Movie.Metadata(url=url, image_url=image_url, page_title=page_title)

    def retrieve_plot(self, movie_response: Response):
        def parse_plot(response: Response) -> str:
            plot = response.xpath("//ul[@id='plot-synopsis-content']/li/text()")
            return plot

        movie_id = self.get_movie_id(movie_response.url)
        plot_url = f"{self.domain}/title/tt{movie_id}/plotsummary"
        yield movie_response.follow(plot_url, callback=parse_plot)

    def parse_movie(self, response: Response) -> Movie:
        """
        Parse a movie page, yielding a `Movie` for the movie.

        :param response: the response of the movie page
        :return: a `Movie` for the movie
        """
        movie_id = self.get_movie_id(response.url)
        title = response.css("span.benbRT::text").get()
        description = response.xpath("//meta[@property='og:description']/@content")

        release_date_str = (response.xpath("//section[@cel_widget_id='StaticFeature_Details']").css(
            "a.ipc-metadata-list-item__list-content-item::text").get())
        release_date = datestr_to_iso(release_date_str)

        duration_str = ''.join(response.xpath("//section[@cel_widget_id='StaticFeature_TechSpecs']").css(
            "div.ipc-metadata-list-item__content-container::text").getall())
        duration = parse_duration(duration_str)

        genres = response.xpath("//div[@data-testid='genres']//a[@class='ipc-chip']/span/text()").getall()
        score = float(response.css("span.cMEQkK::text").get())

        director = response.css("div.fhVOeP a::text")[0].get()
        actors = response.css("a.gCQkeh::text").getall()

        plot = self.retrieve_plot(response).__next__()

        metadata = self.parse_metadata(response)

        return Movie(movie_id=movie_id, title=title, description=description, release=release_date, duration=duration,
                     genres=genres, score=score, director=director, actors=actors, plot=plot, metadata=metadata)

    def parse(self, response: Response, **kwargs):
        # top 250 movies
        movies = response.css("a.ipc-title-link-wrapper::attr(href)").getall()
        for movie in movies:
            # movie is "/title/tt0000001/"
            movie_slug = movie.split("/")[2]

            # extract information about the movie?
            yield self.parse_movie(response)

            # extract the reviews for the movie
            url = self.reviews_api_url(movie_slug)
            yield response.follow(url, callback=self.extract_reviews)

        # # yield self.extract_information(response)  # yield from self.extract_reviews(response)  #  # next_movie_url = self.next_movie_url(response.url)  # yield scrapy.Request(next_movie_url, callback=self.parse)
