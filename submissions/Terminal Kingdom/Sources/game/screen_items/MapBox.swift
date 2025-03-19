import Foundation

enum MapBox {
	static var mainMap: MainMap {
		get async { await MapBoxActor.shared.mainMap! }
	}

	static var miningMap: MineMap {
		get async { await MapBoxActor.shared.miningMap! }
	}

	static var buildingMap: BuildingMap {
		get async { await MapBoxActor.shared.buildingMap! }
	}

	static var showMapBox: Bool {
		get async { await MapBoxActor.shared.showMapBox }
	}

	static var mapType: MapType {
		get async { await Game.shared.player.mapType }
	}

	static var player: Player {
		get async { await mapType.map.player }
	}

	static var tilePlayerIsOn: MapTile {
		get async { await mapType.map.tilePlayerIsOn as! MapTile }
	}

	static func mapBox() async {
		clear()
		await sides()

		switch await mapType {
			case .mainMap:
				await MapBoxActor.shared.mainMap()
			case .mining:
				await MapBoxActor.shared.miningMap()
			default:
				await MapBoxActor.shared.buildingMap()
		}
	}

	static func updateTile(x: Int, y: Int) async {
		switch await mapType {
			case .mainMap:
				await MapBoxActor.shared.updateMainMapTile(x: x, y: y)
			case .mining:
				break
			default:
				await MapBoxActor.shared.updateBuildingMapTile(x: x, y: y)
		}
	}

	static func updateTwoTiles(x1: Int, y1: Int, x2: Int, y2: Int) async {
		guard await mapType != .mine else {
			return
		}
		await updateTile(x: x1, y: y1)
		await updateTile(x: x2, y: y2)
	}

	static func sides() async {
		await Screen.print(x: startX, y: startY - 1, String(repeating: Game.shared.horizontalLine, count: width + 1).styled(with: [.bold, .blue], styledIf: Game.shared.isBuilding))
		for y in startY ..< (endY + 1) {
			await Screen.print(x: startX - 1, y: y, Game.shared.verticalLine.styled(with: [.bold, .blue], styledIf: Game.shared.isBuilding))
			await Screen.print(x: endX, y: y, Game.shared.verticalLine.styled(with: [.bold, .blue], styledIf: Game.shared.isBuilding))
		}
		await Screen.print(x: startX, y: endY, String(repeating: Game.shared.horizontalLine, count: width).styled(with: [.bold, .blue], styledIf: Game.shared.isBuilding))
	}

	static func clear() {
		let spaceString = String(repeating: " ", count: width)
		for y in startY ..< endY {
			Screen.print(x: startX, y: y, spaceString)
		}
	}

	static func movePlayer(_ direction: PlayerDirection) async {
		switch await mapType {
			case .mainMap:
				await MapBoxActor.shared.mainMapMovePlayer(direction)
			case .mining:
				await MapBoxActor.shared.mineMapMovePlayer(direction)
			default:
				await MapBoxActor.shared.buildingMapMovePlayer(direction)
		}
	}

	static func interactWithTile() async {
		await mapType.map.interactWithTile()
	}

	static func findTile(type: MapTileType, in grid: [[MapTile]]) -> (x: Int, y: Int)? {
		for (y, row) in grid.enumerated() {
			if let x = row.firstIndex(where: { tile in
				if case let .door(doorTile) = tile.type, case let .door(checkTile) = type {
					return doorTile == checkTile
				}
				return tile.type == type
			}) {
				return (x, y)
			}
		}
		return nil
	}

	static func destroy() async {
		switch await mapType {
			case .mainMap:
				await MapBoxActor.shared.mainMapDestroy()
			case .mining:
				break
			default:
				await MapBoxActor.shared.buildingMapDestroy()
		}
	}

	static func build() async {
		if await Game.shared.player.items.count(where: { $0.type.isBuildable }) > 0 {
			switch await mapType {
				case .mainMap:
					await MapBoxActor.shared.mainMapBuild()
				case .mining:
					break
				default:
					await MapBoxActor.shared.buildingMapBuild()
			}
		}
	}

	// TODO: (Yes i know this is bad.) Fix this
	static func updateTile(newTile: MapTile, thisOnlyWorksOnMainMap _: Bool, x: Int, y: Int) async {
		switch await mapType {
			case .mainMap:
				await MapBoxActor.shared.updateMainMapTile(newTile: newTile, x: x, y: y)
			default:
				break
		}
	}

	static func updateTile(newTile: MapTile) async {
		switch await mapType {
			case .mainMap:
				await MapBoxActor.shared.updateMainMapTile(newTile: newTile)
			case .mining:
				break
			default:
				await MapBoxActor.shared.updateBuildingMapTile(newTile: newTile)
		}
	}

	static func setMapType(_ mapType: MapType) async {
		await Game.shared.player.setMapType(mapType)
		switch mapType {
			case .mainMap:
				break
			case .mining:
				await MapBoxActor.shared.resetMiningMap()
			default:
				await MapBoxActor.shared.resetBuildingMap(mapType)
		}
		_ = await player
		await mapBox()
	}

	static func showMapBox() async {
		await MapBoxActor.shared.showMapBox()
	}

	static func hideMapBox() async {
		await MapBoxActor.shared.hideMapBox()
	}

	static func setMainMapGridTile(x: Int, y: Int, tile: MapTile) async {
		await MapBoxActor.shared.updateMainMapTile(at: x, y: y, with: tile)
	}

	static func setMapGridTile(x: Int, y: Int, tile: MapTile, mapType: MapType) async {
		switch mapType {
			case .mainMap:
				await MapBoxActor.shared.updateMainMapTile(at: x, y: y, with: tile)
			case .mining:
				break
			default:
				await MapBoxActor.shared.updateBuildingMapTile(at: x, y: y, with: tile)
		}
	}

	static func setMainMapGridTile(tile: MapTile) async {
		await MapBoxActor.shared.updateMainMapTile(at: MapBox.player.x, y: MapBox.player.y, with: tile)
	}

	static func resetMiningMap() async {
		await MapBoxActor.shared.resetMiningMap()
	}

	static func resetBuildingMap(_ mapType: MapType) async {
		await MapBoxActor.shared.resetBuildingMap(mapType)
	}

	static func setBuildingMapPlayer(x: Int, y: Int) async {
		await MapBoxActor.shared.setBuildingMapPlayer(x: x, y: y)
	}

	static func setMainMapPlayerPosition(_ position: (x: Int, y: Int)) async {
		await Game.shared.player.setPlayerPosition(x: position.x, y: position.y)
	}

	static func showKingdomLines(_ value: Bool) async {
		switch await mapType {
			case .mainMap:
				await MapBoxActor.shared.setKingdomLines(value)
			default:
				break
		}
	}
}

enum MapType: Codable, Equatable, Hashable {
	case mainMap
	case mining
	case castle(side: CastleSide)
	case blacksmith
	case mine
	case shop
	case builder
	case hunting_area
	case inventor
	case house
	case stable
	case farm(type: FarmDoors)
	case hospital(side: HospitalSide)
	case carpenter
	case restaurant
	case potter
	case custom(mapID: UUID)

	var map: any MapBoxMap {
		get async {
			switch self {
				case .mainMap:
					await MapBoxActor.shared.mainMap!
				case .mining:
					await MapBoxActor.shared.miningMap!
				default:
					await MapBoxActor.shared.buildingMap!
			}
		}
	}
}

struct Player: Codable {
	var x: Int
	var y: Int
}
