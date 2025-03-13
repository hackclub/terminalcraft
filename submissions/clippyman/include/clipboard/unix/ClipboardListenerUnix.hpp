#ifndef CLIPBOARD_LISTENER_UNIX_HPP_
#define CLIPBOARD_LISTENER_UNIX_HPP_

#include <string>
#include <vector>

#include "clipboard/ClipboardListener.hpp"

class CClipboardListenerUnix : public CClipboardListener
{
public:
    CClipboardListenerUnix() = default;
    ~CClipboardListenerUnix() = default;

    /*
     * Registers a callback for when the user copies something.
     */
    void AddCopyCallback(const std::function<void(const CopyEvent&)>& func) override;

    void PollClipboard() override;

private:
    std::vector<std::function<void(const CopyEvent&)>> m_CopyEventCallbacks;

    std::string m_LastClipboardContent;
};

#endif  // !CLIPBOARD_LISTENER_UNIX_HPP_
