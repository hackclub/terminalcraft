enum MineTileType: TileType {
	// MARK: Plains Biome

	case plain
	case player
	case playerStart
	case stone
	case clay
	case coal
	case iron
	case gold

	func render(grid: [[MineTile]], tileX: Int, tileY: Int) -> String {
		let tile = grid[tileY][tileX]
		let name = switch self {
			case .plain: " "
			case .player: "@".styled(with: [.blue, .bold])
			case .playerStart: " "
			case .stone: !MineTile.isSeen(tile: tile, tileX: tileX, tileY: tileY, grid: grid) ? "." : "S"
			case .coal: !MineTile.isSeen(tile: tile, tileX: tileX, tileY: tileY, grid: grid) ? "." : "C".styled(with: .dim)
			case .iron: !MineTile.isSeen(tile: tile, tileX: tileX, tileY: tileY, grid: grid) ? "." : "I".styled(with: .bold)
			case .clay: !MineTile.isSeen(tile: tile, tileX: tileX, tileY: tileY, grid: grid) ? "." : "c".styled(with: .brown)
			case .gold: !MineTile.isSeen(tile: tile, tileX: tileX, tileY: tileY, grid: grid) ? "." : "G".styled(with: .yellow)
		}
		return name
	}

	var name: String {
		switch self {
			case .plain: "plain"
			case .player: "player"
			case .playerStart: "playerStart"
			case .stone: "stone"
			case .coal: "coal"
			case .iron: "iron"
			case .clay: "clay"
			case .gold: "gold"
		}
	}
}
