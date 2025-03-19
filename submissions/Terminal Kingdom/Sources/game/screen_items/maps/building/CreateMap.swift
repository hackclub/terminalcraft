import Foundation

struct CreateMap {
	var grid: [[MapTile]]
	var x: Int
	var y: Int
	let startX: Int
	let startY: Int
	let doorPosition: DoorPosition

	init(grid: [[MapTile]], x: Int, y: Int, doorPosition: DoorPosition) {
		self.grid = grid
		self.x = x
		self.y = y
		self.startX = x
		self.startY = y
		self.doorPosition = doorPosition
	}

	private enum CheckDoorDirection {
		case up, down, left, right

		var next: Self {
			switch self {
				case .right: .up
				case .up: .left
				case .left: .down
				case .down: .right
			}
		}
	}

	mutating func rightSide() -> BuildingPerimeter {
		calculatePerimeter(startingDirection: .up)
	}

	mutating func leftSide() -> BuildingPerimeter {
		calculatePerimeter(startingDirection: .down)
	}

	mutating func top() -> BuildingPerimeter {
		calculatePerimeter(startingDirection: .left)
	}

	mutating func bottom() -> BuildingPerimeter {
		calculatePerimeter(startingDirection: .right)
	}

	private mutating func calculatePerimeter(startingDirection: CheckDoorDirection) -> BuildingPerimeter {
		var hasReachedStart = false
		var direction = startingDirection
		var buildingPerimeter = BuildingPerimeter()

		struct Position: Hashable {
			var x: Int
			var y: Int
		}

		var visited: Set<Position> = []
		let startingPosition = Position(x: x, y: y)
		visited.insert(startingPosition)

		while !hasReachedStart {
			// TODO: if moving the coordinates to 0,0 this might not work
			if doorPosition == .top || doorPosition == .bottom {
				switch direction {
					case .right:
						x += 1
						if isWhereDoorWillGo(at: x, y: y) {
							hasReachedStart = (x == startX && y == startY)
							buildingPerimeter.rightSide += 1
						} else if isBuilding(at: x, y: y) {
							buildingPerimeter.rightSide += 1
						} else {
							direction = direction.next
							x -= 1 // Backtrack to original position
						}
					case .up:
						y -= 1
						if isWhereDoorWillGo(at: x, y: y) {
							hasReachedStart = (x == startX && y == startY)
							buildingPerimeter.top += 1
						} else if isBuilding(at: x, y: y) {
							buildingPerimeter.top += 1
						} else {
							direction = direction.next
							y += 1 // Backtrack to original position
						}
					case .left:
						x -= 1
						if isWhereDoorWillGo(at: x, y: y) {
							hasReachedStart = (x == startX && y == startY)
							buildingPerimeter.leftSide += 1
						} else if isBuilding(at: x, y: y) {
							buildingPerimeter.leftSide += 1
						} else {
							direction = direction.next
							x += 1 // Backtrack to original position
						}
					case .down:
						y += 1
						if isWhereDoorWillGo(at: x, y: y) {
							hasReachedStart = (x == startX && y == startY)
							buildingPerimeter.bottom += 1
						} else if isBuilding(at: x, y: y) {
							buildingPerimeter.bottom += 1
						} else {
							direction = direction.next
							y -= 1 // Backtrack to original position
						}
				}
			} else if doorPosition == .left || doorPosition == .right {
				switch direction {
					case .right:
						x += 1
						if isWhereDoorWillGo(at: x, y: y) {
							hasReachedStart = (x == startX && y == startY)
							buildingPerimeter.bottom += 1
						} else if isBuilding(at: x, y: y) {
							buildingPerimeter.bottom += 1
						} else {
							direction = direction.next
							x -= 1 // Backtrack to original position
						}
					case .up:
						y -= 1
						if isWhereDoorWillGo(at: x, y: y) {
							hasReachedStart = (x == startX && y == startY)
							buildingPerimeter.rightSide += 1
						} else if isBuilding(at: x, y: y) {
							buildingPerimeter.rightSide += 1
						} else {
							direction = direction.next
							y += 1 // Backtrack to original position
						}
					case .left:
						x -= 1
						if isWhereDoorWillGo(at: x, y: y) {
							hasReachedStart = (x == startX && y == startY)
							buildingPerimeter.top += 1
						} else if isBuilding(at: x, y: y) {
							buildingPerimeter.top += 1
						} else {
							direction = direction.next
							x += 1 // Backtrack to original position
						}
					case .down:
						y += 1
						if isWhereDoorWillGo(at: x, y: y) {
							hasReachedStart = (x == startX && y == startY)
							buildingPerimeter.leftSide += 1
						} else if isBuilding(at: x, y: y) {
							buildingPerimeter.leftSide += 1
						} else {
							direction = direction.next
							y -= 1 // Backtrack to original position
						}
				}
			}

			let currentPosition = Position(x: x, y: y)
			visited.insert(currentPosition)

			if currentPosition == startingPosition, visited.count > 1 {
				hasReachedStart = true
			}
		}
		var newBuildingPerimeter: BuildingPerimeter = .init()
		switch doorPosition {
			case .right, .left:
				newBuildingPerimeter.top = buildingPerimeter.top + 1
				newBuildingPerimeter.bottom = buildingPerimeter.bottom + 1
				newBuildingPerimeter.rightSide = buildingPerimeter.rightSide + 1
				newBuildingPerimeter.leftSide = buildingPerimeter.leftSide + 1
			case .top, .bottom:
				newBuildingPerimeter.top = buildingPerimeter.top + 1 + buildingPerimeter.bottom
				newBuildingPerimeter.bottom = buildingPerimeter.top + 1 + buildingPerimeter.bottom
				newBuildingPerimeter.rightSide = buildingPerimeter.rightSide - 1
				newBuildingPerimeter.leftSide = buildingPerimeter.leftSide - 1
		}

		return newBuildingPerimeter
	}

	private func isBuilding(at x: Int, y: Int) -> Bool {
		guard grid.indices.contains(y), grid[y].indices.contains(x) else { return false }
		if case let .building(tile: building) = grid[y][x].type {
			return building.isPlacedByPlayer
		}
		return false
	}

	private func isWhereDoorWillGo(at x: Int, y: Int) -> Bool {
		x == startX && y == startY
	}
}
