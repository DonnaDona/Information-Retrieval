import { configureStore } from '@reduxjs/toolkit'
import searchReducer from '../src/features/searchSlice'

export default configureStore({
    reducer: {
        search: searchReducer,
    },
})