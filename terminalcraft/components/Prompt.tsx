import { useState } from "react";

type Props = {
    command: string
    setCommand?: Function
    handleCommand?: Function
    readonly?: boolean
}

export default function Prompt({ command, setCommand, readonly, handleCommand }: Props) {
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [showSuggestions, setShowSuggestions] = useState<boolean>(false);

    const availableCommands = ["ls", "cat", "whoami", "help", "clear", "submit", "slack", "exit"];
    const availableFiles = ["about.md", "prizes.md", "faq.md"];

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Tab") {
            e.preventDefault();
            const cmd = command.trim();

            if (cmd === "") {
                setSuggestions(availableCommands);
                setShowSuggestions(true);
                return;
            }

            if (cmd === "cat" || (cmd.startsWith("cat ") && cmd.length === 4)) {
                setSuggestions(availableFiles);
                setShowSuggestions(true);
                return;
            }

            if (!cmd.includes(" ")) {
                const matchedCommands = availableCommands.filter(c =>
                    c.startsWith(cmd.toLowerCase())
                );

                if (matchedCommands.length === 1) {
                    setCommand && setCommand(matchedCommands[0]);
                    setSuggestions([]);
                    setShowSuggestions(false);
                } else if (matchedCommands.length > 1) {
                    setSuggestions(matchedCommands);
                    setShowSuggestions(true);
                }
            }
            else if (cmd.startsWith("cat ")) {
                const filePrefix = cmd.substring(4).trim();
                const matchedFiles = availableFiles.filter(file =>
                    file.startsWith(filePrefix)
                );

                if (matchedFiles.length === 1) {
                    setCommand && setCommand(`cat ${matchedFiles[0]}`);
                    setSuggestions([]);
                    setShowSuggestions(false);
                } else if (matchedFiles.length > 1) {
                    setSuggestions(matchedFiles);
                    setShowSuggestions(true);
                }
            }
        } else if (e.key === "Escape") {
            setShowSuggestions(false);
        }
    };

    return (
        <div className="flex flex-col">
            <form onSubmit={event => {
                event.preventDefault();
                setShowSuggestions(false);
                if (handleCommand) handleCommand(command.toLowerCase());
            }} className="flex flex-row">
                <p className="text-gray-400">you@hackclub ~ %</p>
                <input {...(readonly ? { readOnly: true, autoFocus: false } : { autoFocus: true })}
                    style={{ width: `${command.length < 1 ? 1 : command.length}ch` }}
                    className="ml-3 focus:outline-none text-white bg-transparent caret-transparent"
                    type="text" value={command}
                    onChange={e => {
                        setCommand && setCommand(e.target.value);
                        setShowSuggestions(false);
                    }}
                    onKeyDown={!readonly ? handleKeyDown : undefined} />
                {!readonly ? <span className="w-2 h-5 bg-white animate-blink"></span> : ""}
            </form>

            {showSuggestions && suggestions.length > 0 && (
                <div className="inline-block text-white my-2">
                    <div className="flex flex-wrap gap-2">
                        {suggestions.map((suggestion, index) => (
                            <span
                                key={index}
                                className="cursor-pointer hover:bg-gray-800 px-2 py-1 text-[#4AF626]"
                                onClick={() => {
                                    if (command.trim().startsWith("cat ")) {
                                        setCommand && setCommand(`cat ${suggestion}`);
                                    } else {
                                        setCommand && setCommand(suggestion);
                                    }
                                    setShowSuggestions(false);
                                }}
                            >
                                {suggestion}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}