import React from 'react';

interface TerminalEntryProps {
  type: "input" | "output";
  content: string;
  parseText?: (text: string) => string;
}

export default function TerminalEntry({ type, content, parseText }: TerminalEntryProps) {
  if (type === "input") {
    return (
      <div className="flex items-start">
        <div className="flex items-center flex-wrap">
          <span className="text-gray-400 font-mono mr-2">you@hackclub ~ %</span>
          <span className="text-white font-mono">{content}</span>
        </div>
      </div>
    );
  }

  if (!content.includes("terminalcraft:")) {
    return (
      <div 
        className="text-[#4AF626] [&_h1]:text-xl [&_h1]:font-bold [&_h1]:mb-4 [&_h2]:text-lg [&_h2]:font-bold [&_h2]:mb-3 [&_h3]:text-base [&_h3]:font-bold [&_h3]:mb-2 [&_ul]:list-disc [&_ul]:pl-4 [&_ul]:mb-3 [&_li]:mb-1"
        dangerouslySetInnerHTML={{ __html: parseText ? parseText(content) : content }}
      />
    );
  }

  return (
    <pre 
      className="font-mono text-[#FF5F56] whitespace-pre my-2 block"
      style={{
        letterSpacing: '0',
        lineHeight: '1.2'
      }}
    >{content}</pre>
  );
} 