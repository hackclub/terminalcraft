package net.wiicart.webcli.screen;

import com.googlecode.lanterna.gui2.ProgressBar;
import com.googlecode.lanterna.gui2.WindowBasedTextGUI;
import org.jetbrains.annotations.NotNull;

/**
 * Represents a loading screen, used before a page is loaded.
 */
public final class LoadingScreen extends AbstractScreen<LoadingScreen> {

    private final @NotNull WindowBasedTextGUI gui;
    private final @NotNull ProgressBar progressBar;

    private ScreenFutureRunner<LoadingScreen> future;

    public LoadingScreen(@NotNull WindowBasedTextGUI gui) {
        this.gui = gui;
        progressBar = new ProgressBar();
        future = new ScreenFutureRunner<>(this);


    }

    @Override
    public ScreenFutureRunner<LoadingScreen> show() {
        return future;
    }

    @Override
    boolean readyToExecute() {
        return false;
    }

}
