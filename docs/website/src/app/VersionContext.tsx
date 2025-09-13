"use client"
import { createContext, useState, useContext, Dispatch, SetStateAction } from 'react';
import { Iversion } from '@/assets/js/mytypes';

interface VersionContextType {
  version: Iversion;
  setVersion: Dispatch<SetStateAction<Iversion>>;
}

const VersionContext = createContext<VersionContextType | undefined>(undefined);

export function VersionProvider({ children }: { children: React.ReactNode }) {
  const [version, setVersion] = useState<Iversion>(1.59);

  return (
    <VersionContext.Provider value={{ version, setVersion }}>
      {children}
    </VersionContext.Provider>
  );
}

export function useVersion() {
  const context = useContext(VersionContext);
  if (context === undefined) {
    throw new Error('useVersion must be used within a VersionProvider');
  }
  return context;
}
