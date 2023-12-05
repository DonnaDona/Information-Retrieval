# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass

import scrapy
from typing import List


@dataclass
class Review(scrapy.Item):
    movie_id: str
    url: str
    score: float
    title: str
    text: str


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
    release: str  # use datestr_to_iso
    duration: int
    genres: List[str]
    score: float
    critic_score: float

    director: str
    actors: List[str]

    metadata: Metadata

    plot: str = ""  # set by pipeline (MergePipeline)
    wait_for_plot: bool = False # checked by pipeline (MergePipeline)


@dataclass
class Plot:
    """
    A plot item for a movie.
    
    The pipeline will merge this with the movie item.
    """
    movie_id: str
    text: str
