import React, { useState, useEffect } from 'react';

const ResponsiveText: React.FC = () => {
  const [fontSize, setFontSize] = useState<string>(getFontSize());

  function getFontSize(): string {
    return window.innerWidth < 600 ? '12px' : '16px';
  }

  useEffect(() => {
    const handleResize = () => setFontSize(getFontSize());

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <p style={{ fontSize }}>
      This text adjusts size based on screen width!
    </p>
  );
};

export default ResponsiveText;