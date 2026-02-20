package net.wiicart.webcli.web.renderer.primitivetext;

import org.jetbrains.annotations.NotNull;
import org.jsoup.nodes.Element;

import java.util.List;

final class UnimplementedElementRenderer implements PrimitiveTextBoxRenderer.ElementRenderer {

    @Override
    public List<String> getContent(@NotNull Element element) {
        String text = element.ownText().strip().trim();
        if(text.isEmpty()) {
            return List.of();
        }

        String head = "+-----(UNIMPLEMENTED ELEMENT \"" + element.tagName() + "\")-----+";
        String footer = "+" + "-".repeat(head.length() - 2) + "+";
        return List.of(head, text, footer);
    }
}
