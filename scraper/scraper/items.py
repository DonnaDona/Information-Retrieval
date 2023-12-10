# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from typing import List

import scrapy


@dataclass
class Review:
    movie_id: str
    id: str  # the id of the review (unique in the `source_name` website)
    title: str
    score: float
    content: str
    source_name: str


@dataclass
class Movie:
    @dataclass
    class Metadata:
        url: str
        source_name: str
        image_url: str
        page_title: str

    movie_id: str

    title: str
    description: str
    release: int  # just the year, no need for date operations
    duration: int
    genres: List[str]  # sorted list of genres
    score: float
    critic_score: float

    directors: List[str]  # sorted list of directors
    actors: List[str]  # sorted list of actors

    metadata: Metadata

    plot: str = ""  # set by pipeline (MergePipeline)
    wait_for_plot: bool = False  # checked by pipeline (MergePipeline)


@dataclass
class Plot:
    """
    A plot item for a movie.
    
    The pipeline will merge this with the movie item.
    """
    movie_id: str
    text: str
