import React from 'react'
import {Button} from "@mui/material";
import {useSelector} from "react-redux";
import {selectQuery} from "../features/searchSlice.jsx";

export function SearchButton() {
    const query = useSelector(selectQuery);

    const viewResults = () => {
        window.location.href = `/results?q=${encodeURIComponent(query)}`;
    }

    return (
        <Button onClick={viewResults} variant="contained" disabled={!query} sx={{width: '100%', borderRadius: '10px'}}>
            Search
        </Button>
    )
}