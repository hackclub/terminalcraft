import Foundation

struct BuildingMap: MapBoxMap {
	var grid: [[MapTile]]
	// {
	// didSet {
	// 	if case let .custom(map: map) = mapType {
	// 		map.updateGrid(grid)
	// 	}
	// }
	// }

	var player: Player = .init(x: 1, y: 1)

	var tilePlayerIsOn: MapTile {
		get async {
			grid[player.y][player.x]
		}
	}

	let mapType: MapType

	init(_ mapType: MapType) async {
		self.mapType = mapType
		// TODO: Clean up
		switch mapType {
			case let .custom(mapID):
				self.grid = await Game.shared.maps.customMaps.filter { $0.id == mapID }[0].grid
			case .mainMap, .mining:
				print("Error: Could not find map for \(mapType)")
				exit(8)
			default:
				self.grid = await StaticMaps.buildingMap(mapType: mapType)
		}

		// Coordinates for inside the building
		if await Game.shared.player.position.x == 55, await Game.shared.player.position.y == 23 {
			// Start player in correct spot on start
			player.x = 55
			player.y = 23
		} else if case let .castle(side: side) = mapType {
			switch side {
				case .top:
					player.x = 64
					player.y = 1
				case .bottom:
					player.x = 65
					player.y = 53
				case .right:
					player.x = 129
					player.y = 27
				case .left:
					player.x = 1
					player.y = 27
			}
		} else if case let .farm(type: type) = mapType {
			switch type {
				case .main:
					findPayerStart()
				case .farm_area:
					player.x = 9
					player.y = 1
			}
		} else if case let .hospital(side: side) = mapType {
			switch side {
				case .top:
					findPayerStart()
				case .bottom:
					player.x = 11
					player.y = 9
			}
		} else {
			findPayerStart()
		}
	}

	private mutating func findPayerStart() {
		if let (startX, startY) = MapTile.findTilePosition(of: .playerStart, in: grid) {
			player.x = startX
			player.y = startY
		} else {
			print("Error: Could not find playerStart tile in the building grid.")
		}
	}

	mutating func map() async {
		let viewportWidth = MapBox.width + 1
		let viewportHeight = MapBox.height
		await render(playerX: player.x, playerY: player.y, viewportWidth: viewportWidth, viewportHeight: viewportHeight)
	}

	func updateTile(x: Int, y: Int) async {
		let viewportWidth = MapBox.width + 1
		let viewportHeight = MapBox.height
		let startX = player.x - viewportWidth / 2
		let startY = player.y - viewportHeight / 2

		if x >= startX, x < startX + viewportWidth, y >= startY, y < startY + viewportHeight {
			let screenX = x /* - startX */ + MapBox.startX
			let screenY = y /* - startY */ + MapBox.startY
			await Screen.print(x: screenX, y: screenY, grid[y][x].type.render())
		}
	}

	func isWalkable(x: Int, y: Int) -> Bool {
		guard x >= 0, y >= 0, y < grid.count, x < grid[y].count else { return false }
		return grid[y][x].isWalkable
	}

	func render(playerX: Int, playerY: Int, viewportWidth: Int, viewportHeight: Int) async {
		let halfViewportWidth = viewportWidth / 2
		let halfViewportHeight = viewportHeight / 2

		let startX = max(0, playerX - halfViewportWidth)
		let startY = max(0, playerY - halfViewportHeight)

		let endX = min(grid[0].count, startX + viewportWidth)
		let endY = min(grid.count, startY + viewportHeight)

		for (screenY, mapY) in (startY ..< endY).enumerated() {
			let rowString = await (startX ..< endX).asyncMap { mapX in
				if mapX == playerX, mapY == playerY {
					await MapTileType.player.render()
				} else {
					await grid[mapY][mapX].type.render()
				}
			}.joined()
			Screen.print(x: MapBox.startX, y: MapBox.startY + screenY, rowString)
		}
	}

	mutating func movePlayer(_ direction: PlayerDirection) async {
		let oldX = player.x
		let oldY = player.y

		switch direction {
			case .up where isWalkable(x: player.x, y: player.y - 1):
				player.y -= 1
			case .down where isWalkable(x: player.x, y: player.y + 1):
				player.y += 1
			case .left where isWalkable(x: player.x - 1, y: player.y):
				player.x -= 1
			case .right where isWalkable(x: player.x + 1, y: player.y):
				player.x += 1
			default:
				break
		}

		if oldX != player.x || oldY != player.y {
			await map()
		}
	}

	func interactWithTile() async {
		let tile = grid[player.y][player.x]
		if tile.isInteractable {
			if let event = tile.event {
				await MapTileEvent.trigger(event: event)
			}
		} else {
			await MessageBox.message("There is nothing to do here.", speaker: .game)
		}
	}

	mutating func updateTile(newTile: MapTile) {
		let mapTypeCopy = mapType
		let x = player.x
		let y = player.y
		grid[y][x] = newTile

		Task {
			await Game.shared.maps.updateMap(mapType: mapTypeCopy, x: x, y: y, tile: newTile)
		}
	}

	mutating func build() async {
		await MapBuilding.build(grid: &grid, x: player.x, y: player.y)
	}

	mutating func destroy() async {
		await MapBuilding.destory(grid: &grid, x: player.x, y: player.y)
	}

	mutating func setPlayer(x: Int, y: Int) {
		player.x = x
		player.y = y
	}
}
