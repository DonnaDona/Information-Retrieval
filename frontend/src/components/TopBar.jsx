import React from 'react'
import {AppBar, Box, Toolbar, Typography} from "@mui/material";

export function TopBar() {

    return (
        <Box sx={{flexGrow: 1}}>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{flexGrow: 1, paddingLeft: 8}}>
                        Search & Chill
                    </Typography>
                </Toolbar>
            </AppBar>
        </Box>
    )
}