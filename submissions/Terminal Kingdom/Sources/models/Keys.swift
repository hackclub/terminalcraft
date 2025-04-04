enum Keys {
	static func normal(key: KeyboardKeys) async {
		switch key {
			case .Q:
				endProgram()
			case .w where await Game.shared.config.wasdKeys, .up where await Game.shared.config.arrowKeys, .k where await Game.shared.config.vimKeys:
				await MapBox.movePlayer(.up)
			case .a where await Game.shared.config.wasdKeys, .left where await Game.shared.config.arrowKeys, .h where await Game.shared.config.vimKeys:
				await MapBox.movePlayer(.left)
			case .s where await Game.shared.config.wasdKeys, .down where await Game.shared.config.arrowKeys, .j where await Game.shared.config.vimKeys:
				await MapBox.movePlayer(.down)
			case .d where await Game.shared.config.wasdKeys, .right where await Game.shared.config.arrowKeys, .l where await Game.shared.config.vimKeys:
				await MapBox.movePlayer(.right)
			case .space, .enter:
				await MapBox.interactWithTile()
			case .L where await MapBox.mapType == .mining:
				await MapBox.setMapType(.mine)
				await MapBox.setBuildingMapPlayer(x: 2, y: 2)
				await MapBox.mapBox()
			case .o:
				#if DEBUG
					let tile = await MapBox.mapType.map.tilePlayerIsOn as! MapTile
					await MessageBox.message("\(tile)", speaker: .dev)
				#else
					if await Game.shared.player.name == "testing" {
						let tile = await MapBox.mapType.map.tilePlayerIsOn as! MapTile
						await MessageBox.message("\(tile)", speaker: .dev)
					}
				#endif
			case .zero:
				Screen.clear()
				Screen.initialize()
				await Screen.initializeBoxes()
			case .i:
				await Game.shared.setIsInInventoryBox(true)
				await InventoryBox.sides()
			case .b:
				if await (Game.shared.player.canBuild), await MapBox.mapType != .mining {
					#if DEBUG
						_ = await Game.shared.player.collect(item: .init(type: .lumber), count: 100)
						_ = await Game.shared.player.collect(item: .init(type: .stone), count: 100)
						_ = await Game.shared.player.collect(item: .init(type: .door(tile: .init(type: .builder))), count: 1)
					#endif
					await InventoryBox.setSelectedBuildItemIndex(0)
					await Game.shared.setIsBuilding(true)
					await MapBox.sides()
					await InventoryBox.inventoryBox()
					await MapBox.showKingdomLines(true)
				}
			case .W:
				await MessageBox.lineUp()
			case .S:
				await MessageBox.lineDown()
			#if DEBUG
				case .t:
					let p = await Game.shared.player.position
					if await !(Game.shared.kingdoms.isEmpty) {
						await MapBox.updateTile(newTile: MapTile(type: .npc(tile: NPCTile(npc: NPC(positionToWalkTo: .init(x: p.x, y: p.y - 10, mapType: .mainMap), tilePosition: NPCPosition(x: p.x, y: p.y, mapType: .mainMap, oldTile: .init(type: .cactus, biome: .plains)), kingdomID: Game.shared.kingdoms[0].id))), event: .talkToNPC, biome: .plains))
					}
				case .u:
					if await !(Game.shared.kingdoms.isEmpty) {
						await MessageBox.message("\(Game.shared.kingdoms[0])", speaker: .dev)
					}
			#endif
			default:
				#if DEBUG
					await MessageBox.message("You pressed: \(key.rawValue)", speaker: .game)
				#else
					break
				#endif
		}
	}

	static func building(key: KeyboardKeys) async {
		switch key {
			case .b, .esc:
				await Game.shared.setIsBuilding(false)
				InventoryBox.showBuildHelp = false
				await MapBox.mapBox()
				await InventoryBox.inventoryBox()
				await MapBox.showKingdomLines(false)
			case .w where await Game.shared.config.wasdKeys, .up where await Game.shared.config.arrowKeys, .k where await Game.shared.config.vimKeys:
				await MapBox.movePlayer(.up)
			case .a where await Game.shared.config.wasdKeys, .left where await Game.shared.config.arrowKeys, .h where await Game.shared.config.vimKeys:
				await MapBox.movePlayer(.left)
			case .s where await Game.shared.config.wasdKeys, .down where await Game.shared.config.arrowKeys, .j where await Game.shared.config.vimKeys:
				await MapBox.movePlayer(.down)
			case .d where await Game.shared.config.wasdKeys, .right where await Game.shared.config.arrowKeys, .l where await Game.shared.config.vimKeys:
				await MapBox.movePlayer(.right)
			case .space, .enter:
				await MapBox.build()
			case .e:
				await MapBox.destroy()
			case .tab:
				await InventoryBox.nextBuildItem()
			case .back_tab:
				await InventoryBox.previousBuildItem()
			case .questionMark:
				InventoryBox.showBuildHelp.toggle()
			default:
				#if DEBUG
					await MessageBox.message("You pressed: \(key.rawValue)", speaker: .game)
				#else
					break
				#endif
		}
	}

	static func inventory(key: KeyboardKeys) async {
		switch key {
			case .i, .esc:
				InventoryBox.showHelp = false
				await Game.shared.setIsInInventoryBox(false)
				await InventoryBox.inventoryBox()
			case .up, .back_tab:
				await InventoryBox.previousInventoryItem()
			case .down, .tab:
				await InventoryBox.nextInventoryItem()
			case .questionMark:
				InventoryBox.showHelp.toggle()
			case .d:
				await InventoryBox.destroyItem()
			default:
				#if DEBUG
					await MessageBox.message("You pressed: \(key.rawValue)", speaker: .game)
				#else
					break
				#endif
		}
	}
}
