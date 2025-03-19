import Foundation

enum DoorTileTypes: Codable, Equatable, Hashable {
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
	indirect case custom(mapID: UUID?, doorType: DoorTileTypes)

	var name: String {
		switch self {
			case .castle:
				"Castle"
			case .blacksmith:
				"Blacksmith"
			case .mine:
				"Mine"
			case .shop:
				"Shop"
			case .builder:
				"Builder"
			case .hunting_area:
				"Hunting Area"
			case .inventor:
				"Inventor"
			case .house:
				"House"
			case .stable:
				"Stable"
			case .farm:
				"Farm"
			case .hospital:
				"Hospital"
			case .carpenter:
				"Carpenter"
			case .restaurant:
				"Restaurant"
			case .potter:
				"Potter"
			case let .custom(_, doorType: doorType):
				doorType.name
		}
	}

	var upgrades: [Int: BuildingUpgrade] {
		switch self {
			// case .blacksmith:
			case .builder:
				BuilderUpgrades.upgrades
			// case .carpenter:
			// case .castle(_):
			// case .farm(_):
			// case .hospital(_):
			// case .house:
			// case .hunting_area:
			// case .inventor:
			// case .mine:
			// case .potter:
			// case .restaurant:
			// case .shop:
			// case .stable:
			case let .custom(_, doorType):
				doorType.upgrades
			default:
				[:]
		}
	}

	var coordinatesForStartingVillageBuildings: (x: Int, y: Int) {
		// All in MainMap
		switch self {
			case let .castle(side):
				switch side {
					case .top:
						return (x: 243, y: 119)
					case .right:
						return (x: 250, y: 123)
					case .bottom:
						return (x: 243, y: 127)
					case .left:
						return (x: 236, y: 123)
				}
			case .blacksmith:
				return (x: 267, y: 130)
			case .mine:
				return (x: 216, y: 124)
			case .shop:
				return (x: 277, y: 116)
			case .builder:
				return (x: 302, y: 123)
			case .hunting_area:
				return (x: 233, y: 140)
			case .inventor:
				return (x: 273, y: 108)
			case .house:
				print("house coordinatesForStartingVillageBuildings not set")
				return (x: 1000, y: 1000)
			case .stable:
				print("stable coordinatesForStartingVillageBuildings not set")
				return (x: 1000, y: 1000)
			case let .farm(type):
				switch type {
					case .main:
						return (x: 229, y: 105)
					case .farm_area:
						return (x: 231, y: 101)
				}
			case let .hospital(side: side):
				switch side {
					case .top:
						return (x: 196, y: 116)
					case .bottom:
						return (x: 196, y: 129)
				}
			case .carpenter:
				return (x: 279, y: 136)
			case .restaurant:
				print("restaurant coordinatesForStartingVillageBuildings not set")
				return (x: 1000, y: 1000)
			case .potter:
				print("potter coordinatesForStartingVillageBuildings not set")
				return (x: 1000, y: 1000)
			case .custom:
				print("custom coordinatesForStartingVillageBuildings not set")
				return (x: 1000, y: 1000)
		}
	}

	var price: DoorPrice {
		switch self {
			case .blacksmith:
				.init(items: [.init(item: .lumber, count: 20)])
			case .builder:
				.init(items: [.init(item: .lumber, count: 10), .init(item: .iron, count: 1)])
			case .carpenter:
				.init(items: [.init(item: .lumber, count: 10), .init(item: .iron, count: 1)])
			case .castle:
				.init(items: [.init(item: .coin, count: 100_000)])
			case let .custom(_, doorType):
				doorType.price
			case .farm:
				.init(items: [.init(item: .lumber, count: 10), .init(item: .tree_seed, count: 5)])
			case .hospital:
				.init(items: [.init(item: .lumber, count: 20), .init(item: .potato, count: 10)])
			case .house:
				.init(items: [.init(item: .lumber, count: 10)])
			case .hunting_area:
				.init(items: [.init(item: .lumber, count: 10), .init(item: .sword, count: 1)])
			case .inventor:
				.init(items: [.init(item: .lumber, count: 30), .init(item: .iron, count: 10)])
			case .mine:
				.init(items: [.init(item: .lumber, count: 10)])
			case .potter:
				.init(items: [.init(item: .lumber, count: 10), .init(item: .clay, count: 2)])
			case .restaurant:
				.init(items: [.init(item: .lumber, count: 10), .init(item: .iron, count: 1)])
			case .shop:
				.init(items: [.init(item: .lumber, count: 15)])
			case .stable:
				.init(items: [.init(item: .lumber, count: 10)])
		}
	}
}

struct DoorPrice: Codable {
	var items: [ItemAmount]
}

enum FarmDoors: Codable, Equatable, Hashable {
	case main, farm_area
}

enum HospitalSide: Codable, Equatable, Hashable {
	case top, bottom
}

enum CastleSide: Codable, Equatable, Hashable {
	case top, bottom, right, left
}
