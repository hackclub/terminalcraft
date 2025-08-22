extension String {
	func styled(with textStyles: [TextStyles], styledIf: Bool = true) -> String {
		var newString = self
		for textStyle in textStyles {
			newString = "\(textStyle.rawValue)\(newString)"
		}
		return styledIf ? "\(newString)\(TextStyles.resetAll.rawValue)" : self
	}

	func styled(with textStyle: TextStyles, styledIf: Bool = true) -> String {
		styled(with: [textStyle], styledIf: styledIf)
	}

	/// Removes ANSI escape sequences (style codes) from the string.
	var withoutStyles: String {
		replacingOccurrences(of: "\u{1B}\\[[0-9;]*[a-zA-Z]", with: "", options: .regularExpression)
	}

	/// Splits the string into an array of lines fitting the specified width.
	func wrappedWithStyles(toWidth width: Int) -> [String] {
		var words = split(separator: " ", omittingEmptySubsequences: false)
		var lines: [String] = []
		var currentLine = ""
		var currentLineVisibleWidth = 0

		while !words.isEmpty {
			let word = words.first!
			let wordWithoutStyles = String(word).withoutStyles

			// Calculate the visible width of the word and check if it fits
			if currentLineVisibleWidth + wordWithoutStyles.count + (currentLine.isEmpty ? 0 : 1) <= width {
				// Add space if it's not the first word
				if !currentLine.isEmpty {
					currentLine.append(" ")
					currentLineVisibleWidth += 1
				}
				currentLine += word
				currentLineVisibleWidth += wordWithoutStyles.count
				words.removeFirst()
			} else {
				// If the word itself is too long, split it
				if wordWithoutStyles.count > width {
					let splitIndex = width - currentLineVisibleWidth
					let remainingPart = String(word.dropFirst(splitIndex))
					let styledVisiblePart = word.prefix(splitIndex) // Preserve styles for the visible part

					currentLine += styledVisiblePart
					lines.append(currentLine)

					// Add remaining part back to words
					words[0] = Substring(remainingPart)
					currentLine = ""
					currentLineVisibleWidth = 0
				} else {
					// Word doesn't fit, move to next line
					lines.append(currentLine)
					currentLine = ""
					currentLineVisibleWidth = 0
				}
			}
		}

		// Add the last line if it has content
		if !currentLine.isEmpty {
			lines.append(currentLine)
		}

		return lines
	}
}

enum TextStyles: String, CaseIterable {
	case bold = "\u{1B}[1m"
	case dim = "\u{1B}[2m"
	case italic = "\u{1B}[3m"
	case underline = "\u{1B}[4m"
	case blink = "\u{1B}[5m"
	case inverted = "\u{1B}[7m"
	case hidden = "\u{1B}[8m"
	case resetAll = "\u{1B}[0m"
	case black = "\u{1B}[30m"
	case red = "\u{1B}[31m"
	case green = "\u{1B}[32m"
	case yellow = "\u{1B}[33m"
	case blue = "\u{1B}[34m"
	case magenta = "\u{1B}[35m"
	case cyan = "\u{1B}[36m"
	case white = "\u{1B}[37m"
	case brightBlack = "\u{1B}[90m"
	case brightRed = "\u{1B}[91m"
	case brightGreen = "\u{1B}[92m"
	case brightYellow = "\u{1B}[93m"
	case brightBlue = "\u{1B}[94m"
	case brightMagenta = "\u{1B}[95m"
	case brightCyan = "\u{1B}[96m"
	case brightWhite = "\u{1B}[97m"

	// case darkGray = "\u{1B}[90m"
	// case lightGray = "\u{1B}[37m"
	case orange = "\u{1B}[38;5;214m"
	case purple = "\u{1B}[38;5;129m"
	case pink = "\u{1B}[38;5;213m"
	case brown = "\u{1B}[38;5;94m"
}
