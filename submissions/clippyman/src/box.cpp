#include <ncurses.h>
#include <wchar.h>

#include <sstream>
#include <string>
#include <vector>

static std::vector<std::string> wrap_text(const std::string& text, size_t max_width)
{
    std::vector<std::string> lines;
    std::stringstream        ss(text);
    std::string              line;

    while (std::getline(ss, line, '\n'))
    {
        while (line.length() > max_width)
        {
            lines.push_back(line.substr(0, max_width));
            line = line.substr(max_width);
        }

        lines.push_back(line);
    }

    return lines;
}

// Begin: some code taken from https://github.com/rofl0r/ncdu in src/delete.c and src/util.c
#define ncaddstr(r, c, s) mvaddstr(subwinr + (r), subwinc + (c), s)
#define ncmove(r, c) move(subwinr + (r), subwinc + (c))

int subwinr;
int subwinc;

static void nccreate(int height, int width, const char* title)
{
    int i;

    int winrows, wincols;
    getmaxyx(stdscr, winrows, wincols);
    subwinr = winrows / 2 - height / 2;
    subwinc = wincols / 2 - width / 2;

    /* clear window */
    for (i = 0; i < height; i++)
        mvhline(subwinr + i, subwinc, ' ', width);

    /* box() only works around curses windows, so create our own */
    move(subwinr, subwinc);
    addch(ACS_ULCORNER);
    for (i = 0; i < width - 2; i++)
        addch(ACS_HLINE);
    addch(ACS_URCORNER);

    move(subwinr + height - 1, subwinc);
    addch(ACS_LLCORNER);
    for (i = 0; i < width - 2; i++)
        addch(ACS_HLINE);
    addch(ACS_LRCORNER);

    mvvline(subwinr + 1, subwinc, ACS_VLINE, height - 2);
    mvvline(subwinr + 1, subwinc + width - 1, ACS_VLINE, height - 2);

    /* title */
    attron(A_BOLD);
    mvaddstr(subwinr, subwinc + 4, title);
    attroff(A_BOLD);
}

static void ncprint(int r, int c, const char* fmt, ...)
{
    va_list arg;
    va_start(arg, fmt);
    move(subwinr + r, subwinc + c);
    vw_printw(stdscr, fmt, arg);
    va_end(arg);
}

void delete_draw_confirm(const int seloption)
{
    nccreate(6, 60, "Confirm delete");

    ncprint(1, 2, "Are you sure you want to delete this content?");

    if (seloption == 1)
        attron(A_REVERSE);
    ncaddstr(4, 20, "yes");
    attroff(A_REVERSE);

    if (seloption == 0)
        attron(A_REVERSE);
    ncaddstr(4, 34, "no");
    attroff(A_REVERSE);

    switch (seloption)
    {
        case 0: ncmove(4, 20); break;
        case 1: ncmove(4, 34); break;
    }
}
// End: some code taken from https://github.com/rofl0r/ncdu in src/delete.c and src/util.c

// omfg too many args
void draw_search_box(const std::string& query, const std::vector<std::string>& results, const size_t max_width,
                            const size_t max_visible, const size_t selected, const size_t scroll_offset, const size_t cursor_x, bool is_search_tab)
{
    clear();
    box(stdscr, 0, 0);  // Draw the root box

    attron(A_BOLD);
    mvprintw(1, 2, "Search: %s", query.c_str());
    attroff(A_BOLD);

    size_t row             = 2;  // Start drawing items from row 2
    size_t items_displayed = 0;  // Track the number of items displayed

    for (size_t i = scroll_offset; i < results.size() && items_displayed < max_visible; ++i)
    {
        const bool is_selected = (i == selected);

        // Add vertical spacing between items
        row++;

        for (const std::string& line : wrap_text(results[i], max_width - 6))
        {
            if (is_selected && !is_search_tab)
                attron(A_REVERSE);  // Apply highlight before printing

            // Print the line with padding (4 spaces)
            mvprintw(row++, 6, "%s", line.c_str());  // 6 for padding (2 + 4 spaces)

            if (is_selected && !is_search_tab)
                attroff(A_REVERSE);  // Remove highlight after printing
        }

        items_displayed++;
    }

    // Move the cursor depending on the active tab
    if (is_search_tab)
        move(1, cursor_x);
    else
        move(3 + selected - scroll_offset, 6);  // Move to the selected result
    
    refresh();
}
