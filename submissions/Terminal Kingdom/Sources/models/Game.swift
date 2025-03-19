import Foundation

actor Game {
	static var shared = Game()
	nonisolated static let version = "0.0.1-alpha_3"
	var config: Config = .init()
	var player = PlayerCharacter()
	var startingVillageChecks: StartingVillageChecks = .init()
	var stages: Stages = .init()
	var mapGen: MapGen = .init()
	var maps: Maps = .init()
	private(set) var kingdoms: [Kingdom] = []
	private(set) var messages: [String] = []
	private(set) var crops: Set<TilePosition> = []
	private(set) var movingNpcs: Set<NPCPosition> = [] {
		didSet {} // TODO: for some reason this is fixing where the NPCs are not moving
	}

	private(set) var hasInited: Bool = false
	private(set) var isTypingInMessageBox: Bool = false
	private(set) var map: [[MapTile]] = []
	private(set) var resitrictBuilding: (Bool, TilePosition) = (false, TilePosition(x: 0, y: 0, mapType: .mainMap))
	// Don't save
	private(set) var isInInventoryBox: Bool = false
	private(set) var isBuilding: Bool = false
	var horizontalLine: String { config.useNerdFont ? "─" : "=" }
	var verticalLine: String { config.useNerdFont ? "│" : "|" }
	private(set) var hasStartedCropQueue: Bool = false
	private(set) var hasStartedNPCQueue: Bool = false

	//     private(set) var map = MapGen.generateFullMap()

	private init() {}

	func initGame() async {
		hasInited = true
		map = await mapGen.generateFullMap()
		config = await Config.load()
	}

	func setIsTypingInMessageBox(_ newIsTypingInMessageBox: Bool) async {
		isTypingInMessageBox = newIsTypingInMessageBox
	}

	// func reloadGame(decodedGame: CodableGame) async {
	// 	hasInited = decodedGame.hasInited
	// 	isTypingInMessageBox = decodedGame.isTypingInMessageBox
	// 	// player = decodedGame.player
	// 	map = decodedGame.map
	// 	startingVillageChecks = decodedGame.startingVillageChecks
	// 	stages = decodedGame.stages
	// 	messages = decodedGame.messages
	// 	mapGen = decodedGame.mapGen
	// }

	func addMessage(_ message: String) async {
		messages.append(message)
	}

	func removeMessage(at index: Int) async {
		messages.remove(at: index)
	}

	func addCrop(_ position: TilePosition) async {
		// TODO: cancel the crop queue if crops is empty and remove a crop position if it is fully grown
		crops.insert(position)
		BackgroundTasks.startCropQueue()
	}

	func removeCrop(_ position: TilePosition) async {
		crops.remove(position)
	}

	func addNPC(_ position: NPCPosition) async {
		// TODO: cancel the crop queue if crops is empty and remove a crop position if it is fully grown
		movingNpcs.insert(position)
		BackgroundTasks.startNPCMovingQueue()
	}

	func updateNPC(oldPosition: NPCPosition, newPosition: NPCPosition) async {
		movingNpcs.remove(oldPosition)
		await addNPC(newPosition)
	}

	func removeNPC(_ position: NPCPosition) async {
		movingNpcs.remove(position)
	}

	func setHasStartedNPCMovingQueue(_ newHasStartedNPCMovingQueue: Bool) async {
		hasStartedNPCQueue = newHasStartedNPCMovingQueue
	}

	func setHasStartedCropQueue(_ newHasStartedCropQueue: Bool) async {
		hasStartedCropQueue = newHasStartedCropQueue
	}

	func setIsInInventoryBox(_ newIsInInventoryBox: Bool) async {
		isInInventoryBox = newIsInInventoryBox
	}

	func setIsBuilding(_ newIsBuilding: Bool) async {
		isBuilding = newIsBuilding
	}

	func addMap(map: CustomMap) async {
		await maps.addMap(map: map)
	}

	func removeMap(map: CustomMap) async {
		await maps.removeMap(map: map)
	}

	func removeMap(mapID: UUID) async {
		await maps.removeMap(mapID: mapID)
	}

	@discardableResult
	func messagesRemoveLast() async -> String {
		messages.removeLast()
	}

	func setHasBeenTaughtToChopLumber(_ newHasBeenTaughtToChopLumber: StartingVillageChecksStages) async {
		await startingVillageChecks.setHasBeenTaughtToChopLumber(newHasBeenTaughtToChopLumber)
	}

	func setHasUsedMessageWithOptions(_ newHasUsedMessageWithOptions: Bool) async {
		await startingVillageChecks.setHasUsedMessageWithOptions(newHasUsedMessageWithOptions)
	}

	func loadConfig() async {
		config = await Config.load()
	}

	func getBiome(x: Int, y: Int) async -> BiomeType {
		await mapGen.getBiome(x: x, y: y)
	}

	func getBiomeAtPlayerPosition() async -> BiomeType {
		await mapGen.getBiomeAtPlayerPosition()
	}

	func createKingdom(_ kingdom: Kingdom) async {
		kingdoms.append(kingdom)
	}

	func removeKingdom(_ kingdom: Kingdom) async {
		kingdoms.removeAll(where: { $0.id == kingdom.id })
	}

	func removeKingdom(id: UUID) async {
		kingdoms.removeAll(where: { $0.id == id })
	}

	func addKingdomBuilding(_ building: Building, kingdomID: UUID) async {
		guard let index = kingdoms.firstIndex(where: { $0.id == kingdomID }) else { return }
		kingdoms[index].buildings.append(building)
	}

	func addKingdomNPC(_ uuid: UUID, kingdomID: UUID) async {
		guard let index = kingdoms.firstIndex(where: { $0.id == kingdomID }) else { return }
		kingdoms[index].npcsInKindom.append(uuid)
	}

	func addKingdomData(_ data: KingdomData, npcInKindom: UUID) async {
		guard let index = kingdoms.firstIndex(where: { $0.npcsInKindom.contains(npcInKindom) }) else { return }
		kingdoms[index].data.append(data)
	}

	func removeKingdomData(_ data: KingdomData, npcInKindom: UUID) async {
		guard let index = kingdoms.firstIndex(where: { $0.npcsInKindom.contains(npcInKindom) }) else { return }
		return kingdoms[index].data.removeAll(where: { $0 == data })
	}

	func setKingdomCastle(kingdomID: UUID) async {
		guard let index = kingdoms.firstIndex(where: { $0.id == kingdomID }) else { return }
		return kingdoms[index].setHasCastle()
	}

	func removeKingdomCastle(kingdomID: UUID) async {
		guard let index = kingdoms.firstIndex(where: { $0.id == kingdomID }) else { return }
		kingdoms[index].removeCastle()
	}

	func getKingdomCastle(kingdomID: UUID) async -> Building? {
		kingdoms.first(where: { $0.id == kingdomID })?.getCastle()
	}

	func isInsideKingdom(x: Int, y: Int) async -> UUID? {
		for kingdom in kingdoms where kingdom.contains(x: x, y: y) {
			return kingdom.id
		}
		return nil
	}

	func getKingdom(id: UUID) async -> Kingdom? {
		kingdoms.first { $0.id == id }
	}

	func getKingdomBuilding(for npc: NPC, kingdomID: UUID) async -> Building? {
		kingdoms.first(where: { $0.id == kingdomID })?.buildings.first { $0.id == npc.id }
	}

	func getKingdomBuilding(for npc: NPC) async -> Building? {
		kingdoms.first(where: { $0.npcsInKindom.contains(npc.id) })?.buildings.first { $0.id == npc.id }
	}

	func hasKingdomBuilding(x: Int, y: Int) async -> Building? {
		kingdoms.lazy.flatMap(\.buildings).first { $0.x == x && $0.y == y }
	}

	func updateKingdomBuilding(kingdomID: UUID, buildingID: UUID, newBuilding: Building) async {
		guard let index = kingdoms.firstIndex(where: { $0.id == kingdomID }) else { return }
		guard let buildingIndex = kingdoms[index].buildings.firstIndex(where: { $0.id == buildingID }) else { return }
		kingdoms[index].buildings[buildingIndex] = newBuilding
	}

	func getKingdom(buildingID: UUID) async -> Kingdom? {
		kingdoms.first { $0.buildings.contains { $0.id == buildingID } }
	}

	func getKingdom(for npc: NPC) async -> Kingdom? {
		kingdoms.first { $0.npcsInKindom.contains(npc.id) }
	}

	func renameKingdom(id: UUID, name: String) async {
		guard let index = kingdoms.firstIndex(where: { $0.id == id }) else { return }
		kingdoms[index].name = name
	}

	func setRestrictBuilding(_ newResitrictBuilding: (Bool, TilePosition)) async {
		resitrictBuilding = newResitrictBuilding
	}
}

// TODO: update because Game is not codable
// struct CodableGame: Codable {
// 	var hasInited: Bool
// 	var isTypingInMessageBox: Bool
// 	var player: PlayerCharacterCodable
// 	var map: [[MapTile]]
// 	var startingVillageChecks: StartingVillageChecks
// 	var stages: Stages
// 	var messages: [String]
// 	var mapGen: MapGenSave
// }

struct TilePosition: Codable, Hashable {
	var x: Int
	var y: Int
	var mapType: MapType
}

struct NPCPosition: Codable, Hashable {
	var x: Int
	var y: Int
	var mapType: MapType
	var oldTile: MapTile
}
