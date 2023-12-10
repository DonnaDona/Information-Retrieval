import {createSlice} from '@reduxjs/toolkit'

export const searchSlice = createSlice({
    name: 'search',
    initialState: {
        query: '',
        showResults: false,
        movieResults: [
            {title: "The Matrix", release: "1999", description: "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.", image: "https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Poster.jpg", rating: "8.7", duration: "2h 16m"},
            {title: "The Matrix Reloaded", release: "2003", description: "Freedom fighters Neo, Trinity and Morpheus continue to lead the revolt against the Machine Army, unleashing their arsenal of extraordinary skills and weaponry against the systematic forces of repression and exploitation.", image: "https://upload.wikimedia.org/wikipedia/en/b/ba/Poster_-_The_Matrix_Reloaded.jpg", rating: "7.2", duration: "2h 18m"},
            {title: "The Matrix Revolutions", release: "2003", description: "The human city of Zion defends itself against the massive invasion of the machines as Neo fights to end the war at another front while also opposing the rogue Agent Smith.", image: "https://upload.wikimedia.org/wikipedia/en/3/34/Matrix_revolutions_ver7.jpg", rating: "6.7", duration: "2h 9m"},
            {title: "The Matrix Resurrections", release: "2021", description: "The Matrix Resurrections is an upcoming American science fiction action film produced, co-written, and directed by Lana Wachowski. It is the fourth installment in The Matrix film series, and a sequel to The Matrix Revolutions (2003).", image: "", rating: "N/A", duration: "N/A"},
            {title: "The Matrix", release: "1999", description: "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.", image: "https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Poster.jpg", rating: "8.7", duration: "2h 16m"},
        ],
    },
    reducers: {
        setQuery: (state, action) => {
            state.query = action.payload
        },
        setShowResults: (state, action) => {
            state.showResults = action.payload
        }
    },
})

export const {setQuery, setShowResults} = searchSlice.actions

export const selectQuery = state => state.search.query
export const selectShowResults = state => state.search.showResults
export const selectMovieResults = state => state.search.movieResults

export default searchSlice.reducer