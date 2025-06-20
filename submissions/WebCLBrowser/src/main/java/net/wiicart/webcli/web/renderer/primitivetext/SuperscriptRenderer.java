package net.wiicart.webcli.web.renderer.primitivetext;

import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Unmodifiable;
import org.jsoup.nodes.Element;

import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;

@SuppressWarnings("unused") // Terminals don't seem to support superscript, leaving for more testing later.
final class SuperscriptRenderer implements PrimitiveTextBoxRenderer.ElementRenderer {

    private static final Map<String, String> MAPPINGS = Map.ofEntries(
            Map.entry("a", "ᵃ"),
            Map.entry("b", "ᵇ"),
            Map.entry("c", "ᶜ"),
            Map.entry("d", "ᵈ"),
            Map.entry("e", "ᵉ"),
            Map.entry("f", "ᶠ"),
            Map.entry("g", "ᵍ"),
            Map.entry("h", "ʰ"),
            Map.entry("i", "ᶦ"),
            Map.entry("j", "ʲ"),
            Map.entry("k", "ᵏ"),
            Map.entry("l", "ˡ"),
            Map.entry("m", "ᵐ"),
            Map.entry("n", "ⁿ"),
            Map.entry("o", "ᵒ"),
            Map.entry("p", "ᵖ"),
            Map.entry("q", "ᵠ"),
            Map.entry("r", "ʳ"),
            Map.entry("s", "ˢ"),
            Map.entry("t", "ᵗ"),
            Map.entry("u", "ᵘ"),
            Map.entry("v", "ᵛ"),
            Map.entry("w", "ʷ"),
            Map.entry("x", "ˣ"),
            Map.entry("y", "ʸ"),
            Map.entry("z", "ᶻ")
    );


    @Override
    public @NotNull @Unmodifiable List<String> getContent(@NotNull Element element) {
        String text = element.ownText().strip().trim();
        if(text.isBlank()) {
            return List.of();
        }

        StringBuilder builder = new StringBuilder();
        for(char ch : text.toCharArray()) {
            String character = String.valueOf(ch);
            String key = MAPPINGS.get(character.toLowerCase(Locale.ROOT));
            builder.append(Objects.requireNonNullElse(key, character));
        }
        return List.of(builder.toString());
    }
}
