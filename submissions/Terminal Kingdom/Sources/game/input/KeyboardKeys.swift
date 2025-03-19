enum KeyboardKeys: String {
	case up
	case down
	case right
	case left
	case unknown
	case a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z
	case A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z
	case space = " "
	case backspace
	case enter
	case one = "1"
	case two = "2"
	case three = "3"
	case four = "4"
	case five = "5"
	case six = "6"
	case seven = "7"
	case eight = "8"
	case nine = "9"
	case zero = "0"
	case questionMark = "?"
	case forward_slash = "/"
	case esc
	case tab
	case back_tab

	var isLetter: Bool {
		switch self {
			case .a, .b, .c, .d, .e, .f, .g, .h, .i, .j, .k, .l, .m, .n, .o, .p, .q, .r, .s, .t, .u, .v, .w, .x, .y, .z: true
			case .A, .B, .C, .D, .E, .F, .G, .H, .I, .J, .K, .L, .M, .N, .O, .P, .Q, .R, .S, .T, .U, .V, .W, .X, .Y, .Z: true
			default: false
		}
	}

	var isNumber: Bool {
		switch self {
			case .one, .two, .three, .four, .five, .six, .seven, .eight, .nine, .zero: true
			default: false
		}
	}

	var render: String {
		if self == .space {
			return "space".styled(with: .bold)
		}
		return rawValue.styled(with: .bold)
	}
}
