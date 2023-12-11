import React, {useEffect} from 'react'
import {Stack} from "@mui/material";
import {TopBar} from "../components/TopBar.jsx";
import {MovieCard} from "../components/MovieCard.jsx";
import {useSearchParams} from "react-router-dom";
import {useDispatch} from "react-redux";
import {setQuery} from "./searchSlice.jsx";
import axios from "axios";

export function MovieResults() {

    const [searchParams] = useSearchParams();
    const dispatch = useDispatch();
    const [movieData, setMovieData] = React.useState([]);
    dispatch(setQuery(searchParams.get("q", "")));


    useEffect(()=>{
        axios.get(`/search?q=${searchParams.get("q", "")}`)
            .then((response) => {
                console.log(response.data.results);
                setMovieData(response.data.results);
            })
            .catch((error) => {
                console.error(error);
            });
    },[]);

    const formatMovieUrls = (movie) => {
        const names =["imdb", "metacritic", "rotten tomatoes"];
        const images = {"imdb": "../../public/imdb.png", "metacritic": "../../public/metacritic.png", "rotten tomatoes": "../../public/tomato.png"};
        const upper_names = {"imdb": "IMDb", "metacritic": "Metacritic", "rotten tomatoes": "RT"};
        const urls = [];
        console.log(movie.data_sources);
        for (const name of names) {
            if (movie.data_sources?.[name]) {
                urls.push({name: upper_names[name], url: movie.data_sources?.[name], image: images[name]});
            }
        }
        return urls;
    }

    return (
        <Stack>
            <TopBar/>
            <Stack flexWrap="wrap" flexDirection="row" justifyContent="flex-start" paddingTop={10} paddingLeft={3}>
                {movieData.map((movie, index) => (
                    <MovieCard
                        key={index}
                        title={movie.title}
                        release={movie.release}
                        description={movie.description}
                        image={movie.image_url || "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"}
                        rating={movie.rating}
                        duration={movie.duration !== null ? movie.duration : ""}
                        genres={movie.genres}
                        urls={formatMovieUrls(movie)}
                    />
                ))}
            </Stack>
        </Stack>
    )
}