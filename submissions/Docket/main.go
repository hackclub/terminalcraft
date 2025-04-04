package main

import (
	"strings"
	"time"

	"github.com/gdamore/tcell/v2"
	"github.com/rivo/tview"
)

func main() {
	app := tview.NewApplication()

	// Create the table for containers
	containerTable := tview.NewTable().
		SetBorders(true)

	// Set table headers for containers
	containerHeaders := []string{"ID", "Name", "Status"}
	for i, header := range containerHeaders {
		containerTable.SetCell(0, i, tview.NewTableCell(header).
			SetTextColor(tcell.ColorPurple).
			SetAlign(tview.AlignCenter).
			SetSelectable(false))
	}

	// Function to update the container table with current data
	updateContainerTable := func() {
		containers, err := ListContainers()
		if err != nil {
			panic(err)
		}
		for i := 1; i <= containerTable.GetRowCount(); i++ {
			containerTable.RemoveRow(i)
		}
		for i, container := range containers {
			containerTable.SetCell(i+1, 0, tview.NewTableCell(container["ID"]))
			containerTable.SetCell(i+1, 1, tview.NewTableCell(container["Name"]))
			containerTable.SetCell(i+1, 2, tview.NewTableCell(container["Status"]))
		}
	}

	// Create the table for images
	imageTable := tview.NewTable().
		SetBorders(true)

	// Set table headers for images
	imageHeaders := []string{"ID", "Repository", "Tag"}
	for i, header := range imageHeaders {
		imageTable.SetCell(0, i, tview.NewTableCell(header).
			SetTextColor(tcell.ColorPurple).
			SetAlign(tview.AlignCenter).
			SetSelectable(false))
	}

	updateImageTable := func() {
		images, err := ListImages()
		if (err != nil) {
			panic(err)
		}
		for i := 1; i <= imageTable.GetRowCount(); i++ {
			imageTable.RemoveRow(i)
		}
		for i, image := range images {
			imageTable.SetCell(i+1, 0, tview.NewTableCell(image["ID"]))
			imageTable.SetCell(i+1, 1, tview.NewTableCell(image["Repository"]))
			imageTable.SetCell(i+1, 2, tview.NewTableCell(image["Tag"]))
		}
	}

	// Create form for editing containers
	form := tview.NewForm().
		AddInputField("Name", "", 20, nil, nil).
		AddButton("Cancel", func() {
			app.SetFocus(containerTable)
		}).SetLabelColor(tcell.ColorPurple).SetButtonTextColor(tcell.ColorBlack).SetButtonActivatedStyle(tcell.StyleDefault.Foreground(tcell.ColorBlack).Background(tcell.ColorLightBlue).Underline(true))
	form.SetFieldStyle(tcell.StyleDefault.Foreground(tcell.ColorBlack).Background(tcell.ColorBlue))
	form.AddButton("Save", func() {
		row, _ := containerTable.GetSelection()
		oldName := containerTable.GetCell(row, 1).Text
		// get input value
		newName := form.GetFormItemByLabel("Name").(*tview.InputField).GetText()
		
		RenameContainer(oldName, newName)
		updateContainerTable()
		app.SetFocus(containerTable)
	})
	form.SetBorder(true).SetTitle("Edit Container").SetTitleAlign(tview.AlignLeft).SetTitleColor(tcell.ColorPurple)

	// Create form for creating containers from images
	createForm := tview.NewForm().
		AddInputField("Name", "", 20, nil, nil).
		AddInputField("Port to run on", "", 20, nil, nil).
		AddInputField("Port to expose", "", 20, nil, nil).
		AddButton("Cancel", func() {
			app.SetFocus(imageTable)
		}).SetLabelColor(tcell.ColorPurple).SetButtonTextColor(tcell.ColorBlack).SetButtonActivatedStyle(tcell.StyleDefault.Foreground(tcell.ColorBlack).Background(tcell.ColorLightBlue).Underline(true))
	createForm.SetFieldStyle(tcell.StyleDefault.Foreground(tcell.ColorBlack).Background(tcell.ColorBlue))
	createForm.AddButton("Create", func() {
		row, _ := imageTable.GetSelection()
		image := imageTable.GetCell(row, 1).Text
		name := createForm.GetFormItemByLabel("Name").(*tview.InputField).GetText()
		hostPort := createForm.GetFormItemByLabel("Port to run on").(*tview.InputField).GetText()
		containerPort := createForm.GetFormItemByLabel("Port to expose").(*tview.InputField).GetText()
		CreateContainerFromImage(image, name, hostPort, containerPort)
		updateContainerTable()
		app.SetFocus(imageTable)
	})
	createForm.SetBorder(true).SetTitle("Create Container").SetTitleAlign(tview.AlignLeft).SetTitleColor(tcell.ColorPurple)

	instructions := tview.NewTextView().
		SetText("Press 'd' to delete, 'r' to run, 's' to stop, 'e' to edit, the arrow keys to switch tabs").
		SetTextColor(tcell.ColorPurple).
		SetTextAlign(tview.AlignCenter)

	// Create flex layout for containers
	containerFlex := tview.NewFlex().
		SetDirection(tview.FlexRow).
		AddItem(
			tview.NewFlex().
				AddItem(containerTable, 0, 1, true).
				AddItem(form, 0, 1, false),
			0, 1, true).
		AddItem(instructions, 1, 1, false)

	containerTable.SetSelectable(true, false).SetSelectedFunc(func(row, column int) {
		if row == 0 {
			return // Ignore header row
		}
		app.SetFocus(containerTable)
	})

	containerTable.SetSelectedStyle(tcell.StyleDefault.
		Background(tcell.ColorBlue).
		Foreground(tcell.ColorBlack))

	containerTable.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		row, _ := containerTable.GetSelection()
		if row == 0 {
			return event // Ignore header row
		}
		containerID := containerTable.GetCell(row, 0).Text

		switch event.Rune() {
		case 'd':
			DeleteContainer(containerID)
			updateContainerTable()
		case 'r':
			RunContainer(containerID)
			updateContainerTable()
		case 's':
			StopContainer(containerID)
			updateContainerTable()
		case 'e':
			name := containerTable.GetCell(row, 1).Text
			form.GetFormItemByLabel("Name").(*tview.InputField).SetText(name)
			app.SetFocus(form)
		}
		return event
	})

	// Create flex layout for images
	imageFlex := tview.NewFlex().
		SetDirection(tview.FlexRow).
		AddItem(
			tview.NewFlex().
				AddItem(imageTable, 0, 1, true).
				AddItem(createForm, 0, 1, false),
			0, 1, true).
		AddItem(instructions, 1, 1, false)

	imageTable.SetSelectable(true, false).SetSelectedFunc(func(row, column int) {
		if row == 0 {
			return // Ignore header row
		}
		app.SetFocus(imageTable)
	})

	imageTable.SetSelectedStyle(tcell.StyleDefault.
		Background(tcell.ColorBlue).
		Foreground(tcell.ColorBlack))

	imageTable.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		row, _ := imageTable.GetSelection()
		if row == 0 {
			return event // Ignore header row
		}
		imageID := imageTable.GetCell(row, 0).Text

		switch event.Rune() {
		case 'd':
			DeleteImage(imageID)
			updateImageTable()
		case 'c':
			repoStringlist := strings.Split(imageTable.GetCell(row, 1).Text, "/")
			repo := repoStringlist[len(repoStringlist)-1]

			createForm.GetFormItemByLabel("Name").(*tview.InputField).SetText(repo)
			app.SetFocus(createForm)
		}
		return event
	})

	// Create pages to switch between containers and images
	pages := tview.NewPages().
		AddPage("Containers", containerFlex, true, true).
		AddPage("Images", imageFlex, true, false)

	// Create tab bar
	tabBar := tview.NewTextView().
		SetDynamicColors(true).
		SetRegions(true).
		SetWrap(false)

	updateTabBar := func(activePage string) {
		if activePage == "Containers" {
			tabBar.SetText("[blue]Containers[white] | [white]Images")
			instructions.SetText("Press 'd' to delete, 'r' to run, 's' to stop, 'e' to edit, the arrow keys to switch tabs")
		} else {
			tabBar.SetText("[white]Containers | [blue]Images[white]")
			instructions.SetText("Press 'd' to delete, 'c' to create container, the arrow keys to switch tabs")
		}
	}
	updateTabBar("Containers")

	// Create main layout
	mainFlex := tview.NewFlex().
		SetDirection(tview.FlexRow).
		AddItem(tabBar, 1, 1, false).
		AddItem(pages, 0, 1, true)

	app.SetRoot(mainFlex, true).
		SetBeforeDrawFunc(func(screen tcell.Screen) bool {
			screen.Clear() // Ensures transparent effect
			screen.SetStyle(tcell.StyleDefault.
				Foreground(tcell.ColorWhite). // Text color
				Background(tcell.ColorBlack)) // Transparent bg
			return false
		})

	go func() {
		for {
			time.Sleep(2 * time.Second)
			app.QueueUpdateDraw(updateContainerTable)
			app.QueueUpdateDraw(updateImageTable)
		}
	}()
	app.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
		if event.Modifiers()&tcell.ModCtrl != 0 {
			switch event.Key() {
			case tcell.KeyLeft: // Ctrl + Left arrow switches to Containers
				pages.SwitchToPage("Containers")
				updateTabBar("Containers")
			case tcell.KeyRight: // Ctrl + Right arrow switches to Images
				pages.SwitchToPage("Images")
				updateTabBar("Images")
			}
		}
		return event
	})

	if err := app.Run(); err != nil {
		panic(err)
	}
}
