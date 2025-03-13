#include <getopt.h>
#include <ncurses.h>
#include <wchar.h>
#include <unistd.h>

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#if !PLATFORM_UNIX
#include <chrono>
#include <thread>
#endif

#include "EventData.hpp"
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

#if PLATFORM_XORG
#include "clipboard/x11/ClipboardListenerX11.hpp"
#elif PLATFORM_WAYLAND
#include "clipboard/wayland/ClipboardListenerWayland.hpp"
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


std::string g_path;

void CopyCallback(const CopyEvent& event)
{
    info("Copied: {}", event.content);
}

void CopyEntry(const CopyEvent& event)
{
    FILE*                     file = fopen(g_path.c_str(), "r+");
    rapidjson::Document       doc;
    char                      buf[UINT16_MAX] = { 0 };
    rapidjson::FileReadStream stream(file, buf, sizeof(buf));

    if (doc.ParseStream(stream).HasParseError())
    {
        fclose(file);
        die("Failed to parse {}: {} at offset {}", g_path, rapidjson::GetParseError_En(doc.GetParseError()),
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
    rapidjson::Value                  value_content(event.content.c_str(), allocator);
    doc["entries"].AddMember(id_ref, value_content, allocator);

    size_t i = 0;
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

    std::filesystem::create_directories(path.substr(0, path.rfind('/')));
    auto f = fmt::output_file(path, fmt::file::CREATE | fmt::file::RDWR | fmt::file::TRUNC);
    f.print("{}", json);
    f.close();
}

std::vector<std::string> wrap_text(const std::string& text, size_t max_width)
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

void draw_search_box(const std::string& query, const std::vector<std::string>& results, const size_t max_width,
                     const size_t max_visible, const size_t selected, const size_t scroll_offset)
{
    clear();
    box(stdscr, 0, 0); // Draw the root box

    attron(A_BOLD);
    mvprintw(1, 2, "Search: %s", query.c_str());
    attroff(A_BOLD);

    int row = 2; // Start drawing items from row 2
    size_t items_displayed = 0; // Track the number of items displayed

    for (size_t i = scroll_offset; i < results.size() && items_displayed < max_visible; ++i)
    {
        const std::vector<std::string>& wrapped_lines = wrap_text(results[i], max_width - 6); // Adjust width for padding
        const bool is_selected = (i == selected);

        // Add vertical spacing between items
        row++;

        for (const std::string& line : wrapped_lines)
        {
            if (is_selected)
                attron(A_REVERSE); // Apply highlight before printing

            // Print the line with padding (4 spaces)
            mvprintw(row++, 6, "%s", line.c_str()); // 6 for padding (2 + 4 spaces)

            if (is_selected)
                attroff(A_REVERSE); // Remove highlight after printing
        }

        items_displayed++;
    }

    const int cursor_x = 2 + 8 + query.length(); // 2 for box border, 8 for "Search: ", query.length() for the query
    move(1, cursor_x); // Move the cursor near the search query
    refresh();
}

int search_algo(const Config& config)
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

    initscr();             // Initialize ncurses
    noecho();              // Disable echoing
    cbreak();              // Enable immediate character input
    keypad(stdscr, TRUE);  // Enable arrow keys

    std::vector<std::string> entries_value;
    for (auto it = doc["entries"].MemberBegin(); it != doc["entries"].MemberEnd(); ++it)
        entries_value.push_back(it->value.GetString());

    std::string              query;
    int                      ch            = 0;
    size_t                   selected      = 0;
    size_t                   scroll_offset = 0;
    std::vector<std::string> results{ entries_value };  // Start with full list

    bool copied = false;
    const int max_width   =  getmaxx(stdscr) - 5;
    const int max_visible = ((getmaxy(stdscr) - 3) / 2) * 0.75;
    draw_search_box(query, results, max_width, max_visible, selected, scroll_offset);

    // Press 'ESC' to exit
    size_t i = 0;
    while ((ch = getch()) != 27)
    {
        MEVENT event;
        if (ch == KEY_MOUSE && getmouse(&event) == OK)
        {
            const int row = event.y - 3;
            if (row >= 0 && row < max_visible && (scroll_offset + row) < results.size())
                selected = scroll_offset + row;
        }
        else if (ch == KEY_BACKSPACE || ch == 127)
        {
            if (!query.empty()) 
            {query.pop_back(); i = 0;}
        }
        else if (ch == KEY_DOWN)
        {
            if (selected < results.size() - 1)
            {
                ++selected;
                if (selected >= scroll_offset + max_visible)
                    ++scroll_offset;
            }
        }
        else if (ch == KEY_UP)
        {
            if (selected > 0)
            {
                --selected;
                if (selected < scroll_offset)
                    --scroll_offset;
            }
        }
        else if (ch == '\n' && selected < std::string::npos-1 && !results.empty())
        {
            copied = true;
            goto endwin;
        }
        else if (isprint(ch))
        {
            query += ch;
            selected      = 0;
            scroll_offset = 0;

            results.clear();
            rapidjson::GenericStringRef<char> ch_ref(&query.back());
            // {"index":{"c":{"0": [1,3,7]}}
            if (doc["index"].HasMember(ch_ref))
            {
                // {"0": [1,3,7]}
                for (auto it = doc["index"][ch_ref.s].MemberBegin(); it != doc["index"][ch_ref.s].MemberEnd(); ++it)
                {
                    if (!it->value.IsArray())
                        continue;
                    // [1,3,7]
                    for (auto it2 = it->value.GetArray().Begin(); it2 != it->value.GetArray().End(); ++it2)
                    {
                        unsigned int n_i = it2->GetUint();
                        if (n_i <= i && n_i == i)
                        {
                            results.push_back(doc["entries"][it->name.GetString()].GetString());
                            break;
                        }
                    }
                }
            }
            ++i;

            if (selected >= results.size())
                selected = results.empty() ? -1 : 0;  // Keep selection valid
        }

        draw_search_box(query, ((results.empty() || query.empty()) ? entries_value : results), max_width, max_visible, selected, scroll_offset);
    }

endwin:
    endwin();
    if (copied)
        info("Copied selected content:\n{}", results[selected]);
    return 0;
}

// clang-format off
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

bool parseargs(int argc, char* argv[], Config& config, const std::string_view configFile)
{
    int opt               = 0;
    int option_index      = 0;
    opterr                = 1;  // re-enable since before we disabled for "invalid option" error
    const char* optstring = "-Vhisp:C:";

    // clang-format off
    static const struct option opts[] = {
        {"path",  required_argument, 0, 'p'},
        {"input", no_argument,       0, 'i'},
        {"search",no_argument,       0, 's'},
        {"config",required_argument, 0, 'C'},
        {"gen-config",no_argument,   0, 6969},
        {0,0,0,0}
    };

    // clang-format on
    optind = 0;
    while ((opt = getopt_long(argc, argv, optstring, opts, &option_index)) != -1)
    {
        switch (opt)
        {
            case 0: break;

            case 'i': config.terminal_input = true; break;
            case 'p': config.path = optarg; break;
            case 's': config.search = true; break;
            case 'C': // we have already did it in parse_config_path()
                break;

            case 6969:
                if (OPTIONAL_ARGUMENT_IS_PRESENT)
                    config.generateConfig(optarg);
                else
                    config.generateConfig(configFile);
                exit(EXIT_SUCCESS);

            default: return false;
        }
    }

    return true;
}

int main(int argc, char* argv[])
{
#if PLATFORM_XORG
    CClipboardListenerX11 clipboardListener;
    clipboardListener.AddCopyCallback(CopyCallback);
    clipboardListener.AddCopyCallback(CopyEntry);
#elif PLATFORM_WAYLAND
    CClipboardListenerWayland clipboardListener;
    clipboardListener.AddCopyCallback(CopyCallback);
    clipboardListener.AddCopyCallback(CopyEntry);
#endif

    const std::string& configDir  = getConfigDir();
    const std::string& configFile = parse_config_path(argc, argv, configDir);

    Config config(configFile, configDir);
    if (!parseargs(argc, argv, config, configFile))
        return 1;

    config.loadConfigFile(configFile);
    g_path = config.path;

    CreateInitialCache(config.path);
    setlocale(LC_ALL, "");

    if (config.search)
        return search_algo(config);

    bool piped = !isatty(STDIN_FILENO);
    debug("piped = {}", piped);
    if (piped || config.terminal_input || PLATFORM_UNIX)
    {
        CClipboardListenerUnix clipboardListenerUnix;
        clipboardListenerUnix.AddCopyCallback(CopyEntry);

        if (!piped)
            info("Type or Paste the text to copy, then press CTRL+D to save and exit");

        clipboardListenerUnix.PollClipboard();
        return EXIT_SUCCESS;
    }

#if !PLATFORM_UNIX
    while (true)
    {
        // debug("POLLING");
        clipboardListener.PollClipboard();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
#endif

    return EXIT_SUCCESS;
}
