enum Quest: Codable, Equatable {
	case chopLumber(count: Int = 10, for: String? = nil)

	// MARK: Blacksmith

	case blacksmith1
	case blacksmith2
	case blacksmith3
	case blacksmith4
	case blacksmith5
	case blacksmith6
	case blacksmith7
	case blacksmith8
	case blacksmith9
	case blacksmith10

	// MARK: Mine

	case mine1
	case mine2
	case mine3
	case mine4
	case mine5
	case mine6
	case mine7
	case mine8
	case mine9
	case mine10

	// MARK: Builder

	case builder1
	case builder2
	case builder3
	case builder4
	case builder5
	case builder6
	case builder7
	case builder8
	case builder9
	case builder10

	// MARK: Farm

	case farm1
	case farm2
	case farm3
	case farm4
	case farm5

	var label: String {
		get async {
			switch self {
				case let .chopLumber(count, `for`):
					if let `for` {
						"Go get \(count) lumber for the \(`for`)"
					} else {
						"Go get \(count) lumber"
					}
				case .blacksmith1: "Go get iron from the Mine and bring it to the Blacksmith"
				case .blacksmith2: "Go collect 20 lumber and band bring it to the Blacksmith"
				case .blacksmith3: "Bring lumber to the Carpenter and bring it back to the Blacksmith"
				case .blacksmith4: "Get 5 coal from the Miner"
				case .blacksmith5: "Use the furnace to craft steel"
				case .blacksmith6: "Make a pickaxe on the anvil"
				case .blacksmith7:
					switch await Game.shared.stages.blacksmith.stage7Stages {
						case .notStarted: "Blacksmith Stage 7 not started"
						case .makeSword: "Make a sword at the anvil"
						case .bringToHunter: "Bring the sword to the hunter"
						case .comeBack: "Return to the Blacksmith"
						case .done: "Blacksmith Stage 7 done"
					}
				case .blacksmith8:
					switch await Game.shared.stages.blacksmith.stage8Stages {
						case .notStarted: "Blacksmith Stage 8 not started"
						case .getMaterials: "Get materials from the Miner"
						case .makeSteel: "Make steel on the anvil"
						case .comeBack: "Return to the Blacksmith"
						case .done: "Blacksmith Stage 8 done"
					}
				case .blacksmith9: "Sell the steel in the shop"
				case .blacksmith10: "Collect the Blacksmith's gift"
				case .mine1: "Get a pickaxe from the blacksmith and bring it to the Miner"
				case .mine2: "Mine 20 clay for the Miner"
				case .mine3: "Give 50 lumber to the Miner to upgrade the mine"
				case .mine4:
					switch await Game.shared.stages.mine.stage4Stages {
						case .notStarted: "Mine Stage 4 not started"
						case .collectPickaxe: "Get a pickaxe from the Blacksmith"
						case .mine: "Mine 30 stone for the Miner"
						case .done: "Mine Stage 4 done"
					}
				case .mine5: "Mine 20 iron for the Miner"
				case .mine6:
					switch await Game.shared.stages.mine.stage6Stages {
						case .notStarted: "Mine Stage 6 not started"
						case .goGetAxe: "Collect an axe from the Blacksmith"
						case .collect: "Collect 100 lumber to upgrade the mine"
						case .done: "Mine Stage 6 done"
					}
				case .mine7: "Upgrade the mine!"
				case .mine8: "Collect the Blacksmith's gift"
				case .mine9: "Mine 5 gold for the Miner"
				case .mine10:
					switch await Game.shared.stages.mine.stage10Stages {
						case .notStarted: "Mine Stage 10 not started"
						case .goToSalesman: "Bring the coins back to the Miner"
						case .comeBack: "Return to the Miner"
						case .done: "Mine Stage 10 done"
					}
				case .builder1: "Collect materials from the Miner"
				case .builder2: "Collect 20 lumber for the Builder"
				case .builder3: "Make a door at the workbench"
				case .builder4: "Go talk to the King"
				case .builder5: "Build a house for the Builder"
				case .builder6: "Collect 30 lumber for the Builder"
				case .builder7: "Decorate the inside of your house"
				case .builder8: "Talk to the Builder"
				case .builder9: "Build a house for the Builder"
				case .builder10: "Take the door and have fun creating!"
				case .farm1: "Collect a tree seed for the Farmer"
				case .farm2: "Plant the tree seed in the pot"
				case .farm3: "Collect the tree and bring it to the Farmer"
				case .farm4:
					switch await Game.shared.stages.farm.stage4Stages {
						case .notStarted:
							"Farm Stage 4 not started"
						case .collect:
							"Go get 10 clay from the mine"
						case .comeBack:
							"Return to the farmer"
						case .done:
							"Farm Stage 4 done"
					}
				case .farm5: "Get a pot from the potter."
			}
		}
	}
}
