import React from 'react'
import {InputAdornment, TextField} from "@mui/material";
import {selectQuery, setQuery} from "../features/searchSlice.jsx";
import {useDispatch, useSelector} from "react-redux";
import SearchIcon from '@mui/icons-material/Search';

export function TextInput() {
    const dispatch = useDispatch();
    const query = useSelector(selectQuery);

    const handleChange = (event) => {
        if (event.key === 'Enter') {
            console.log('enter pressed');
            window.location.href = `/results?q=${encodeURIComponent(query)}`;
        }
    }

    return (
        <TextField
            placeholder="Search..."
            type="text"
            variant="outlined"
            size="small"
            value={query}
            onChange={(event) => dispatch(setQuery(event.target.value))}
            onKeyDown={handleChange}
            sx={{width: '100%'}}

            InputProps={{
                sx: {borderRadius: 4, paddingY: 0.25, bgcolor: 'white'},
                startAdornment: (
                    <InputAdornment position="start">
                        <SearchIcon/>
                    </InputAdornment>
                )
            }}

        />
    )
}