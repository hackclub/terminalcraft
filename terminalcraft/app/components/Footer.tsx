import React from 'react';

interface FooterProps {
  commitHash: string;
}

export default function Footer({ commitHash }: FooterProps) {
  return (
    <div className="py-4 text-gray-400 text-xs sm:text-sm flex items-center justify-center gap-2">
      <span>© {new Date().getFullYear()} Hack Club</span>
      <span className="px-2">•</span>
      <span>{commitHash}</span>
    </div>
  );
} 