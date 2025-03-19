struct MainMap: MapBoxMap {
	var grid: [[MapTile]]
	var showKingdomLines: Bool = false

	var player: Player {
		get async { await Game.shared.player.position }
	}

	#if DEBUG
		private var hasFoundPlayerStart = false
	#endif

	private init() {
		self.grid = []
		print("This shouldn't be used")
	}

	init() async {
		self.grid = await Game.shared.map
	}

	var tilePlayerIsOn: MapTile {
		get async {
			await grid[player.y][player.x]
		}
	}

	func isWalkable(x: Int, y: Int) async -> Bool {
		guard x >= 0, y >= 0, y < grid.count, x < grid[y].count else { return false }
		if grid[y][x].type == .building(tile: .init(isPlacedByPlayer: true)) {
			return await Game.shared.isBuilding
		}
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
		let oldX = await player.x
		let oldY = await player.y
		var x: Int { get async { await player.x } }
		var y: Int { get async { await player.y } }

		await Game.shared.player.setDirection(direction)

		switch direction {
			case .up where await isWalkable(x: x, y: y - 1):
				await Game.shared.player.setPlayerPosition(x: player.x, y: player.y - 1)
			case .down where await isWalkable(x: x, y: y + 1):
				await Game.shared.player.setPlayerPosition(x: player.x, y: player.y + 1)
			case .left where await isWalkable(x: x - 1, y: y):
				await Game.shared.player.setPlayerPosition(x: player.x - 1, y: player.y)
			case .right where await isWalkable(x: x + 1, y: y):
				await Game.shared.player.setPlayerPosition(x: player.x + 1, y: player.y)
			default:
				break
		}

		await tilePlayerIsOn.type.specialAction(direction: direction, grid: grid)
		let a = await oldX != x
		let b = await oldY != y
		if a || b {
			await map()
			if await Game.shared.isInsideKingdom(x: x, y: y) != nil {
				await StatusBox.setShowKingdomInfo(true)
			} else {
				await StatusBox.setShowKingdomInfo(false)
			}
			await StatusBox.position()
		}
	}

	mutating func map() async {
		#if DEBUG
			if !hasFoundPlayerStart {
				if let (startX, startY) = MapTile.findTilePosition(of: .playerStart, in: grid) {
					await Game.shared.player.setPlayerPosition(x: startX, y: startY)
				} else {
					print("Error: Could not find playerStart tile in the grid.")
				}
				hasFoundPlayerStart = true
			}
		#endif

		let viewportWidth = MapBox.width
		let viewportHeight = MapBox.height
		await render(playerX: player.x, playerY: player.y, viewportWidth: viewportWidth, viewportHeight: viewportHeight)
		if showKingdomLines {
			await renderKingdomLines()
		}
	}

	// TODO: make this one tile and use it twice. Also update existing full redraws
	// TODO: rename to rerender tile
	func updateTile(x: Int, y: Int) async {
		let viewportWidth = MapBox.width
		let viewportHeight = MapBox.height
		let startX = await player.x - viewportWidth / 2
		let startY = await player.y - viewportHeight / 2

		if x >= startX, x < startX + viewportWidth, y >= startY, y < startY + viewportHeight {
			let screenX = x - startX + MapBox.startX
			let screenY = y - startY + MapBox.startY
			await Screen.print(x: screenX, y: screenY, grid[y][x].type.render())
		}
	}

	func interactWithTile() async {
		let tile = await grid[player.y][player.x]
		if tile.isInteractable {
			if let event = tile.event {
				await MapTileEvent.trigger(event: event)
			}
		} else {
			await MessageBox.message("There is nothing to do here.", speaker: .game)
		}
	}

	mutating func updateTile(newTile: MapTile) async {
		await grid[player.y][player.x] = newTile
	}

	mutating func updateTile(newTile: MapTile, x: Int, y: Int) async {
		grid[y][x] = newTile
	}

	mutating func build() async {
		await MapBuilding.build(grid: &grid, x: player.x, y: player.y)
	}

	mutating func destroy() async {
		await MapBuilding.destory(grid: &grid, x: player.x, y: player.y)
	}

	mutating func setShowKingdomLines(_ show: Bool) async {
		showKingdomLines = show
		await map()
	}

	private mutating func renderKingdomLines() async {
		let kingdoms: [Kingdom] = await Game.shared.kingdoms

		for kingdom in kingdoms {
			if let castle = kingdom.getCastle() {
				let x = castle.x
				let y = castle.y
				let radius = kingdom.radius
				let viewportWidth = MapBox.width
				let viewportHeight = MapBox.height
				let startX = await player.x - viewportWidth / 2
				let startY = await player.y - viewportHeight / 2

				for tileY in (y - radius) ... (y + radius) {
					for tileX in (x - radius) ... (x + radius) {
						let dx = abs(tileX - x)
						let dy = abs(tileY - y)

						if dx == radius || dy == radius {
							if tileX >= startX, tileX < startX + viewportWidth, tileY >= startY, tileY < startY + viewportHeight {
								let screenX = tileX - startX + MapBox.startX
								let screenY = tileY - startY + MapBox.startY
								Screen.print(x: screenX, y: screenY, "*".styled(with: [.bold, .red]))
							}
						}
					}
				}
			}
		}
	}
}
