// tui.hpp
#pragma once

#ifdef _WIN32 // windows

#include <wchar.h>
#include <windows.h>

#else // not windows

#include <csignal>
#include <err.h>       // err
#include <fcntl.h>     // open
#include <sys/ioctl.h> // ioctl, TIOCGWINSZ
#include <unistd.h>    // close

#endif

#include <cassert>
#include <iostream>
#include <ostream>
#include <sstream>
#include <string>

namespace tui {
    // only the Esc character
    constexpr const char ESC = '\x1B';
    // Control Sequence Introducer actually == "ESC[" almost everything starts with this
    constexpr const char* CSI = "\x1B[";

    // variadic template function to concatenate any number of arguments
    template <typename... Args> std::string concat(Args&&... args) {
        std::ostringstream oss;
        (void)std::initializer_list<int>{
            (oss << std::forward<Args>(args), 0)...}; // using initializer_list for fold-like behavior
        return oss.str();
    }

// Control Sequence Introducer
#define csi(...) std::cout << concat("\x1B[", __VA_ARGS__);
// function using Control Sequence Introducer
#define csi_fn(name, ...)                                                                                              \
    inline void name() { csi(__VA_ARGS__) }

// ANSII Escape Sequence
#define esc(...) std::cout << concat("\x1B", __VA_ARGS__);
// function using ANSII Escape Sequence
#define esc_fn(name, ...)                                                                                              \
    inline void name() { esc(__VA_ARGS__) }

#ifdef _WIN32 // windows
// basic setup of windows terminal handling
#define win_setup()                                                                                                    \
    HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);                                                                    \
    if (hStdin == INVALID_HANDLE_VALUE) {                                                                              \
        std::cerr << "Error getting the standard input handle." << std::endl;                                          \
        exit(1);                                                                                                       \
    }                                                                                                                  \
    DWORD mode;                                                                                                        \
    if (!GetConsoleMode(hStdin, &mode)) {                                                                              \
        std::cerr << "Error getting the console mode." << std::endl;                                                   \
        exit(1);                                                                                                       \
    }
#endif

    inline void enable_raw_mode() {
#ifdef _WIN32 // windows
        win_setup();

        DWORD newMode = mode;
        newMode &= ~(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT | ENABLE_PROCESSED_INPUT);

        if (!SetConsoleMode(hStdin, newMode)) {
            std::cerr << "Error setting the console to raw mode." << std::endl;
            exit(1);
        }
#else // not windows
        system("stty raw");
        system("stty -echo");

        // struct termios term {};
        // if (tcgetattr(STDIN_FILENO, &term) == -1) {
        //     std::cerr << "Error getting terminal attributes." << std::endl;
        //     exit(1);
        // }

        // struct termios raw = term;
        // raw.c_lflag &= ~(ICANON | ECHO);

        // if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == -1) {
        //     std::cerr << "Error setting terminal to raw mode." << std::endl;
        //     exit(1);
        // }
#endif
    }

    inline void disable_raw_mode() {
#ifdef _WIN32 // windows
        win_setup();

        // Restore original mode
        mode |= (ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT | ENABLE_PROCESSED_INPUT);
        if (!SetConsoleMode(hStdin, mode)) {
            std::cerr << "Error restoring the console mode." << std::endl;
            exit(1);
        }
#else // not windows
        system("stty -raw");
        system("stty echo");

        // struct termios term {};
        // if (tcgetattr(STDIN_FILENO, &term) == -1) {
        //     std::cerr << "Error getting terminal attributes." << std::endl;
        //     exit(1);
        // }

        // // Restore original attributes
        // term.c_lflag |= (ICANON | ECHO);

        // if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &term) == -1) {
        //     std::cerr << "Error restoring terminal mode." << std::endl;
        //     exit(1);
        // }
#endif
    }

#undef win_setup

    namespace cursor {
// template for moving cursor
// moves cursor `n` times to `dir`
#define move_n(dir, ch)                                                                                                \
    inline void dir(unsigned n = 1) { csi(n, '#', ch); }

        move_n(up, 'A');
        move_n(down, 'B');
        move_n(right, 'C');
        move_n(left, 'D');

        // moves cursor one row up, scrolling if needed
        esc_fn(up_n_scroll, 'M');
        // moves cursor to beginning of next line, `n` rows down
        move_n(next_line, 'E');
        // moves cursor to beginning of previous line, `n` rows up
        move_n(prev_line, 'F');

        // moves cursor to home position (1;1)
        csi_fn(home, 'H');
        // moves cursor to (`row`; `col`), INFO: both `row` and `col` start at 1
        inline void set_position(unsigned row, unsigned col) { csi(row, ';', col, 'H'); }
        // moves cursor to column `n`
        move_n(to_column, 'G');
#undef move_n

        // save cursor position
        esc_fn(save, '7');
        // restore previously saved cursor position
        esc_fn(restore, '8');

        // set visibility
        inline void visible(bool visible) { csi("?25", (visible ? 'h' : 'l')); }

        // tell the terminal to check where the cursor is
        csi_fn(query_position, "6n");

        // returns: (rows;cols)
        // WARN: can be quite slow, don't use on eg. every screen update!
        inline std::pair<unsigned, unsigned> get_position() {
            query_position();
            std::flush(std::cout);
            // Read the response: ESC [ rows ; cols R
            char ch = 0;
            unsigned rows = 0;
            unsigned cols = 0;
            if (std::cin.get(ch) && ch == ESC && std::cin.get(ch) && ch == '[') {
                std::cin >> rows;
                std::cin.get(ch); // skip the ';'
                std::cin >> cols;
                std::cin.ignore(); // skip the 'R'
            }

            return {rows, cols};
        }
    } // namespace cursor

    namespace screen {
        // clears
        csi_fn(clear, "2J");
        csi_fn(clear_line, "2K");
        csi_fn(clear_line_right, "K");

        // erases
        inline void erase_in_line(unsigned n = 0) { csi(n, 'K'); }
        inline void erase_in_display(unsigned n = 0) { csi(n, 'J'); }
        csi_fn(erase_saved_lines, "3J");

        csi_fn(save, "?47h");
        csi_fn(restore, "?47l");

        inline void alternative_buffer(bool enable) { csi("?1049", (enable ? 'h' : 'l')); }

        inline void scroll_up(unsigned n = 1) { csi(n, 'S'); }
        inline void scroll_down(unsigned n = 1) { csi(n, 'T'); }

        // get the size of the terminal.
        // returns: (rows;cols)/(y;x)
        inline std::pair<unsigned, unsigned> size() {
#ifdef _WIN32
            HANDLE console;
            CONSOLE_SCREEN_BUFFER_INFO info;
            short rows;
            short columns;
            // create a handle to the console screen
            console = CreateFileW(L"CONOUT$", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                                  OPEN_EXISTING, 0, NULL);
            if (console == INVALID_HANDLE_VALUE)
                return {0, 0};

            // calculate the size of the console window
            if (GetConsoleScreenBufferInfo(console, &info) == 0)
                return {0, 0};
            CloseHandle(console);
            columns = info.srWindow.Right - info.srWindow.Left + 1;
            rows = info.srWindow.Bottom - info.srWindow.Top + 1;

            return {rows, columns};
#else
            struct winsize ws {};
            int fd = 0;

            // open the controlling terminal.
            fd = open("/dev/tty", O_RDWR | O_CLOEXEC);
            if (fd < 0) {
                err(1, "/dev/tty");
            }

            // get window size of terminal
            if (ioctl(fd, TIOCGWINSZ, &ws) < 0) {
                err(1, "/dev/tty");
            }

            // printf("%d rows by %d columns\n", ws.ws_row, ws.ws_col);
            // printf("(%d by %d pixels)\n", ws.ws_xpixel, ws.ws_ypixel);
            close(fd);
            return {ws.ws_row, ws.ws_col};
#endif
        }
    } // namespace screen

    namespace text {
        namespace style {
            enum Style {
                reset = 0,
                bold = 1,
                dim = 2,
                italic = 3,
                underline = 4,
                blink = 5,
                inverted = 7,
                invisible = 8,
                strikethrough = 9,
            };

            inline std::string style(const Style& style) { return concat(CSI, static_cast<unsigned>(style), 'm'); }

// generate for cout << STYLE_style(); eg.: cout << bold_style();
#define stylize(STYLE)                                                                                                 \
    inline std::string STYLE##_style() { return style(STYLE); }
// generate for cout << STYLE_style(text); eg.: cout << bold_style(text);
#define stylize_text(STYLE)                                                                                            \
    inline std::string STYLE##_style(const std::string& text) { return concat(style(STYLE), text, reset_style()); }    \
    inline std::string STYLE##_style(const char* text) { return concat(style(STYLE), text, reset_style()); }
// generate all
#define make_stylizer(STYLE) stylize(STYLE) stylize_text(STYLE)

            stylize(reset);
            inline std::string style_and_reset(const Style& st, const std::string& text) {
                return concat(style(st), text, reset_style());
            }

            make_stylizer(bold);
            make_stylizer(dim);
            make_stylizer(italic);
            make_stylizer(underline);
            make_stylizer(blink);
            make_stylizer(inverted);
            make_stylizer(invisible);
            make_stylizer(strikethrough);
#undef make_stylizer
#undef stylize_text
#undef stylize

            // printf '\e]8;;http://example.com\e\\This is a link\e]8;;\e\\\n'
            // printf 'ESC]8;;{link}ESC\\{text}ESC]8;;ESC\\'
            inline std::string link(const std::string& link, const std::string& text) {
                return concat(ESC, "]8;;", link, ESC, "\\", text, ESC, "]8;;", ESC, "\\");
            }
            inline std::string link(const char* link, const char* text) {
                return concat(ESC, "]8;;", link, ESC, "\\", text, ESC, "]8;;", ESC, "\\");
            }

        } // namespace style

        namespace color {
            enum Color {
                black = 0,
                red,
                green,
                yellow,
                blue,
                magenta,
                cyan,
                white,
                basic,
            };

            // fg or bg
            inline std::string colorizer(const Color& c, bool fg) {
                return concat(CSI, (fg ? '3' : '4'), static_cast<unsigned>(c), 'm');
            }

// generate for cout << COLOR_{fg, bg}();
#define colorize(COLOR)                                                                                                \
    inline std::string COLOR##_fg() { return colorizer(COLOR, true); }                                                 \
    inline std::string COLOR##_bg() { return colorizer(COLOR, false); }

// generate for cout << COLOR_{fg, bg}(text);
#define colorize_text(COLOR)                                                                                           \
    inline std::string COLOR##_fg(const std::string& text) {                                                           \
        return concat(colorizer(COLOR, true), text, style::reset_style());                                             \
    }                                                                                                                  \
    inline std::string COLOR##_fg(const char* text) {                                                                  \
        return concat(colorizer(COLOR, true), text, style::reset_style());                                             \
    }                                                                                                                  \
    inline std::string COLOR##_bg(const std::string& text) {                                                           \
        return concat(colorizer(COLOR, false), text, style::reset_style());                                            \
    }                                                                                                                  \
    inline std::string COLOR##_bg(const char* text) {                                                                  \
        return concat(colorizer(COLOR, false), text, style::reset_style());                                            \
    }

// generate all
#define make_colorizer(COLOR) colorize(COLOR) colorize_text(COLOR)
            make_colorizer(black);
            make_colorizer(red);
            make_colorizer(green);
            make_colorizer(yellow);
            make_colorizer(blue);
            make_colorizer(magenta);
            make_colorizer(cyan);
            make_colorizer(white);
            make_colorizer(basic);
#undef make_colorizer
#undef colorize_text
#undef colorize

            // r, g, b values have to be valid:  [0;255]
            inline std::string rgb(unsigned r, unsigned g, unsigned b, bool fg) {
                assert(r >= 0 && r <= 255 && g >= 0 && g <= 255 && b >= 0 && b <= 255);
                return concat(CSI, (fg ? '3' : '4'), "8;2;", r, ';', g, ';', b, 'm');
            }
            inline std::string rgb(unsigned r, unsigned g, unsigned b, bool fg, const std::string& text) {
                return concat(rgb(r, g, b, fg), text, style::reset_style());
            }

        } // namespace color

    } // namespace text

    class string : public std::string {
      public:
        string() = default;
        template <typename T> string(T s) : std::string(concat(s)) {}
        string(const char* s) : std::string(s) {}
        string(const std::string& s) : std::string(s) {}

// generate this.STYLE(): eg this.italic()
#define make_style(STYLE)                                                                                              \
    inline tui::string STYLE() const { return text::style::STYLE##_style(*this); }

        make_style(bold);
        make_style(dim);
        make_style(italic);
        make_style(underline);
        make_style(blink);
        make_style(inverted);
        make_style(invisible);
        make_style(strikethrough);
#undef make_style

// generate this.COLOR(): eg this.red()
#define make_color(COLOR)                                                                                              \
    inline tui::string COLOR() const { return text::color::COLOR##_fg(*this); }                                        \
    inline tui::string on_##COLOR() const { return text::color::COLOR##_bg(*this); }

        make_color(black);
        make_color(red);
        make_color(green);
        make_color(yellow);
        make_color(blue);
        make_color(magenta);
        make_color(cyan);
        make_color(white);
        make_color(basic);
#undef make_color

        inline string link(const char* link) { return text::style::link(link, *this); }
        inline string rgb(unsigned r, unsigned g, unsigned b) const { return text::color::rgb(r, g, b, true, *this); }
        inline string on_rgb(unsigned r, unsigned g, unsigned b) const {
            return text::color::rgb(r, g, b, false, *this);
        }
    };

    // void handle_resize(int /*sig*/) { screen::clear(); }
    using fn_ptr = void (*)(int);
    // WARN: does not work on windows
    // needs a void function, that takes an int
    // function pointer: `void function_name(int sig) { stuff }`
    inline void set_up_resize(fn_ptr handle_resize) {
#ifdef _WIN32
        // TODO: make it work, or at least try to
#else
        // register the signal handler for SIGWINCH
        struct sigaction sa {};
        sa.sa_handler = handle_resize;
        sa.sa_flags = SA_RESTART; // restart functions if interrupted by handler
        sigaction(SIGWINCH, &sa, nullptr);
#endif
    }

    inline void init(bool enable_cursor = false) {
#ifdef _WIN32
        SetConsoleOutputCP(65001); // use utf-8
#endif
        tui::enable_raw_mode();
        tui::cursor::visible(enable_cursor);
        tui::screen::alternative_buffer(true);
        tui::screen::clear();
        tui::cursor::home();
    }
    inline void reset() {
        tui::screen::alternative_buffer(false);
        tui::cursor::visible(true);
        tui::disable_raw_mode();
    }
    namespace input {
#include "input.hpp"
    } // namespace input
} // namespace tui
