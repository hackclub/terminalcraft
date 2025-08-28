package ui

import (
	"os"
	"path/filepath"
	"rinogodson/DreamShell/filehandler"

	"github.com/gdamore/tcell/v2"
	"github.com/rivo/tview"
)

func ListUI() {
	app := tview.NewApplication()

	list := tview.NewList()
	list.SetBorder(true)
	list.SetTitleColor(tcell.Color225)
	list.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		if event.Key() == tcell.KeyCtrlJ {
			list.SetCurrentItem(list.GetCurrentItem() + 1)
		} else if event.Key() == tcell.KeyCtrlK {
			list.SetCurrentItem(list.GetCurrentItem() - 1)
		}
		return event
	})

	dreams := filehandler.GetFiles()

	for _, dream := range dreams {
		item := filehandler.ParseInput(dream.Name())
		list.AddItem(item[0], item[1], 0, nil)
	}

	listBox := tview.NewFlex()
	listBox.SetTitle("[#D787FF]╯✨[#FFD8FF] DreamShell (list) ✨[#D787FF]╰").SetBorder(true)
	listBox.SetBorderColor(tcell.Color177)
	listBox.SetTitleColor(tcell.Color225)
	listBox.SetBorderPadding(1, 1, 3, 3)
	listBox.AddItem(list, 0, 1, true)

	previewBox := tview.NewFlex()
	previewBox.SetBorder(true)
	previewBox.SetBorderColor(tcell.Color177)
	previewBox.SetTitleColor(tcell.Color225)
	previewBox.SetDirection(tview.FlexRow)

	pTitle := tview.NewTextView().SetTextAlign(tview.AlignCenter).SetTextColor(tcell.Color225)
	pDesc := tview.NewTextView()
	pDesc.SetBorderPadding(1,1,3,3)
	pDate := tview.NewTextView().SetTextAlign(tview.AlignCenter)
	ptags := tview.NewTextView().SetTextAlign(tview.AlignCenter).SetTextColor(tcell.Color225)
	phelp := tview.NewTextView().SetText("ESC TO CLOSE").SetTextAlign(tview.AlignRight).SetTextColor(tcell.ColorGray)
	previewBox.AddItem(pTitle, 1, 1, false)
	previewBox.AddItem(pDesc, 0, 1, true)
	previewBox.AddItem(pDate, 1, 1, false)
	previewBox.AddItem(ptags, 1, 1, false)
	previewBox.AddItem(phelp, 1, 1, false)

	modal := func(p tview.Primitive, width, height int) tview.Primitive {
		return tview.NewFlex().
			AddItem(nil, 0, 1, false).
			AddItem(tview.NewFlex().SetDirection(tview.FlexRow).
				AddItem(nil, 0, 1, false).
				AddItem(p, height, 1, true).
				AddItem(nil, 0, 1, false), width, 1, true).
			AddItem(nil, 0, 1, false)
	}

	container := tview.NewPages()
	container.AddPage("main", modal(listBox, 70, 35), true, true)
	container.AddPage("preview", modal(previewBox, 66, 33), true, true)
	container.HidePage("preview")

	list.SetSelectedFunc(func(index int, primaryText string, secondaryText string, _ rune) {
		container.ShowPage("preview")
		home, err := os.UserHomeDir()
		if err != nil {
			panic(err)
		}
		text := filehandler.GetContent(filepath.Join(home, ".dreamshell", "dreams", dreams[index].Name()))
		textContent := filehandler.ParseDream(text)
		pTitle.SetText(textContent[0])
		pDesc.SetText(textContent[1])
		ptags.SetText(textContent[2])
		pDate.SetText(secondaryText)
	})

	previewBox.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		if event.Key() == tcell.KeyEscape {
			container.HidePage("preview")
		}
		return event
	})

	if err := app.SetRoot(container,
		true).EnableMouse(true).Run(); err != nil {
		panic(err)
	}
}
