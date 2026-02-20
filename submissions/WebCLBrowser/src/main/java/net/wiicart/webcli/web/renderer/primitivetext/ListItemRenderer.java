package net.wiicart.webcli.web.renderer.primitivetext;

import org.jetbrains.annotations.NotNull;
import org.jsoup.nodes.Element;

import java.util.List;

final class ListItemRenderer implements PrimitiveTextBoxRenderer.ElementRenderer {

    @Override
    public List<String> getContent(@NotNull Element element) {
        String text = element.ownText().strip().trim();
        if(text.isBlank()) {
            return List.of();
        }

        return List.of(" •" + text);
    }
}
