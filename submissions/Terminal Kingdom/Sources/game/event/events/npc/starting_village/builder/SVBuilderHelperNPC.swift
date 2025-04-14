enum SVBuilderHelperNPC: StartingVillageNPC {
	static func talk() async {
		await MessageBox.message("I'm busy here...", speaker: .builder_helper)
	}
}
