#ifndef PLATFORM_UNIX
#define PLATFORM_UNIX 0
#endif

#define _POSIX_C_SOURCE 2  // getopt
#include <getopt.h>
#include <ncurses.h>
#include <unistd.h>

#include <algorithm>
#include <cctype>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <string>
#include <string_view>
#include <vector>
#if !PLATFORM_UNIX
#include <chrono>
#include <thread>
#endif

#include "EventData.hpp"
#include "clipboard/ClipboardListener.hpp"
#include "clipboard/unix/ClipboardListenerUnix.hpp"
#include "config.hpp"
#include "fmt/base.h"
#include "fmt/format.h"
#include "fmt/os.h"
#include "rapidjson/document.h"
#include "rapidjson/error/en.h"
#include "rapidjson/filereadstream.h"
#include "rapidjson/filewritestream.h"
#include "rapidjson/prettywriter.h"
#include "rapidjson/rapidjson.h"
#include "utf8.h"
#include "util.hpp"
#if PLATFORM_X11
#include <xcb/xproto.h>

#include "clipboard/x11/ClipboardListenerX11.hpp"
#elif PLATFORM_WAYLAND
#include "clipboard/wayland/ClipboardListenerWayland.hpp"
extern "C" {
#include "clipboard/wayland/wayclip/common.h"
}
#endif

// clang-format off
// https://cfengine.com/blog/2021/optional-arguments-with-getopt-long/
// because "--opt-arg arg" won't work
// but "--opt-arg=arg" will
#define OPTIONAL_ARGUMENT_IS_PRESENT \
    ((optarg == NULL && optind < argc && argv[optind][0] != '-') \
     ? (bool) (optarg = argv[optind++]) \
     : (optarg != NULL))
// clang-format on

// include/config.hpp
Config config;
// src/box.cpp
void draw_search_box(const std::string& query, const std::vector<std::string>& results, const size_t max_width,
                     const size_t max_visible, const size_t selected, const size_t scroll_offset, const size_t cursor_x,
                     bool is_search_tab);
void delete_draw_confirm(const int seloption);

static void version()
{
    fmt::print("clippyman " VERSION " branch " BRANCH "\n");
    std::exit(EXIT_SUCCESS);
}

static void help(bool invalid_opt = false)
{
    constexpr std::string_view help =
R"(Usage: clippyman [OPTIONS]...
    -i, --input                 Save input text from stdin (pipes) or by typing
    -c, --copy                  Copy the input from stdin into the clipboard (x11 only)
    -p, --path <path>           Path to where we'll search/save the clipboard history
    -P, --primary [<bool>]      Use the primary clipboard instead
    -S, --silent [<bool>]       Print or Not an info message along the search content you selected
    --wl-seat <name>            The seat for using in wayland (just leave it empty if you don't know what's this)
    -s, --search                Delete/Search clipboard history.
                                Press TAB to switch beetwen search bar and clipboard history.
                                In clipboard history: press 'd' for delete, press enter for output selected text

    -C, --config <path>         Path to the config file to use
    --gen-config [<path>]       Generate default config file to config folder (if path, it will generate to the path)
                                Will ask for confirmation if file exists already

    -h, --help                  Print this help menu
    -V, --version               Print the version along with the git branch it was built
)";
    fmt::print("{}\n", help);
    std::exit(invalid_opt);
}

void CopyCallback(const CopyEvent& event)
{
    info("Copied: {}", event.content);
}

void CopyEntry(const CopyEvent& event)
{
    FILE*                     file = fopen(config.path.c_str(), "r+");
    rapidjson::Document       doc;
    char                      buf[UINT16_MAX] = { 0 };
    rapidjson::FileReadStream stream(file, buf, sizeof(buf));

    if (doc.ParseStream(stream).HasParseError())
    {
        fclose(file);
        die("Failed to parse {}: {} at offset {}", config.path, rapidjson::GetParseError_En(doc.GetParseError()),
            doc.GetErrorOffset());
    }

    rapidjson::Document::AllocatorType& allocator = doc.GetAllocator();

    std::string id_str{ "0" };
    if (!doc["entries"].ObjectEmpty())
    {
        const auto& lastId = (doc["entries"].MemberEnd() - 1)->name;
        id_str             = fmt::to_string(std::stoi(lastId.GetString()) + 1);
    }
    rapidjson::GenericStringRef<char> id_ref(id_str.c_str());
    rapidjson::Value                  value_content(event.content.c_str(), event.content.size(), allocator);
    doc["entries"].AddMember(id_ref, value_content, allocator);

    unsigned int i = 0;
    for (const char* ptr = event.content.c_str(); *ptr; ++i)
    {
        char utf8_char[5] = { 0 };  // UTF-8 characters are max 4 bytes + null terminator
        int  codepoint;
        ptr = utf8codepoint(ptr, &codepoint);
        utf8catcodepoint(utf8_char, codepoint, sizeof(utf8_char));

        std::string      ch_str(utf8_char);
        rapidjson::Value key;
        key.SetString(ch_str.c_str(), static_cast<rapidjson::SizeType>(ch_str.length()), allocator);

        if (doc["index"].HasMember(key))
        {
            if (!doc["index"][key].HasMember(id_ref))
                doc["index"][key].AddMember(id_ref, rapidjson::kArrayType, allocator);

            doc["index"][key][id_ref.s].PushBack(i, allocator);
        }
        else
        {
            rapidjson::Value array(rapidjson::kArrayType);
            array.PushBack(i, allocator);
            rapidjson::Value obj(rapidjson::kObjectType);
            obj.AddMember(id_ref, array, allocator);
            doc["index"].AddMember(key, obj, allocator);
        }
    }

    // seek back to the beginning to overwrite
    fseek(file, 0, SEEK_SET);

    char                                                writeBuffer[UINT16_MAX] = { 0 };
    rapidjson::FileWriteStream                          writeStream(file, writeBuffer, sizeof(writeBuffer));
    rapidjson::PrettyWriter<rapidjson::FileWriteStream> fileWriter(writeStream);
    fileWriter.SetFormatOptions(rapidjson::kFormatSingleLineArray);  // Disable newlines between array elements
    doc.Accept(fileWriter);

    fflush(file);
    ftruncate(fileno(file), ftell(file));
    fclose(file);
}

void CreateInitialCache(const std::string& path)
{
    if (access(path.data(), F_OK) == 0)
        return;

    constexpr std::string_view json =
R"({
    "entries": {},
    "index": {}
})";

    const size_t pos = path.rfind('/');
    if (pos != path.npos)
        std::filesystem::create_directories(path.substr(0, pos));

    auto f = fmt::output_file(path, fmt::file::CREATE | fmt::file::RDWR | fmt::file::TRUNC);
    f.print("{}", json);
    f.close();
}

static void removeEntries(std::vector<std::string>& results_value, std::vector<std::string>& results_id,
                          const std::string& query)
{
    auto it_id = results_id.begin();

    auto new_end = std::remove_if(results_value.begin(), results_value.end(), [&](const std::string& s) {
        bool remove = !hasStart(s, query);
        if (remove)
            it_id = results_id.erase(it_id);
        else
            ++it_id;
        return remove;
    });

    results_value.erase(new_end, results_value.end());
}

#define SEARCH_TITLE_LEN (2 + 8)  // 2 for box border, 8 for "Search: "
int search_algo(const CClipboardListener& clipboardListener, const Config& config)
{
    initscr();
    noecho();
    cbreak();              // Enable immediate character input
    keypad(stdscr, TRUE);  // Enable arrow keys

restart:
    FILE*                     file = fopen(config.path.c_str(), "r+");
    rapidjson::Document       doc;
    char                      buf[UINT16_MAX] = { 0 };
    rapidjson::FileReadStream stream(file, buf, sizeof(buf));

    if (doc.ParseStream(stream).HasParseError())
    {
        fclose(file);
        endwin();
        die("Failed to parse {}: {} at offset {}", config.path, rapidjson::GetParseError_En(doc.GetParseError()),
            doc.GetErrorOffset());
    }

    std::vector<std::string> entries_id, entries_value;
    for (auto it = doc["entries"].MemberBegin(); it != doc["entries"].MemberEnd(); ++it)
    {
        entries_id.push_back(it->name.GetString());
        entries_value.push_back(it->value.GetString());
    }
    std::vector<std::string> results(entries_value), results_id(entries_id);

    std::string query;
    int         ch            = 0;
    size_t      selected      = 0;
    size_t      scroll_offset = 0;
    size_t      cursor_x      = SEARCH_TITLE_LEN;
    bool        is_search_tab = true;

    const int max_width   = getmaxx(stdscr) - 5;
    const int max_visible = ((getmaxy(stdscr) - 3) / 2) * 0.75;
    draw_search_box(query, results, max_width, max_visible, selected, scroll_offset, cursor_x, is_search_tab);
    move(1, cursor_x);

    bool del          = false;
    bool del_selected = false;
    while ((ch = getch()) != ERR)
    {
        if (!del && ch == 27)  // ESC
            break;

        if (ch == '\t')
        {
            is_search_tab = !is_search_tab;
        }
        else if (is_search_tab)
        {
            del         = false;
            bool erased = false;
            if (ch == KEY_BACKSPACE || ch == 127)
            {
                if (!query.empty())
                {
                    // decrease then pass
                    if (cursor_x > SEARCH_TITLE_LEN)
                        query.erase(--cursor_x - SEARCH_TITLE_LEN, 1);

                    erased     = true;
                    results    = entries_value;
                    results_id = entries_id;
                    removeEntries(results, results_id, query);
                }
            }
            else if (ch == KEY_LEFT)
            {
                if (cursor_x > SEARCH_TITLE_LEN)
                    --cursor_x;
            }
            else if (ch == KEY_RIGHT)
            {
                if (cursor_x < SEARCH_TITLE_LEN + query.size())
                    ++cursor_x;
            }
            else if (ch == KEY_DOWN)
            {
                is_search_tab = false;
            }
            else if (!(ch >= KEY_UP && ch <= KEY_MAX))
            {
                // pass then increase
                if (!erased)
                    query.insert(cursor_x++ - SEARCH_TITLE_LEN, 1, ch);
                erased = false;

                selected      = 0;
                scroll_offset = 0;

                removeEntries(results, results_id, query);
            }
        }
        else
        {
            // go up
            if (ch == KEY_DOWN || ch == KEY_RIGHT)
            {
                if (del)
                    del_selected = false;

                else if (selected < results.size() - 1)
                {
                    ++selected;
                    if (selected >= scroll_offset + max_visible)
                        ++scroll_offset;
                }
            }
            // go down
            else if (ch == KEY_UP || ch == KEY_LEFT)
            {
                if (del)
                {
                    del_selected = true;
                }
                else if (selected == 0)
                {
                    is_search_tab = true;
                }
                else if (selected > 0)
                {
                    --selected;
                    if (selected < scroll_offset)
                        --scroll_offset;
                }
            }
            // pressed 'd' and operation delete is false
            else if (ch == 'd' && !del)
            {
                del = true;
            }
            // operation delete and choose "yes"
            else if (del && ch == '\n' && del_selected)
            {
                del          = false;
                del_selected = false;
                results.clear();
                entries_id.clear();
                entries_value.clear();

                doc["entries"].EraseMember(results_id[selected].c_str());
                // {"c":{"0": [1,3,7]}}
                for (auto it = doc["index"].MemberBegin(); it != doc["index"].MemberEnd(); ++it)
                    doc["index"][it->name.GetString()].EraseMember(results_id[selected].c_str());
                results_id.clear();

                selected      = 0;
                scroll_offset = 0;
                fseek(file, 0, SEEK_SET);

                char                                                writeBuffer[UINT16_MAX] = { 0 };
                rapidjson::FileWriteStream                          writeStream(file, writeBuffer, sizeof(writeBuffer));
                rapidjson::PrettyWriter<rapidjson::FileWriteStream> fileWriter(writeStream);
                fileWriter.SetFormatOptions(
                    rapidjson::kFormatSingleLineArray);  // Disable newlines between array elements
                doc.Accept(fileWriter);
                ftruncate(fileno(file), ftell(file));
                fflush(file);
                goto restart;  // yes... let's just restart everything for now
            }
            // operation delete and pressed 'q' or "no"
            else if (del && (!del_selected || ch == 'q'))
            {
                del = false;
            }
            // pressed an item
            else if (ch == '\n' && !results.empty())
            {
                endwin();
                clipboardListener.CopyToClipboard(results[selected]);
                return 0;
            }
        }

        if (del)
            delete_draw_confirm(del_selected);
        else
            draw_search_box(query, (query.empty() ? entries_value : results), max_width, max_visible, selected,
                            scroll_offset, cursor_x, is_search_tab);

        curs_set(is_search_tab);
    }

    endwin();
    return 0;
}

// clang-format off
static bool str_to_bool(const std::string_view str)
{
    return (str == "true" || str == "1" || str == "enable");
}

// parseargs() but only for parsing the user config path trough args
// and so we can directly construct Config
static std::string parse_config_path(int argc, char* argv[], const std::string& configDir)
{
    int opt = 0;
    int option_index = 0;
    opterr = 0;
    const char *optstring = "-C:";
    static const struct option opts[] = {
        {"config", required_argument, 0, 'C'},
        {0,0,0,0}
    };

    while ((opt = getopt_long(argc, argv, optstring, opts, &option_index)) != -1)
    {
        switch (opt)
        {
            // skip errors or anything else
            case 0:
            case '?':
                break;

            case 'C': 
                if (!std::filesystem::exists(optarg))
                    die("config file '{}' doesn't exist", optarg);
                return optarg;
        }
    }

    return configDir + "/config.toml";
}

bool parseargs(int argc, char* argv[], Config& config, const std::string& configFile)
{
    int opt               = 0;
    int option_index      = 0;
    opterr                = 1;  // re-enable since before we disabled for "invalid option" error
    const char* optstring = "-Vhiscp:C:P::S::";

    // clang-format off
    static const struct option opts[] = {
        {"version",     no_argument,       0, 'V'},
        {"help",        no_argument,       0, 'h'},
        {"input",       no_argument,       0, 'i'},
        {"search",      no_argument,       0, 's'},
        {"copy",        no_argument,       0, 'c'},

        {"primary",     optional_argument, 0, 'P'},
        {"silent",      optional_argument, 0, 'S'},
        {"path",        required_argument, 0, 'p'},
        {"config",      required_argument, 0, 'C'},
        {"wl-seat",     required_argument, 0, 6968},
        {"gen-config",  optional_argument, 0, 6969},

        {0,0,0,0}
    };

    // clang-format on
    optind = 0;
    while ((opt = getopt_long(argc, argv, optstring, opts, &option_index)) != -1)
    {
        switch (opt)
        {
            case 0:   break;
            case '?': help(EXIT_FAILURE); break;

            case 'V': version(); break;
            case 'h': help(); break;

            case 'p':  config.path = optarg; break;
            case 's':  config.arg_search = true; break;
            case 'i':  config.arg_terminal_input = true; break;
            case 'c':  config.arg_copy_input = true; break;
            case 6968: config.wl_seat = optarg;
            case 'C':  break;  // we have already did it in parse_config_path()

            case 'P':
                if (OPTIONAL_ARGUMENT_IS_PRESENT)
                    config.primary_clip = str_to_bool(optarg);
                else
                    config.primary_clip = true;
                break;

            case 'S':
                if (OPTIONAL_ARGUMENT_IS_PRESENT)
                    config.silent = str_to_bool(optarg);
                else
                    config.silent = true;
                break;

            case 6969:
                if (OPTIONAL_ARGUMENT_IS_PRESENT)
                    config.generateConfig(optarg);
                else
                    config.generateConfig(configFile);
                std::exit(EXIT_SUCCESS);

            default: return false;
        }
    }

    return true;
}

int main(int argc, char* argv[])
{
    const std::string& configDir  = getConfigDir();
    const std::string& configFile = parse_config_path(argc, argv, configDir);

    config.Init(configFile, configDir);
    config.loadConfigFile(configFile);
    if (!parseargs(argc, argv, config, configFile))
        return 1;

    CreateInitialCache(config.path);
    setlocale(LC_ALL, "");

    if ((config.arg_search && config.arg_terminal_input) ||
        (config.arg_search && config.arg_copy_input))
        die("Please only use either --search or --input/--copy");

    CClipboardListenerUnix clipboardListenerUnix;

    bool piped    = !isatty(STDIN_FILENO);
    bool gotstdin = false;
    if (!config.arg_search && (piped || PLATFORM_UNIX || config.arg_terminal_input))
    {
#if !PLATFORM_X11
        if (config.arg_copy_input)
        {
            warn("NOT yet implemented copy to clipboard in here, only X11.");
            return EXIT_FAILURE;
        }
#endif
        clipboardListenerUnix.AddCopyCallback(CopyEntry);

        if (!piped)
            info("Type or Paste the text to save in the clipboard history, then press enter and CTRL+D to save and exit");

        clipboardListenerUnix.PollClipboard();
        gotstdin = true;
#if !PLATFORM_X11
        return EXIT_SUCCESS;
#endif
    }

#if !PLATFORM_UNIX
#if PLATFORM_X11
    CClipboardListenerX11 clipboardListener;
    clipboardListener.AddCopyCallback(CopyCallback);
    clipboardListener.AddCopyCallback(CopyEntry);
#elif PLATFORM_WAYLAND
    struct wc_options wl_options = {
        "text/plain;charset=utf-8",
        config.wl_seat.empty() ? NULL : config.wl_seat.c_str(),
        false,
        config.primary_clip
    };
    CClipboardListenerWayland clipboardListener(wl_options);
    clipboardListener.AddCopyCallback(CopyCallback);
    clipboardListener.AddCopyCallback(CopyEntry);
#endif

    if (config.arg_search)
        return search_algo(clipboardListener, config);

    if (config.arg_copy_input)
    {
#if !PLATFORM_X11
        warn("NOT yet implemented copy to clipboard in here, only X11.");
        return EXIT_FAILURE;
#endif
        if (!gotstdin)
        {
            info("Type or Paste the text to copy into the clipboard, then press enter and CTRL+D to save and exit");
            clipboardListener.CopyToClipboard(getin());
        }
        else
        {
            clipboardListener.CopyToClipboard(clipboardListenerUnix.getLastClipboardContent());
        }
        return EXIT_SUCCESS;
    }

    while (true)
    {
        // debug("POLLING");
        clipboardListener.PollClipboard();
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
#else
    if (config.arg_search)
        return search_algo(clipboardListenerUnix, config);
#endif

    return EXIT_SUCCESS;
}
