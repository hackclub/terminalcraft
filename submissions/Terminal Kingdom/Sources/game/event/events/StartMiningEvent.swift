enum StartMiningEvent {
	static func startMining() async {
		await MapBox.setMapType(.mining)
	}
}
