"use client"
import { Analytics } from '@vercel/analytics/react';
import { Toaster } from "sonner";
import { VersionProvider } from "./VersionContext";
import dynamic from 'next/dynamic';

//import "./globals.css";
import '../assets/css/quick-styles.css';
import '../assets/css/app.css';

import Header from '../ui/Header/Header';
import SiteOverview from "../ui/SiteOverview/SiteOverview";
import Footer from "../ui/Footer/Footer";
import { useVersion } from "./VersionContext";
import { ScrollToSection } from '../ui/ScrollAssist';

function SiteLayout({ children }: { children: React.ReactNode }) {
  const { version, setVersion } = useVersion();
  return (
    <>
      <ScrollToSection />
      <Header version={version} setVersion={setVersion} />
      <main className="flex">
        <SiteOverview version={version} />
        <main className="flex fd-column width100per">
          {children}
          <Footer />
        </main>
      </main>
    </>
  )
}

import { Suspense } from 'react';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
<div id="root">
        <Toaster position="top-right" />
        <VersionProvider>
          <Suspense>
            <SiteLayout>{children}</SiteLayout>
          </Suspense>
        </VersionProvider>
        <Analytics />
      </div>
      </body>
    </html>
  );
}
