package net.wiicart.webcli.web.renderer.primitivetext;

import org.jetbrains.annotations.Contract;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Unmodifiable;
import org.jsoup.nodes.Element;

import java.util.List;

final class LineRenderer implements PrimitiveTextBoxRenderer.ElementRenderer {

    private static final String LINE = "_".repeat(PrimitiveTextBoxRenderer.ROW_SIZE);

    @Contract(value = "_ -> new", pure = true)
    @Override
    public @NotNull @Unmodifiable List<String> getContent(@NotNull Element element) {
        return List.of(LINE);
    }
}
