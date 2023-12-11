import React, {useEffect, useState} from 'react';
import {Alert, CircularProgress, Snackbar, Stack} from "@mui/material";
import {TopBar} from "../components/TopBar.jsx";
import {MovieCard} from "../components/MovieCard.jsx";
import {useSearchParams} from "react-router-dom";
import {useDispatch} from "react-redux";
import {setQuery} from "./searchSlice.jsx";
import axios from "axios";

export function MovieResults() {

    const [searchParams] = useSearchParams();
    const dispatch = useDispatch();
    dispatch(setQuery(searchParams.get("q", "")));
    const query = searchParams.get("q", "");

    const [items, setItems] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [visibleError, setVisibleError] = useState(false);
    const [nextUrl, setNextUrl] = useState(null);

    const fetchData = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const url = nextUrl || `/search/?q=${query}`;
            const response = await axios.get(url);
            setItems([...items, ...response.data.results]);
            setNextUrl(response.data.next);

        } catch (error) {
            setError(error);
            setVisibleError(true);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        setItems([]);
        fetchData();
    }, [query]);

    const handleScroll = () => {
        const threshold = 0.9;
        if (isLoading || error || !nextUrl) return;
        const scrollHeight = document.documentElement.scrollHeight;
        const scrollTop = document.documentElement.scrollTop;
        const clientHeight = document.documentElement.clientHeight;
        if (scrollTop + clientHeight >= scrollHeight * threshold)
            fetchData();

    };

    useEffect(() => {
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [isLoading]);

    const formatMovieUrls = (movie) => {
        const names = ["imdb", "metacritic", "rotten tomatoes"];
        const images = {
            "imdb": "../../public/imdb.png",
            "metacritic": "../../public/metacritic.png",
            "rotten tomatoes": "../../public/tomato.png"
        };
        const upper_names = {"imdb": "IMDb", "metacritic": "Metacritic", "rotten tomatoes": "RT"};
        const urls = [];
        for (const name of names) {
            if (movie.data_sources?.[name]) {
                urls.push({name: upper_names[name], url: movie.data_sources[name].url, image: images[name]});
            }
        }
        console.log(urls);
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

    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }

        setVisibleError(false);
    }

    return (
        <Stack>
            <TopBar/>
            <Stack justifyContent="center">
                <Stack flexWrap="wrap" flexDirection="row" justifyContent="start" marginTop={4} paddingLeft={3}>
                    {items.map((movie, index) => (
                        <MovieCard
                            key={index}
                            title={movie.title}
                            release={movie.release}
                            description={movie.description}
                            image={movie.image_url || "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"}
                            rating={formatMovieRating(movie)}
                            duration={movie.duration !== null ? movie.duration : ""}
                            genres={movie.genres}
                            urls={formatMovieUrls(movie)}
                        />
                    ))}
                </Stack>
            </Stack>
            {(nextUrl !== null && error === null) &&
                <Stack alignItems="center" marginX={46} marginY={16}><CircularProgress thickness={4}
                                                                                       size={60}/></Stack>}

            <Snackbar open={visibleError} autoHideDuration={6000} onClose={handleClose}>
                <Alert onClose={handleClose} variant="filled" severity="error" sx={{width: '100%'}}>
                    There was an error loading the movies. Please try again later.
                </Alert>
            </Snackbar>
        </Stack>
    )
}