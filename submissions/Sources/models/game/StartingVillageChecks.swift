actor StartingVillageChecks {
	private(set) var hasBeenTaughtToChopLumber: StartingVillageChecksStages = .no
	private(set) var hasUsedMessageWithOptions: Bool = false
	private(set) var firstTimes: FirstTimes = .init()

	func setHasBeenTaughtToChopLumber(_ newHasBeenTaughtToChopLumber: StartingVillageChecksStages) {
		hasBeenTaughtToChopLumber = newHasBeenTaughtToChopLumber
	}

	func setHasUsedMessageWithOptions(_ newHasUsedMessageWithOptions: Bool) {
		hasUsedMessageWithOptions = newHasUsedMessageWithOptions
	}

	func setHasTalkedToSalesmanBuy(_ bool: Bool = true) {
		firstTimes.hasTalkedToSalesmanBuy = bool
	}

	func setHasTalkedToSalesmanSell(_ bool: Bool = true) {
		firstTimes.hasTalkedToSalesmanSell = bool
	}

	func setHasTalkedToSalesmanHelp() {
		firstTimes.hasTalkedToSalesmanHelp = true
	}
}

struct FirstTimes: Codable {
	var hasTalkedToSalesmanBuy: Bool = false
	var hasTalkedToSalesmanSell: Bool = false
	var hasTalkedToSalesmanHelp: Bool = false
}

enum StartingVillageChecksStages: Codable, Equatable {
	case no, inProgress(by: ChoppingLumberTeachingDoorTypes), yes
}

enum ChoppingLumberTeachingDoorTypes: String, Codable, Equatable {
	case builder, miner

	var name: String {
		rawValue.capitalized
	}
}
