#include "util.hpp"

#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <vector>
#include <string>
#include "fmt/ranges.h"

bool hasStart(const std::string_view fullString, const std::string_view start)
{
    if (start.length() > fullString.length())
        return false;
    return (fullString.substr(0, start.size()) == start);
}

void ctrl_d_handler(const std::istream& cin)
{
    if (cin.eof())
        die("Exiting due to CTRL-D or EOF");
}

std::string expandVar(std::string ret, bool dont)
{
    if (ret.empty() || dont)
        return ret;

    const char* env;
    if (ret.front() == '~')
    {
        env = std::getenv("HOME");
        if (env == nullptr)
            die("FATAL: $HOME enviroment variable is not set (how?)");

        ret.replace(0, 1, env);  // replace ~ with the $HOME value
    }
    else if (ret.front() == '$')
    {
        ret.erase(0, 1);

        std::string   temp;
        const size_t& pos = ret.find('/');
        if (pos != std::string::npos)
        {
            temp = ret.substr(pos);
            ret.erase(pos);
        }

        env = std::getenv(ret.c_str());
        if (env == nullptr)
            die("No such enviroment variable: {}", ret);

        ret = env;
        ret += temp;
    }

    return ret;
}

std::string getin()
{
    std::vector<std::string> lines;
    std::string              line;

    while (std::getline(std::cin, line))
    {
        if (std::cin.eof())
            break;

        lines.push_back(line);
    }

    return fmt::format("{}", fmt::join(lines, "\n"));
}

std::string getHomeConfigDir()
{
    const char* dir = std::getenv("XDG_CONFIG_HOME");
    if (dir != NULL && dir[0] != '\0' && std::filesystem::exists(dir))
    {
        std::string str_dir(dir);
        if (str_dir.back() == '/')
            str_dir.pop_back();
        return str_dir;
    }
    else
    {
        const char* home = std::getenv("HOME");
        if (home == nullptr)
            die("Failed to find $HOME, set it to your home directory!");

        return std::string(home) + "/.config";
    }
}

std::string getConfigDir()
{ return getHomeConfigDir() + "/clippyman"; }
