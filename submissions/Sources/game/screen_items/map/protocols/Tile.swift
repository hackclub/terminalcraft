protocol Tile: Equatable, Hashable, Codable {
	associatedtype pTileType: TileType
	associatedtype pTileEvent: TileEvent

	var type: pTileType { get }
	var isWalkable: Bool { get }
	var event: pTileEvent? { get }
}
