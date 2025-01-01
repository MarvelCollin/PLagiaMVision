import React, { useState } from 'react';

interface HoverInformationProps {
  text: string;
  children: React.ReactNode;
}

const HoverInformation: React.FC<HoverInformationProps> = ({ text, children }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div 
      className="relative"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      <div 
        className={`
          absolute z-50 w-64 p-4 bottom-full left-1/2 transform -translate-x-1/2 mb-2
          bg-gray-800 text-white text-sm rounded-lg shadow-lg
          transition-all duration-200 ease-in-out
          ${isVisible 
            ? 'opacity-100 translate-y-0' 
            : 'opacity-0 translate-y-2 pointer-events-none'
          }
        `}
      >
        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-0 h-0 
                      border-8 border-transparent border-t-gray-800" />
        {text}
      </div>
    </div>
  );
};

export default HoverInformation;
