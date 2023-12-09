import React from 'react'
import {Box, Stack} from "@mui/material";
import {TopBar} from "../components/TopBar.jsx";
import {MovieCard} from "../components/MovieCard.jsx";

export function MovieResults() {

    const movieData = [
        {title: "The Matrix", release: "1999", description: "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.", image: "https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Poster.jpg", rating: "8.7", duration: "2h 16m"},
        {title: "The Matrix Reloaded", release: "2003", description: "Freedom fighters Neo, Trinity and Morpheus continue to lead the revolt against the Machine Army, unleashing their arsenal of extraordinary skills and weaponry against the systematic forces of repression and exploitation.", image: "https://upload.wikimedia.org/wikipedia/en/b/ba/Poster_-_The_Matrix_Reloaded.jpg", rating: "7.2", duration: "2h 18m"},
        {title: "The Matrix Revolutions", release: "2003", description: "The human city of Zion defends itself against the massive invasion of the machines as Neo fights to end the war at another front while also opposing the rogue Agent Smith.", image: "https://upload.wikimedia.org/wikipedia/en/3/34/Matrix_revolutions_ver7.jpg", rating: "6.7", duration: "2h 9m"},
        {title: "The Matrix Resurrections", release: "2021", description: "The Matrix Resurrections is an upcoming American science fiction action film produced, co-written, and directed by Lana Wachowski. It is the fourth installment in The Matrix film series, and a sequel to The Matrix Revolutions (2003).", image: "", rating: "N/A", duration: "N/A"},
        {title: "The Matrix", release: "1999", description: "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.", image: "https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Poster.jpg", rating: "8.7", duration: "2h 16m"},
    ]

    return (
        <Box>
            <TopBar/>
            <Stack flexWrap="wrap" flexDirection="row" justifyContent="center" paddingTop={10}>
                {movieData.map((movie, index) => (
                    <MovieCard
                        key={index}
                        title={movie.title}
                        release={movie.release}
                        description={movie.description.split(" ").slice(0, 10).join(" ") + "..."}
                        image={movie.image || "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"}
                        rating={movie.rating}
                        duration={movie.duration}
                    />
                ))}
            </Stack>

        </Box>
    )
}