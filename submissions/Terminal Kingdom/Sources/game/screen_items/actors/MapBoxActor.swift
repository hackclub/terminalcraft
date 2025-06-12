import Foundation

// TODO: could this be better?
actor MapBoxActor {
	nonisolated(unsafe) static var shared = MapBoxActor()
	var mainMap: MainMap?
	private(set) var miningMap: MineMap?
	private(set) var buildingMap: BuildingMap?
	private(set) var showMapBox = true

	private init() {
		self.mainMap = nil
		self.miningMap = nil
		self.buildingMap = nil
	}

	init() async {
		self.mainMap = await MainMap()
		self.miningMap = await MineMap()
		self.buildingMap = await BuildingMap(.castle(side: .left))
	}

	func updateMainMapTile(at x: Int, y: Int, with tile: MapTile) async {
		mainMap!.grid[y][x] = tile
	}

	func updateMiningMapTile(at x: Int, y: Int, with tile: MineTile) async {
		miningMap!.grid[y][x] = tile
	}

	func updateBuildingMapTile(at x: Int, y: Int, with tile: MapTile) async {
		buildingMap!.grid[y][x] = tile
		await Game.shared.maps.updateMap(mapType: buildingMap!.mapType, x: x, y: y, tile: tile)
	}

	func updateMainMapTile(newTile: MapTile) async {
		var map = mainMap!
		await map.updateTile(newTile: newTile)
		mainMap = map
	}

	func updateMainMapTile(newTile: MapTile, x: Int, y: Int) async {
		var map = mainMap!
		await map.updateTile(newTile: newTile, x: x, y: y)
		mainMap = map
	}

	func updateBuildingMapTile(newTile: MapTile) async {
		buildingMap!.updateTile(newTile: newTile)
	}

	func resetMiningMap() async {
		miningMap = await .init()
	}

	func resetBuildingMap(_ mapType: MapType) async {
		buildingMap = await .init(mapType)
	}

	func mainMapBuild() async {
		var map = mainMap
		await map!.build()
		mainMap = map
	}

	func mainMapDestroy() async {
		var map = mainMap
		await map!.destroy()
		mainMap = map
	}

	func buildingMapBuild() async {
		var map = buildingMap
		await map!.build()
		buildingMap = map
	}

	func buildingMapDestroy() async {
		var map = buildingMap
		await map!.destroy()
		buildingMap = map
	}

	func mainMapMovePlayer(_ direction: PlayerDirection) async {
		var map = mainMap
		await map!.movePlayer(direction)
		mainMap = map
	}

	func mineMapMovePlayer(_ direction: PlayerDirection) async {
		var map = miningMap
		await map!.movePlayer(direction)
		miningMap = map
	}

	func buildingMapMovePlayer(_ direction: PlayerDirection) async {
		var map = buildingMap
		await map!.movePlayer(direction)
		buildingMap = map
	}

	func mainMap() async {
		var map = mainMap
		await map!.map()
		mainMap = map
	}

	func updateMainMapTile(x: Int, y: Int) async {
		await mainMap!.updateTile(x: x, y: y)
	}

	func buildingMap() async {
		var map = buildingMap
		await map!.map()
		buildingMap = map
	}

	func updateBuildingMapTile(x: Int, y: Int) async {
		await buildingMap!.updateTile(x: x, y: y)
	}

	func miningMap() async {
		var map = miningMap
		await map!.map()
		miningMap = map
	}

	func showMapBox() async {
		showMapBox = true
		await MapBox.mapBox()
	}

	func hideMapBox() async {
		showMapBox = false
		MapBox.clear()
	}

	func setBuildingMapPlayer(x: Int, y: Int) async {
		var map = buildingMap
		map!.setPlayer(x: x, y: y)
		buildingMap = map
	}

	func setKingdomLines(_ value: Bool) async {
		var map = mainMap
		await map!.setShowKingdomLines(value)
		mainMap = map
	}
}
