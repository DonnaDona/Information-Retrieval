import json
import logging
from typing import Any

import scrapy
from scrapy.http import Response

from .utils import datestr_to_iso, parse_duration
from ..items import Movie


class RottenTomatoesSpider(scrapy.Spider):
    name = "rottentomatoes"

    _DOMAIN = "https://www.rottentomatoes.com"
    PAGE_LIST_URL = f"{_DOMAIN}/napi/browse/movies_at_home/sort:popular"

    start_urls = [PAGE_LIST_URL]

    def parse_scores(self, response: Response):
        json_str = response.xpath("//script[@id='scoreDetails']/text()").get()
        scores_json = json.loads(json_str)
        scoreboard = scores_json["scoreboard"]
        if not scoreboard or len(scoreboard) == 0:
            return float('nan'), float('nan')

        critic_score = float('nan')
        audience_score = float('nan')

        if "tomatometerScore" in scoreboard and "value" in scoreboard["tomatometerScore"]:
            critic_score = float(scoreboard["tomatometerScore"]["value"])
        if "audienceScore" in scoreboard and "value" in scoreboard["audienceScore"]:
            audience_score = float(scoreboard["audienceScore"]["value"])

        return critic_score, audience_score

    def parse_movie(self, response: Response):
        page_type = response.xpath("//meta[@property='og:type']/@content")
        if page_type.get() == "video.movie":
            movie_id = response.url.split("/")[4]
            title = response.css("h1.title::text").get().strip()
            description = response.xpath("//meta[@property='og:description']/@content").get().strip()

            movie_info = response.xpath("//ul[@id='info']")
            movie_info_selector = lambda title: movie_info.xpath(f"//li[contains(.//b/text(), '{title}')]//span")

            release_str = movie_info_selector("Release Date (Theaters):").xpath("./time/@datetime").get()
            if not release_str:
                release_str = movie_info_selector("Release Date (Streaming):").xpath("./time/@datetime").get()
            release = datestr_to_iso(release_str, "%b %d, %Y")

            genre = movie_info_selector("Genre:").xpath("./text()").get()
            genre = [g.strip() for g in genre.split(",")]

            duration_str = movie_info_selector("Runtime:").xpath("./time/text()").get()
            # parse_duration expects a space between numbers and units
            duration_str = duration_str.replace("m", " m").replace("h", " h")
            duration = parse_duration(duration_str)

            director = movie_info_selector("Director:").xpath("./a/text()").get()

            critic_score, audience_score = self.parse_scores(response)

            metadata = Movie.Metadata(url=response.xpath("//link[@rel='canonical']/@href").get(),
                                      image_url=response.xpath("//meta[@property='og:image']/@content").get(),
                                      page_title=response.css("title::text").get().strip(),
                                      source_name="Rotten Tomatoes")

            plot = response.xpath("//p[@data-qa='movie-info-synopsis']/text()").get().strip()

            # get the div that contains the class .cast-and-crew-item
            actors = response.xpath("//div[contains(@class, 'cast-and-crew-item')]//a/p/text()").getall()
            actors = [a.strip() for a in actors]

            yield Movie(movie_id=movie_id, title=title, description=description, release=release, duration=duration,
                        genres=genre, score=audience_score, critic_score=critic_score, director=director, actors=actors,
                        plot=plot, metadata=metadata)

    def parse_movie_list(self, response: Response) -> Any:
        response_json = response.json()
        movies = response_json["grid"]["list"]
        next_page = response_json["pageInfo"]["endCursor"]

        movie_urls = [f"{self._DOMAIN}{movie['mediaUrl']}" for movie in movies]

        yield from response.follow_all(movie_urls, callback=self.parse_movie, priority=1)

        if next_page:
            yield response.follow(f"{self.PAGE_LIST_URL}?after={next_page}", callback=self.parse_movie_list, priority=0)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        yield from self.parse_movie_list(response)
