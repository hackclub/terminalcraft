import Foundation

struct NPCTile: Codable, Hashable, Equatable {
	let id: UUID
	var npc: NPC

	init(id: UUID = UUID()) {
		self.id = id
		self.npc = .init(isStartingVillageNPC: false, kingdomID: id)
	}

	init(id: UUID = UUID(), npc: NPC) {
		self.id = id
		self.npc = npc
	}

	static func renderNPC(tile: NPCTile) async -> String {
		if !tile.npc.hasTalkedToBefore {
			if let job = tile.npc.job, !job.isHelper {
				return "!".styled(with: [.bold, .red])
			}
		}
		switch tile.npc.job {
			default:
				// TODO: Not sure if this will stay
				if tile.npc.positionToWalkTo != nil {
					return await (Game.shared.config.useNerdFont ? "" : "N").styled(with: .bold)
				} else {
					let nerdFontSymbol = tile.npc.gender == .male ? "󰙍" : "󰙉"
					return await (Game.shared.config.useNerdFont ? nerdFontSymbol : "N").styled(with: .bold)
				}
		}
	}

	static func move(position: NPCPosition) async {
		let npcTile = await MapBox.mapType.map.grid[position.y][position.x] as! MapTile

		if case let .npc(tile: tile) = npcTile.type, let positionToWalkTo = tile.npc.positionToWalkTo {
			// Reached the destination
			if positionToWalkTo == .init(x: position.x, y: position.y, mapType: position.mapType) {
				await Game.shared.removeNPC(position)
				if case let .door(doorTile) = position.oldTile.type {
					if case let .custom(mapID, _) = doorTile.type {
						// TODO: fix this when multidoors in custom maps
						guard let customMapIndex = await Game.shared.maps.customMaps.firstIndex(where: { $0.id == mapID }) else { return }
						let grid = await Game.shared.maps.customMaps[customMapIndex].grid

						for (yIndex, y) in grid.enumerated() {
							if let xIndex = y.firstIndex(where: { if case .door = $0.type { true } else { false }}) {
								// Restore the door tile
								await MapBox.updateTile(newTile: MapTile(
									type: .door(tile: doorTile),
									isWalkable: npcTile.isWalkable,
									event: npcTile.event,
									biome: npcTile.biome
								),
								thisOnlyWorksOnMainMap: true, x: position.x, y: position.y)
								var doorPosition: DoorPosition = .bottom
								if yIndex == 0 {
									doorPosition = .top
								} else if yIndex == grid.count - 1 {
									doorPosition = .bottom
								} else if xIndex == 0 {
									doorPosition = .left
								} else if xIndex == grid[yIndex].count - 1 {
									doorPosition = .right
								}
								let npcX: Int
								let npcY: Int
								switch doorPosition {
									case .left:
										npcX = xIndex + 1
										npcY = yIndex + 1
									case .right:
										npcX = xIndex - 1
										npcY = yIndex - 1
									case .top:
										npcX = xIndex - 1
										npcY = yIndex + 1
									case .bottom:
										npcX = xIndex + 1
										npcY = yIndex - 1
								}

								var newGrid = await Game.shared.maps.customMaps[customMapIndex].grid
								var newTile = tile
								newTile.npc.removePostion()
								newGrid[npcY][npcX] = MapTile(
									type: .npc(tile: newTile),
									isWalkable: npcTile.isWalkable,
									event: npcTile.event,
									biome: npcTile.biome
								)
								await Game.shared.maps.updateCustomMap(at: customMapIndex, with: newGrid)
								break
							}
						}

					} else {}
					// put npc in the custom map
					return
				} else {
					var npcNew = tile
					npcNew.npc.removePostion()
					await MapBox.updateTile(newTile: MapTile(
						type: .npc(tile: npcNew),
						isWalkable: npcTile.isWalkable,
						event: npcTile.event,
						biome: npcTile.biome
					), thisOnlyWorksOnMainMap: true, x: position.x, y: position.y)
					return
				}
			}
			let newNpcPosition = await NPCMoving.move(
				target: positionToWalkTo,
				current: .init(x: position.x, y: position.y, mapType: position.mapType)
			)

			let currentTile = await MapBox.mapType.map.grid[newNpcPosition.y][newNpcPosition.x] as! MapTile

			let newPosition = NPCPosition(
				x: newNpcPosition.x,
				y: newNpcPosition.y,
				mapType: position.mapType,
				oldTile: currentTile
			)

			await withTaskGroup(of: Void.self) { group in
				group.addTask {
					// Restore old tile
					await MapBox.setMapGridTile(
						x: position.x,
						y: position.y,
						tile: position.oldTile,
						mapType: position.mapType
					)
				}

				group.addTask {
					// Update new tile to NPC
					await MapBox.setMapGridTile(
						x: newNpcPosition.x,
						y: newNpcPosition.y,
						tile: MapTile(
							type: .npc(tile: tile),
							isWalkable: npcTile.isWalkable,
							event: npcTile.event,
							biome: npcTile.biome
						),
						mapType: position.mapType
					)
				}

				group.addTask {
					await Game.shared.updateNPC(oldPosition: position, newPosition: newPosition)
				}

				group.addTask {
					await MapBox.updateTwoTiles(x1: newNpcPosition.x, y1: newNpcPosition.y, x2: position.x, y2: position.y)
				}
			}
		}
	}
}

extension NPCTile {
	func encode(to encoder: any Encoder) throws {
		var container = encoder.container(keyedBy: CodingKeys.self)
		try container.encode(id, forKey: .id)
		try container.encode(npc, forKey: .npc)
	}

	enum CodingKeys: CodingKey {
		case id
		case npc
	}

	init(from decoder: any Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.id = try container.decode(UUID.self, forKey: .id)
		self.npc = try container.decode(NPC.self, forKey: .npc)
	}
}
