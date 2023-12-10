# Scraper

This sub-directory contains the Scrapy project for scraping the movie data.

## Websites

The following websites are scraped:

- [IMDb](https://www.imdb.com/)
- [Metacritic](https://www.metacritic.com/)
- [Rotten Tomatoes](https://www.rottentomatoes.com/)

The spider for each of these websites is located in `scraper/spiders/`.

## Setup

To run any spider, it is assumed that a .env file exists in the root of the project.

Checkout the root-level README for more information on the .env file.

In particular, the following environment variables are used:

- `USE_POSTGRES`: Whether to use PostgreSQL or default standard output

In case of PostgreSQL:

- `DB_HOST`: Hostname of the PostgreSQL server
- `DB_PORT`: Port of the PostgreSQL server
- `DB_NAME`: Name of the database
- `DB_USER`: Username of the database user
- `DB_PASSWORD`: Password of the database user

## Data model

The structure of the movie can be seen in `scraper/items.py`. Note that the database structure is slightly different;
for more details see `PostgresPipeline` in `scraper/pipelines.py`.

## Running

Assuming all the required Python packages are installed, the spiders can be run from inside this directory using the
following command:

```bash
scrapy crawl imdb # Run the IMDb spider
```

```bash
scrapy crawl metacritic # Run the Metacritic spider
```

```bash
scrapy crawl rottentomatoes # Run the Rotten Tomatoes spider
```

## Spiders description

### IMDb spider

The IMDb spider follows these steps:

1. Fetch the top 250 movies from https://www.imdb.com/chart/top/
2. For each movie, fetch the movie page
    - Extract from the page the information about the movie
    - Fetch the plot page and extract the plot, if available
3. For each movie, visit the next page
    - With probability 0.95 (95%), visit every movie in the "Similar Movies" section of the current movie's page.
    - With probability 0.05 (5%), visit the next page of the top 250 movies.
4. Repeat step 3 until there are no more pages to visit.

The choice of this process is due to the fact that IMDb tries to prevent scraping by having no pagination, but only
dynamically loaded content: there is no list of all movies that can be scraped. The only way to get the most important
movies was to load the 250 most popular movies and then follow the "Similar Movies" links.

It's relevant to add that the requests are scheduled in a "hierarchical" way: the importance of a movie is lower as
it's depth increases. This is done to ensure that every "similar" movie is scraped before going to the next round of 
similar movies.
When the spider goes back to the top 250 movies, the depth for that request is reset to 0.

Unfortunately the IMDb spider scrapes much less movies than the other two, because the "Similar Movies" section often
suggests movies that were scraped before, and the spider will skip them.

### Metacritic spider

The Metacritic spider follows these steps:

1. Load the first page of the "Browse movies" page (https://www.metacritic.com/browse/movie/)
2. For each movie, fetch the movie page
    - Extract from the page the information about the movie
3. Load the next page and repeat step 2 until there are no more pages to visit.

Metacritic contains 15,890 movies; some of them cannot be scraped because they lack some information (e.g. release year,
duration, etc.). The spider will skip these movies and continue with the next one.

### Rotten Tomatoes spider

The Rotten Tomatoes spider works in a similar way to the Metacritic spider.
The only difference is in how it fetches the list of movies: while Metacritic can exploit the pagination of the browse
page to get all the movies, RottenTomatoes uses dynamic loading; for this reason, we used the API that the website
uses to load the movies.

Specifically, calling the API returns a list of movies with their respective urls. After the spider visits each of 
these movies, it calls the API again with an `after` parameter specified in the previous response, which returns the
next page of movies. This process is repeated until the API returns an empty list of movies.

## Pipelines

The pipelines are located in `scraper/pipelines.py`.

The pipelines are executed in the following order:
- `MergePipeline`: merges the movie objects with their respective plots (only for IMDb)
- `FormatPipeline`: format the movie object correctly to be inserted in the database
- `PostgresPipeline`: insert the movie object in the database

### MergePipeline
IMDb has the plot of the movie in a separate page, so the spider has to fetch it separately. This pipeline merges the
plot with the movie object.

The field `movie_id` is used to recognize the plot corresponding to a specific movie.
If a movie arrives but the plot is not yet available, the movie is stored in a temporary buffer. When the plot arrives,
the movie is retrieved from the buffer and the plot is merged with it.

Although supported, the other way around is not possible: the requests for the plots are scheduled only after the movie
has been scraped, so it's not possible for a plot to arrive before the movie.

### FormatPipeline
This pipeline formats the movie object correctly to be inserted in the database.

As of now, this consists only in sorting all the arrays in the movie object, so that the order of the elements in the
db is consists.
This is required since the `directors` field is used as a key in the database, and the order of the elements in the
array is relevant.

### PostgresPipeline
This pipeline inserts the movie object in the database.
The pipeline is executed only if the `USE_POSTGRES` environment variable is set to `true`.

The database is PostgreSQL, and the connection is made using the `psycopg2` library.

The database has two tables: `movies` and `data_sources`.

#### `movies` table
The movies table describes a movie, independently of the website it was scraped from, to avoid duplicates.

When a movie is scraped, the spider checks if the movie is already present in the database. 
If it is not, the movie is inserted in the database, otherwise the movie is updated with the "most relevant" 
information.
In the case of plot and description, the longest one is kept; in the case of genres, the union of the two is kept.
All the other fields are updated if they are empty in the database.

This way, only one entry exists for a specific movie, but it merges the information from all the websites.

#### `data_sources` table
The data_sources table describes the source of the information for a specific movie.

Each movie can have multiple sources, since it can be scraped from multiple websites. 

The table has a foreign key to the `movies` table, and multiple fields containing information about the website
the movie was scraped from.

Basically, everything that is about the movie itself is stored in the `movies` table, while everything that is about
the source of the information is stored in the `data_sources` table.

For example, in the `data_sources` there is the name of the website, the score the movie has on that website,
the url that was scraped, etc.
For more details, see the `PostgresPipeline` class in `scraper/pipelines.py`.
