import React from 'react'
import {Stack, Typography} from "@mui/material";
import {SearchCard} from "../components/SearchCard.jsx";

export function SearchPage() {

    return (
        <Stack className="search-page-container" padding={20} alignItems="center">
            <img src='/robotLogo.svg' alt="logo" width="200" height="200"/>
            <Typography variant="h3" component="div" sx={{paddingBottom: 4}}>
                Search & Chill
            </Typography>
            <SearchCard/>
        </Stack>
    )
}