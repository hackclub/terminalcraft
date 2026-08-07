package ui

import "github.com/rivo/tview"

func TviewConfigInit()  {	
	tview.Borders.Horizontal = '─'
	tview.Borders.Vertical = '│'
	tview.Borders.TopLeft = '╭'
	tview.Borders.TopRight = '╮'
	tview.Borders.BottomLeft = '╰'
	tview.Borders.BottomRight = '╯'

	tview.Borders.BottomRightFocus = '┛'
	tview.Borders.BottomLeftFocus = '┗'
	tview.Borders.TopRightFocus = '┓'
	tview.Borders.TopLeftFocus = '┏'
	tview.Borders.HorizontalFocus = '━'
	tview.Borders.VerticalFocus = '┃'
}
