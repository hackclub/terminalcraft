package Msg

import (
	"github.com/epiclabs-io/winman"
	"github.com/rivo/tview"
)

// MsgBox creates a new modal message box
func MsgBox(title, text string, buttons []string, callback func(clicked string)) *winman.WindowBase {

	msgBox := winman.NewWindow()
	message := tview.NewTextView().SetText(text).SetTextAlign(tview.AlignCenter)
	buttonBar := tview.NewFlex().
		SetDirection(tview.FlexColumn)

	content := tview.NewFlex().
		SetDirection(tview.FlexRow).
		AddItem(nil, 0, 1, false).
		AddItem(message, 0, 1, false).
		AddItem(buttonBar, 1, 0, true)

	msgBox.SetRoot(content)
	msgBox.SetTitle(title).
		SetRect(4, 2, 30, 6)
	msgBox.Draggable = true
	msgBox.Modal = true

	for _, buttonText := range buttons {
		button := func(buttonText string) *tview.Button {
			return tview.NewButton(buttonText).SetSelectedFunc(func() {
				msgBox.Hide()
				callback(buttonText)
			})
		}(buttonText)
		buttonBar.AddItem(button, 0, 1, true)
	}

	return msgBox
}

func Help() *winman.WindowBase {

	msgBox := winman.NewWindow()
	message := tview.NewTextView().SetText("H for Hex, T for Text, B for BIN, B64 for Base64, B32 for Base32. \n Enter in BIN like this format: \n  1001100 1101111 1110110 1100101 0100000 1011001 1001111 1010101").SetTextAlign(tview.AlignCenter)
	content := tview.NewFlex().
		SetDirection(tview.FlexRow).
		AddItem(message, 0, 1, false)
	msgBox.SetRoot(content)
	msgBox.SetTitle("Help").
		SetRect(4, 2, 60, 9)
	msgBox.Draggable = true
	msgBox.Modal = true

	return msgBox
}