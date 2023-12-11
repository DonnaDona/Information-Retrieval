import React from 'react'
import {AppBar, Avatar, Box, Toolbar} from "@mui/material";
import {TextInput} from "./TextInput.jsx";
import {SearchButton} from "./SearchButton.jsx";

export function TopBar() {

    return (
        <Box sx={{flexGrow: 1}}>
            <AppBar elevation={1} position="static" sx={{bgcolor: "white", padding: 0.5}}>
                <Toolbar>
                    <a href={'/'}><Avatar sx={{width: 40, height: 50, marginLeft: 1}} src="/robotLogo.svg"/></a>
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