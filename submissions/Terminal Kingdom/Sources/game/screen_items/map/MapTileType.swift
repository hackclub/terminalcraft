enum MapTileType: TileType {
	// MARK: Plains Biome

	case plain
	case water
	case tree

	// MARK: Desert Biome

	case sand
	case cactus

	// MARK: Snow Biome

	case snow
	case snow_tree
	case ice

	// MARK: Other Biome

	case stone
	case lava

	// MARK: Other

	case path // TODO: Make buildable
	case player

	// MARK: Buildable

	case building(tile: BuildingTile)
	case door(tile: DoorTile)
	case chest /* (tile: ChestTile) */
	case bed(tile: BedTile)
	case desk(tile: DeskTile)
	case fence(tile: FenceTile)
	case gate(tile: GateTile)

	// MARK: Dont Generate

	case TOBEGENERATED
	case playerStart
	case biomeTOBEGENERATED(type: BiomeType)

	// MARK: Building Stuff

	case station(station: StationTile)
	case startMining

	// MARK: Crops

	// TODO: rename crop -> tile
	case crop(crop: CropTile)
	case pot(tile: PotTile)

	// MARK: NPC

	case npc(tile: NPCTile)
	case shopStandingArea(type: ShopStandingAreaType)

	var isBuildable: Bool {
		switch self {
			case .building, .door, .fence, .gate, .chest, .bed, .desk, .path: true
			default: false
		}
	}

	var isPlainLike: Bool {
		switch self {
			case .plain, .snow: true
			default: false
		}
	}

	func render() async -> String {
		switch self {
			case .plain: " "
			case .water: "W".styled(with: .brightBlue)
			case .path: "P"
			case .tree: await (Game.shared.config.useNerdFont ? "󰐅" : "T").styled(with: .green)
			case let .building(tile: buildingTile): await Game.shared.config.icons.buildingIcon.styled(with: .dim, styledIf: Game.shared.isBuilding && buildingTile.isPlacedByPlayer)
			case .player: await Game.shared.config.icons.characterIcon.styled(with: [.blue, .bold])
			case .sand: "S".styled(with: .yellow)
			case let .door(doorTile): await DoorTile.renderDoor(tile: doorTile)
			case .TOBEGENERATED: "."
			case .playerStart: " "
			case .snow: "S".styled(with: .bold)
			case .snow_tree: await (Game.shared.config.useNerdFont ? "󰐅" : "T").styled(with: .bold)
			case .cactus: await (Game.shared.config.useNerdFont ? "󰶵" : "C").styled(with: .brightGreen)
			case .ice: "I".styled(with: .brightCyan)
			case .fence: await (Game.shared.config.useNerdFont ? "f" : "f").styled(with: .brown)
			case .gate: "g"
			case let .crop(crop: cropTile): await CropTile.renderCrop(tile: cropTile)
			case let .pot(tile: potTile): await PotTile.renderCropInPot(tile: potTile)
			case let .station(station: station): StationTile.render(tile: station)
			case .startMining: "M"
			case let .npc(tile: tile): await NPCTile.renderNPC(tile: tile)
			case .shopStandingArea(type: _): "."
			case .biomeTOBEGENERATED(type: _): "/"
			case .chest /* (tile: _) */: await (Game.shared.config.useNerdFont ? "󰜦" : "C").styled(with: .yellow)
			case .bed: await Game.shared.config.useNerdFont ? "" : "B"
			case .desk: await Game.shared.config.useNerdFont ? "󱈹" : "D"
			case .stone: "S".styled(with: .dim)
			case .lava: "L".styled(with: .red)
		}
	}

	var name: String {
		switch self {
			case .plain: "plain"
			case .water: "water"
			case .tree: "tree"
			case .sand: "sand"
			case .cactus: "cactus"
			case .snow: "snow"
			case .snow_tree: "snow_tree"
			case .ice: "ice"
			case .path: "path"
			case .building: "building"
			case .player: "player"
			case let .door(tile): tile.type.name
			case .TOBEGENERATED: "TOBEGENERATED"
			case .playerStart: "playerStart"
			case let .station(station: station): station.type.name
			case .startMining: "startMining"
			case .fence: "fence"
			case .gate: "gate"
			case let .crop(crop):
				crop.type.rawValue
			case let .pot(tile):
				tile.cropTile.type.rawValue
			case let .npc(tile):
				tile.npc.job?.render ?? "None"
			case let .shopStandingArea(type):
				type.rawValue
			case let .biomeTOBEGENERATED(type: biome):
				biome.rawValue
			case .chest: "chest"
			case .bed: "bed"
			case .desk: "desk"
			case .stone: "stone"
			case .lava: "lava"
		}
	}

	func specialAction(direction: PlayerDirection, grid: [[MapTile]]) async {
		let player = await Game.shared.player.position
		func isWalkable(x: Int, y: Int) -> Bool {
			guard x >= 0, y >= 0, y < grid.count, x < grid[y].count else { return false }
			return grid[y][x].isWalkable
		}
		switch self {
			case .ice:
				switch direction {
					case .up where isWalkable(x: player.x, y: player.y - 1):
						await Game.shared.player.setPlayerPosition(addY: -1)
					case .down where isWalkable(x: player.x, y: player.y + 1):
						await Game.shared.player.setPlayerPosition(addY: 1)
					case .left where isWalkable(x: player.x - 1, y: player.y):
						await Game.shared.player.setPlayerPosition(addX: -1)
					case .right where isWalkable(x: player.x + 1, y: player.y):
						await Game.shared.player.setPlayerPosition(addX: 1)
					default:
						break
				}
			default:
				return
		}
	}
}

enum ShopStandingAreaType: String, Hashable, Codable {
	case buy, sell, help
}

enum BiomeType: String, Hashable, Codable {
	case plains, desert, snow, forest, volcano, tundra, ocean, coast, swamp, mountain
}
