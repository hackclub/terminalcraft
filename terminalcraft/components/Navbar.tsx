"use client"
import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();
  const [activeTab, setActiveTab] = useState(pathname);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const tabs = [
    { name: 'Terminal', path: '/', icon: '>' },
    { name: 'Resources', path: '/resources', icon: '?' },
    { name: 'Gallery', path: '/gallery', icon: '[]' },
  ];

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <nav className="bg-[#2D2D2D] border-b border-[#404040] px-4 py-3 relative">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Logo/Brand */}
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-[#4AF626] rounded-full animate-pulse"></div>
          <span className="text-[#4AF626] font-mono text-lg font-bold">terminalcraft</span>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-1">
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

        {/* Desktop Terminal Status */}
        <div className="hidden lg:flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-[#808080] font-mono text-xs">
            <div className="w-2 h-2 bg-[#27C93F] rounded-full animate-pulse"></div>
            <span>online</span>
          </div>
          <div className="text-[#808080] font-mono text-xs">
            you@hackclub
          </div>
        </div>

        {/* Mobile Status (simplified) */}
        <div className="flex lg:hidden items-center space-x-3">
          <div className="flex items-center space-x-2 text-[#808080] font-mono text-xs">
            <div className="w-2 h-2 bg-[#27C93F] rounded-full animate-pulse"></div>
            <span className="hidden sm:inline">online</span>
          </div>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={toggleMobileMenu}
          className="md:hidden text-[#808080] hover:text-[#4AF626] p-2 rounded-md transition-colors"
          aria-label="Toggle mobile menu"
        >
          {isMobileMenuOpen ? (
            <X className="w-5 h-5" />
          ) : (
            <Menu className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="md:hidden absolute top-full left-0 right-0 bg-[#2D2D2D] border-b border-[#404040] shadow-lg z-50 animate-slide-down">
          <div className="px-4 py-3 space-y-2">
            {tabs.map((tab) => (
              <Link
                key={tab.path}
                href={tab.path}
                onClick={closeMobileMenu}
                className={`
                  block px-4 py-3 rounded-md font-mono text-sm transition-all duration-200
                  ${pathname === tab.path 
                    ? 'bg-black text-[#4AF626] shadow-lg' 
                    : 'text-[#808080] hover:text-[#4AF626] hover:bg-[#1E1E1E]'
                  }
                `}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-sm">{tab.icon}</span>
                  <span>{tab.name}</span>
                  {pathname === tab.path && (
                    <div className="ml-auto w-2 h-2 bg-[#4AF626] rounded-full"></div>
                  )}
                </div>
              </Link>
            ))}
            
            {/* Mobile Terminal Status */}
            <div className="px-4 py-3 border-t border-[#404040] mt-3">
              <div className="flex items-center justify-between text-[#808080] font-mono text-xs">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-[#27C93F] rounded-full animate-pulse"></div>
                  <span>Status: Online</span>
                </div>
                <span>you@hackclub</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
