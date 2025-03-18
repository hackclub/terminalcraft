import Foundation

enum InventoryBox {
	private(set) nonisolated(unsafe) static var updateInventoryBox = false
	private(set) nonisolated(unsafe) static var updateInventory = false
	nonisolated(unsafe) static var showHelp: Bool = false
	nonisolated(unsafe) static var showBuildHelp: Bool = false

	static var inventoryItems: [Item] {
		get async {
			await Game.shared.player.items
				.reduce(into: [Item]()) { result, item in
					// Deduplicate based on `type` or any relevant property
					if !result.contains(where: { $0.type == item.type }) {
						result.append(item)
					}
				}
				.sorted(by: { $0.type.inventoryName < $1.type.inventoryName })
		}
	}

	static var buildableItems: [Item] {
		get async {
			await Game.shared.player.items
				.filter(\.type.isBuildable)
				.reduce(into: [Item]()) { result, item in
					// Deduplicate based on `type` or any relevant property
					if !result.contains(where: { $0.type == item.type }) {
						result.append(item)
					}
				}
				.sorted(by: sortBuildables)
		}
	}

	static func sides() async {
		await Screen.print(x: startX + 2, y: startY - 1, String(repeating: Game.shared.horizontalLine, count: width - 2).styled(with: [.bold, .yellow], styledIf: Game.shared.isInInventoryBox).styled(with: [.bold, .blue], styledIf: Game.shared.isBuilding))
		for y in (startY - 1) ..< endY {
			await Screen.print(x: startX, y: y, Game.shared.verticalLine.styled(with: [.bold, .yellow], styledIf: Game.shared.isInInventoryBox).styled(with: [.bold, .blue], styledIf: Game.shared.isBuilding))
			await Screen.print(x: endX, y: y, Game.shared.verticalLine.styled(with: [.bold, .yellow], styledIf: Game.shared.isInInventoryBox).styled(with: [.bold, .blue], styledIf: Game.shared.isBuilding))
		}
		await Screen.print(x: startX, y: endY, String(repeating: Game.shared.horizontalLine, count: width).styled(with: [.bold, .yellow], styledIf: Game.shared.isInInventoryBox).styled(with: [.bold, .blue], styledIf: Game.shared.isBuilding))
	}

	static func inventoryBox() async {
		updateInventoryBox = false
		clear()
		await sides()
		await printInventory()
	}

	static func printInventory() async {
		if updateInventory {
			updateInventory = false
		}
		clear()
		if showHelp {
			Screen.print(x: startX + 2, y: startY, "Press '\(KeyboardKeys.i.render)' to toggle inventory")
			Screen.print(x: startX + 2, y: startY + 1, "Press '\(KeyboardKeys.d.render)' to destroy 1")
		} else if showBuildHelp {
			Screen.print(x: startX + 2, y: startY, "Press '\(KeyboardKeys.b.render)' to toggle inventory")
			Screen.print(x: startX + 2, y: startY + 1, "Press '\(KeyboardKeys.enter.render)' or '\(KeyboardKeys.space.render)' to build")
			Screen.print(x: startX + 2, y: startY + 2, "Press '\(KeyboardKeys.e.render)' to destroy")
			Screen.print(x: startX + 2, y: startY + 3, "Press '\(KeyboardKeys.tab.render)' and '\(KeyboardKeys.back_tab.render)' to cycle items")
			await Screen.print(x: startX + 2, y: startY + 2, "\(buildableItems.count) buildable items, \(inventoryItems.count) total items, \(selectedBuildItemIndex) selected")
		} else if await Game.shared.isBuilding {
			var alreadyPrinted: [ItemType] = []
			let buildableItems = await buildableItems.enumerated()
			for (index, item) in buildableItems {
				if !alreadyPrinted.contains(where: { $0 == item.type }) {
					var icon = ""
					if index == selectedBuildItemIndex, await Game.shared.isBuilding {
						icon = "> ".styled(with: .bold)
					} else if index != selectedBuildItemIndex, await Game.shared.isBuilding {
						// icon = "  "
						icon = " "
					}
					await Screen.print(x: startX + 2, y: startY + alreadyPrinted.count, "\(icon)\(item.inventoryName): \(Game.shared.player.getCount(of: item.type))")
					alreadyPrinted.append(item.type)
				}
			}
		} else {
			var alreadyPrinted: [ItemType] = []
			let inventoryItems = await inventoryItems.enumerated()
			for (index, item) in inventoryItems {
				if !alreadyPrinted.contains(where: { $0 == item.type }) {
					var icon = ""
					if index == selectedInventoryIndex, await Game.shared.isInInventoryBox {
						icon = "> ".styled(with: .bold)
					} else if index != selectedInventoryIndex, await Game.shared.isInInventoryBox {
						icon = "  "
					}
					await Screen.print(x: startX + 3, y: startY + alreadyPrinted.count, "\(icon)\(item.inventoryName): \(Game.shared.player.getCount(of: item.type))")
					alreadyPrinted.append(item.type)
				}
			}
		}
		let isInInventoryBox = await Game.shared.isInInventoryBox
		let isBuilding = await Game.shared.isBuilding

		if isInInventoryBox || isBuilding {
			if !showHelp {
				Screen.print(x: startX + 2, y: endY - 1, "Press '\(KeyboardKeys.questionMark.render)' for controls")
			} else {
				Screen.print(x: startX + 2, y: endY - 1, "Press '\(KeyboardKeys.questionMark.render)' to leave")
			}
		} else {
			Screen.print(x: startX + 2, y: endY - 1, "Press '\(KeyboardKeys.i.render)'")
		}
	}

	private static func sortBuildables(_ lhs: Item, _ rhs: Item) -> Bool {
		if lhs.type == .lumber {
			return true
		} else if rhs.type == .lumber {
			return false
		}
		return lhs.type.inventoryName < rhs.type.inventoryName
	}

	static func destroyItem() async {
		if await inventoryItems.isEmpty {
			return
		}
		let uuid = await inventoryItems[selectedInventoryIndex].id
		await Game.shared.player.destroyItem(id: uuid)
	}

	static func clear() {
		let spaceString = String(repeating: " ", count: width - 2)
		for y in startY ..< endY {
			Screen.print(x: startX + 2, y: y, spaceString)
		}
	}

	static func nextBuildItem() async {
		await addToSelectedBuildItemIndex(1)
	}

	static func previousBuildItem() async {
		await addToSelectedBuildItemIndex(-1)
	}

	static func nextInventoryItem() async {
		await addToSelectedInventoryIndex(1)
	}

	static func previousInventoryItem() async {
		await addToSelectedInventoryIndex(-1)
	}

	static func setUpdateInventoryBox() {
		updateInventoryBox = true
	}
}

extension InventoryBox {
	private nonisolated(unsafe) static var _selectedBuildItemIndex: Int = 0 { didSet { updateInventory = true } }
	nonisolated(unsafe) static var selectedBuildItemIndex: Int {
		_selectedBuildItemIndex
	}

	static func setSelectedBuildItemIndex(_ newIndex: Int) async {
		let clampedIndex = await max(0, min(newIndex, buildableItems.count - 1))
		_selectedBuildItemIndex = clampedIndex
	}

	static func addToSelectedBuildItemIndex(_ amount: Int) async {
		await setSelectedBuildItemIndex(selectedBuildItemIndex + amount)
	}
}

extension InventoryBox {
	private nonisolated(unsafe) static var _selectedInventoryIndex: Int = 0 { didSet { updateInventory = true } }
	nonisolated(unsafe) static var selectedInventoryIndex: Int {
		_selectedInventoryIndex
	}

	static func setSelectedInventoryIndex(_ newIndex: Int) async {
		let clampedIndex = await max(0, min(newIndex, inventoryItems.count - 1))
		_selectedInventoryIndex = clampedIndex
	}

	static func addToSelectedInventoryIndex(_ amount: Int) async {
		await setSelectedInventoryIndex(selectedInventoryIndex + amount)
	}
}

extension InventoryBox {
	private nonisolated(unsafe) static var _showInventoryBox = true
	nonisolated(unsafe) static var showInventoryBox: Bool { _showInventoryBox }
	static func setShowInventoryBox(_ newValue: Bool) async {
		_showInventoryBox = newValue
		if newValue {
			await inventoryBox()
		} else {
			clear()
		}
	}
}
