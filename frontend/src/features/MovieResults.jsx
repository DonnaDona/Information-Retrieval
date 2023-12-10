import React from 'react'
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


    axios.get(`/search?q=${searchParams.get("q", "")}`)
        .then((response) => {
            setMovieData(response.data);
        })
        .catch((error) => {
            console.error(error);
        });

    const formatMovieUrls = (movie) => [
        {name: "IMDB", url: movie.urls?.imdb, image: "../../public/imdb.png"},
        {name: "Metacritic", url: movie.urls?.metacritic, image: "../../public/metacritic.png"},
        {
            name: "Rotten Tomatoes",
            url: movie.urls?.rotten_tomatoes,
            image: "../../public/tomato.png"
        }
    ];

    return (
        <Stack>
            <TopBar/>
            <Stack flexWrap="wrap" flexDirection="row" justifyContent="flex-start" paddingTop={10} paddingLeft={3}>
                {movieData.map((movie, index) => (
                    <MovieCard
                        key={index}
                        title={movie.title}
                        release={movie.release}
                        description={movie.description.split(" ").slice(0, 10).join(" ") + "..."}
                        image={movie.image || "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"}
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