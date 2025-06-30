package main

import (
	"go/Crypto-Hacks/BIN"
	"go/Crypto-Hacks/Base"
	"go/Crypto-Hacks/Hex"
	"fmt"
	"go/Crypto-Hacks/msg"
	"github.com/epiclabs-io/winman"
	"github.com/rivo/tview"
)


func main() {
var app *tview.Application = tview.NewApplication()
	var wm *winman.Manager= winman.NewWindowManager()

	var quitMsgBox *winman.WindowBase= Msg.MsgBox("Confirmation", "Really quit?", []string{"Yes", "No"}, func(clicked string) {
		if clicked == "Yes" {
			app.Stop()
		}
	})
	wm.AddWindow(quitMsgBox)
	var help *winman.WindowBase= Msg.Help()
	wm.AddWindow(help)

	setFocus := func(p tview.Primitive) {
		go app.QueueUpdateDraw(func() {
			app.SetFocus(p)
		})
	}

	var createForm func(modal bool) *winman.WindowBase
	var counter int = 0

	createForm = func(modal bool) *winman.WindowBase {
		counter++
		var form *tview.Form= tview.NewForm()
		var form1 *tview.Form= tview.NewForm()
		var form2 *tview.Form= tview.NewForm()
		var All *tview.Grid= tview.NewGrid().
		SetSize(10,4,0,0)
		
		var window *winman.WindowBase= winman.NewWindow().
			SetRoot(All).
			SetResizable(false).
			SetDraggable(true).
			SetModal(modal)

		var quit func()= func() {
			if wm.WindowCount() == 3 {
				quitMsgBox.Show()
				wm.Center(quitMsgBox)
				setFocus(quitMsgBox)
			} else {
				wm.RemoveWindow(window)
				setFocus(wm)
			}
		}
				var hhelp func()= func() {
	
				wm.RemoveWindow(help)
				setFocus(wm)
			
		}

		var display *tview.TextView = tview.NewTextView().
		SetText("Output Here:").
		SetTextAlign(tview.AlignLeft)
		
			All.AddItem(form.AddInputField("Enter Here", "", 40, nil, nil).
			AddFormItem(display).
			AddButton("T 2 H", func() {
				var out string = Hex.Normal2Hex(form.GetFormItem(0).(*tview.InputField).GetText())
				display.SetText(fmt.Sprintf( "Output Here:" + out))
			}).
			AddButton("T 2 B", func() {
				var out string= BIN.Normal2BIN(form.GetFormItem(0).(*tview.InputField).GetText())
						display.SetText(fmt.Sprintf( "Output Here:" + out))
			}).
			AddButton("T 2 B64", func() {
				var out string= Base.Normal2base64(form.GetFormItem(0).(*tview.InputField).GetText())
						display.SetText(fmt.Sprintf( "Output Here:" + out))
			}).
			AddButton("T 2 B32", func() {
				var out string = Base.Normal2base32(form.GetFormItem(0).(*tview.InputField).GetText())
						display.SetText(fmt.Sprintf( "Output Here:" + out))
			}), 0,0,5,4,0,0,false)


			All.AddItem(form1.
			AddButton("New", func() {
			newWnd  := createForm(false).Show()
				wm.AddWindow(newWnd)
				setFocus(newWnd)
			}).
			AddButton("Close", quit).
			SetHorizontal(false), 6,0,1,4,0,0, false)
			All.AddItem(form2.AddButton("H 2 T", func() {
				var out string= Hex.Hex2Normal(form.GetFormItem(0).(*tview.InputField).GetText())
				display.SetText(fmt.Sprintf( "Output Here:" + out))
			}).
			AddButton("B 2 T", func() {
				var out string= BIN.BIN2Normal(form.GetFormItem(0).(*tview.InputField).GetText())
						display.SetText(fmt.Sprintf( "Output Here:" + out))
			}).
			AddButton("B64 2 T", func() {
				var out string= Base.Base642Normal(form.GetFormItem(0).(*tview.InputField).GetText())
						display.SetText(fmt.Sprintf( "Output Here:" + out))
			}).
			AddButton("B32 2 T", func() {
				var out string = Base.Base322Normal(form.GetFormItem(0).(*tview.InputField).GetText())
						display.SetText(fmt.Sprintf( "Output Here:" + out))
			}), 8,0,1,4,0,0,true)
			

		var title string= fmt.Sprintf("Crypto-Hacks%d", counter)
		window.SetBorder(true).SetTitle(title).SetTitleAlign(tview.AlignCenter)
		window.SetRect(2+counter*2, 2+counter, 50, 30)
		window.AddButton(&winman.Button{
			Symbol:    'X',
			Alignment: winman.ButtonLeft,
			OnClick:   quit,
		})

		var maxMinButton *winman.Button
		maxMinButton = &winman.Button{
			Symbol:    '▴',
			Alignment: winman.ButtonRight,
			OnClick: func() {
				if window.IsMaximized() {
					window.Restore()
					maxMinButton.Symbol = '▴'
				} else {
					window.Maximize()
					maxMinButton.Symbol = '▾'
				}
			},
		}
		window.AddButton(maxMinButton)
		window.AddButton(&winman.Button{
			Symbol: '?',
			OnClick: func ()  {
				help.Show()
				help.AddButton(&winman.Button{
					Symbol: 'X',
					OnClick: hhelp,
				})
			},


		})
		wm.AddWindow(window)
		return window
	}

	for i := 0; i < 1; i++ {
		createForm(false).Show()
	}

	if err := app.SetRoot(wm, true).EnableMouse(true).Run(); err != nil {
		panic(err)
	}

}
