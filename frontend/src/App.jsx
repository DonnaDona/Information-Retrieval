import './App.css'
import {SearchPage} from "./features/SearchPage.jsx";
import {Box, Stack} from "@mui/material";
import {useSelector} from "react-redux";
import {selectShowResults} from "./features/searchSlice.jsx";
import {MovieResults} from "./features/MovieResults.jsx";

function App() {
    const showResults = useSelector(selectShowResults);

    return (
        <Box>
            <Stack>
                {showResults ? (<MovieResults/>) :(<SearchPage/>)}
            </Stack>
        </Box>
    )
}

export default App
