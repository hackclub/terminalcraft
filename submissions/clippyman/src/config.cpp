#include "config.hpp"

#include <cstdlib>
#include <filesystem>
#include <string_view>

#include "fmt/os.h"
#include "util.hpp"

void Config::Init(const std::string_view configFile, const std::string_view configDir)
{
    if (!std::filesystem::exists(configDir))
    {
        warn("clippyman config folder was not found, Creating folders at {}!", configDir);
        std::filesystem::create_directories(configDir);
    }

    if (!std::filesystem::exists(configFile))
    {
        warn("config file {} not found, generating new one", configFile);
        this->generateConfig(configFile);
    }
}

void Config::loadConfigFile(const std::string_view filename)
{
    try
    {
        this->tbl = toml::parse_file(filename);
    }
    catch (const toml::parse_error& err)
    {
        die("Parsing config file '{}' failed:\n"
              "{}\n"
              "\t(error occurred at line {} column {})",
            filename, err.description(),
            err.source().begin.line, err.source().begin.column);
    }

    this->path         = getValue<std::string>("config.path", "~/.cache/clippyman/history.json");
    this->wl_seat      = getValue<std::string>("config.wl-seat", "");
    this->primary_clip = getValue<bool>("config.primary", false);
}

void Config::generateConfig(const std::string_view filename)
{
    if (std::filesystem::exists(filename))
    {
        if (!askUserYorN(false, "WARNING: config file '{}' already exists. Do you want to overwrite it?", filename))
            std::exit(1);
    }

    auto f = fmt::output_file(filename.data());
    f.print("{}", AUTOCONFIG);
}
