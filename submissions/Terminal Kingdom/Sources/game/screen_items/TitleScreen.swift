struct TitleScreen {
	private nonisolated(unsafe) var startX: Int { 0 }
	private nonisolated(unsafe) var middleX: Int { Screen.columns / 2 }
	private nonisolated(unsafe) var endX: Int { Screen.columns }

	private nonisolated(unsafe) var startY: Int { 0 }
	private nonisolated(unsafe) var middleY: Int { Screen.rows / 2 }
	private nonisolated(unsafe) var endY: Int { Screen.rows }

	private nonisolated(unsafe) var selectedOptionIndex = 0
	private nonisolated(unsafe) var selectedSettingOptionIndex = 0
	private nonisolated(unsafe) var config = Config()

	mutating func show() async -> TitleScreenOptions {
		// Quickly start a new game in debug mode
		#if DEBUG
			return TitleScreenOptions.newGameOption
		#else
			selectedOptionIndex = 0
			while true {
				Screen.clear()
				let text = "Welcome to Terminal Kingdom!"
				let x = middleX - (text.count / 2)
				let y = middleY - (Screen.rows / 2)
				Screen.print(x: x, y: y, text.styled(with: .bold))
				let optionsX = middleX - (text.count / 4)
				let icon = await " \(Game.shared.config.icons.selectedIcon)"

				for (index, option) in TitleScreenOptions.allCases.enumerated() {
					let isSelected = selectedOptionIndex == index
					Screen.print(x: optionsX, y: y + 3 + index, "\(isSelected ? icon : "  ")\(option.label)".styled(with: .bold, styledIf: isSelected))
				}

				let key = TerminalInput.readKey()
				switch key {
					case .enter:
						return TitleScreenOptions.allCases[selectedOptionIndex]
					case .up, .w, .k, .back_tab:
						selectedOptionIndex = max(0, selectedOptionIndex - 1)
					case .down, .s, .j, .tab:
						selectedOptionIndex = min(TitleScreenOptions.allCases.count - 1, selectedOptionIndex + 1)
					case .zero:
						Screen.clear()
						Screen.initialize()
					case .q:
						endProgram()
					default:
						break
				}
			}
		#endif
	}

	enum TitleScreenOptions: CaseIterable {
		case newGameOption
		case loadGameOption
		case helpOption
		case settingsOption
		case quitOption

		var label: String {
			switch self {
				case .newGameOption:
					"New Game"
				case .loadGameOption:
					"Load Game"
				case .helpOption:
					"Help"
				case .settingsOption:
					"Settings"
				case .quitOption:
					"Quit"
			}
		}

		func action(screen: inout TitleScreen) async {
			switch self {
				case .newGameOption:
					await newGame()
				case .loadGameOption:
					if await loadGame() {
						// Load game
						await MessageBox.message("Games can not be loaded at this time. Creating new game.", speaker: .game)
						await newGame()
					} else {
						await MessageBox.message("No saved game found. Creating new game.", speaker: .game)
						await newGame()
					}
				case .helpOption:
					screen.help()
				case .settingsOption:
					await screen.settings()
				case .quitOption:
					endProgram()
			}
		}
	}

	enum SettingsScreenOptions: CaseIterable {
		case useNerdFontOption
		case wasdKeysOption
		case arrowKeysOption
		case vimKeysOption

		var label: String {
			switch self {
				case .useNerdFontOption:
					"Use Nerd Font"
				case .vimKeysOption:
					"Use Vim Keys for moving"
				case .arrowKeysOption:
					"Use Arrow Keys for moving"
				case .wasdKeysOption:
					"Use WASD Keys for moving"
			}
		}

		func action(config: inout Config) {
			switch self {
				case .useNerdFontOption:
					config.useNerdFont.toggle()
				case .vimKeysOption:
					config.vimKeys.toggle()
				case .arrowKeysOption:
					config.arrowKeys.toggle()
				case .wasdKeysOption:
					config.wasdKeys.toggle()
			}
		}

		func configOption(_ config: Config) -> String {
			switch self {
				case .useNerdFontOption:
					config.useNerdFont ? "On" : "Off"
				case .vimKeysOption:
					config.vimKeys ? "On" : "Off"
				case .arrowKeysOption:
					config.arrowKeys ? "On" : "Off"
				case .wasdKeysOption:
					config.wasdKeys ? "On" : "Off"
			}
		}
	}

	func help() {
		let text = "Help"
		let x = middleX
		let y = middleY - (Screen.rows / 2)
		Screen.print(x: x - (text.count / 2), y: y, text.styled(with: .bold))
		var yStart = 3
		// TODO: change depending on user's config
		yStart = printHelpMessage(x: x, y: y + yStart, "Press \("wasd".styled(with: .bold)) or the \("arrow keys".styled(with: .bold)) to move.")
		yStart = printHelpMessage(x: x, y: y + yStart, "Press \(KeyboardKeys.space.render) or \(KeyboardKeys.enter.render) to interact with the tile you are on.")
		yStart = printHelpMessage(x: x, y: y + yStart, "Press \(KeyboardKeys.i.render) to open the inventory.")
		yStart = printHelpMessage(x: x, y: y + yStart, "Press \(KeyboardKeys.b.render) to start building.")
		yStart = printHelpMessage(x: x, y: y + yStart, "Press \(KeyboardKeys.zero.render) to resize the screen.")
		yStart = printHelpMessage(x: x, y: y + yStart, "Press \(KeyboardKeys.W.render) and \(KeyboardKeys.S.render) to scroll up and down in the message box.")
		yStart = printHelpMessage(x: x, y: y + yStart, "Press \(KeyboardKeys.Q.render) to quit.")

		yStart = printHelpMessage(x: x, y: y + yStart, "Press any key to leave.")
		Screen.print(x: Screen.columns - 1 - Game.version.count, y: Screen.rows - 1, Game.version)
	}

	mutating func settings() async {
		// TODO: reload config after saving so this isn't async
		config = await Config.load()
		let text = "Settings"
		let x = middleX
		let y = middleY - (Screen.rows / 2)
		while true {
			Screen.clear()
			Screen.print(x: x - (text.count / 2), y: y, text.styled(with: .bold))
			var lastIndex = SettingsScreenOptions.allCases.count - 1
			var yStart = 3
			for (index, option) in SettingsScreenOptions.allCases.enumerated() {
				yStart = await printSettingsOption(x: x, y: y + yStart, index: index, text: option.label, configOption: option.configOption(config))
				lastIndex = index
			}

			let skip = lastIndex + 1
			yStart = await printSettingsOption(x: x, y: yStart + 1, index: lastIndex + 2, text: "Save and Quit", configOption: "")
			yStart = await printSettingsOption(x: x, y: yStart, index: lastIndex + 3, text: "Quit", configOption: "")
			let key = TerminalInput.readKey()
			switch key {
				case .up, .w, .k, .back_tab:
					selectedSettingOptionIndex = max(0, selectedSettingOptionIndex - 1)
					if selectedSettingOptionIndex == skip {
						selectedSettingOptionIndex = selectedSettingOptionIndex - 1
					}
				case .down, .s, .j, .tab:
					selectedSettingOptionIndex = min(SettingsScreenOptions.allCases.count - 1 + 3, selectedSettingOptionIndex + 1)
					if selectedSettingOptionIndex == skip {
						selectedSettingOptionIndex = selectedSettingOptionIndex + 1
					}
				case .enter:
					if selectedSettingOptionIndex == lastIndex + 2 {
						await config.write()
						await Game.shared.loadConfig()
						return
					} else if selectedSettingOptionIndex == lastIndex + 3 {
						return
					} else {
						SettingsScreenOptions.allCases[selectedSettingOptionIndex].action(config: &config)
					}
				default:
					break
			}
		}
	}

	private func printSettingsOption(x: Int, y: Int, index: Int, text: String, configOption: String) async -> Int {
		let isSelected = selectedSettingOptionIndex == index
		let configOptionToPrint = configOption == "" ? "" : ": \(configOption)"
		await Screen.print(x: x - (text.count / 2), y: y, "\(isSelected ? "\(Game.shared.config.icons.selectedIcon) " : " ")\(text)\(configOptionToPrint)".styled(with: .bold, styledIf: isSelected))
		return y + 1
	}

	private func printHelpMessage(x: Int, y: Int, _ text: String) -> Int {
		Screen.print(x: x - (text.withoutStyles.count / 2), y: y, text)
		return y + 1
	}
}
