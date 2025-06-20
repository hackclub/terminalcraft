package net.wiicart.webcli.web.renderer.primitivetext;

import org.jetbrains.annotations.NotNull;
import org.jsoup.nodes.Element;

import java.util.ArrayList;
import java.util.List;

final class TextRenderer implements PrimitiveTextBoxRenderer.ElementRenderer {

    private static final String START_AND_END = "+" + "-".repeat(PrimitiveTextBoxRenderer.ROW_SIZE - 2) + "+";

    @Override
    public @NotNull List<String> getContent(@NotNull Element element) {
        String text = element.ownText().strip().trim();

        if(text.isEmpty()) {
            return List.of();
        }

        List<String> list = new ArrayList<>();
        list.add(START_AND_END);

        StringBuilder builder = new StringBuilder("|");
        String[] words = text.split(" ");
        for(String word : words) {
            if(builder.length() + word.length() < PrimitiveTextBoxRenderer.ROW_SIZE - 2) {
                builder.append(word);
                builder.append(" ");
            } else {
                complete(builder);
                list.add(builder.toString());
                builder = new StringBuilder("|" + word + " ");
            }
        }

        if(!builder.isEmpty()) {
            complete(builder);
            list.add(builder.toString());
        }

        list.add(START_AND_END);
        list.add("");

        return list;
    }

    private void complete(@NotNull StringBuilder builder) {
        int length = builder.length();
        builder.append(" ".repeat(Math.max(0, PrimitiveTextBoxRenderer.ROW_SIZE - length - 1))).append("|");
    }
}
