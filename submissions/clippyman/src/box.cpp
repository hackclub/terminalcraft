#include <ncurses.h>
#include <wchar.h>

#include <sstream>
#include <string>
#include <vector>

static std::vector<std::string> wrap_text(const std::string& text, const size_t max_width)
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
void draw_search_box(const std::string& query, const std::vector<std::string>& results,
                     const std::vector<std::string>& results_id, const size_t selected, size_t& scroll_offset,
                     const size_t cursor_x, const bool is_search_tab)
{
    erase();
    box(stdscr, 0, 0);

    int maxy, maxx;
    getmaxyx(stdscr, maxy, maxx);

    // header
    attron(A_BOLD);
    mvprintw(1, 2, "Search: %s", query.c_str());
    attroff(A_BOLD);
    mvprintw(2, 2, results.size() == 1 ? "(1 result)" : "(%zu results)", results.size());

    // First ensure selected item is visible
    size_t lines_above = 0;
    if (selected < scroll_offset)
    {
        scroll_offset = selected;
    }
    else
    {
        // Calculate lines needed to show selected item
        size_t needed_lines = 3;  // header + spacing (1)
        for (size_t i = scroll_offset; i <= selected; i++)
        {
            const auto& wrapped = wrap_text(results[i], maxx - 11);
            needed_lines += wrapped.size() + 1;
            if (needed_lines > static_cast<size_t>(maxy - 1))
            {
                scroll_offset = i;
                break;
            }
            if (i == selected)
            {
                lines_above = needed_lines - (1 + wrapped.size());
            }
        }
    }

    // Draw visible items
    size_t row = 2;
    for (size_t i = scroll_offset; i < results.size(); i++)
    {
        const bool is_selected = (i == selected);
        const auto& wrapped    = wrap_text(results[i], maxx - 11);

        // Check space for this item
        if (row + 1 + wrapped.size() >= static_cast<size_t>(maxy - 1))
            break;

        // Draw item
        ++row;
        for (const std::string& line : wrapped)
        {
            if (is_selected && !is_search_tab)
                attron(A_REVERSE);
            mvprintw(++row, 6, "#%s: %s", results_id[i].c_str(), line.c_str());
            if (is_selected && !is_search_tab)
                attroff(A_REVERSE);
        }
    }

    if (is_search_tab)
        move(1, cursor_x);
    else
        // Calculate cursor row based on lines above selected item
        move(3 + lines_above, 6);

    refresh();
}
