package ui

import (
	"fmt"
	"rinogodson/DreamShell/filehandler"
	"strings"
	"time"

	"github.com/gdamore/tcell/v2"
	"github.com/rivo/tview"
)

type AppState struct {
	selectedPane int
}

func NewUI() {
	themeColor := tcell.Color147
	app := tview.NewApplication()
	state := &AppState{}
	state.selectedPane = 0

	titleArea := tview.NewTextArea().SetPlaceholder("Dream Title...")
	titleArea.SetTitle("[#AFAFFF]─╮ [#FFFFD7]✦[#AFAFFF] Title [#FFFFD7]✦[#AFAFFF] ╭──").SetBorder(true)
	titleArea.SetBorderColor(themeColor)
	titleArea.SetTitleColor(themeColor)
	titleArea.SetBorderPadding(0, 0, 1, 1)
	titleArea.SetTextStyle(tcell.StyleDefault.Foreground(tcell.Color230).Bold(true))
	titleArea.SetTitleAlign(tview.AlignRight)
	titleArea.SetPlaceholderStyle(tcell.StyleDefault.Foreground(tcell.ColorSilver))

	bodyArea := tview.NewTextArea().SetPlaceholder("I dreamed about...")
	bodyArea.SetTitle("[#AFAFFF]─╮ [#FFFFD7]✦[#AFAFFF] Body [#FFFFD7]✦[#AFAFFF] ╭──").SetBorder(true)
	bodyArea.SetBorderColor(themeColor)
	bodyArea.SetTitleColor(themeColor)
	bodyArea.SetBorderPadding(0, 0, 1, 1)
	bodyArea.SetTextStyle(tcell.StyleDefault.Foreground(tcell.Color230))
	bodyArea.SetTitleAlign(tview.AlignRight)
	bodyArea.SetPlaceholderStyle(tcell.StyleDefault.Foreground(tcell.ColorSilver))

	tagArea := tview.NewTextArea().SetPlaceholder("#lucid if it was lucid. tags format : '#tag1 #tag2 ...'")
	tagArea.SetTitle("[#AFAFFF]─╮ [#FFFFD7]✦[#AFAFFF] Tags (optional) [#FFFFD7]✦[#AFAFFF] ╭──").SetBorder(true)
	tagArea.SetTitleAlign(tview.AlignRight)
	tagArea.SetBorderColor(themeColor)
	tagArea.SetTitleColor(themeColor)
	tagArea.SetBorderPadding(0, 0, 1, 1)
	tagArea.SetTextStyle(tcell.StyleDefault.Foreground(tcell.Color193))
	tagArea.SetPlaceholderStyle(tcell.StyleDefault.Foreground(tcell.ColorSilver))

	helpArea := tview.NewTextView()
	helpArea.SetText("╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍ TAB for help ")
	helpArea.SetTextStyle(tcell.StyleDefault.Foreground(tcell.ColorSilver).Bold(true))
	helpArea.SetTextAlign(tview.AlignRight)

	titleArea.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		if event.Key() == tcell.KeyCtrlN {
			app.SetFocus(bodyArea)
		} else if event.Key() == tcell.KeyCtrlB {
			app.SetFocus(tagArea)
		}
		return event
	})

	bodyArea.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		if event.Key() == tcell.KeyCtrlN {
			app.SetFocus(tagArea)
		} else if event.Key() == tcell.KeyCtrlB {
			app.SetFocus(titleArea)
		}
		return event
	})

	tagArea.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		if event.Key() == tcell.KeyCtrlN {
			app.SetFocus(titleArea)
		} else if event.Key() == tcell.KeyCtrlB {
			app.SetFocus(bodyArea)
		}
		return event
	})

	mainView := tview.NewGrid().SetRows(3, 0, 3, 1).SetColumns(0)
	mainView.AddItem(titleArea, 0, 0, 1, 1, 0, 0, (state.selectedPane == 0))
	mainView.AddItem(bodyArea, 1, 0, 1, 1, 0, 0, (state.selectedPane == 1))
	mainView.AddItem(tagArea, 2, 0, 1, 1, 0, 0, (state.selectedPane == 2))
	mainView.AddItem(helpArea, 3, 0, 1, 1, 0, 0, false)
	mainView.SetTitle("[#D787FF]╯✨[#FFD8FF] DreamShell ✨[#D787FF]╰").SetBorder(true)
	mainView.SetBorderColor(tcell.Color177)
	mainView.SetTitleColor(tcell.Color225)
	mainView.SetBorderPadding(1, 0, 3, 3)

	modal := func(p tview.Primitive, width, height int) tview.Primitive {
		return tview.NewFlex().
			AddItem(nil, 0, 1, false).
			AddItem(tview.NewFlex().SetDirection(tview.FlexRow).
				AddItem(nil, 0, 1, false).
				AddItem(p, height, 1, true).
				AddItem(nil, 0, 1, false), width, 1, true).
			AddItem(nil, 0, 1, false)
	}

	help := tview.NewTextView()
	help.SetText("Ctrl + i for help\nCtrl + w to log the dream\nCtrl + n for next pane\nCtrl + b for previous pane\nCtrl + x to exit\n\nTags Syntax:\n  #tag1 #tag2 ... #tagn\n\n  add #lucid if it was lucid").SetBorder(true)
	help.SetTextStyle(tcell.StyleDefault.Foreground(tcell.ColorSilver).Bold(true))
	help.SetTextAlign(tview.AlignLeft)
	help.SetBorderPadding(1, 0, 2, 2)
	help.SetTitle("[#FFFFFF]─╮ [#FFFFD7]✦[#AFAFFF] Help [#FFFFD7]✦[#FFFFFF] ╭──")

	helpLever := false
	container := tview.NewPages()
	container.AddPage("main", modal(mainView, 70, 35), true, true)
	container.AddPage("modal", modal(help, 40, 14), true, true)
	container.HidePage("modal")
	container.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		if event.Key() == tcell.KeyCtrlX {
			app.Stop()
		} else if event.Key() == tcell.KeyCtrlG {
			state.selectedPane = (state.selectedPane + 1) % 3
		} else if event.Key() == tcell.KeyCtrlW {
			if !filehandler.TagValidator(tagArea.GetText()) {
				tagArea.SetTitle("[#AFAFFF]─╮ [#FFFFD7]✦[#FF0000] Tags: Format Error [#FFFFD7]✦[#AFAFFF] ╭──")
				tagArea.SetTitleColor(tcell.ColorRed)
			} else {
				tags := filehandler.ExtractTags(tagArea.GetText())
				filehandler.CreateFile(titleArea.GetText()+"~"+time.Now().String(), "# "+titleArea.GetText()+"\n"+bodyArea.GetText()+"\n"+strings.Join(tags, " "))
				app.Stop()
				fmt.Println("Dream Logged Successfully: " + titleArea.GetText())
				fmt.Println("on " + time.Now().String())
			}
		} else if event.Key() == tcell.KeyCtrlI {
			helpLever = !helpLever
			if helpLever {
				container.ShowPage("modal")
			} else {
				container.HidePage("modal")
			}
			if len(titleArea.GetText()) != 0 {
				if titleArea.GetText()[len(titleArea.GetText())-1] == '\t' {
					titleArea.SetText(titleArea.GetText()[:len(titleArea.GetText())-1], true)
				}
			}
		}
		return event
	})

	if err := app.SetRoot(container,
		true).EnableMouse(true).Run(); err != nil {
		panic(err)
	}
}
