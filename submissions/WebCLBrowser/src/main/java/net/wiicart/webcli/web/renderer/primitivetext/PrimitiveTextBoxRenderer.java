package net.wiicart.webcli.web.renderer.primitivetext;

import com.googlecode.lanterna.TerminalSize;
import com.googlecode.lanterna.TextColor;
import com.googlecode.lanterna.graphics.SimpleTheme;
import com.googlecode.lanterna.gui2.LinearLayout;
import com.googlecode.lanterna.gui2.Panel;
import com.googlecode.lanterna.gui2.TextBox;
import net.wiicart.webcli.web.renderer.Renderer;
import org.jetbrains.annotations.NotNull;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;

import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Set;

// Fully text-based renderer that renders all text in to a single TextBox.
public class PrimitiveTextBoxRenderer implements Renderer {

    static final int ROW_SIZE = 60;

    private final Document document;

    public PrimitiveTextBoxRenderer(@NotNull Document document) {
        this.document = document;
    }

    @Override
    public void applyContent(@NotNull Panel panel) {
        TextBox textBox = generateFullBodyTextBox();
        textBox.setTheme(new SimpleTheme(TextColor.ANSI.BLACK, TextColor.ANSI.WHITE_BRIGHT));
        Iterator<Element> it = document.body().stream().iterator();
        while (it.hasNext()) {
            Element element = it.next();

            ElementRenderer renderer = Type.getRenderer(element);
            for(String string : renderer.getContent(element)) {
                textBox.addLine(string);
            }
        }
        panel.addComponent(textBox);
    }

    public static @NotNull TextBox generateFullBodyTextBox() {
        TextBox box = new TextBox(new TerminalSize(100, 100), TextBox.Style.MULTI_LINE);
        box.setLayoutData(LinearLayout.createLayoutData(LinearLayout.Alignment.Fill));
        box.setSize(new TerminalSize(100, 100));
        box.setTheme(new SimpleTheme(TextColor.ANSI.WHITE, TextColor.ANSI.BLACK));
        box.setReadOnly(true);
        return box;
    }

    enum Type {
        HEADER(Set.of("h1", "h2", "h3", "h4", "h5", "h6", "header"), new ASCIIHeaderRenderer()),
        TEXT(Set.of("p", "span", "div", "textarea"), new TextRenderer()),
        IMAGE(Set.of("img"), new ImageRenderer()),
        LIST(Set.of("menu", "ul", "ol"), new TextRenderer()),
        BREAK(Set.of("br"), new BreakRenderer()),
        LINK(Set.of("a"), new LinkRenderer()),
        LINE(Set.of("hr"), new LineRenderer()),
        BUTTON(Set.of("button"), new ButtonRenderer()),
        LIST_ITEM(Set.of("li"), new ListItemRenderer()),
        SMALL_SCRIPT(Set.of("sup", "sub"), new ScriptRenderer());

        private final Set<String> tags;
        private final ElementRenderer renderer;

        private static final UnimplementedElementRenderer UNIMPLEMENTED = new UnimplementedElementRenderer();

        Type(@NotNull Set<String> tags, @NotNull ElementRenderer renderer) {
            this.tags = tags;
            this.renderer = renderer;
        }

        public static @NotNull ElementRenderer getRenderer(@NotNull Element element) {
            for(Type type : Type.values()) {
                if(type.tagMatches(element.tagName())) {
                    return type.renderer;
                }
            }
            return UNIMPLEMENTED;
        }

        public boolean tagMatches(@NotNull String tag) {
            return tags.contains(tag.toLowerCase(Locale.ROOT));
        }
    }

    interface ElementRenderer {

        List<String> getContent(@NotNull Element element);

    }
}
