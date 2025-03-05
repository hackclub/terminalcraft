import React from 'react';

interface TitleBarProps {
  title: string;
  onClose?: () => void;
}

export default function TitleBar({ title, onClose }: TitleBarProps) {
  return (
    <div className="bg-[#2D2D2D] px-3 py-2 flex items-center gap-2 border-b border-[#404040]">
      <div className="flex gap-1.5">
        <div 
          className="w-3 h-3 rounded-full bg-[#FF5F56] flex items-center justify-center cursor-pointer hover:opacity-80"
          onClick={onClose}
        >
          <div className="w-2.5 h-2.5 rounded-full bg-[#FF5F56] shadow-inner"></div>
        </div>
        <div className="w-3 h-3 rounded-full bg-[#FFBD2E] flex items-center justify-center">
          <div className="w-2.5 h-2.5 rounded-full bg-[#FFBD2E] shadow-inner"></div>
        </div>
        <div className="w-3 h-3 rounded-full bg-[#27C93F] flex items-center justify-center">
          <div className="w-2.5 h-2.5 rounded-full bg-[#27C93F] shadow-inner"></div>
        </div>
      </div>
      <div className="flex-1 text-center text-xs sm:text-sm text-gray-400 font-medium">{title}</div>
    </div>
  );
} 