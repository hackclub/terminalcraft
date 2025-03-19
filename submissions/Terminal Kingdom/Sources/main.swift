import Foundation

Screen.clear()
Screen.Cursor.moveToTop()

TerminalInput.enableRawMode()

defer {
	TerminalInput.restoreOriginalMode()
}

if await Game.shared.hasInited == false {
	Screen.initialize()
	await Game.shared.initGame()
	MapBoxActor.shared = await MapBoxActor()
	await showTitleScreen()
	// await startCropQueue()
	await mainGameLoop()
}

func showTitleScreen() async {
	var screen = TitleScreen()
	let option = await screen.show()
	Screen.clear()
	if option == .helpOption {
		await option.action(screen: &screen)
		_ = TerminalInput.readKey()
		await showTitleScreen()
	} else if option == .settingsOption {
		await option.action(screen: &screen)
		await showTitleScreen()
	} else {
		await Screen.initializeBoxes()
		await option.action(screen: &screen)
	}
}

func endProgram() {
	// TODO: Save game
	//    let filePath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first
	//    if let filePath {
	//        let file = filePath.appendingPathComponent("terminalkingdom.game.json")
	//
	//        do {
	//            let game = CodableGame(location: await Game.shared.location, hasInited: await Game.shared.hasInited, isTypingInMessageBox: await Game.shared.isTypingInMessageBox, player: await Game.shared.player, map: await Game.shared.map, startingVillageChecks: await Game.shared.startingVillageChecks, stages: await Game.shared.stages, messages: await Game.shared.messages)
	//            let JSON = try JSONEncoder().encode(game)
	//            try JSON.write(to: filePath)
	//        } catch {
	//
	//        }
	//    }
	TerminalInput.restoreOriginalMode()
	Screen.clear()
	exit(0)
}

func loadGame() async -> Bool {
	// let filePath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first
	//
	// if let filePath {
	// 	let file = filePath.appendingPathComponent("terminalkingdom.game.json")
	// 	do {
	// 		let fileData = try Data(contentsOf: file)
	// 		let decodedGame = try JSONDecoder().decode(CodableGame.self, from: fileData)
	// 		await Game.shared.reloadGame(decodedGame: decodedGame)
	// 		return true
	// 	} catch {
	// 		// print("Error reading or decoding the file: \(error)")
	// 	}
	// }
	false
}

func newGame() async {
	await MessageBox.message("Welcome to Terminal Kingdom!", speaker: .game)
	let playerName = await MessageBox.messageWithTyping("Let's create your character. What is your name?", speaker: .game)
	await MessageBox.message("Welcome \(playerName)!", speaker: .game)
	await Game.shared.player.setName(playerName)
	await StatusBox.statusBox()
}

func mainGameLoop() async {
	while true {
		if StatusBox.updateQuestBox {
			await StatusBox.questArea()
		}
		if InventoryBox.updateInventoryBox {
			await InventoryBox.inventoryBox()
		}
		if InventoryBox.updateInventory {
			await InventoryBox.printInventory()
		}

		guard await !(Game.shared.isTypingInMessageBox) else { continue }

		let key = TerminalInput.readKey()
		if await Game.shared.isInInventoryBox {
			await Keys.inventory(key: key)
		} else if await Game.shared.isBuilding {
			await Keys.building(key: key)
		} else {
			await Keys.normal(key: key)
		}
	}
}
