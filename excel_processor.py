import pandas as pd

class ExcelProcessor:
    def __init__(self):
        self.df = None
        self.filepath = None
        
    def load_file(self, filepath: str) -> list[str]:
        """Loads the Excel file and returns the list of column names."""
        self.filepath = filepath
        self.df = pd.read_excel(filepath)
        return self.df.columns.tolist()
        
    def extract_context_items(self, selected_columns: list[str]) -> list[str]:
        """
        Creates a list of strings representing each row, combining the selected columns.
        E.g. "University: MIT, Program: Computer Science"
        """
        if self.df is None or not selected_columns:
            return []
            
        items = []
        for index, row in self.df.iterrows():
            parts = []
            for col in selected_columns:
                val = row.get(col, "")
                parts.append(f"{col}: {val}")
            
            combined = ", ".join(parts)
            items.append(combined)
            
        return items
        
    def save_filtered_file(self, save_path: str, filter_results: list[int]):
        """
        Filters the dataframe to keep only rows where filter_results[i] == 1,
        and saves it to the specified path.
        """
        if self.df is None:
            raise ValueError("No data loaded")
            
        if len(filter_results) != len(self.df):
            raise ValueError(f"Length mismatch: {len(filter_results)} results vs {len(self.df)} rows")
            
        # Create a boolean mask from the 1/0 results
        mask = [bool(res == 1) for res in filter_results]
        
        filtered_df = self.df[mask]
        filtered_df.to_excel(save_path, index=False)
        return len(filtered_df)
