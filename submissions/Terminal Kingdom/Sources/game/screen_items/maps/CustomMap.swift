import Foundation

struct CustomMap: Codable, Equatable {
	let id: UUID
	var grid: [[MapTile]]

	init?(id: UUID = UUID(), grid: [[MapTile]]) throws(CustomMapError) {
		self.id = id
		if grid.isEmpty {
			throw .emptyGrid
		}
		// must have a player start tile
		// if !grid.contains(where: {
		// 	!$0.contains(where: { tile in
		// 		tile.type == .playerStart
		// 	})
		// }) {
		// 	throw .noPlayerStartTile
		// }
		self.grid = grid
	}

	mutating func updateGrid(_ grid: [[MapTile]]) {
		self.grid = grid
	}
}

enum CustomMapError: Error {
	case emptyGrid
	case noPlayerStartTile
}
