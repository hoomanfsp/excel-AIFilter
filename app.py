import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import asyncio
import os
from excel_processor import ExcelProcessor
from openrouter_api import OpenRouterFilter

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Excel Filterer via Gemini API")
        self.geometry("700x800")
        self.minsize(600, 700)
        
        self.excel_processor = ExcelProcessor()
        self.checkboxes = {}
        self.selected_file = None

        # --- UI Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(self.main_frame, text="OpenRouter Excel Filterer", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # API Key
        self.api_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.api_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.api_frame.grid_columnconfigure(1, weight=1)
        
        self.api_label = ctk.CTkLabel(self.api_frame, text="OpenRouter API Key:")
        self.api_label.grid(row=0, column=0, padx=(0, 10))
        
        self.api_entry = ctk.CTkEntry(self.api_frame, show="*", placeholder_text="Enter your OpenRouter API Key")
        self.api_entry.grid(row=0, column=1, sticky="ew")
        
        # Topic
        self.topic_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.topic_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.topic_frame.grid_columnconfigure(1, weight=1)
        
        self.topic_label = ctk.CTkLabel(self.topic_frame, text="Topic to match:")
        self.topic_label.grid(row=0, column=0, padx=(0, 10))
        
        self.topic_entry = ctk.CTkEntry(self.topic_frame, placeholder_text="e.g., Computer Science")
        self.topic_entry.grid(row=0, column=1, sticky="ew")
        
        # File Selection
        self.file_btn = ctk.CTkButton(self.main_frame, text="Select Excel File", command=self.select_file)
        self.file_btn.grid(row=3, column=0, padx=20, pady=(20, 5))
        
        self.file_label = ctk.CTkLabel(self.main_frame, text="No file selected", text_color="gray")
        self.file_label.grid(row=4, column=0, padx=20, pady=(0, 10))
        
        # Column Selection Frame
        self.col_label = ctk.CTkLabel(self.main_frame, text="Select Columns to send as Context:", font=ctk.CTkFont(weight="bold"))
        self.col_label.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, height=150)
        self.scrollable_frame.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_rowconfigure(6, weight=1)
        
        # Action Button & Progress
        self.start_btn = ctk.CTkButton(self.main_frame, text="Start Filtering", command=self.start_filtering_thread, fg_color="#28a745", hover_color="#218838")
        self.start_btn.grid(row=7, column=0, padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready")
        self.status_label.grid(row=9, column=0, padx=20, pady=(0, 20))

    def select_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if filepath:
            self.selected_file = filepath
            self.file_label.configure(text=os.path.basename(filepath), text_color=("black", "white"))
            
            try:
                columns = self.excel_processor.load_file(filepath)
                self.populate_columns(columns)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load Excel file:\n{str(e)}")
                self.selected_file = None
                self.file_label.configure(text="No file selected", text_color="gray")

    def populate_columns(self, columns):
        # Clear existing checkboxes
        for cb in self.checkboxes.values():
            cb.destroy()
        self.checkboxes.clear()
        
        # Create new checkboxes
        for i, col in enumerate(columns):
            var = ctk.StringVar(value="off")
            cb = ctk.CTkCheckBox(self.scrollable_frame, text=col, variable=var, onvalue="on", offvalue="off")
            cb.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.checkboxes[col] = (cb, var)
            
    def start_filtering_thread(self):
        api_key = self.api_entry.get().strip()
        topic = self.topic_entry.get().strip()
        
        if not api_key:
            messagebox.showwarning("Input Error", "Please enter your OpenRouter API Key.")
            return
        if not self.selected_file:
            messagebox.showwarning("Input Error", "Please select an Excel file.")
            return
        if not topic:
            messagebox.showwarning("Input Error", "Please enter a topic.")
            return
            
        selected_cols = [col for col, (cb, var) in self.checkboxes.items() if var.get() == "on"]
        if not selected_cols:
            messagebox.showwarning("Input Error", "Please select at least one column to use as context.")
            return
            
        # Disable inputs
        self.start_btn.configure(state="disabled", text="Filtering...")
        self.file_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Preparing data...")
        
        # Ask for save location immediately
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Filtered File As",
            initialfile="filtered_output.xlsx"
        )
        
        if not save_path:
            self.reset_ui()
            return
            
        # Start background thread
        threading.Thread(target=self.run_filtering, args=(api_key, topic, selected_cols, save_path), daemon=True).start()

    def update_progress(self, current, total):
        # Schedule update on main thread
        progress_val = current / total if total > 0 else 0
        self.after(0, lambda: self.progress_bar.set(progress_val))
        self.after(0, lambda: self.status_label.configure(text=f"Processed {current} / {total} rows... (Rate limiting to 15 Req/Min)"))

    def run_filtering(self, api_key, topic, selected_cols, save_path):
        try:
            # 1. Extract context items from Excel
            items = self.excel_processor.extract_context_items(selected_cols)
            
            # 2. Setup OpenRouter
            api_client = OpenRouterFilter(api_key=api_key)
            
            # 3. Process batches via asyncio
            results = asyncio.run(api_client.filter_all_async(
                all_items=items, 
                topic=topic, 
                batch_size=25, 
                progress_callback=self.update_progress
            ))
            
            # 4. Save results
            self.after(0, lambda: self.status_label.configure(text="Saving Excel file..."))
            rows_saved = self.excel_processor.save_filtered_file(save_path, results)
            
            self.after(0, lambda: messagebox.showinfo("Success", f"Filtering complete!\nSaved {rows_saved} matching rows to:\n{save_path}"))
            
        except Exception as e:
            error_str = str(e)
            if "RetryError" in error_str or "429" in error_str:
                self.after(0, lambda: messagebox.showerror("Rate Limit Exceeded", "Google/OpenRouter's free tier rate limit was completely exhausted despite our automatic retries. Please wait a minute and try again."))
            else:
                self.after(0, lambda: messagebox.showerror("Processing Error", f"An error occurred during filtering:\n\n{error_str}"))
            
        finally:
            self.after(0, self.reset_ui)
            
    def reset_ui(self):
        self.start_btn.configure(state="normal", text="Start Filtering")
        self.file_btn.configure(state="normal")
        self.status_label.configure(text="Ready")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()
