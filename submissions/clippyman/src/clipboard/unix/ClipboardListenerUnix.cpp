#include "clipboard/unix/ClipboardListenerUnix.hpp"

/*
 * Registers a callback for when the user copies something.
 */
void CClipboardListenerUnix::AddCopyCallback(const std::function<void(const CopyEvent&)>& func)
{
    m_CopyEventCallbacks.push_back(func);
}

void CClipboardListenerUnix::PollClipboard()
{
    CopyEvent copyEvent{ getin() };
    if (copyEvent.content == m_LastClipboardContent)
        return;

    if (copyEvent.content.find_first_not_of(' ') == std::string::npos)
        return;

    m_LastClipboardContent = copyEvent.content;
    for (const auto& callback : m_CopyEventCallbacks)
        callback(copyEvent);
}
