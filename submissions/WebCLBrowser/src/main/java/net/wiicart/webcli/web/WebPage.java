package net.wiicart.webcli.web;

import com.googlecode.lanterna.gui2.Panel;
import net.wiicart.webcli.util.URLUtil;
import net.wiicart.webcli.web.renderer.primitivetext.PrimitiveTextBoxRenderer;
import org.jetbrains.annotations.Contract;
import org.jetbrains.annotations.NotNull;
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.Progress;
import org.jsoup.nodes.Document;

import java.io.IOException;

// https://www.baeldung.com/java-with-jsoup
@SuppressWarnings("unused")
public final class WebPage {

    private final @NotNull String title;

    private final @NotNull Document document;

    @Contract("_ -> new")
    public static @NotNull WebPage fromAddress(@NotNull String address) throws IOException {
        address = URLUtil.normalizeURL(address);
        return new WebPage(address);
    }

    @Contract("_, _ -> new")
    public static @NotNull WebPage fromAddress(@NotNull String address, @NotNull Progress<Connection.Response> progress) throws IOException {
        address = URLUtil.normalizeURL(address);
        return new WebPage(address, progress);
    }

    private WebPage(@NotNull String address) throws IOException {
        document = Jsoup.connect(address)
                .followRedirects(true)
                .timeout(15000)
                .get();

        title = document.title();
    }

    private WebPage(@NotNull String address, Progress<Connection.Response> progress) throws IOException {
        document = Jsoup.connect(address)
                .onResponseProgress(progress)
                .followRedirects(true)
                .timeout(10000)
                .get();

        title = document.title();
    }

    public @NotNull String getTitle() {
        return title;
    }

    public void applyContent(@NotNull Panel panel) {
        PrimitiveTextBoxRenderer renderer = new PrimitiveTextBoxRenderer(document);
        renderer.applyContent(panel);
    }

}
