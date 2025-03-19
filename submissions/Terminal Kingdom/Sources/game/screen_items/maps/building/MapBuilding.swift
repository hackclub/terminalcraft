import Foundation

enum MapBuilding {
	static func build(grid: inout [[MapTile]], x: Int, y: Int) async {
		if !grid[y][x].type.isPlainLike {
			await MessageBox.message("You can't build here.", speaker: .game)
			return
		}

		let selectedItem = await InventoryBox.buildableItems[InventoryBox.selectedBuildItemIndex]
		if await Game.shared.player.has(item: selectedItem.type, count: selectedItem.type == .lumber ? 5 : 1) {
			if await Game.shared.stages.builder.stage5Stages == .buildHouse {
				await BuildForBuilderStage5.build(grid: &grid, x: x, y: y)
			} else if await Game.shared.stages.builder.stage7Stages == .buildInside, case .custom(mapID: _) = await MapBox.mapType {
				await BuildForBuilderStage7.build(grid: &grid, x: x, y: y)
			} else {
				await buildNormally(grid: &grid, x: x, y: y)
			}
		} else {
			await MessageBox.message("You don't have enough items to build", speaker: .game)
		}
	}

	// TODO: Put anything that can happen later in a Task
	static func destory(grid: inout [[MapTile]], x: Int, y: Int) async {
		if grid[y][x].type.isBuildable {
			await removeNormally(grid: &grid, x: x, y: y)
		} else {
			await MessageBox.message("You can't remove this tile.", speaker: .game)
		}
	}

	static func removeNormally(grid: inout [[MapTile]], x: Int, y: Int) async {
		let tile = grid[y][x]
		guard tile.type.isBuildable else {
			await MessageBox.message("You can't remove this tile.", speaker: .game)
			return
		}
		func placeTile(tile: some BuildableTile, count: Int = 1, name: String, item: () -> ItemType) async {
			if tile.isPlacedByPlayer {
				grid[y][x] = await MapTile(type: .plain, biome: Game.shared.getBiome(x: x, y: y))
				let itemToCollect = item()
				_ = await Game.shared.player.collect(item: .init(type: itemToCollect), count: count)
			} else {
				await MessageBox.message("You can't remove this \(name).", speaker: .game)
			}
		}
		switch tile.type {
			case let .building(tile: buildingTile):
				await placeTile(tile: buildingTile, count: 4, name: "building", item: { .lumber })
			case let .door(tile: doorTile):
				await placeTile(tile: doorTile, name: "\(doorTile.type.name) Door") {
					if case let .custom(mapID: id, doorType: doorType) = doorTile.type {
						Task {
							if let id {
								await Game.shared.removeMap(mapID: id)
							}
						}
						if case .castle = doorType {
							Task {
								guard let building = await Game.shared.hasKingdomBuilding(x: x, y: y) else { return }
								guard let kingdom = await Game.shared.getKingdom(buildingID: building.id) else { return }
								await Game.shared.removeKingdom(id: kingdom.id)
							}
						}
						return .door(tile: .init(type: .custom(mapID: nil, doorType: doorType)))
					} else {
						return .door(tile: doorTile)
					}
				}
			case let .fence(tile: fenceTile):
				await placeTile(tile: fenceTile, name: "fence", item: { .fence })
			case let .gate(tile: gateTile):
				await placeTile(tile: gateTile, name: "gate", item: { .gate })
			case .chest:
				// TODO: break chest
				await MessageBox.message("You can't remove this chest yet", speaker: .game)
			case let .bed(tile: bedTile):
				await placeTile(tile: bedTile, name: "bed", item: { .bed })
			case let .desk(tile: deskTile):
				await placeTile(tile: deskTile, name: "desk", item: { .desk })
			default:
				await MessageBox.message("This is a not buildable tile", speaker: .game)
		}
	}

	static func buildNormally(grid: inout [[MapTile]], x: Int, y: Int) async {
		let selectedItem = await InventoryBox.buildableItems[InventoryBox.selectedBuildItemIndex]
		if selectedItem.type == .lumber {
			if await Game.shared.player.has(item: .lumber, count: 5) {
				grid[y][x] = MapTile(type: .building(tile: .init(isPlacedByPlayer: true)), biome: grid[y][x].biome)
				await Game.shared.player.removeItem(item: .lumber, count: 5)
			}
		} else {
			if await Game.shared.player.has(item: selectedItem.type, count: 1) {
				if case let .door(tile: tile) = selectedItem.type {
					do {
						let (doorPosition, buildingPerimeter) = try await CreateCustomMap.checkDoor(tile: tile, grid: grid, x: x, y: y)
						let map = await CreateCustomMap.createCustomMap(buildingPerimeter: buildingPerimeter, doorPosition: doorPosition, doorType: tile.type)
						guard let customMap = try CustomMap(grid: map) else {
							await MessageBox.message("An error occurred while creaing map", speaker: .game)
							return
						}

						// Success
						if tile.type == .builder {
							await Game.shared.addMap(map: customMap)
							grid[y][x] = MapTile(type: .door(tile: .init(type: .custom(mapID: customMap.id, doorType: tile.type), isPlacedByPlayer: true)), isWalkable: true, event: .openDoor, biome: grid[y][x].biome)
							await Game.shared.player.removeItem(item: .door(tile: tile), count: 1)
							await startKingdom(grid: &grid, x: x, y: y, doorPosition: doorPosition)
						} else {
							guard let kingdomID = await Game.shared.isInsideKingdom(x: x, y: y) else {
								await MessageBox.message("You have to be inside of a kingdom to place this door", speaker: .game)
								return
							}
							await Game.shared.addMap(map: customMap)
							grid[y][x] = MapTile(type: .door(tile: .init(type: .custom(mapID: customMap.id, doorType: tile.type), isPlacedByPlayer: true)), isWalkable: true, event: .openDoor, biome: grid[y][x].biome)
							await Game.shared.player.removeItem(item: .door(tile: tile), count: 1)
							await Game.shared.addKingdomBuilding(.init(type: tile.type, x: x, y: y), kingdomID: kingdomID)
						}
						if await Game.shared.stages.builder.stage5Stages == .buildHouse {
							await Game.shared.stages.builder.setStage5HasBuiltHouse(true)
						}
					} catch {
						await MessageBox.message("An error occurred: \(error.localizedDescription)", speaker: .game)
					}
				} else {
					grid[y][x] = MapTile(type: itemTypeToMapTileType(selectedItem.type)!, biome: grid[y][x].biome)
					await Game.shared.player.removeItem(item: selectedItem.type, count: 1)
				}
			}
		}
	}

	private static func itemTypeToMapTileType(_ itemType: ItemType) -> MapTileType? {
		// only used in building
		switch itemType {
			case .door:
				Task {
					await MessageBox.message("This shouldn't have happen", speaker: .game)
				}
				return nil
			case .fence: return .fence(tile: .init(isPlacedByPlayer: true))
			case .gate: return .gate(tile: .init(isPlacedByPlayer: true))
			case .bed: return .bed(tile: .init(isPlacedByPlayer: true))
			case .desk: return .desk(tile: .init(isPlacedByPlayer: true))
			case .chest: return .chest
			default: return nil
		}
	}

	private static func startKingdom(grid: inout [[MapTile]], x: Int, y: Int, doorPosition: DoorPosition) async {
		guard await MapBox.mapType == .mainMap else {
			await MessageBox.message("You can't start a kingdom here.", speaker: .game)
			return
		}
		let kingdom = await Kingdom(name: "\(Game.shared.player.name)'s Kingdom", buildings: [.init(type: .builder, x: x, y: y)])
		await Game.shared.createKingdom(kingdom)
		await MessageBox.message("A builder should be coming any minute now.", speaker: .player)

		let npcStartX = 235
		let npcStartY = 122
		let oldTile = await MapBox.mainMap.grid[npcStartY][npcStartX]
		let positionToWalkTo = switch doorPosition {
			case .left: TilePosition(x: x, y: y, mapType: .mainMap)
			case .right: TilePosition(x: x, y: y, mapType: .mainMap)
			case .top: TilePosition(x: x, y: y, mapType: .mainMap)
			case .bottom: TilePosition(x: x, y: y, mapType: .mainMap)
		}
		let tilePosition = NPCPosition(x: npcStartX, y: npcStartY, mapType: .mainMap, oldTile: oldTile)
		let npcTile = NPCTile(npc: NPC(job: .builder, positionToWalkTo: positionToWalkTo, tilePosition: tilePosition, kingdomID: kingdom.id))
		let npcMapTile = MapTile(type: .npc(tile: npcTile), event: .talkToNPC, biome: .plains)

		grid[npcStartY][npcStartX] = npcMapTile
	}
}

extension Int {
	func isWithInOneOf(_ other: Int) -> Bool {
		self == other || self == other + 1 || self == other - 1
	}
}

private enum BuildForBuilderStage5 {
	static func build(grid: inout [[MapTile]], x: Int, y: Int) async {
		var buildingsPlaced: Int { Game.shared.stages.builder.stage5BuildingsPlaced }
		if buildingsPlaced == 0 {
			await MapBuilding.buildNormally(grid: &grid, x: x, y: y)
			await Game.shared.stages.builder.setStage5LastBuildingPlaced(.init(x: x, y: y))
		} else {
			// let lastBuildingPlaced = await Game.shared.stages.builder.stage5LastBuildingPlaced
			// if let lastBuildingPlaced {
			// if x.isWithInOneOf(lastBuildingPlaced.x), y.isWithInOneOf(lastBuildingPlaced.y) {
			await MapBuilding.buildNormally(grid: &grid, x: x, y: y)
			await Game.shared.stages.builder.setStage5LastBuildingPlaced(.init(x: x, y: y))
			// } else {
			// 	await MessageBox.message("To build a house, you should only build next to the last building you placed.", speaker: .game)
			// 	return
			// }
			// } else {
			// 	await MessageBox.message("You haven't placed a building?", speaker: .game)
			// 	return
			// }
		}
	}
}

private enum BuildForBuilderStage7 {
	static func build(grid: inout [[MapTile]], x: Int, y: Int) async {
		// This will only be called inside of a house.
		await MapBuilding.buildNormally(grid: &grid, x: x, y: y)
		await Game.shared.stages.builder.setStage7HasBuiltInside(true)
	}
}
