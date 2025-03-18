#ifndef _UTIL_HPP_
#define _UTIL_HPP_

#include <iostream>
#include "fmt/base.h"
#include "fmt/color.h"

/* https://stackoverflow.com/questions/874134/find-out-if-string-ends-with-another-string-in-c#874160
 * Check if substring exists at the start
 * @param fullString The string to lookup
 * @param start The string to check at the start of fullString
 */
bool hasStart(const std::string_view fullString, const std::string_view start);

/* Write error message and exit if EOF (or CTRL-D most of the time)
 * @param cin The std::cin used for getting the input
 */ 
void ctrl_d_handler(const std::istream& cin);

/* Replace special symbols such as ~ and $ (at the begging) in std::string
 * @param str The string
 * @param dont Don't do it
 * @return The modified string
 */
std::string expandVar(std::string ret, bool dont = false);

/*
 * Get the user config directory
 * either from $XDG_CONFIG_HOME or from $HOME/.config/
 * @return user's config directory
 */
std::string getHomeConfigDir();

/*
 * Get the customfetch config directory
 * where we'll have "config.toml"
 * from getHomeConfigDir()
 * @return customfetch's config directory
 */
std::string getConfigDir();


#define BOLD_COLOR(x) (fmt::emphasis::bold | fmt::fg(x))

template <typename... Args>
void error(const std::string_view fmt, Args&&... args) noexcept
{
    fmt::print(stderr, BOLD_COLOR(fmt::rgb(fmt::color::red)), "ERROR\033[0m: {}\n",
               fmt::format(fmt::runtime(fmt), std::forward<Args>(args)...));
}

template <typename... Args>
void die(const std::string_view fmt, Args&&... args) noexcept
{
    fmt::print(stderr, BOLD_COLOR(fmt::rgb(fmt::color::red)), "FATAL\033[0m: {}\n",
               fmt::format(fmt::runtime(fmt), std::forward<Args>(args)...));
    std::exit(1);
}

template <typename... Args>
void debug(const std::string_view fmt, Args&&... args) noexcept
{
#if DEBUG
    fmt::print(BOLD_COLOR((fmt::rgb(fmt::color::hot_pink))), "[DEBUG]: {}\n",
               fmt::format(fmt::runtime(fmt), std::forward<Args>(args)...));
#endif
}

template <typename... Args>
void warn(const std::string_view fmt, Args&&... args) noexcept
{
    fmt::print(BOLD_COLOR((fmt::rgb(fmt::color::yellow))), "WARNING\033[0m: {}\n",
               fmt::format(fmt::runtime(fmt), std::forward<Args>(args)...));
}

template <typename... Args>
void info(const std::string_view fmt, Args&&... args) noexcept
{
    fmt::print(BOLD_COLOR((fmt::rgb(fmt::color::cyan))), "INFO\033[0m: {}\n",
               fmt::format(fmt::runtime(fmt), std::forward<Args>(args)...));
}

/** Ask the user a yes or no question.
 * @param def The default result
 * @param fmt The format string
 * @param args Arguments in the format
 * @returns the result, y = true, n = false, only returns def if the result is def
 */
template <typename... Args>
bool askUserYorN(bool def, const std::string_view fmt, Args&&... args)
{
    const std::string& inputs_str = fmt::format(" [{}]: ", def ? "Y/n" : "y/N");
    std::string result;
    fmt::print(fmt::runtime(fmt), std::forward<Args>(args)...);
    fmt::print("{}", inputs_str);

    while (std::getline(std::cin, result) && (result.length() > 1))
        fmt::print(BOLD_COLOR(fmt::rgb(fmt::color::yellow)), "Please answear y or n,{}", inputs_str);

    ctrl_d_handler(std::cin);

    if (result.empty())
        return def;

    if (def ? std::tolower(result[0]) != 'n' : std::tolower(result[0]) != 'y')
        return def;

    return !def;
}


#endif  // !_UTIL_HPP_
