import { useState, useEffect, KeyboardEvent } from 'react';

interface Props {
    onCommand: (command: string) => void;
    isPassword?: boolean;
}

export default function Prompt({ onCommand, isPassword = false }: Props) {
    const [command, setCommand] = useState("");
    const [hasFocus, setHasFocus] = useState(true);
    const [commandHistory, setCommandHistory] = useState<string[]>([]);
    const [historyIndex, setHistoryIndex] = useState(-1);
    const [cursorPosition, setCursorPosition] = useState(0);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            if (command.trim()) {
                setCommandHistory(prev => [...prev, command]);
            }
            onCommand(command);
            setCommand("");
            setHistoryIndex(-1);
            setCursorPosition(0);
            return;
        }

        if (e.key === "ArrowUp") {
            e.preventDefault();
            if (commandHistory.length > 0) {
                const newIndex = historyIndex + 1;
                if (newIndex < commandHistory.length) {
                    setHistoryIndex(newIndex);
                    const historicCommand = commandHistory[commandHistory.length - 1 - newIndex];
                    setCommand(historicCommand);
                    setCursorPosition(historicCommand.length);
                }
            }
            return;
        }

        if (e.key === "ArrowDown") {
            e.preventDefault();
            if (historyIndex > 0) {
                const newIndex = historyIndex - 1;
                setHistoryIndex(newIndex);
                const historicCommand = commandHistory[commandHistory.length - 1 - newIndex];
                setCommand(historicCommand);
                setCursorPosition(historicCommand.length);
            } else if (historyIndex === 0) {
                setHistoryIndex(-1);
                setCommand("");
                setCursorPosition(0);
            }
            return;
        }

        if (e.key === "ArrowLeft") {
            if (cursorPosition > 0) {
                setCursorPosition(cursorPosition - 1);
            }
            return;
        }

        if (e.key === "ArrowRight") {
            if (cursorPosition < command.length) {
                setCursorPosition(cursorPosition + 1);
            }
            return;
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value;
        setCommand(newValue);
        setCursorPosition(e.target.selectionStart || newValue.length);
    };

    const handleClick = (e: React.MouseEvent<HTMLInputElement>) => {
        const input = e.target as HTMLInputElement;
        setCursorPosition(input.selectionStart || input.value.length);
    };

    useEffect(() => {
        // Update cursor position in the input element
        const input = document.querySelector('input') as HTMLInputElement;
        if (input) {
            input.setSelectionRange(cursorPosition, cursorPosition);
        }
    }, [cursorPosition]);

    return (
        <div className="flex items-center relative">
            <span className="text-gray-400 font-mono mr-2">you@hackclub ~ %</span>
            <style jsx global>{`
                .cursor {
                    position: absolute;
                    width: 8px;
                    height: 17px;
                    background: #fff;
                    animation: blink 1s step-end infinite;
                    margin-left: 1px;
                    top: 50%;
                    transform: translateY(-50%);
                }
                
                @keyframes blink {
                    0%, 49% { opacity: 1; }
                    50%, 100% { opacity: 0; }
                }

                input {
                    padding-right: 8px;
                    line-height: 1.2;
                }
            `}</style>
            <div className="relative flex-1">
                <input
                    type={isPassword ? "password" : "text"}
                    value={command}
                    onChange={handleChange}
                    onKeyDown={handleKeyDown}
                    onClick={handleClick}
                    onFocus={() => setHasFocus(true)}
                    onBlur={() => setHasFocus(false)}
                    className="bg-transparent outline-none w-full text-white font-mono caret-transparent"
                    autoFocus
                    spellCheck="false"
                    autoCapitalize="none"
                    autoComplete="off"
                    autoCorrect="off"
                />
                {hasFocus && <div className="cursor" style={{ left: `${cursorPosition}ch` }} />}
            </div>
        </div>
    );
} 