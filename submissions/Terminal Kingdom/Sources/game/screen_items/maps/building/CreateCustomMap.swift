import Foundation

enum CreateCustomMap {
	static func checkDoor(tile: DoorTile, grid: [[MapTile]], x: Int, y: Int) async throws(DoorPlaceError) -> (DoorPosition, BuildingPerimeter) {
		guard y > 0, y < grid.count - 1, x > 0, x < grid[0].count - 1 else {
			throw .invalidPosition
		}
		if !(grid[y][x].type == .plain) {
			throw .noSpace
		}
		if await !Game.shared.player.has(item: .door(tile: tile), count: 1) {
			throw .noDoor
		}
		let doorPosition = try getDoorPosition(grid: grid, x: x, y: y)
		var createMap = CreateMap(grid: grid, x: x, y: y, doorPosition: doorPosition)
		let perimeter = switch doorPosition {
			case .bottom: createMap.bottom()
			case .left: createMap.leftSide()
			case .right: createMap.rightSide()
			case .top: createMap.top()
		}
		if (perimeter.top != perimeter.bottom) || (perimeter.leftSide != perimeter.rightSide) {
			throw .notARectangle
		}
		return (doorPosition, perimeter)
	}

	private static func getDoorPosition(grid: [[MapTile]], x: Int, y: Int) throws(DoorPlaceError) -> DoorPosition {
		var buildingsNearby = 0
		var validDoorPosition: DoorPosition?

		var buildingOnTheTop = false
		var buildingOnTheBottom = false
		var buildingOnTheLeft = false
		var buildingOnTheRight = false

		if isBuilding(grid, x: x, y: y + 1) {
			buildingOnTheTop = true
			buildingsNearby += 1
		}

		if isBuilding(grid, x: x, y: y - 1) {
			buildingOnTheBottom = true
			buildingsNearby += 1
		}

		if isBuilding(grid, x: x + 1, y: y) {
			buildingOnTheRight = true
			buildingsNearby += 1
		}

		if isBuilding(grid, x: x - 1, y: y) {
			buildingOnTheLeft = true
			buildingsNearby += 1
		}

		if buildingOnTheTop == false {
			validDoorPosition = .bottom
		}

		if buildingOnTheBottom == false {
			validDoorPosition = .top
		}

		if buildingOnTheLeft == false {
			validDoorPosition = .left
		}

		if buildingOnTheRight == false {
			validDoorPosition = .right
		}

		guard let doorPosition = validDoorPosition else {
			throw .invalidPosition
		}

		guard buildingsNearby == 3 else {
			throw .notEnoughBuildingsNearby
		}
		return doorPosition
	}

	private static func isBuilding(_ grid: [[MapTile]], x: Int, y: Int) -> Bool {
		guard grid.indices.contains(y), grid[y].indices.contains(x) else { return false }
		if case let .building(tile: building) = grid[y][x].type {
			return building.isPlacedByPlayer
		}
		return false
	}

	static func createCustomMap(buildingPerimeter: BuildingPerimeter, doorPosition: DoorPosition, doorType: DoorTileTypes) async -> [[MapTile]] {
		let ratio = 4

		let topLength = buildingPerimeter.top * ratio
		// let bottomLength = buildingPerimeter.bottom * ratio
		let rightLength = buildingPerimeter.rightSide * ratio
		// let leftLength = buildingPerimeter.leftSide * ratio

		var map: [[MapTile]] = await Array(repeating: Array(repeating: .init(type: .plain, isWalkable: true, biome: Game.shared.getBiomeAtPlayerPosition()), count: topLength), count: rightLength)

		for (indexY, y) in map.enumerated() {
			let buildingTile = await MapTile(type: .building(tile: .init(isPlacedByPlayer: false)), isWalkable: false, biome: Game.shared.getBiomeAtPlayerPosition())
			for (indexX, _) in y.enumerated() {
				if indexY == 0 {
					map[indexY][indexX] = buildingTile
				}
				if indexX == 0 {
					map[indexY][indexX] = buildingTile
				}
				if indexY == (rightLength - 1) {
					map[indexY][indexX] = buildingTile
				}
				if indexX == (topLength - 1) {
					map[indexY][indexX] = buildingTile
				}
			}
		}
		// TODO: put door in the position that best matches where it is in the grid
		var doorX, doorY: Int
		switch doorPosition {
			case .top:
				doorX = topLength / 2
				doorY = 0
			case .right:
				doorX = topLength - 1
				doorY = rightLength / 2
			case .left:
				doorX = 0
				doorY = rightLength / 2
			case .bottom:
				doorX = topLength / 2
				doorY = rightLength - 1
		}

		map[doorY][doorX] = await .init(type: .door(tile: .init(type: doorType, isPlacedByPlayer: false)), isWalkable: true, biome: Game.shared.getBiomeAtPlayerPosition())

		if doorType == .builder {
			if doorPosition == .top {
				map[doorY + 2][doorX] = await .init(type: .station(station: .init(type: .workbench)), isWalkable: true, event: .useStation, biome: Game.shared.getBiomeAtPlayerPosition())
			} else if doorPosition == .right {
				map[doorY][doorX - 2] = await .init(type: .station(station: .init(type: .workbench)), isWalkable: true, event: .useStation, biome: Game.shared.getBiomeAtPlayerPosition())
			} else if doorPosition == .left {
				map[doorY][doorX + 2] = await .init(type: .station(station: .init(type: .workbench)), isWalkable: true, event: .useStation, biome: Game.shared.getBiomeAtPlayerPosition())
			} else if doorPosition == .bottom {
				map[doorY - 2][doorX] = await .init(type: .station(station: .init(type: .workbench)), isWalkable: true, event: .useStation, biome: Game.shared.getBiomeAtPlayerPosition())
			}
		}
		if case .castle = doorType {
			if let kingdomID = await Game.shared.isInsideKingdom(x: Game.shared.player.position.x, y: Game.shared.player.position.y) {
				if doorPosition == .top {
					map[doorY + 2][doorX] = await .init(type: .desk(tile: .init(isPlacedByPlayer: false)), isWalkable: true, event: .editKingdom(kingdomID: kingdomID), biome: Game.shared.getBiomeAtPlayerPosition())
				} else if doorPosition == .right {
					map[doorY][doorX - 2] = await .init(type: .desk(tile: .init(isPlacedByPlayer: false)), isWalkable: true, event: .editKingdom(kingdomID: kingdomID), biome: Game.shared.getBiomeAtPlayerPosition())
				} else if doorPosition == .left {
					map[doorY][doorX + 2] = await .init(type: .desk(tile: .init(isPlacedByPlayer: false)), isWalkable: true, event: .editKingdom(kingdomID: kingdomID), biome: Game.shared.getBiomeAtPlayerPosition())
				} else if doorPosition == .bottom {
					map[doorY - 2][doorX] = await .init(type: .desk(tile: .init(isPlacedByPlayer: false)), isWalkable: true, event: .editKingdom(kingdomID: kingdomID), biome: Game.shared.getBiomeAtPlayerPosition())
				}
			}
		}

		var startX, startY: Int
		switch doorPosition {
			case .top:
				startX = doorX
				startY = doorY + 1
			case .right:
				startX = doorX - 1
				startY = doorY
			case .left:
				startX = doorX + 1
				startY = doorY
			case .bottom:
				startX = doorX
				startY = doorY - 1
		}
		map[startY][startX] = await .init(type: .playerStart, isWalkable: true, biome: Game.shared.getBiomeAtPlayerPosition())

		return map
	}
}

struct BuildingPerimeter {
	var rightSide: Int = 0
	var leftSide: Int = 0
	var top: Int = 0
	var bottom: Int = 0
}

enum DoorPosition {
	case top, bottom, right, left
}
