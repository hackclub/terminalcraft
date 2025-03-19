extension Sequence {
	func asyncMap<T, E>(_ transform: (Element) async throws(E) -> T) async throws(E) -> [T] where E: Error {
		var values = [T]()

		for element in self {
			try await values.append(transform(element))
		}

		return values
	}

	func asyncForEach<E>(_ operation: (Element) async throws(E) -> Void) async throws(E) where E: Error {
		for element in self {
			try await operation(element)
		}
	}
}
