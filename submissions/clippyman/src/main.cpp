#ifndef PLATFORM_UNIX
#define PLATFORM_UNIX 0
#endif

#include <getopt.h>
#include <ncurses.h>
#include <unistd.h>

#include <algorithm>
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

Config config;
// src/box.cpp
void draw_search_box(const std::string& query, const std::vector<std::string>& entries_id,
                     const std::vector<std::string>& results, const size_t max_width, const size_t max_visible,
                     const size_t selected, const size_t scroll_offset, const size_t cursor_x, bool is_search_tab);
void delete_draw_confirm(int seloption, const char* id);


static void version()
{
    fmt::print("clippyman " VERSION " branch " BRANCH "\n");
    std::exit(EXIT_SUCCESS);
}

static void help(bool invalid_opt = false)
{
    constexpr std::string_view help =
R"(Usage: clippyman [OPTIONS]...
    -i, --input                 Enter in terminal input mode
    -p, --path <path>           Path to where we'll search/save the clipboard history
    -s, --search		Delete/Search history (d for delete, enter for output selected text)
    -P, --primary [<bool>]      Use the primary clipboard instead
    --wl-seat <name>            The seat for using in wayland (just leave it empty if you don't know what's this)

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
    rapidjson::Value                  value_content(event.content.c_str(), allocator);
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

int search_algo(const Config& config)
{
restart:
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

    initscr();
    noecho();
    cbreak();              // Enable immediate character input
    keypad(stdscr, TRUE);  // Enable arrow keys

    std::vector<std::string> entries_id, entries_value, results, results_id;
    for (auto it = doc["entries"].MemberBegin(); it != doc["entries"].MemberEnd(); ++it)
    {
        entries_id.push_back(it->name.GetString());
        entries_value.push_back(it->value.GetString());
        results_id.push_back(it->name.GetString());
        results.push_back(it->value.GetString());
    }

    std::string query;
    int         ch            = 0;
    size_t      selected      = 0;
    size_t      scroll_offset = 0;
    size_t      cursor_x      = 2 + 8;  // 2 for box border, 8 for "Search: "
    bool        is_search_tab = true;

    const int max_width   = getmaxx(stdscr) - 5;
    const int max_visible = ((getmaxy(stdscr) - 3) / 2) * 0.75;
    draw_search_box(query, results_id, results, max_width, max_visible, selected, scroll_offset, cursor_x, is_search_tab);
    move(1, cursor_x);

    size_t i            = 0;
    bool   del          = false;
    bool   del_selected = false;
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
            curs_set(1);
            del = false;
            bool erased = false;
            if (ch == KEY_BACKSPACE || ch == 127)
            {
                if (!query.empty())
                {
                    // decrease then pass
                    if (cursor_x > 2 + 8)
                        query.erase(--cursor_x - 2 - 8, 1);
                    i = 0;

                    if (!query.empty()) {
                        ch = query.back();
                        erased = true;
                    }
                }
            }
            else if (ch == KEY_LEFT)
            {
                if (cursor_x > 2 + 8)
                    --cursor_x;
            }
            else if (ch == KEY_RIGHT)
            {
                if (cursor_x < 2 + 8 + query.size())
                    ++cursor_x;
            }
            
            if (isprint(ch))
            {
                if (i == 0)
                {
                    results.clear();
                    results_id.clear();
                }
                if (!erased)
                    // pass then increase
                    query.insert(cursor_x++ - 2 - 8, 1, ch);

                selected      = 0;
                scroll_offset = 0;

                if (i > 0)
                {
                    results.erase(std::remove_if(results.begin(), results.end(),[&](const std::string& s){return s[i] != ch;}),
                                  results.end());
                }
                else
                {
                    rapidjson::GenericStringRef<char> ch_ref(&query.back());

                    // {"index":{"c":{"0": [1,3,7]}}}
                    if (doc["index"].HasMember(ch_ref))
                    {
                        // {"0": [1,3,7]}
                        for (auto it_id = doc["index"][ch_ref.s].MemberBegin();
                             it_id != doc["index"][ch_ref.s].MemberEnd(); ++it_id)
                        {
                            if (!it_id->value.IsArray())
                                continue;
                            // [1,3,7]
                            for (auto it_arr = it_id->value.GetArray().Begin(); it_arr != it_id->value.GetArray().End();
                                 ++it_arr)
                            {
                                unsigned int n_i = it_arr->GetUint();
                                if (n_i <= i && n_i == i)
                                {
                                    results_id.push_back(it_id->name.GetString());
                                    results.push_back(doc["entries"][it_id->name.GetString()].GetString());
                                    break;
                                }
                            }
                        }
                    }
                }
                ++i;

                if (selected >= results.size())
                    selected = results.empty() ? -1 : 0;  // Keep selection valid
            }
        }
        else
        {
            curs_set(0);
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
            else if (ch == KEY_UP || ch == KEY_LEFT)
            {
                if (del)
                    del_selected = true;

                else if (selected > 0)
                {
                    --selected;
                    if (selected < scroll_offset)
                        --scroll_offset;
                }
            }
            else if (ch == 'd' && !del)
            {
                del = true;
            }
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
                fileWriter.SetFormatOptions(rapidjson::kFormatSingleLineArray);  // Disable newlines between array elements
                doc.Accept(fileWriter);
                fflush(file);
                ftruncate(fileno(file), ftell(file));
                goto restart;  // yes... let's just restart everything for now
            }
            else if (del && (!del_selected || ch == 'q'))
            {
                del = false;
            }
            else if (ch == '\n' && selected < std::string::npos - 1 && !results.empty())
            {
                endwin();
                info("Copied selected content:\n{}", results[selected]);
                return 0;
            }
        }

        if (del)
            delete_draw_confirm(del_selected, results_id[selected].c_str());
        else
            draw_search_box(query, ((results_id.empty() || query.empty()) ? entries_id : results_id),
                            ((results.empty() || query.empty()) ? entries_value : results), max_width, max_visible,
                            selected, scroll_offset, cursor_x, is_search_tab);
    }

    endwin();
    return 0;
}

static bool str_to_bool(const std::string_view str)
{
    return (str == "true" || str == "1" || str == "enable");
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

bool parseargs(int argc, char* argv[], Config& config, const std::string& configFile)
{
    int opt               = 0;
    int option_index      = 0;
    opterr                = 1;  // re-enable since before we disabled for "invalid option" error
    const char* optstring = "-Vhisp:C:P::";

    // clang-format off
    static const struct option opts[] = {
        {"version",    no_argument,       0, 'V'},
        {"help",       no_argument,       0, 'h'},
        {"input",      no_argument,       0, 'i'},
        {"search",     no_argument,       0, 's'},

        {"path",       required_argument, 0, 'p'},
        {"config",     required_argument, 0, 'C'},
        {"primary",    optional_argument, 0, 'P'},
        {"wl-seat",    required_argument, 0, 6968},
        {"gen-config", optional_argument, 0, 6969},

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
            case 6968: config.wl_seat = optarg;
            case 'C':  break;  // we have already did it in parse_config_path()

            case 'P':
                if (OPTIONAL_ARGUMENT_IS_PRESENT)
                    config.primary_clip = str_to_bool(optarg);
                else
                    config.primary_clip = true;
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
#if PLATFORM_XORG
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

    const std::string& configDir  = getConfigDir();
    const std::string& configFile = parse_config_path(argc, argv, configDir);

    config.Init(configFile, configDir);
    config.loadConfigFile(configFile);
    if (!parseargs(argc, argv, config, configFile))
        return 1;

    CreateInitialCache(config.path);
    setlocale(LC_ALL, "");

    if (config.arg_search && config.arg_terminal_input)
        die("Please only use either --search or --input");

    if (config.arg_search)
        return search_algo(config);

    bool piped = !isatty(STDIN_FILENO);
    // debug("piped = {}", piped);
    if (piped || PLATFORM_UNIX || config.arg_terminal_input)
    {
        CClipboardListenerUnix clipboardListenerUnix;
        clipboardListenerUnix.AddCopyCallback(CopyEntry);

        if (!piped)
            info("Type or Paste the text to copy, then press enter and CTRL+D to save and exit");

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
