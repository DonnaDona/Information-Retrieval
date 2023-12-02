from typing import Generator, Iterable, Any

import scrapy
from scrapy.http import Response

from .utils import parse_duration, datestr_to_iso, try_func
from ..items import Review, Movie, Plot


class IMDBSpider(scrapy.Spider):
    name = "imdb"

    _DOMAIN = "https://www.imdb.com"

    start_urls = ["https://www.imdb.com/search/title/?title_type=feature,tv_movie&count=250"]

    REVIEWS_LIMIT = 1000  # The API returns at most 1000 reviews

    def reviews_api_url(self, movie_slug, datakey=None):
        """
        Generate the URL for the API that returns the reviews of a movie.

        :param movie_slug: the slug of the movie, i.e. the part of the URL that identifies the movie
        :param datakey: the offset of the reviews to return, expressed as a string found in the HTML of reviews page
        :return: the URL of the API
        """
        url = f"{self._DOMAIN}/title/{movie_slug}/reviews/_ajax?sort=reviewVolume&dir=desc&ratingFilter=0"
        if datakey:
            url = f"{url}&dataKey={datakey}"
        return url

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
        return f"{self._DOMAIN}/title/tt{next_movie_id}/{'/'.join(rest_url)}"

    def extract_reviews(self, response: Response, extracted: int = 0) -> Generator[Review, None, None]:
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
                yield Review(url=f"{self._DOMAIN}{permalink}", movie_id=self.get_movie_id(response.url), score=score,
                             text=text)
        next_datakey = response.xpath("//div[@class='load-more-data']/@data-key")

        current_movie_id = self.get_movie_id(response.url)
        if extracted < self.REVIEWS_LIMIT and next_datakey:
            next_datakey = next_datakey.get()
            next_url = self.reviews_api_url(f"tt{current_movie_id}", next_datakey)
            yield response.follow(next_url, callback=self.extract_reviews, cb_kwargs={"extracted": extracted})

    def parse_metadata(self, response: Response) -> Movie.Metadata:
        url = response.xpath("//link[@rel='canonical']/@href").get()
        image_url = response.xpath("//meta[@property='og:image']/@content").get()
        page_title = response.xpath("//title/text()").get()
        return Movie.Metadata(url=url, image_url=image_url, page_title=page_title)

    def parse_plot(self, response: Response, movie_id: str, similar_movies: list[str]):
        plot = response.xpath(
            "//div[@data-testid='sub-section-synopsis']//div[@class='ipc-html-content-inner-div']//text()").getall()
        yield Plot(movie_id=movie_id, text=''.join(plot))

        for movie_relative_url in similar_movies:
            yield response.follow(self._DOMAIN + movie_relative_url, callback=self.parse_movie)

    def parse_movie(self, response: Response) -> Movie:
        """
        Parse a movie page, yielding a `Movie` for the movie.

        :param response: the response of the movie page
        :return: a `Movie` for the movie
        """
        movie_id = self.get_movie_id(response.url)
        title = response.css("h1 ::text").get()
        description = response.xpath("//meta[@name='description']/@content").get()

        release_date_str = response.xpath("//section[@cel_widget_id='StaticFeature_Details']").css(
            "a.ipc-metadata-list-item__list-content-item::text").get()
        release_date_str = release_date_str.split("(")[0].strip()
        release_date = datestr_to_iso(release_date_str)

        duration_str = ''.join(response.xpath("//section[@cel_widget_id='StaticFeature_TechSpecs']").css(
            "div.ipc-metadata-list-item__content-container::text").getall())
        duration = parse_duration(duration_str)

        genres = response.xpath("//div[@data-testid='genres']").css("a.ipc-chip span::text").getall()
        score = float(response.css("span.cMEQkK::text").get() or float('nan'))

        director = response.css("ul.title-pc-list").css("a::text").get()
        actors = response.css("a.gCQkeh::text").getall()

        metadata = self.parse_metadata(response)

        similar_movies = response.xpath("//div[@data-testid='shoveler-items-container']").css(
            "a.ipc-poster-card__title--clickable::attr(href)").getall()

        yield Movie(movie_id=movie_id, title=title, description=description, release=release_date, duration=duration,
                    genres=genres, score=score, director=director, actors=actors, metadata=metadata)
        yield response.follow(f"{self._DOMAIN}/title/tt{movie_id}/plotsummary/", callback=self.parse_plot,
                              cb_kwargs={"movie_id": movie_id, "similar_movies": similar_movies})

    def parse_movie_list(self, response: Response, start: int = 0):
        movie_urls = response.css("a.ipc-title-link-wrapper::attr(href)").getall()

        for relative_url in movie_urls:
            # url: /title/tt0000001/
            relative_url = relative_url.split("?")[0][:-1]
            url = self._DOMAIN + relative_url
            yield response.follow(url + "/", callback=self.parse_movie)

        # no next page: the loading is with javascript  # if not ab:  #     next_page = self._DOMAIN + response.css("a.lister-page-next::attr(href)").get()  # else:  #     next_page = self.start_urls[0] + "&start=" + str(start + 250)  # if next_page:  #     if self._DOMAIN not in next_page:  #         next_page = self._DOMAIN + next_page  #     yield response.follow(next_page, callback=self.parse_movie_list, cb_kwargs={"start": start + 250})

    def parse(self, response: Response, **kwargs: Any) -> Any:
        if response.url == self.start_urls[0]:
            yield from self.parse_movie_list(response)
