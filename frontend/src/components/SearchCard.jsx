import React from 'react'
import {Box, Card} from "@mui/material";
import {TextInput} from "./TextInput.jsx";
import {SearchButton} from "./SearchButton.jsx";

export function SearchCard() {

    return (
        <Card sx={{width: 800, padding: 3, borderRadius: '20px', boxShadow: 4}}>
            <Box paddingBottom={4}>
                <TextInput/>
            </Box>

            <SearchButton/>
        </Card>
    )
}