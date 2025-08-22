import Foundation
#if os(macOS)
	import Darwin
#elseif os(Linux)
	import Glibc
#endif
enum UnixTerminalInput {
	#if os(macOS) || os(Linux)
		static func readKey() -> KeyboardKeys {
			var buffer = [UInt8](repeating: 0, count: 3)
			read(STDIN_FILENO, &buffer, 3)

			if buffer[0] == 27 { // Escape character
				if buffer[1] == 91 { // CSI (Control Sequence Introducer)
					switch buffer[2] {
						case 65: return .up
						case 66: return .down
						case 67: return .right
						case 68: return .left
						case 90: return .back_tab // Shift + Tab
						default: return .unknown
					}
				}
				return .esc
			} else if buffer[0] == 9 {
				return .tab
			} else if buffer[0] == 13 || buffer[0] == 10 {
				return .enter
			} else if buffer[0] == 32 {
				return .space
			} else if buffer[0] == 8 || buffer[0] == 127 {
				return .backspace
			} else if buffer[0] >= 48, buffer[0] <= 57 { // Numeric characters
				return KeyboardKeys(rawValue: String(UnicodeScalar(buffer[0]))) ?? .unknown
			} else if buffer[0] >= 32, buffer[0] <= 126 { // Printable characters
				return KeyboardKeys(rawValue: String(UnicodeScalar(buffer[0]))) ?? .unknown
			}

			return .unknown
		}
	#endif
}
