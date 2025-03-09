type Props = {
    command: string
    setCommand?: Function
    handleCommand?: Function
    readonly?: boolean
}

export default function Prompt({ command, setCommand, readonly, handleCommand }: Props) {
    return (
        <form onSubmit={event => {
            event.preventDefault(); // prevent form from causing redirect

            if (handleCommand) handleCommand(command.toLowerCase());
        }} className="flex flex-row">
            <p className="text-gray-400">you@hackclub ~ %</p>
            <input {...(readonly ? { readOnly: true, autoFocus: false } : { autoFocus: true })} 
            style={{ width: `${command.length < 1 ? 1 : command.length}ch` }} 
            className="ml-3 focus:outline-none text-white bg-transparent caret-transparent" 
            type="text" value={command} onChange={e => setCommand ? setCommand!(e.target.value) : void 0} />
            { !readonly ? <span className="w-2 h-5 bg-white animate-blink"></span> : ""}
        </form>
    )
}