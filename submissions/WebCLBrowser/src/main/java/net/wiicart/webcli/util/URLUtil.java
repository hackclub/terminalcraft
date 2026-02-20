package net.wiicart.webcli.util;

import org.jetbrains.annotations.NotNull;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class URLUtil {

    private static final Pattern URL_WITH_HTTP_NO_PAGE = Pattern.compile(
            "https?://([a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,63}/?"
    );

    private URLUtil() {}

    // Normalizes a String url by adding https:// to the front if necessary, among other things.
    public static @NotNull String normalizeURL(@NotNull String url) {
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            url = "https://" + url;
        }

        Matcher matcher = URL_WITH_HTTP_NO_PAGE.matcher(url);
        if(matcher.matches()) {
            if(url.endsWith("/")) {
                url = url + "index.html";
            } else {
                url = url + "/index.html";
            }
        }
        return url;
    }

    public static @NotNull String simplify(@NotNull String url) {
        return url.replace("http://", "")
                .replace("https://", "")
                .replace("index.html/", "")
                .replace("index.html", "")
                .replace(".html", "");
    }

}
