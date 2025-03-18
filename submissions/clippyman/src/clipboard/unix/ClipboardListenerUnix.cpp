#include "clipboard/unix/ClipboardListenerUnix.hpp"

#include <unistd.h>

#include <cctype>
#include <climits>
#include <iostream>
#include <string>
#include <vector>

#include "fmt/ranges.h"

std::string in()
{
    std::vector<std::string> lines;
    std::string line;

    while (std::getline(std::cin, line))
    {
        if (std::cin.eof())
            break;

        lines.push_back(line);
    }

    return fmt::format("{}", fmt::join(lines, "\n"));
}

/*
 * Registers a callback for when the user copies something.
 */
void CClipboardListenerUnix::AddCopyCallback(const std::function<void(const CopyEvent&)>& func)
{
    m_CopyEventCallbacks.push_back(func);
}

void CClipboardListenerUnix::PollClipboard()
{
    CopyEvent copyEvent{in()};
    if (copyEvent.content == m_LastClipboardContent)
        return;

    if (copyEvent.content.find_first_not_of(' ') == std::string::npos)
        return;

    m_LastClipboardContent = copyEvent.content;
    for (const auto& callback : m_CopyEventCallbacks)
        callback(copyEvent);
}
