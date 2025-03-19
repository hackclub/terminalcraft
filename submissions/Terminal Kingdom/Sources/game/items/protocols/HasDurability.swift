import Foundation

protocol HasDurability {
	var durability: Int { get }
	mutating func removeDurability(count: Int)
}
