import { Route, Routes } from "react-router";
import { Analytics } from '@vercel/analytics/react';


import './assets/css/quick-styles.css'
import './assets/css/app.css'

import MainPage from "./pages/MainPage";
import Header from './ui/Header/Header.tsx';
import SiteOverview from "./ui/SiteOverview/SiteOverview.tsx";
import ComponentsPage from "./pages/ComponentsPage.tsx";
import AdvanceMethodsPage from "./pages/AdvanceMethodsPage.tsx";

function App() {

    return (
        <>
            <Header />
            <main className="flex">
                <SiteOverview />
                <Routes>
                    <Route path="/getting-started" element={<MainPage />} />
                    <Route path="/components" element={<ComponentsPage />} />
                    <Route path="/advance-methods" element={<AdvanceMethodsPage />} />
                </Routes>
            </main>
            <Analytics/>

        </>
    )
}

export default App
