"use client"
import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();
  const [activeTab, setActiveTab] = useState(pathname);

  const tabs = [
    { name: 'Terminal', path: '/', icon: '>' },
    { name: 'Gallery', path: '/gallery', icon: '[]' },
  ];

  return (
    <nav className="bg-[#2D2D2D] border-b border-[#404040] px-4 py-3">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Logo/Brand */}
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-[#4AF626] rounded-full animate-pulse"></div>
          <span className="text-[#4AF626] font-mono text-lg font-bold">terminalcraft</span>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center space-x-1">
          {tabs.map((tab) => (
            <Link
              key={tab.path}
              href={tab.path}
              className={`
                relative px-4 py-2 rounded-md font-mono text-sm transition-all duration-200
                ${pathname === tab.path 
                  ? 'bg-black text-[#4AF626] shadow-lg' 
                  : 'text-[#808080] hover:text-[#4AF626] hover:bg-[#1E1E1E]'
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <span className="text-xs">{tab.icon}</span>
                <span>{tab.name}</span>
              </div>
              {pathname === tab.path && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#4AF626] rounded-full"></div>
              )}
            </Link>
          ))}
        </div>

        {/* Terminal Status */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-[#808080] font-mono text-xs">
            <div className="w-2 h-2 bg-[#27C93F] rounded-full animate-pulse"></div>
            <span>online</span>
          </div>
          <div className="text-[#808080] font-mono text-xs">
            you@hackclub
          </div>
        </div>
      </div>
    </nav>
  );
} 