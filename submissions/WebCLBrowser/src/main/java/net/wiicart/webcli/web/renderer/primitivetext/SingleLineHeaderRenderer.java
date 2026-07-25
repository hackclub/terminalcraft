package net.wiicart.webcli.web.renderer.primitivetext;

import org.jetbrains.annotations.Contract;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Unmodifiable;
import org.jsoup.nodes.Element;

import java.util.List;
import java.util.Map;

final class SingleLineHeaderRenderer implements PrimitiveTextBoxRenderer.ElementRenderer {

    private static final Map<String, String> HEADERS = Map.of(
            "header", "======",
            "h1", "======",
            "h2", "=====",
            "h3", "====",
            "h4", "===",
            "h5", "==",
            "h6", "="
    );

    @Contract(pure = true)
    @Override
    public @NotNull @Unmodifiable List<String> getContent(@NotNull Element element) {
        String text = element.ownText().trim().strip();
        if(text.isEmpty()) {
            return List.of();
        }

        String ends = HEADERS.get(element.tagName());
        if(ends == null) {
            ends = "=";
        }

        return List.of(
                " ",
                ends + text + ends
        );
    }
}
