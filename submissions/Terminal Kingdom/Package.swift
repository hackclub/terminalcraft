// swift-tools-version: 6.0
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
	name: "TerminalKingdom",
	platforms: [
		.macOS(.v15),
	],
	dependencies: [
		.package(url: "https://github.com/tayloraswift/swift-noise", from: "1.1.0"),
	],
	targets: [
		// Targets are the basic building blocks of a package, defining a module or a test suite.
		// Targets can depend on other targets in this package and products from dependencies.
		.executableTarget(
			name: "TerminalKingdom",
			dependencies: [.product(name: "Noise", package: "swift-noise")],
			resources: [
				.process("Resources/"),
			]
		),
	]
)
