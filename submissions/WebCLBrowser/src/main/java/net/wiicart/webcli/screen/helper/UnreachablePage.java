package net.wiicart.webcli.screen.helper;

import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.List;

public final class UnreachablePage {

    private UnreachablePage() {}

    private static final List<String> LINES = new ArrayList<>();
    static {
        LINES.add("$$$$$$$$\\ $$$$$$$\\  $$$$$$$\\   $$$$$$\\  $$$$$$$\\  ");
        LINES.add("$$  _____|$$  __$$\\ $$  __$$\\ $$  __$$\\ $$  __$$\\ ");
        LINES.add("$$ |      $$ |  $$ |$$ |  $$ |$$ /  $$ |$$ |  $$ |");
        LINES.add("$$$$$\\    $$$$$$$  |$$$$$$$  |$$ |  $$ |$$$$$$$  |");
        LINES.add("$$  __|   $$  __$$< $$  __$$< $$ |  $$ |$$  __$$< ");
        LINES.add("$$ |      $$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |");
        LINES.add("$$$$$$$$\\ $$ |  $$ |$$ |  $$ | $$$$$$  |$$ |  $$ |");
        LINES.add("\\________|\\__|  \\__|\\__|  \\__| \\______/ \\__|  \\__|");
        LINES.add("");
        LINES.add("Unable to reach page");
        LINES.add("status: {status}");
    }

    private static final List<String> FOUR_ZERO_FOUR = new ArrayList<>();
    static {
        FOUR_ZERO_FOUR.add("________________________________________________                        ");
        FOUR_ZERO_FOUR.add("| 0000    0000   000000000000  0000    0000    |\\                      ");
        FOUR_ZERO_FOUR.add("| 0000    0000   0000    0000  0000    0000    | \\     _    _         ");
        FOUR_ZERO_FOUR.add("| 0000000000000000000    000000000000000000000 |  \\   | \\  | \\       ");
        FOUR_ZERO_FOUR.add("|         0000   0000    0000          0000    |   |--|  \\_|  \\_____  ");
        FOUR_ZERO_FOUR.add("|         0000   0000    0000          0000    |  /    \\____    _____\\");
        FOUR_ZERO_FOUR.add("|         0000   000000000000          0000    | /          |  /       ");
        FOUR_ZERO_FOUR.add("________________________________________________/           |_/        ");
        FOUR_ZERO_FOUR.add("               404 | Not Found                                         ");
        FOUR_ZERO_FOUR.add("                                                                       ");
    }

    public static @NotNull List<String> withCode(int code) {
        if(code == 404) {
            return FOUR_ZERO_FOUR;
        }

        List<String> list = new ArrayList<>(LINES);
        String pos = list.get(10);
        list.set(10, pos.replace("{status}", String.valueOf(code)));
        return list;
    }

}
