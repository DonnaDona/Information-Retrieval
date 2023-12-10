import React from 'react'
import ReactDOM from 'react-dom/client'

import {Provider} from 'react-redux'
import store from '../app/store'

import './index.css'
import {createBrowserRouter, RouterProvider,} from "react-router-dom";
import {DevSupport} from "@react-buddy/ide-toolbox";
import {ComponentPreviews, useInitial} from "./dev/index.js";
import ErrorPage from "./features/ErrorPage.jsx";
import {SearchPage} from "./features/SearchPage.jsx";
import {MovieResults} from "./features/MovieResults.jsx";

const router = createBrowserRouter([
    {
        path: "/",
        element: <SearchPage/>,
        errorElement: <ErrorPage/>,
    },
    {
        path: "/results",
        element: <MovieResults/>,
        errorElement: <ErrorPage/>,
    }
]);

ReactDOM.createRoot(document.getElementById('root')).render(
    <Provider store={store}>
        <DevSupport ComponentPreviews={ComponentPreviews}
                    useInitialHook={useInitial}
        >
            <RouterProvider router={router}/>
        </DevSupport>
    </Provider>
)
