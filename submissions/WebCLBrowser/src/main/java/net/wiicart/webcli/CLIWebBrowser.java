package net.wiicart.webcli;

import com.googlecode.lanterna.TextColor;
import com.googlecode.lanterna.gui2.MultiWindowTextGUI;
import com.googlecode.lanterna.screen.Screen;
import com.googlecode.lanterna.terminal.DefaultTerminalFactory;
import com.googlecode.lanterna.terminal.Terminal;
import net.wiicart.webcli.screen.WebPageScreen;
import org.jetbrains.annotations.NotNull;

import java.io.IOException;

public final class CLIWebBrowser {

    public CLIWebBrowser() {
        try (Terminal terminal = createTerminalAndInit()){
            terminal.setBackgroundColor(TextColor.ANSI.RED);
            Screen screen = createScreen();
            screen.startScreen();
            MultiWindowTextGUI gui = new MultiWindowTextGUI(screen);
            WebPageScreen screen1 = new WebPageScreen(gui);
            screen1.show();
            terminal.exitPrivateMode();
            terminal.flush();
        } catch(IOException e) {
            throw new RuntimeException(e);
        }
    }

    private @NotNull Terminal createTerminalAndInit() {
        try {
            DefaultTerminalFactory factory = new DefaultTerminalFactory();
            Terminal terminal = factory.createTerminal();
            terminal.enterPrivateMode();
            return terminal;
        } catch(IOException e) {
            throw new RuntimeException(e);
        }
    }

    private @NotNull Screen createScreen() {
        try {
            DefaultTerminalFactory factory = new DefaultTerminalFactory();
            return factory.createScreen();
        } catch(IOException e) {
            throw new RuntimeException(e);
        }
    }

}
