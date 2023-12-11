import {useEffect, useState} from "react";
import axios from "axios";
import {Box, Container, Stack, Typography} from "@mui/material";
import {MovieCard} from "./MovieCard.jsx";
import {computeMovieCardProps} from "../utils.js";
import KeyboardDoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight';
import KeyboardDoubleArrowLeftIcon from '@mui/icons-material/KeyboardDoubleArrowLeft';

export function RecommendationsBar({query}) {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [items, setItems] = useState([]);
    const [isOpen, setOpen] = useState(true);

    const fetchData = async (retries = 0) => {
        setLoading(true);
        setError(null);
        try {
            const url = `/recommend/?q=${query}`;
            const response = await axios.get(url);
            setItems(response.data);
        } catch (error) {
            if (retries < 3) {
                await new Promise((resolve) => setTimeout(resolve, 500));
                fetchData(retries + 1);
                return
            }
            setError(error);
            setVisibleError(true);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchData();
    }, [query]);
    
    function computeArrow() {
        const style = {
            color: '#888888',
            marginLeft: '-24px',
            cursor: 'pointer'
        }
        if (!isOpen) {
            return <KeyboardDoubleArrowLeftIcon sx={style} fontSize={"large"}
                                               onClick={() => setOpen(!isOpen)}/>
        } else {
            return <KeyboardDoubleArrowRightIcon sx={style} fontSize={"large"}
                                                onClick={() => setOpen(!isOpen)}/>
        }
    }

    return items.length > 0 && (<Box sx={{
        transition: 'width 0.3s ease-in-out',
        paddingTop: 2,
        paddingLeft: 6,
        paddingRight: 3,
        background: 'rgba(255,255,255,.8)',
        borderLeft: 2,
        width: isOpen ? '400px' : '0%',
    }}
                 justifyContent={'center'} alignItems={'center'}>
        {computeArrow()}
        <div style={{marginLeft: isOpen ? 0 : 16}}>
            <Typography variant="h5" color={"black"} sx={{
                marginLeft: 2, paddingBottom: 2, fontWeight: 'bold'
            }}>Recommendations</Typography>
            <Stack>
                {items.map((movie, idx) => (
                    <MovieCard key={idx} {...computeMovieCardProps(movie)} description={null} height={300}/>))}
            </Stack>
        </div>
    </Box>)
}

