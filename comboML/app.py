from textual.app import App, ComposeResult, Binding
from textual.widgets import Header, Footer, ListView, ListItem, Label
from textual.containers import Vertical
import pandas as pd
import numpy as np
from itertools import combinations
from sklearn.metrics import r2_score
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from pathlib import Path

class ComboMLApp(App):
    CSS_PATH = "/Users/tariqmahmood/Projects/MLPypi/comboML/combo_ml.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit Application"),
        Binding("r", "reset", "Reset Selection"),
    ]

    def __init__(self, dataset_path):
        super().__init__()
        self.dataset_path = dataset_path
        self.dataset = pd.read_csv(dataset_path)
        self.numeric_features = list(self.dataset.select_dtypes(include=['number']).columns)
        self.selected_target = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Select a target variable (numeric only):"),
            ListView(
                *[ListItem(Label(feature)) for feature in self.numeric_features]
            ),
            Footer()
        )

    def on_mount(self):
        self.query_one(ListView).focus()

    def on_list_view_selected(self, event):
        list_view = self.query_one(ListView)
        highlighted_index = list_view.index  # Get index of selected item

        if highlighted_index is not None:
            highlighted = list_view.children[highlighted_index]  # Get selected ListItem
            if isinstance(highlighted, ListItem):
                label = highlighted.query_one(Label)
                self.selected_target = label.renderable if isinstance(label.renderable, str) else str(label.renderable)
                self.evaluate_linear_regression()


    def action_reset(self):
        self.selected_target = None
        self.notify("Selection reset. Choose a new target variable.")

    def impute_missing_with_mean(self, df):
        imputer = SimpleImputer(strategy='mean')
        return pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

    def evaluate_linear_regression(self):
        if self.selected_target is None:
            self.notify("No target variable selected!")
            return

        if self.selected_target not in self.dataset.columns:
            self.notify("Invalid target variable selected!")
            return

        X = self.dataset.drop(columns=[self.selected_target])
        y = self.dataset[self.selected_target].dropna()  # Drop NaN values in target

        numeric_columns = X.select_dtypes(include=['number']).columns
        X_numeric = X[numeric_columns]

        if X_numeric.empty:
            self.notify("No numeric features available for regression.")
            return

        X_numeric = self.impute_missing_with_mean(X_numeric)

        best_r2 = -float('inf')
        best_features = []
        feature_names = list(X_numeric.columns)

        for r in range(1, min(len(feature_names) + 1, 4)):  # Use up to 3 features
            for feature_combination in combinations(feature_names, r):
                feature_subset = X_numeric[list(feature_combination)]
                model = LinearRegression()
                model.fit(feature_subset, y)
                y_pred = model.predict(feature_subset)
                r2 = r2_score(y, y_pred)

                if r2 > best_r2:
                    best_r2 = r2
                    best_features = list(feature_combination)

        self.notify(f"Best Features: {best_features}\nBest R² Score: {best_r2:.2f}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python combo_ml.py <filepath>")
    else:
        ComboMLApp(sys.argv[1]).run()
