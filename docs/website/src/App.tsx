import { Route, Routes } from "react-router";
import { Analytics } from '@vercel/analytics/react';
import { Toaster } from "sonner";


import './assets/css/quick-styles.css'
import './assets/css/app.css'

import MainPage from "./pages/MainPage";
import Header from './ui/Header/Header.tsx';
import SiteOverview from "./ui/SiteOverview/SiteOverview.tsx";
import ComponentsPage from "./pages/ComponentsPage.tsx";
import AdvancedMethodsPage from "./pages/AdvancedMethodsPage.tsx";

function App() {

    return (
        <>
            <Toaster position="top-right" />
            <Header />
            <main className="flex">
                <SiteOverview />
                <Routes>
                    <Route path="/getting-started" element={<MainPage />} />
                    <Route path="/components" element={<ComponentsPage />} />
                    <Route path="/advanced-methods" element={<AdvancedMethodsPage />} />
                    <Route path="*" element={<p className="page">Page Not Found</p>} />
                </Routes>
            </main>
            <Analytics/>

        </>
    )
}

export default App
