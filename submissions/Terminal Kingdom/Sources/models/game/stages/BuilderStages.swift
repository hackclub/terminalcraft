import Foundation

actor BuilderStages {
	private(set) var stageNumber = 0
	var isDone: Bool { stageNumber > 10 }
	private(set) var stage1ItemsUUIDsToRemove: [UUID]?
	private(set) var stage2LumberUUIDToRemove: [UUID]?
	private(set) var stage2AxeUUIDToRemove: UUID?
	private(set) var stage3ItemsToMakeDoorUUIDsToRemove: [UUID]?
	private(set) var stage3DoorUUIDToRemove: UUID?
	private(set) var stage5HasBuiltHouse: Bool = false
	private(set) var stage5BuildingsPlaced: Int = 0
	private(set) var stage5LastBuildingPlaced: LastBuildingPlaced? {
		didSet {
			stage5BuildingsPlaced += 1
		}
	}

	private(set) var stage5ItemsToBuildHouseUUIDsToRemove: [UUID]?
	private(set) var stage6LumberUUIDToRemove: UUID?
	private(set) var stage6AxeUUIDToRemove: UUID?
	private(set) var stage7ItemsToBuildInsideUUIDsToRemove: [UUID]?
	private(set) var stage7HasBuiltInside: Bool = false
	private(set) var stage8_UUID: [UUID]?

	private(set) var stage1Stages: BuilderStage1Stages = .notStarted
	private(set) var stage2Stages: BuilderStage2Stages = .notStarted
	private(set) var stage3Stages: BuilderStage3Stages = .notStarted
	private(set) var stage4Stages: BuilderStage4Stages = .notStarted
	private(set) var stage5Stages: BuilderStage5Stages = .notStarted
	private(set) var stage6Stages: BuilderStage6Stages = .notStarted
	private(set) var stage7Stages: BuilderStage7Stages = .notStarted
	private(set) var stage8Stages: BuilderStage8Stages = .notStarted
	private(set) var stage9Stages: BuilderStage9Stages = .notStarted
	private(set) var stage10Stages: BuilderStage10Stages = .notStarted

	func next() {
		stageNumber += 1
	}

	func setStage1ItemsUUIDsToRemove(_ uuids: [UUID]) {
		stage1ItemsUUIDsToRemove = uuids
	}

	func setStage2LumberUUIDToRemove(_ uuids: [UUID]) {
		stage2LumberUUIDToRemove = uuids
	}

	func setStage2AxeUUIDToRemove(_ uuid: UUID) {
		stage2AxeUUIDToRemove = uuid
	}

	func setStage3ItemsToMakeDoorUUIDsToRemove(_ uuids: [UUID]) {
		stage3ItemsToMakeDoorUUIDsToRemove = uuids
	}

	func setStage3DoorUUIDToRemove(_ uuid: UUID) {
		stage3DoorUUIDToRemove = uuid
	}

	func setStage5ItemsToBuildHouseUUIDsToRemove(_ uuids: [UUID]) {
		stage5ItemsToBuildHouseUUIDsToRemove = uuids
	}

	func setStage5HasBuiltHouse(_ hasBuilt: Bool) {
		stage5HasBuiltHouse = hasBuilt
	}

	func setStage5LastBuildingPlaced(_ building: LastBuildingPlaced) {
		stage5LastBuildingPlaced = building
	}

	func setStage6LumberUUIDToRemove(_ uuid: UUID) {
		stage6LumberUUIDToRemove = uuid
	}

	func setStage6AxeUUIDToRemove(_ uuid: UUID) {
		stage6AxeUUIDToRemove = uuid
	}

	func setStage7ItemsToBuildInsideUUIDsToRemove(_ uuids: [UUID]) {
		stage7ItemsToBuildInsideUUIDsToRemove = uuids
	}

	func setStage7HasBuiltInside(_ hasBuilt: Bool) {
		stage7HasBuiltInside = hasBuilt
	}

	func setStage8_UUID(_ uuids: [UUID]) {
		stage8_UUID = uuids
	}

	func setStage1Stages(_ stage: BuilderStage1Stages) {
		stage1Stages = stage
	}

	func setStage2Stages(_ stage: BuilderStage2Stages) {
		stage2Stages = stage
	}

	func setStage3Stages(_ stage: BuilderStage3Stages) {
		stage3Stages = stage
	}

	func setStage4Stages(_ stage: BuilderStage4Stages) {
		stage4Stages = stage
	}

	func setStage5Stages(_ stage: BuilderStage5Stages) {
		stage5Stages = stage
	}

	func setStage6Stages(_ stage: BuilderStage6Stages) {
		stage6Stages = stage
	}

	func setStage7Stages(_ stage: BuilderStage7Stages) {
		stage7Stages = stage
	}

	func setStage8Stages(_ stage: BuilderStage8Stages) {
		stage8Stages = stage
	}

	func setStage9Stages(_ stage: BuilderStage9Stages) {
		stage9Stages = stage
	}

	func setStage10Stages(_ stage: BuilderStage10Stages) {
		stage10Stages = stage
	}

	struct LastBuildingPlaced: Codable {
		var x: Int
		var y: Int
	}
}
