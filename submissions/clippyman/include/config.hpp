#ifndef _CONFIG_HPP_
#define _CONFIG_HPP_

#include <string>
#include <string_view>
#include "toml++/toml.hpp"
#include "util.hpp"

class Config
{
public:
    // Create .config directories and files and load the config file (args or default)
    Config(const std::string_view configFile, const std::string_view configDir);

    bool search = false;
    bool terminal_input = false;
    std::string path;

    /**
     * Load config file and parse every config variables
     * @param filename The config file path
     * @param colors The colors struct where we'll put the default config colors.
     *               It doesn't include the colors in config.alias-colors
     */
    void loadConfigFile(const std::string_view filename);

    /**
     * Generate a config file
     * @param filename The config file path
     */
    void generateConfig(const std::string_view filename);

private:
    toml::table tbl;

    /**
     * Get value of config variables
     * @param value The config variable "path" (e.g "config.source-path")
     * @param fallback Default value if couldn't retrive value
     */
    template <typename T>
    T getValue(const std::string_view value, const T&& fallback, bool dont_expand_var = false) const
    {        
        const std::optional<T>& ret = this->tbl.at_path(value).value<T>();
        if constexpr (toml::is_string<T>)  // if we want to get a value that's a string
            return ret ? expandVar(ret.value(), dont_expand_var) : expandVar(fallback, dont_expand_var);
        else
            return ret.value_or(fallback);
    }
};

inline constexpr std::string_view AUTOCONFIG = R"([config]
terminal-input = false

path = "~/.cache/clippyman/history.json"
)";

#endif // _CONFIG_HPP_
