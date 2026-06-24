package net.wiicart.webcli.web.renderer.primitive;

import com.googlecode.lanterna.SGR;
import com.googlecode.lanterna.TerminalSize;
import com.googlecode.lanterna.TextColor;
import com.googlecode.lanterna.graphics.SimpleTheme;
import com.googlecode.lanterna.gui2.EmptySpace;
import com.googlecode.lanterna.gui2.LinearLayout;
import com.googlecode.lanterna.gui2.Panel;
import com.googlecode.lanterna.gui2.TextBox;
import net.wiicart.webcli.web.renderer.Renderer;
import org.jetbrains.annotations.NotNull;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;

import java.util.Iterator;
import java.util.Locale;
import java.util.Set;

@SuppressWarnings("unused")
public final class PrimitiveRenderer implements Renderer {

    private final Document document;

    private static final Set<String> HEADERS = Set.of("h1", "h2", "h3", "h4", "h5", "h6");

    @SuppressWarnings("unused")
    public PrimitiveRenderer(@NotNull Document document) {
        this.document = document;
    }

    public void applyContent(@NotNull Panel panel) {
        panel.addComponent(new EmptySpace(TextColor.ANSI.WHITE, new TerminalSize(500, 1)));

        Iterator<Element> it = document.body().stream().iterator();
        while (it.hasNext()) {
            Element element = it.next();
            String text = element.ownText().strip().trim();
            if(text.isEmpty()) {
                continue;
            }

            if(HEADERS.contains(element.tagName().toLowerCase(Locale.ROOT))) {
                panel.addComponent(createHeaderTextBox(text));
            } else {
                panel.addComponent(createTextBox(text));
            }
            System.out.println(text);
        }
    }

    private @NotNull TextBox createTextBox(String content) {
        TextBox textBox = new TextBox(content, TextBox.Style.MULTI_LINE);
        textBox.setTheme(new SimpleTheme(TextColor.ANSI.BLACK, TextColor.ANSI.WHITE));
        textBox.setLayoutData(LinearLayout.createLayoutData(LinearLayout.Alignment.Fill));
        textBox.setReadOnly(true);
        return textBox;
    }

    private @NotNull TextBox createHeaderTextBox(@NotNull String content) {
        TextBox box = createTextBox(content);
        box.setTheme(new SimpleTheme(TextColor.ANSI.BLACK, TextColor.ANSI.WHITE, SGR.BOLD));
        return createTextBox(content);
    }

    protected interface ElementRenderer {

        void applyContent(@NotNull Panel panel, @NotNull Element element);

    }

}
