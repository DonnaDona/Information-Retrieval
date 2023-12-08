import React from 'react'
import {Button} from "@mui/material";

export function SearchButton() {
    const handleClick = () => {
        console.log("Search button clicked");
    }

    return (
        <Button variant="contained" onClick={handleClick} sx={{width: 800, borderRadius: '20px'}}>
            Search
        </Button>
    )
}