import logging
from random import random, shuffle
from typing import Generator, Any

import scrapy
from scrapy.http import Response

from .utils import parse_duration
from ..items import Review, Movie, Plot


class IMDBSpider(scrapy.Spider):
    name = "imdb"

    RANDOM_WALK = True
    RANDOM_WALK_PROBABILITY = 0.05  # probability of following a random link instead of the next one

    _DOMAIN = "https://www.imdb.com"

    start_urls = ["https://www.imdb.com/search/title/?title_type=feature,tv_movie&count=250"]

    REVIEWS_LIMIT = 50  # The API returns at most 1000 reviews

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

    def reviews_api_url(self, movie_slug, datakey=None):
        """
        Generate the URL for the API that returns the reviews of a movie.

        :param movie_slug: the slug of the movie, i.e. the part of the URL that identifies the movie
        :param datakey: the offset of the reviews to return, expressed as a string found in the HTML of reviews page
        :return: the URL of the API
        """
        url = f"{self._DOMAIN}/title/{movie_slug}/reviews/_ajax?sort=reviewVolume&dir=desc&ratingFilter=0"
        if datakey:
            url = f"{url}&paginationKey={datakey}"
        return url

    def extract_reviews(self, response: Response, extracted: int = 0) -> Generator[Review, None, None]:
        """
        Extract the reviews from a movie page.

        :param response: the response of the movie page
        :param extracted: the number of reviews extracted so far for the current movie
        :return: a generator of reviews for the movie
        """
        reviews = response.css("div.lister-item")
        for review in reviews:
            review_id = review.xpath("./@data-review-id").get()
            score = review.xpath(
                ".//div[@class='ipl-ratings-bar']//span[@class='rating-other-user-rating']//span//text()").get()
            title = review.xpath(".//a[@class='title']/text()").get().strip()
            text = '\n'.join(review.xpath(".//div[@class='text show-more__control']/text()").getall())
            if score and text:
                extracted += 1
                yield Review(movie_id=self.get_movie_id(response.url), score=float(score), title=title, content=text,
                             source_name="IMDb", id=review_id)
                if extracted >= self.REVIEWS_LIMIT:
                    return
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
        return Movie.Metadata(url=url, image_url=image_url, page_title=page_title, source_name="IMDb")

    def parse_plot(self, response: Response, movie_id: str):
        plot = response.xpath(
            "//div[@data-testid='sub-section-synopsis']//div[@class='ipc-html-content-inner-div']//text()").getall()

        if not plot:
            summaries = response.xpath(
                "//div[@data-testid='sub-section-summaries']//li//div[@class='ipc-html-content-inner-div']/text()").getall()
            if not summaries or len(summaries) == 0:
                plot = ""
            else:
                plot = max(summaries, key=len)

        yield Plot(movie_id=movie_id, text=''.join(plot))

    def parse_movie(self, response: Response, depth: int = 0) -> Generator[Any, None, None]:
        """
        Parse a movie page, yielding a `Movie` for the movie.

        :param response: the response of the movie page
        :param depth: The depth of the current request. Each time a linked is followed in the "similar movies" section,
                      the depth increases.
        :return: a `Movie` for the movie
        """
        movie_id = self.get_movie_id(response.url)
        page_type = response.xpath("//meta[@property='og:type']/@content")

        similar_movies = response.xpath("//div[@data-testid='shoveler-items-container']").css(
            "a.ipc-poster-card__title--clickable::attr(href)").getall()
        shuffle(similar_movies)  # increase randomness

        if page_type and page_type.get() == "video.movie":
            try:
                title = response.css("h1 ::text").get()
                description = response.xpath("//meta[@name='description']/@content").get()

                # release_year_str is the first a child of the ul adjacent to the h1
                release_year_str = response.xpath("//h1/following-sibling::ul//a/text()").get()

                release_year = int(release_year_str)

                duration_str = ''.join(response.xpath("//section[@cel_widget_id='StaticFeature_TechSpecs']").css(
                    "div.ipc-metadata-list-item__content-container::text").getall())
                duration = parse_duration(duration_str)

                genres = response.xpath("//div[@data-testid='genres']").css("a.ipc-chip span::text").getall()
                score = float(response.css("span.cMEQkK::text").get() or float('nan'))

                # get all the a text of the first li of the first ul with class ipc-metadata-list
                directors = response.css("ul.ipc-metadata-list")[0].css("li")[0].css("a::text").getall()
                actors = response.css("a.gCQkeh::text").getall()

                metadata = self.parse_metadata(response)

                logging.info(f"Movie {movie_id} parsed (depth {depth})")

                yield Movie(movie_id=movie_id, title=title, description=description, release=release_year,
                            duration=duration, genres=genres, score=score, critic_score=score, directors=directors,
                            actors=actors, metadata=metadata, wait_for_plot=True)

                yield response.follow(f"{self._DOMAIN}/title/tt{movie_id}/plotsummary/", callback=self.parse_plot,
                                      priority=2,  # highest priority: the plot is the most important information now
                                      cb_kwargs={"movie_id": movie_id})

                yield response.follow(self.reviews_api_url(f"tt{movie_id}"), callback=self.extract_reviews, priority=2,
                                      # high priority: the reviews are important
                                      cb_kwargs={"extracted": 0})


            except Exception as e:
                # the movie could not be parsed, but the walk should continue
                logging.error(f"Error while parsing movie {movie_id}: {e}")

        # Both movie information and plot were scraped, go to the next movie
        if self.RANDOM_WALK:
            if (len(self.movies_list) > 0  # There is actually a race condition here, but it should be fine
                    and random() < self.RANDOM_WALK_PROBABILITY):
                yield response.follow(self.movies_list.pop(), callback=self.parse_movie, priority=1,
                                      cb_kwargs={"depth": 0})
                logging.info("Following random link instead of the next one")

        for movie_relative_url in similar_movies:
            logging.info(f"Following similar movie {movie_relative_url}")
            yield response.follow(self._DOMAIN + movie_relative_url, callback=self.parse_movie, priority=-depth,
                                  cb_kwargs={"depth": depth + 1})

    def parse_movie_list(self, response: Response, start: int = 0):
        movie_urls = response.css("a.ipc-title-link-wrapper::attr(href)").getall()

        shuffle(movie_urls)

        if self.RANDOM_WALK:
            # if the random walk is enabled, only the first movie is parsed; after this, there is a probability
            # (1 - RANDOM_WALK_PROBABILITY) of exploring the similar movies of the current movie, and a probability
            # RANDOM_WALK_PROBABILITY of following a random link in self.movies_list.
            self.movies_list = [self._DOMAIN + movie_url for movie_url in reversed(movie_urls)]
            # suffle the movies list
            yield response.follow(self.movies_list.pop(), callback=self.parse_movie, priority=1, cb_kwargs={"depth": 0})
            return

        for relative_url in movie_urls:
            # url: /title/tt0000001/
            relative_url = relative_url.split("?")[0][:-1]
            url = self._DOMAIN + relative_url
            yield response.follow(url + "/", callback=self.parse_movie, priority=1, cb_kwargs={"depth": 0})

        # no next page: the loading is with javascript  # if not ab:  #     next_page = self._DOMAIN + response.css("a.lister-page-next::attr(href)").get()  # else:  #     next_page = self.start_urls[0] + "&start=" + str(start + 250)  # if next_page:  #     if self._DOMAIN not in next_page:  #         next_page = self._DOMAIN + next_page  #     yield response.follow(next_page, callback=self.parse_movie_list, cb_kwargs={"start": start + 250})

    def parse(self, response: Response, **kwargs: Any) -> Any:
        if response.url == self.start_urls[0]:
            yield from self.parse_movie_list(response)
        else:
            yield from self.parse_movie(response, depth=0)
