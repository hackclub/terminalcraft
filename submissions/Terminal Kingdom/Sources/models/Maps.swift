import Foundation

actor Maps {
	var customMaps: [CustomMap] = []
	private(set) var blacksmith: [[MapTile]] = []
	private(set) var builder: [[MapTile]] = []
	private(set) var carpenter: [[MapTile]] = []
	private(set) var castle: [[MapTile]] = []
	private(set) var farm: [[MapTile]] = []
	private(set) var hospital: [[MapTile]] = []
	private(set) var house: [[MapTile]] = []
	private(set) var hunting_area: [[MapTile]] = []
	private(set) var inventor: [[MapTile]] = []
	private(set) var mainMap: [[MapTile]] = []
	private(set) var mine: [[MapTile]] = []
	private(set) var mining: [[MapTile]] = []
	private(set) var potter: [[MapTile]] = []
	private(set) var restaurant: [[MapTile]] = []
	private(set) var shop: [[MapTile]] = []
	private(set) var stable: [[MapTile]] = []

	func updateCustomMap(at index: Int, with grid: [[MapTile]]) async {
		guard index < customMaps.count else { return }
		customMaps[index].updateGrid(grid)
	}

	func addMap(map: CustomMap) async {
		customMaps.append(map)
	}

	func removeMap(map: CustomMap) async {
		customMaps.removeAll(where: { $0.id == map.id })
	}

	func removeMap(mapID: UUID) async {
		customMaps.removeAll(where: { $0.id == mapID })
	}

	func setMap(mapType: MapType, map: [[MapTile]]) async {
		switch mapType {
			case .blacksmith:
				blacksmith = map
			case .builder:
				builder = map
			case .carpenter:
				carpenter = map
			case .castle:
				castle = map
			case let .custom(mapID: id):
				if let index = customMaps.firstIndex(where: { $0.id == id }) {
					customMaps[index].updateGrid(map)
				} else {
					print("Custom Map not found")
					exit(12)
				}
			case .farm:
				farm = map
			case .hospital:
				hospital = map
			case .house:
				house = map
			case .hunting_area:
				hunting_area = map
			case .inventor:
				inventor = map
			case .mainMap:
				print("Main Map should not be put here")
				exit(11)
			case .mine:
				mine = map
			case .mining:
				print("Mining Map should not be put here")
				exit(11)
			case .potter:
				potter = map
			case .restaurant:
				restaurant = map
			case .shop:
				shop = map
			case .stable:
				stable = map
		}
	}

	func getMapType(mapType: MapType) async -> [[MapTile]] {
		switch mapType {
			case .blacksmith:
				return blacksmith
			case .builder:
				return builder
			case .carpenter:
				return carpenter
			case .castle:
				return castle
			case .custom:
				print("Custom Map should not be put here (9)")
				exit(9)
			case .farm:
				return farm
			case .hospital:
				return hospital
			case .house:
				return house
			case .hunting_area:
				return hunting_area
			case .inventor:
				return inventor
			case .mainMap:
				print("Main Map should not be put here")
				exit(9)
			case .mine:
				return mine
			case .mining:
				print("Mining Map should not be put here")
				exit(9)
			case .potter:
				return potter
			case .restaurant:
				return restaurant
			case .shop:
				return shop
			case .stable:
				return stable
		}
	}

	func updateMap(mapType: MapType, x: Int, y: Int, tile: MapTile) async {
		switch mapType {
			case .blacksmith:
				blacksmith[y][x] = tile
			case .builder:
				builder[y][x] = tile
			case .carpenter:
				carpenter[y][x] = tile
			case .castle:
				castle[y][x] = tile
			case let .custom(mapID: id):
				guard let customMapIndex = customMaps.firstIndex(where: { $0.id == id }) else {
					print("Custom Map not found (10)")
					exit(10)
				}
				await updateCustomMap(at: customMapIndex, with: customMaps[customMapIndex].grid)
			case .farm:
				farm[y][x] = tile
			case .hospital:
				hospital[y][x] = tile
			case .house:
				house[y][x] = tile
			case .hunting_area:
				hunting_area[y][x] = tile
			case .inventor:
				inventor[y][x] = tile
			case .mainMap:
				mainMap[y][x] = tile
				exit(9)
			case .mine:
				mine[y][x] = tile
			case .mining:
				print("Mining Map should not be put here")
				exit(10)
			case .potter:
				potter[y][x] = tile
			case .restaurant:
				restaurant[y][x] = tile
			case .shop:
				shop[y][x] = tile
			case .stable:
				stable[y][x] = tile
		}
	}
}
