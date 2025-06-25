import pandas as pd
import os
from textual.app import App, ComposeResult
from textual.widgets import Header, Button, Input, Static, Footer, Select
from textual.containers import Vertical, Horizontal

class Data_Anlyzer(App):
    CSS_PATH="style.css"
    def __init__(self):
        super().__init__()
        self.df = None
        self.file_ext = None
        self.file_path = None
        self.selected_column = None
        self.selected_row = None
        self.new_value = None
        self.colsort=None

    def compose(self)-> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Please insert your file's path:", id="qs1"),
            Input(placeholder="e.g. data.csv", id="file_path"),
            Static(id="status"),
            Static(id="menu_label")
        )
        yield Static(".", id="Sortchoice")
        yield Static("output", id="output")
        yield Static(".",id="again")
        yield Horizontal(
                Button("1. Print the whole data", id="whole"),
                Button("2. Describe", id="describe"),
                Button("3. Sort Data", id="sort"),
                id="qs1_1"
            )
        yield Horizontal(
            Button("4. Check null", id="nullcheck"),
            Button("Search for a value", id="search"),
            Button("6. Save data",id="save"),
            id="qs1_2"
        )
        yield Button("Edit Data", id="edit")
        yield Horizontal(
            Button("Ascending", id="ascend"), Button("Descending", id="descend"), id="sorting"
        )
        yield Horizontal(
            Button("Fill",id="fill"), Button("Revome", id="remove"), id="null"
        )
        yield Vertical(
            Static("Enter search value", id="inputqs"),
            Input(placeholder="eg.270, Ahmed", id="input"), Button("Submit Search", id="submit_search"),id="searchinput"
        )
        yield Vertical(
            Static("columnname", id="df"),
            Static("Enter the column name", id="columnname"),
            Input(placeholder="Items", id="inputcolumn"), 
            Button("Submit column", id="columnbutton"),id="columninput"
        )
        yield Vertical(
            Static("rowname", id="row"),
            Static("Enter the row name", id="rowname"),
            Input(placeholder="1/35", id="inputrow"), 
            Button("Submit row", id="rowbutton"),id="rowinput"
        )
        yield Vertical(
            Static("value", id="value"),
            Static("Enter the the new value", id="valuename"),
            Input(placeholder="e.g. 37.5", id="inputvalue"), 
            Button("Submit value", id="valuebutton"),id="valueinput"
        )
        yield Vertical(
                        Input(placeholder="item/id", id="sortcol"), Button("submit column", id="subcol"), id="sortincol"
        )
        
        yield Footer()



    def on_mount(self)-> None:
        self.query_one("#qs1", Static).display=True
        self.query_one("#file_path", Input).display=True
        self.query_one("#status", Static).display=True
        self.query_one("#menu_label", Static).display=False
        self.query_one("#output",Static).display=False
        self.query_one("#qs1_1", Horizontal).display=False
        self.query_one("#qs1_2", Horizontal).display=False
        self.query_one("#again", Static).display=False
        self.query_one("#Sortchoice", Static).display=False
        self.query_one("#sorting", Horizontal).display=False
        self.query_one("#null", Horizontal).display=False
        self.query_one("#searchinput",Vertical).display=False
        self.query_one("#edit",Button).display=False
        self.query_one("#columninput", Vertical).display=False
        self.query_one("#rowinput", Vertical).display=False
        self.query_one("#valueinput", Vertical).display=False
        self.query_one("#sortincol", Vertical).display=False


            

    def clear(self):
        self.query_one("#qs1", Static).display=False
        self.query_one("#file_path", Input).display=False
        self.query_one("#status", Static).display=False
        self.query_one("#menu_label", Static).display=False
        self.query_one("#output", Static).display=False
        self.query_one("#qs1_1", Horizontal).display=False
        self.query_one("#qs1_2", Horizontal).display=False
        self.query_one("#again", Static).display=False
        self.query_one("#Sortchoice", Static).display=False
        self.query_one("#sorting", Horizontal).display=False
        self.query_one("#null", Horizontal).display=False
        self.query_one("#searchinput", Vertical).display=False
        self.query_one("#edit", Button).display=False
        self.query_one("#columninput", Vertical).display=False
        self.query_one("#rowinput", Vertical).display=False
        self.query_one("#valueinput", Vertical).display=False
        self.query_one("#sortincol", Vertical).display=False





    def on_button_pressed(self, event: Button.Pressed):
        self.current_action=event.button.id
        output=self.query_one("#output", Static)
        label=self.query_one("#menu_label", Static)
        qs11=self.query_one("#qs1_1", Horizontal)
        qs12=self.query_one("#qs1_2", Horizontal)
        label2=self.query_one("#again", Static)
        sorting=self.query_one("#sorting", Horizontal)
        sortchoice=self.query_one("#Sortchoice", Static)
        null=self.query_one("#null", Horizontal)
        inputi=self.query_one("#input", Input)
        search_container=self.query_one("#searchinput", Vertical)
        edit=self.query_one("#edit",Button)
        label2.display=False
        output.display=False
        label.display=False
        qs11.display=False
        qs12.display=False
        sorting.display=False
        sortchoice.display=False
        null.display=False
        search_container.display=False
        if self.df is not None:
            if event.button.id=="whole":
                self.clear()
                label.update("The data is below")
                label.display=True
                output.update(str(self.df))
                output.display=True
                label2.update("Choose the next process")
                label2.display=True
                qs11.display=True
                qs12.display=True
            elif event.button.id =="describe":
                self.clear()
                label.update("The data is described below")
                output.update(str(self.df.describe()))
                output.display=True        
                label2.update("Choose a process")
                label2.display=True
                qs11.display= True
                qs12.display=True
            elif event.button.id=="sort":
                self.clear()
                label.update("Choose your column")
                label2.update(str(self.df.columns))
                self.query_one("#sortincol", Vertical).display=True
                label.display=True
                label2.display=True
            
            elif event.button.id == "search":
                self.clear()
                # Just show the search box
                self.query_one("#searchinput", Vertical).display = True
                self.query_one("#menu_label", Static).update("🔍 Enter a value to search for:")
                self.query_one("#menu_label", Static).display = True
            
            
            elif event.button.id=="edit":
                self.clear()
                self.query_one("#columninput").display=True
                column=self.query_one("#df", Static)
                column.update(str(self.df.columns))
                column.display=True


            
            elif event.button.id=="nullcheck":
                self.clear()
                if self.df.isnull().values.any():
                    output.update("missing data was found, What to do")
                    output.display=True
                    null.display=True
                else:
                    output.update("No missing data found")
                    output.display=True
                    label2.update("Choose a process")
                    label2.display=True
                    qs11.display= True
                    qs12.display=True
            elif event.button.id == "save":
                self.clear()

                sortchoice.display = True
                label2.display = True
                qs11.display = True
                qs12.display = True

                if not self.file_path:
                    sortchoice.update(" No file loaded to save.")
                    return

                file_root, ext = os.path.splitext(self.file_path)
                new_path = f"{file_root}_updated{ext}"

                try:
                    if self.file_ext == ".csv":
                        self.df.to_csv(new_path, index=False)
                    elif self.file_ext == ".xlsx":
                        self.df.to_excel(new_path, index=False, engine="openpyxl")
                    elif self.file_ext == ".json":
                        self.df.to_json(new_path, orient="records", indent=4)
                    else:
                        sortchoice.update("Unsupported file format.")
                        return

                    sortchoice.update(f"✅ Data saved successfully to: {new_path}")
                except Exception as e:
                    sortchoice.update(f"Data was not saved {e}")


        #secondry buttons
            elif event.button.id=="ascend":
                self.clear()
                sortchoice.update("The data is sorted descendingly below:")
                sortchoice.display=True
                self.df=self.df.sort_values(by=self.colsort, ascending=True)
                output.update(str(self.df))
                output.display=True
                sorting.display=False
                label.display=False
                label2.update("Choose a process")
                label2.display=True
                qs11.display= True
                qs12.display=True
            elif event.button.id=="descend":
                self.clear()
                sortchoice.update("The data is sorted descendingly below:")
                sortchoice.display=True
                self.df = self.df.sort_values(by=self.colsort, ascending=False)
                output.update(str(self.df))
                output.display=True
                sorting.display=False
                label.display=False
                label2.update("Choose a process")
                label2.display=True
                qs11.display= True
                qs12.display=True
            elif event.button.id=="fill":
                self.clear()
                sortchoice.update("Missing data is now filled with zeros")
                sortchoice.display=True
                null.display=False
                self.df=self.df.fillna(0)
                output.update(str(self.df))
                output.display=True
                label2.update("Choose a process")
                label2.display=True
                qs11.display= True
                qs12.display=True
            elif event.button.id=="remove":
                self.clear()
                sortchoice.update("Rows with missing data is now removed")
                sortchoice.display=True
                null.display=False
                self.df=self.df.dropna()
                output.update(str(self.df))
                output.display=True
                label2.update("Choose a process")
                label2.display=True
                qs11.display= True
                qs12.display=True
            elif event.button.id == "submit_search":
                self.clear()
                input_widget = self.query_one("#input", Input)
                output = self.query_one("#output", Static)
                search_value = input_widget.value.strip()

                if not search_value:
                    output.update("❌ Search value cannot be empty.")
                else:
                    # Search case-insensitively across all columns as strings
                    mask = self.df.astype(str).apply(
                    lambda row: row.str.contains(search_value, case=False, na=False),
                    axis=1)

                    results = self.df[mask.any(axis=1)]

                    if not results.empty:
                        output.update(str(results))
                    else:
                        output.update("No match found.")

                output.display = True
                self.query_one("#searchinput", Vertical).display = False
                label = self.query_one("#menu_label", Static)
                label.update("Rows including the value you searched are below:")
                label.display = True

                self.query_one("#again", Static).update("Choose a process")
                self.query_one("#again", Static).display = True
                self.query_one("#qs1_1", Horizontal).display = True
                self.query_one("#qs1_2", Horizontal).display = True


            elif event.button.id=="rowbutton":
                self.clear()
                self.query_one("#valueinput", Vertical).display=True
            elif event.button.id=="columnbutton":
                self.clear()
                self.query_one("#rowinput", Vertical).display=True
            elif event.button.id == "valuebutton":
                self.clear()
                self.df.at[int(self.selected_row), self.selected_column] = self.new_value
                output.update(str(self.df.iloc[int(self.selected_row)]))
                output.display = True
                label2.update("Choose a process")
                label2.display=True
                qs11.display= True
                qs12.display=True
            elif event.button.id=="subcol":
                self.clear()
                label.update("Choose how to sort")
                label.display=True
                sorting.display=True


        else:
            output.update("Data is not uploaded")
            

    


    def on_input_submitted(self, event:Input.Submitted) -> None:
        output=self.query_one("#output", Static)
        if event.input.id == "file_path":
            file_path = event.value.strip()
            status_widget = self.query_one("#status", Static)
            label= self.query_one("#menu_label", Static)
            path=self.query_one("#file_path", Input)
            qs1=self.query_one("#qs1",Static)
            qs11=self.query_one("#qs1_1",Horizontal)
            qs12=self.query_one("#qs1_2", Horizontal)
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                status_widget.update("The path you entered is invalid. if you forgot to remove the qoutations, remove them and try again")
                status_widget.display = True
                return
            ext = os.path.splitext(file_path)[1].lower()

            try:
                if ext == ".csv":
                    self.df = pd.read_csv(file_path)
                    status_widget.update("The file is uploaded succesfully")
                elif ext == ".xlsx":
                    self.df = pd.read_excel(file_path, engine="openpyxl")
                    status_widget.update("The file is uploaded succesfully")
                elif ext == ".json":
                    self.df = pd.read_json(file_path)
                    status_widget.update("The file is uploaded succesfully")
                else:
                    status_widget.update("File type is not supported.")
                self.file_ext = ext
                self.file_path = file_path                
                status_widget.update("File uploaded.")
                status_widget.display=True
                label.update("Choose a process")
                label.display=True
                qs11.display=True
                qs12.display=True
                self.query_one("#edit", Button).display=True
            except Exception as e:
                status_widget.update(f"File is not uploaded {e}")
        
        elif event.input.id == "input":
            search_value = event.value.strip()

            # Search across the entire DataFrame (case-insensitive)
            matches = self.df[
                self.df.astype(str).apply(
                    lambda row: row.str.contains(search_value, case=False, na=False),
                    axis=1
                )
            ]

            if not matches.empty:
                output.update(str(matches))
            else:
                output.update("No match found.")
        elif event.input.id == "inputcolumn":
            self.selected_column = event.value.strip()
        elif event.input.id == "inputrow":
            self.selected_row = event.value.strip()
        elif event.input.id == "inputvalue":
            self.new_value = event.value.strip()
        elif event.input.id=="sortcol":
            self.colsort=event.value.strip()

        




if __name__ == "__main__":
    app = Data_Anlyzer()
    app.run()


