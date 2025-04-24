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
import ReferencePage from "./pages/ReferencePage.tsx";
import ExtrasPage from "./pages/ExtrasPage.tsx";

function App() {

    return (
        <>
            <Toaster position="top-right" />
            <Header />
            <main className="flex">
                <SiteOverview />
                <Routes>
                    <Route path="/" element={<MainPage />} />
                    <Route path="/getting-started" element={<MainPage />} />
                    <Route path="/components" element={<ComponentsPage />} />
                    <Route path="/advanced-methods" element={<AdvancedMethodsPage />} />
                    <Route path="/reference" element={<ReferencePage />} />
                    <Route path="/extras" element={<ExtrasPage />} />
                    <Route path="/versions" element={<p className="main-page page">Will contain list of versions from 1.58+</p>} />
                    <Route path="*" element={<p className="page">Page Not Found</p>} />
                </Routes>
            </main>
            <Analytics/>
        </>
    )
}

export default App
