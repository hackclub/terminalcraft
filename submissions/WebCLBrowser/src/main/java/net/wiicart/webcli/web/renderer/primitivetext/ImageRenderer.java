package net.wiicart.webcli.web.renderer.primitivetext;

import org.jetbrains.annotations.NotNull;
import org.jsoup.nodes.Element;

import java.util.List;

final class ImageRenderer implements PrimitiveTextBoxRenderer.ElementRenderer {

    private static final String FORMAT = "[IMAGE alt=\"{alt}\"]";

    @Override
    public List<String> getContent(@NotNull Element element) {
        String text = element.attr("alt");
        text = FORMAT.replace("{alt}", text);
        return List.of(text);
    }
}
