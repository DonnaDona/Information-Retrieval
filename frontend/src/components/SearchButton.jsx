import React from 'react'
import {Button} from "@mui/material";
import {useDispatch, useSelector} from "react-redux";
import {selectQuery, setShowResults} from "../features/searchSlice.jsx";

export function SearchButton() {
    const dispatch = useDispatch();
    const query = useSelector(selectQuery);

    const handleClick = () => {
        dispatch(setShowResults(true));
    }

    return (
        <Button variant="contained" onClick={handleClick} disabled={!query} sx={{width: '100%', borderRadius: '10px'}}>
            Search
        </Button>
    )
}