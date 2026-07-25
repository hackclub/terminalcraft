package net.wiicart.webcli.screen;

import com.googlecode.lanterna.TerminalSize;
import com.googlecode.lanterna.gui2.BasicWindow;
import com.googlecode.lanterna.gui2.Borders;
import com.googlecode.lanterna.gui2.Button;
import com.googlecode.lanterna.gui2.Direction;
import com.googlecode.lanterna.gui2.Label;
import com.googlecode.lanterna.gui2.LinearLayout;
import com.googlecode.lanterna.gui2.Panel;
import com.googlecode.lanterna.gui2.TextBox;
import com.googlecode.lanterna.gui2.Window;
import com.googlecode.lanterna.gui2.WindowBasedTextGUI;
import org.jetbrains.annotations.NotNull;

import java.util.Set;

public final class URLEntryScreen extends AbstractScreen<URLEntryScreen> {

    private static final Set<Window.Hint> ENTRY_HINTS = Set.of(Window.Hint.CENTERED, Window.Hint.FIT_TERMINAL_WINDOW);

    private final WindowBasedTextGUI gui;
    private final TextBox textBox = new TextBox(new TerminalSize(50, 1));
    private String entry; // The URL that was entered
    private boolean execute = false;

    private final ScreenFutureRunner<URLEntryScreen> future;

    public URLEntryScreen(@NotNull WindowBasedTextGUI gui) {
        this.gui = gui;
        future = new ScreenFutureRunner<>(this);
        initTextBox();
        // Do not call show() here
    }

    private void initTextBox() {
        textBox.withBorder(Borders.singleLine("Enter your URL:"));
    }

    public ScreenFutureRunner<URLEntryScreen> show() {
        Window window = createWindow();
        gui.addWindowAndWait(window);
        execute = true;
        return future;
    }

    private @NotNull Panel createEntryPanel(Window window) {
        Panel panel = new Panel();
        panel.setLayoutManager(new LinearLayout(Direction.VERTICAL));
        panel.setSize(new TerminalSize(25, 6));
        panel.addComponent(new Label("Enter a URL:"));
        panel.addComponent(textBox);
        panel.addComponent(new Button("Go", () -> {
            entry = textBox.getText();
            future.executeRunnables();
            window.close();
        }));
        return panel;
    }

    private @NotNull Window createWindow() {
        BasicWindow window = new BasicWindow("CLI Web Browser");
        window.setTitle("Web Browser");
        window.setComponent(createEntryPanel(window));
        window.setHints(ENTRY_HINTS);
        return window;
    }

    public String getEntry() {
        return entry;
    }

    @Override
    boolean readyToExecute() {
        return execute;
    }
}