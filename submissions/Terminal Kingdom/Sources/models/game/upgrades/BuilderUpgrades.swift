enum BuilderUpgrades {
	static let upgrades: [Int: BuildingUpgrade] = [
		2: .init(cost: [.init(item: .lumber, count: 40), .init(item: .stone, count: 10)]),
	]
}
