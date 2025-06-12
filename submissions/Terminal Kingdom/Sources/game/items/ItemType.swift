enum ItemType: Codable, Equatable, Hashable {
	// MARK: Weapons

	case sword, axe(type: AxeItem), pickaxe(type: PickaxeItem), boomerang // bow? net? dagger?

	// MARK: Armor?

	case backpack(type: BackpackItem) // TODO: DO BACKPACK

	// MARK: Food

	// MARK: Materials

	case lumber // plank?
	case iron
	case coal
	case gold
	case stone
	case clay
	case tree_seed
	case stick
	case steel

	// MARK: Buildings

	case door(tile: DoorTile)
	case fence
	case gate
	case chest /* (tile: ChestTile) */
	case bed
	case desk

	// MARK: Other

	case coin

	// MARK: Crops

	case carrot
	case potato
	case wheat
	case lettuce
	case pot

	var isBuildable: Bool {
		switch self {
			case .door, .fence, .gate, .lumber, .chest, .bed, .desk, .pot: true
			default: false
		}
	}

	var inventoryName: String {
		switch self {
			case .sword: "Sword"
			case let .axe(type: type): "Axe (\(type.durability))"
			case let .pickaxe(type: type): "Pickaxe (\(type.durability))"
			case .boomerang: "Boomerang"
			case let .backpack(type: type): "\(type.inventoryName) Backpack"
			case .lumber: "Lumber"
			case .iron: "Iron"
			case .coal: "Coal"
			case .gold: "Gold"
			case .stone: "Stone"
			case .tree_seed: "Tree Seed"
			case let .door(tile: tile): "\(tile.type.name) Door"
			case .fence: "Fence"
			case .gate: "Gate"
			case .coin: "Coin"
			case .clay: "Clay"
			case .stick: "Stick"
			case .steel: "Steel"
			case .carrot: "Carrot"
			case .lettuce: "Lettuce"
			case .potato: "Potato"
			case .wheat: "Wheat"
			case .chest: "Chest"
			case .bed: "Bed"
			case .desk: "Desk"
			case .pot: "Pot"
		}
	}

	var price: Int? {
		switch self {
			case .sword: 10
			case let .axe(type): (type.durability / 11) * 2
			case let .pickaxe(type): (type.durability / 10) * 2
			case .boomerang: 10
			case .backpack: 10
			case .lumber: 1
			case .iron: 5
			case .coal: 2
			case .stone: 5
			case .tree_seed: 1
			case .clay: 2
			case .stick: 1
			case .steel: 3
			case .carrot: 1
			case .lettuce: 1
			case .potato: 1
			case .wheat: 1
			default: nil
		}
	}
}

enum BackpackItem: Codable, Equatable {
	case small, medium, large

	var inventoryName: String {
		switch self {
			case .small: "Small"
			case .medium: "Medium"
			case .large: "Large"
		}
	}
}
