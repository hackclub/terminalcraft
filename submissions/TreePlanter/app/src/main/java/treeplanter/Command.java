package treeplanter;

import static treeplanter.TerminalCommands.terminalCommands;

public class Command {
    public Command() {
        terminalCommands.put(getID(), this);
    }

    public void action(String[] args) {
        System.out.println("Unimplemented");
    };

    public String getID() {
        return "Unimplemented";
    };
}
