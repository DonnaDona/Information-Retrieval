import {useEffect, useState} from 'react';
import {Alert, CircularProgress, Snackbar, Stack, Typography} from "@mui/material";
import {TopBar} from "../components/TopBar.jsx";
import {MovieCard} from "../components/MovieCard.jsx";
import {useSearchParams} from "react-router-dom";
import {useDispatch} from "react-redux";
import {setQuery} from "./searchSlice.jsx";
import {computeMovieCardProps} from "../utils.js";
import axios from "axios";
import {RecommendationsBar} from "../components/RecommendationsBar.jsx";

export function MovieResults() {

    const [searchParams] = useSearchParams();
    const dispatch = useDispatch();
    dispatch(setQuery(searchParams.get("q", "")));
    const query = searchParams.get("q", "");

    const [items, setItems] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [visibleError, setVisibleError] = useState(false);
    const [nextUrl, setNextUrl] = useState(`/search/?q=${query}&page=1`);

    const fetchData = async (tried=0) => {
        setIsLoading(true);
        setError(null);

        try {
            const url = nextUrl;
            const response = await axios.get(url);
            setItems([...items, ...response.data.results]);
            setNextUrl(response.data.next);

        } catch (error) {
            if (tried < 3) {
                await new Promise((resolve) => setTimeout(resolve, 500));
                fetchData(tried + 1);
                return;
            }
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
        if (scrollTop + clientHeight >= scrollHeight * threshold) fetchData();

    };

    useEffect(() => {
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [isLoading]);


    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }

        setVisibleError(false);
    }

    return (<>
        <TopBar/>
        <Stack direction={"row"}>
            <Stack flexGrow={1}>
                <Stack justifyContent="center">
                    {items.length > 0 &&
                        <Stack flexWrap="wrap" flexDirection="row" justifyContent="start" marginTop={4} paddingLeft={3}>
                            {items.map((movie, index) => (<MovieCard
                                key={index}
                                {...computeMovieCardProps(movie)}
                            />))}
                        </Stack>}
                    {items.length === 0 && !isLoading &&
                        <Stack justifyContent="center" alignItems="center" marginTop={24}>
                            <img src="/no-results.png" alt="logo" width="300" height="310"/>
                            <Typography component="h2" variant="span" marginTop={4}>No results found</Typography>
                        </Stack>}
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
            {items.length > 0 && (<RecommendationsBar query={query}/>)}
        </Stack></>)
}