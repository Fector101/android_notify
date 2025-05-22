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
import VersionsPage from "./pages/VersionsPage.tsx";
import { useState } from "react";
import HomePage from "./pages/HomePage.tsx";

function App() {
    const [version,setVersion]=useState(1.59)
    return (
        <>
            <Toaster position="top-right" />
            <Header version={version} setVersion={setVersion}/>
            <main className="flex">
                <SiteOverview version={version} />
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/getting-started" element={<MainPage />} />
                    <Route path="/components" element={<ComponentsPage version={version} />} />
                    <Route path="/advanced-methods" element={<AdvancedMethodsPage version={version} />} />
                    <Route path="/reference" element={<ReferencePage version={version} />} />
                    <Route path="/extras" element={<ExtrasPage />} />
                    {/* <Route path="/versions" element={<p className="main-page page">Will contain list of versions from 1.58+</p>} /> */}
                    <Route path="/versions" element={<VersionsPage setVersion={setVersion} />} />
                    <Route path="*" element={<p className="page">Page Not Found</p>} />
                </Routes>
            </main>
            <Analytics />
        </>
    )
}

export default App
