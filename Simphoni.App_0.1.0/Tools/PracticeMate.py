import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# Initialize data storage
try:
    data = pd.read_csv('practice_data.csv')
except FileNotFoundError:
    data = pd.DataFrame(columns=['Date', 'Duration', 'Category', 'Notes'])

# Main Application Class
class PracticeMateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PracticeMate")
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        
        # Practice Log Frame
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text='Practice Log')
        
        # Goal Setting Frame
        self.goal_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.goal_frame, text='Goal Setting')
        
        # Data Visualization Frame
        self.visual_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.visual_frame, text='Data Visualization')
        
        # Initialize sections
        self.create_log_section()
        self.create_goal_section()
        self.create_visualization_section()
    
    # Practice Log Section
    def create_log_section(self):
        ttk.Label(self.log_frame, text="Practice Log", font=("Helvetica", 16)).pack(pady=10)
        
        # Duration
        ttk.Label(self.log_frame, text="Duration (minutes):").pack()
        self.duration_entry = ttk.Entry(self.log_frame)
        self.duration_entry.pack()
        
        # Category
        ttk.Label(self.log_frame, text="Category:").pack()
        self.category_entry = ttk.Entry(self.log_frame)
        self.category_entry.pack()
        
        # Notes
        ttk.Label(self.log_frame, text="Notes:").pack()
        self.notes_entry = ttk.Entry(self.log_frame)
        self.notes_entry.pack()
        
        # Save Button
        ttk.Button(self.log_frame, text="Save Practice Session", command=self.save_session).pack(pady=10)
    
    def save_session(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        duration = self.duration_entry.get()
        category = self.category_entry.get()
        notes = self.notes_entry.get()
        
        if not duration:
            messagebox.showerror("Error", "Duration is required.")
            return
        
        new_data = pd.DataFrame({
            'Date': [date],
            'Duration': [duration],
            'Category': [category],
            'Notes': [notes]
        })
        
        global data
        data = pd.concat([data, new_data], ignore_index=True)
        data.to_csv('practice_data.csv', index=False)
        
        messagebox.showinfo("Success", "Session saved successfully.")
        
        # Clear entries
        self.duration_entry.delete(0, 'end')
        self.category_entry.delete(0, 'end')
        self.notes_entry.delete(0, 'end')
    
    # Goal Setting Section
    def create_goal_section(self):
        ttk.Label(self.goal_frame, text="Goal Setting", font=("Helvetica", 16)).pack(pady=10)
        
        # Goal Name
        ttk.Label(self.goal_frame, text="Goal Name:").pack()
        self.goal_name_entry = ttk.Entry(self.goal_frame)
        self.goal_name_entry.pack()
        
        # Target Date
        ttk.Label(self.goal_frame, text="Target Date (YYYY-MM-DD):").pack()
        self.target_date_entry = ttk.Entry(self.goal_frame)
        self.target_date_entry.pack()
        
        # Progress
        ttk.Label(self.goal_frame, text="Progress (0-100):").pack()
        self.progress_entry = ttk.Entry(self.goal_frame)
        self.progress_entry.pack()
        
        # Save Goal Button
        ttk.Button(self.goal_frame, text="Save Goal", command=self.save_goal).pack(pady=10)
    
    def save_goal(self):
        goal_name = self.goal_name_entry.get()
        target_date = self.target_date_entry.get()
        progress = self.progress_entry.get()
        
        if not goal_name or not target_date or not progress:
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            progress = int(progress)
            if not (0 <= progress <= 100):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Progress must be an integer between 0 and 100.")
            return
        
        # Save goal to a CSV file
        try:
            goals = pd.read_csv('goals.csv')
        except FileNotFoundError:
            goals = pd.DataFrame(columns=['Goal Name', 'Target Date', 'Progress'])
        
        new_goal = pd.DataFrame({
            'Goal Name': [goal_name],
            'Target Date': [target_date],
            'Progress': [progress]
        })
        
        goals = pd.concat([goals, new_goal], ignore_index=True)
        goals.to_csv('goals.csv', index=False)
        
        messagebox.showinfo("Success", "Goal saved successfully.")
        
        # Clear entries
        self.goal_name_entry.delete(0, 'end')
        self.target_date_entry.delete(0, 'end')
        self.progress_entry.delete(0, 'end')
    
    # Data Visualization Section
    def create_visualization_section(self):
        ttk.Label(self.visual_frame, text="Data Visualization", font=("Helvetica", 16)).pack(pady=10)
        
        # Plot button
        ttk.Button(self.visual_frame, text="Plot Practice Time", command=self.plot_practice_time).pack(pady=10)
    
    def plot_practice_time(self):
        if data.empty:
            messagebox.showinfo("Info", "No data to display.")
            return
        
        # Group data by date and sum duration
        grouped_data = data.groupby('Date').sum()
        
        fig, ax = plt.subplots()
        ax.plot(grouped_data.index, grouped_data['Duration'], marker='o')
        ax.set_xlabel('Date')
        ax.set_ylabel('Total Duration (minutes)')
        ax.set_title('Practice Time Over Time')
        ax.tick_params(axis='x', rotation=45)
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.visual_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        
        # Add toolbar
        # toolbar = NavigationToolbar2Tk(canvas, self.visual_frame)
        # toolbar.update()
        # canvas.get_tk_widget().pack()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PracticeMateApp(root)
    root.mainloop()