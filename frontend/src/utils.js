const formatMovieUrls = (movie) => {
    const names = ["imdb", "metacritic", "rotten tomatoes"];
    const images = {
        "imdb": "/imdb.png", "metacritic": "/metacritic.png", "rotten tomatoes": "/tomato.png"
    };
    const upper_names = {"imdb": "IMDb", "metacritic": "Metacritic", "rotten tomatoes": "RT"};
    const urls = [];
    for (const name of names) {
        if (movie.data_sources?.[name]) {
            urls.push({name: upper_names[name], url: movie.data_sources[name].url, image: images[name]});
        }
    }
    return urls;
}

const formatMovieRating = (movie) => {
    const names = ["imdb", "metacritic", "rotten tomatoes"];
    let avgRating = 0;
    let count = 0;

    for (const name of names) {
        if (name in movie.data_sources && movie.data_sources[name].score !== null) {
            avgRating += movie.data_sources[name].score;
            count++;
        }
    }
    if (count === 0) return null;

    avgRating = avgRating / count;

    return avgRating.toFixed(1);
}

function computeMovieCardProps(movie) {
    return {
        title: movie.title,
        release: movie.release,
        description: movie.description.substring(0, 300) + "...",
        image: movie.image_url || "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png",
        rating: formatMovieRating(movie),
        duration: movie.duration !== null ? movie.duration : "",
        genres: movie.genres,
        urls: formatMovieUrls(movie)
    }
}

export {computeMovieCardProps};