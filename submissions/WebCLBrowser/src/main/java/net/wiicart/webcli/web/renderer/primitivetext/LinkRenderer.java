package net.wiicart.webcli.web.renderer.primitivetext;

import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Unmodifiable;
import org.jsoup.nodes.Element;

import java.util.List;

final class LinkRenderer implements PrimitiveTextBoxRenderer.ElementRenderer {

    private static final String FORMAT = "[⚡LINK text=\"{text}\" link=\"{link}\"]";

    @Override
    public @NotNull @Unmodifiable List<String> getContent(@NotNull Element element) {
        String text = element.ownText().strip().trim();
        String link = element.attr("href").strip().trim();
        return List.of(FORMAT.replace("{text}", text).replace("{link}", link));
    }

}
