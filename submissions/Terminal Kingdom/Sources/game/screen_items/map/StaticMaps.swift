import Foundation

enum StaticMaps {
	static var MainMap: [[MapTile]] {
		loadMap(fileName: "main")
	}

	static func buildingMap(mapType: MapType) async -> [[MapTile]] {
		if await Game.shared.maps.getMapType(mapType: mapType) == [] {
			let map = loadMap(fileName: mapTypeToBuilding(mapType: mapType).rawValue)
			await Game.shared.maps.setMap(mapType: mapType, map: map)
			return map
		} else {
			return await Game.shared.maps.getMapType(mapType: mapType)
		}
	}

	private static func loadMap(fileName: String) -> [[MapTile]] {
		if let fileURL = Bundle.module.url(forResource: fileName, withExtension: "json") {
			do {
				let data = try Data(contentsOf: fileURL)
				return try JSONDecoder().decode([[MapTile]].self, from: data)
			} catch {
				print("Error loading or decoding JSON: \(error)")
				exit(1)
			}
		} else {
			print("Could not find the \(fileName) map json file.")
			exit(1)
		}
	}

	static func mapTypeToBuilding(mapType: MapType) -> MapFileName {
		switch mapType {
			case .castle: return .castle
			case .blacksmith: return .blacksmith
			case .mine: return .mine
			case .shop: return .shop
			case .builder: return .builder
			case .hunting_area: return .hunting_area
			case .inventor: return .inventor
			case .house: return .house
			case .stable: return .stable
			case .farm: return .farm
			case .hospital: return .hospital
			case .carpenter: return .carpenter
			case .restaurant: return .restaurant
			case .potter: return .potter
			case .mainMap:
				print("Map should not be passed into buildingMap.")
				return .blacksmith
			case .mining:
				print("Mining should not be passed into buildingMap.")
				return .blacksmith
			case .custom:
				print("Custom map should not be passed into buildingMap.")
				return .blacksmith
		}
	}
}

enum MapFileName: String, CaseIterable {
	case castle
	case blacksmith
	case mine
	case shop
	case builder
	case hunting_area
	case inventor
	case house
	case stable
	case farm
	case hospital
	case carpenter
	case restaurant
	case potter
}
