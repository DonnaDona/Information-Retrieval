import React from 'react'
import {AppBar, Box, Toolbar} from "@mui/material";
import {TextInput} from "./TextInput.jsx";
import {SearchButton} from "./SearchButton.jsx";

export function TopBar() {

    return (
        <Box sx={{flexGrow: 1}}>
            <AppBar elevation={0} position="static" sx={{bgcolor: "#eceff1", padding: 0.5}}>
                <Toolbar>
                    <Box paddingLeft={4}>
                        <TextInput/>
                    </Box>
                    <Box paddingX={1}>
                        <SearchButton/>
                    </Box>
                </Toolbar>
            </AppBar>
        </Box>
    )
}