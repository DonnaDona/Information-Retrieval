import { createSlice } from '@reduxjs/toolkit'

export const searchSlice = createSlice({
    name: 'search',
    initialState: {
        query: '',
    },
    reducers: {
        setQuery: (state, action) => {
            state.query = action.payload
        }
    },
})

export const { setQuery } = searchSlice.actions

export const selectQuery = state => state.search.query

export default searchSlice.reducer