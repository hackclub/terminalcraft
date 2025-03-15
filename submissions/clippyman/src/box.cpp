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

void delete_draw_confirm(int seloption, const char* id)
{
    nccreate(6, 60, "Confirm delete");

    ncprint(1, 2, "Are you sure you want to delete id %s?", id);

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
// End

void draw_search_box(const std::string& query, const std::vector<std::string>& entries_id, const std::vector<std::string>& results, const size_t max_width,
                            const size_t max_visible, const size_t selected, const size_t scroll_offset)
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
            if (is_selected)
                attron(A_REVERSE);  // Apply highlight before printing

            // Print the line with padding (4 spaces)
            mvprintw(row++, 6, "%s. %s", entries_id[i].c_str(), line.c_str());  // 6 for padding (2 + 4 spaces)

            if (is_selected)
                attroff(A_REVERSE);  // Remove highlight after printing
        }

        items_displayed++;
    }

    // Move the cursor near the search query
    const int cursor_x = 2 + 8 + query.length();  // 2 for box border, 8 for "Search: ", query.length() for the query
    move(1, cursor_x);
    refresh();
}
