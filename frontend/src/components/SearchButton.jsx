import React from 'react'
import {Button} from "@mui/material";
import {useDispatch, useSelector} from "react-redux";
import {selectQuery} from "../features/searchSlice.jsx";
import {useNavigate} from "react-router-dom";

export function SearchButton() {
    const query = useSelector(selectQuery);
    const navigate = useNavigate();

    const viewResults = () => {
        navigate(`/results?q=${encodeURIComponent(query)}`);
    }

    return (
        <Button onClick={viewResults} variant="contained" disabled={!query} sx={{width: '100%', borderRadius: '10px'}}>
            Search
        </Button>
    )
}