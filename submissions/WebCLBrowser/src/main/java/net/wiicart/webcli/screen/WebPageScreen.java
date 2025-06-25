package net.wiicart.webcli.screen;

import com.googlecode.lanterna.SGR;
import com.googlecode.lanterna.TerminalSize;
import com.googlecode.lanterna.TextColor;
import com.googlecode.lanterna.graphics.SimpleTheme;
import com.googlecode.lanterna.gui2.BasicWindow;
import com.googlecode.lanterna.gui2.Direction;
import com.googlecode.lanterna.gui2.EmptySpace;
import com.googlecode.lanterna.gui2.Label;
import com.googlecode.lanterna.gui2.LinearLayout;
import com.googlecode.lanterna.gui2.Panel;
import com.googlecode.lanterna.gui2.ProgressBar;
import com.googlecode.lanterna.gui2.TextBox;
import com.googlecode.lanterna.gui2.TextGUI;
import com.googlecode.lanterna.gui2.Window;
import com.googlecode.lanterna.gui2.WindowBasedTextGUI;
import com.googlecode.lanterna.gui2.WindowListenerAdapter;
import com.googlecode.lanterna.input.KeyStroke;
import net.wiicart.webcli.screen.helper.ToolBar;
import net.wiicart.webcli.screen.helper.UnreachablePage;
import net.wiicart.webcli.util.URLUtil;
import net.wiicart.webcli.web.renderer.primitivetext.PrimitiveTextBoxRenderer;
import net.wiicart.webcli.web.WebPage;
import org.jetbrains.annotations.Contract;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.jsoup.Connection;
import org.jsoup.HttpStatusException;
import org.jsoup.Progress;

import java.util.Set;

public final class WebPageScreen extends AbstractScreen<WebPageScreen> {

    private static final Set<Window.Hint> ENTRY_HINTS = Set.of(Window.Hint.CENTERED, Window.Hint.FIT_TERMINAL_WINDOW);

    private final WindowBasedTextGUI gui;

    private final ScreenFutureRunner<WebPageScreen> future;

    private @NotNull Node currentNode = new Node("");

    private final Panel content = new Panel();

    private final Label title = loadTitle();

    private final ToolBar toolBar = new ToolBar(this, "Title", "Enter a website address here");

    private final EmptySpace emptySpace;

    private ProgressBar progress;

    private final Window window;

    public WebPageScreen(@NotNull WindowBasedTextGUI gui) {
        this.gui = gui;
        emptySpace = new EmptySpace(TextColor.ANSI.WHITE, new TerminalSize(getColumnCount(), 1));
        emptySpace.setLayoutData(LinearLayout.createLayoutData(LinearLayout.Alignment.Fill, LinearLayout.GrowPolicy.CanGrow));
        window = createWindow();
        future = new ScreenFutureRunner<>(this);
    }

    private @NotNull Window createWindow() {
        BasicWindow window1 = new BasicWindow("Web Browser");

        Panel root = new Panel();
        root.setLayoutData(LinearLayout.createLayoutData(LinearLayout.Alignment.Fill));
        root.setLayoutManager(new LinearLayout(Direction.VERTICAL));
        root.addComponent(title);
        Panel toolBarWrapper = new Panel();
        toolBarWrapper.setLayoutData(LinearLayout.createLayoutData(LinearLayout.Alignment.Center));
        toolBarWrapper.setSize(new TerminalSize(getColumnCount(), 1));
        toolBarWrapper.setTheme(new SimpleTheme(TextColor.ANSI.BLUE, TextColor.ANSI.WHITE_BRIGHT));
        toolBarWrapper.setLayoutData(LinearLayout.createLayoutData(LinearLayout.Alignment.Center, LinearLayout.GrowPolicy.CanGrow));
        toolBar.setPanelSize(getColumnCount());
        toolBarWrapper.addComponent(toolBar.getPanel());
        root.addComponent(toolBarWrapper);
        root.addComponent(emptySpace);

        content.setLayoutData(LinearLayout.createLayoutData(LinearLayout.Alignment.Fill));
        root.addComponent(content);

        window1.setComponent(root);
        window1.setHints(ENTRY_HINTS);
        window1.addWindowListener(new WindowListenerAdapter() {
            @Override
            public void onResized(Window window, TerminalSize oldSize, TerminalSize newSize) {
                emptySpace.setSize(new TerminalSize(newSize.getColumns(), 1));
                toolBar.setPanelSize(newSize.getColumns());
            }
        });
        return window1;
    }

    @Override
    public ScreenFutureRunner<WebPageScreen> show() {
        loadTitle();
        goToAddress("https://www.wiicart.net/clbrowser", false);
        gui.addWindowAndWait(window);
        return future;
    }

    @Override
    boolean readyToExecute() {
        return false;
    }

    public void backwards() {
        Node previous = currentNode.previous;
        if(previous != null) {
            currentNode = previous;
            refresh();
        }
    }

    public void forwards() {
        Node next = currentNode.next;
        if(next != null) {
            currentNode = next;
            refresh();
        }
    }

    public void refresh() {
        content.removeAllComponents();
        content.addComponent(PrimitiveTextBoxRenderer.generateFullBodyTextBox()
                .addLine("Loading..."));
        goToAddress(currentNode.address, false);
    }

    public void goToAddress(String address, boolean updateNode) {
        try {
            if(updateNode) {
                updateCurrentNode(address);
            }
            content.removeAllComponents();
            progress = new ProgressBar(0, 100, getColumnCount());
            progress.setValue(0);
            content.addComponent(progress);
            WebPage page = WebPage.fromAddress(address, generateProgressUpdate());
            title.setText(page.getTitle());
            toolBar.setAddress(URLUtil.simplify(address));
            content.removeAllComponents();
            page.applyContent(content);
        } catch(HttpStatusException e) {
            toErrorPage(e.getStatusCode(), e.getMessage());
        } catch(Exception e) {
            toErrorPage(000, e.getMessage());
        }
    }

    private void toErrorPage(int code, @Nullable String message) {
        content.removeAllComponents();
        TextBox box = PrimitiveTextBoxRenderer.generateFullBodyTextBox();
        for(String string : UnreachablePage.withCode(code)) {
            box.addLine(string);
        }

        if(message != null) {
            box.addLine(message);
        }

        title.setText("Error " + code);
        content.addComponent(box);
    }

    // Moves the current node to a new node of the current webpage,
    // updates the previous to reflect the new page.
    private void updateCurrentNode(String address) {
        Node newNode = new Node(address);
        newNode.previous = currentNode;
        currentNode.next = newNode;
        currentNode = newNode;
    }

    public void exit() {
        window.close();
    }

    private @NotNull Label loadTitle() {
        Label title1 = new Label("Blank Page");
        title1.setTheme(new SimpleTheme(TextColor.ANSI.BLUE, TextColor.ANSI.WHITE));
        title1.addStyle(SGR.BOLD);
        title1.addStyle(SGR.FRAKTUR);
        title1.setLayoutData(LinearLayout.createLayoutData(LinearLayout.Alignment.Center));
        title1.setSize(new TerminalSize(100, 100));
        return title1;
    }


    private static class Node {

        private final String address;

        private Node previous;
        private Node next;

        public Node(String address) {
            this.address = address;
        }
    }

    public int getColumnCount() {
        return gui.getScreen().getTerminalSize().getColumns();
    }

    @SuppressWarnings("unused")
    public int getRowCount() {
        return gui.getScreen().getTerminalSize().getRows();
    }

    @Contract(pure = true)
    private @NotNull Progress<Connection.Response> generateProgressUpdate() {
        return (processed, total, percent, context) -> {
            int processedPercent = Float.valueOf(percent).intValue();
            progress.setValue(processedPercent);
        };
    }

    @SuppressWarnings("unused")
    private static final class EscapeListener implements TextGUI.Listener {

        @Override
        public boolean onUnhandledKeyStroke(TextGUI textGUI, KeyStroke keyStroke) {
            return false;
        }
    }
}
