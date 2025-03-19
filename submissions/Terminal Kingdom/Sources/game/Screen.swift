import Foundation
#if os(macOS)
	import Darwin
#elseif os(Linux)
	import Glibc
#elseif os(Windows)
	import WinSDK
#endif

enum Placement {
	case middle
	case int(Int)
	case end
	case start
}

enum Screen {
	private(set) nonisolated(unsafe) static var columns: Int = 0
	private(set) nonisolated(unsafe) static var rows: Int = 0

	static func initialize() {
		if let terminalSize = getTerminalSize() {
			columns = terminalSize.columns
			rows = terminalSize.rows
		} else {
			Swift.print("Error: Could not determine terminal size.")
			exit(123)
		}
	}

	static func initializeBoxes() async {
		await MessageBox.messageBox()
		await MapBox.mapBox()
		await InventoryBox.inventoryBox()
		await StatusBox.statusBox()
	}

	private struct TerminalSize {
		let rows: Int
		let columns: Int
	}

	enum Cursor {
		public static func move(to x: Int, _ y: Int) {
			Swift.print("\u{1B}[\(y);\(x)H", terminator: "")
		}

		public static func moveToTop() {
			Swift.print("\u{1B}[H", terminator: "")
		}
	}

	private static func getTerminalSize() -> TerminalSize? {
		#if os(Linux)
			var windowSize = winsize()
			if ioctl(STDOUT_FILENO, UInt(TIOCGWINSZ), &windowSize) == 0 {
				let rows = Int(windowSize.ws_row)
				let columns = Int(windowSize.ws_col)
				return TerminalSize(rows: rows, columns: columns)
			}
		#elseif os(Windows)
			var consoleInfo = CONSOLE_SCREEN_BUFFER_INFO()
			let handle = GetStdHandle(STD_OUTPUT_HANDLE)
			GetConsoleScreenBufferInfo(handle, &consoleInfo)
			let rows = Int(consoleInfo.srWindow.Bottom - consoleInfo.srWindow.Top + 1)
			let columns = Int(consoleInfo.srWindow.Right - consoleInfo.srWindow.Left + 1)
			return TerminalSize(rows: rows, columns: columns)
		#else
			var windowSize = winsize()
			if ioctl(STDOUT_FILENO, TIOCGWINSZ, &windowSize) == 0 {
				let rows = Int(windowSize.ws_row)
				let columns = Int(windowSize.ws_col)
				return TerminalSize(rows: rows, columns: columns)
			}
		#endif
		return nil
	}

	static func clear() {
		Swift.print("\u{1B}[2J", terminator: "")
	}

	static func print(x: Int, y: Int, _ text: String) {
		// let x = max(1, min(x, columns))
		// let y = max(1, min(y, rows))
		Screen.print(x: .int(x), y: .int(y), text)
	}

	static func print(x: Placement, y: Placement, _ text: String) {
		let placementX = switch x {
			case .middle: (columns / 2) - (text.count / 2)
			case let .int(x): max(1, min(x, columns))
			case .end: columns - text.count
			case .start: 0
		}

		let placementY = switch y {
			case .middle: rows / 2
			case let .int(y): max(1, min(y, rows))
			case .end: rows
			case .start: 0
		}

		// Move the cursor and print text
		Cursor.move(to: placementX, placementY)
		Swift.print(text)
	}
}

extension MapBox {
	static var startX: Int { StatusBox.endX + 1 }
	static var endX: Int { Screen.columns }
	static var width: Int {
		endX - startX
	}

	static var startY: Int { 2 }
	static var endY: Int { (Screen.rows / 2) + (Screen.rows / 4) }
	static var height: Int {
		endY - startY
	}
}

extension MessageBox {
	static var startX: Int { StatusBox.endX }
	static var endX: Int { Screen.columns }
	static var width: Int {
		endX - startX
	}

	static var startY: Int { MapBox.endY }
	static var endY: Int { Screen.rows - 1 }
	static var height: Int {
		endY - startY
	}
}

extension StatusBox {
	static var startX: Int { 0 }
	static var endX: Int { Screen.columns / 4 }
	static var width: Int {
		endX - startX
	}

	static var startY: Int { 1 }
	static var endY: Int { Screen.rows / 2 }
	static var height: Int {
		endY - startY
	}
}

extension InventoryBox {
	static var startX: Int { StatusBox.startX }
	static var endX: Int { StatusBox.endX }
	static var width: Int {
		endX - startX
	}

	static var startY: Int { StatusBox.endY + 1 }
	static var endY: Int { Screen.rows - 1 }
	static var height: Int {
		endY - startY
	}
}
