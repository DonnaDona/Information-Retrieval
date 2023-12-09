import {createSlice} from '@reduxjs/toolkit'

export const searchSlice = createSlice({
    name: 'search',
    initialState: {
        query: '',
        showResults: false,
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

export default searchSlice.reducer