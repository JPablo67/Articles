import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import numpy as np
import random

# Historical data structure: {date: {diary_name: number_of_articles}}
historical_data = defaultdict(dict)


# Function to load historical data from a text file
def load_data_from_file(filename):
    global historical_data
    historical_data = defaultdict(dict)  # Reset the dictionary
    try:
        with open(filename, 'r') as file:
            for line in file:
                # Each line is in the format: YYYY-MM-DD, number_of_articles, diary_name
                date_str, count_str, diary_name = line.strip().split(',')
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                article_count = int(count_str)
                historical_data[date][diary_name] = article_count
        print(f"Data successfully loaded from {filename}.")
    except FileNotFoundError:
        messagebox.showerror("Error", f"File {filename} not found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data from file: {e}")


# Function to add new article count for the selected day and diary
def add_article_count(date, diary_name, count):
    historical_data[date][diary_name] = count
    messagebox.showinfo("Success", f"Articles for {date} from {diary_name} updated with {count} articles.")


# Function to calculate the average for each weekday over the past 6 months for a specific diary
def calculate_weekday_averages(diary_name):
    weekday_data = defaultdict(list)  # {0: [counts for Monday], 1: [counts for Tuesday], ...}
    six_months_ago = datetime.now().date() - timedelta(days=180)

    for date, diaries in historical_data.items():
        if date >= six_months_ago and diary_name in diaries:
            count = diaries[diary_name]
            weekday = date.weekday()
            weekday_data[weekday].append(count)

    # Calculate averages
    weekday_averages = {day: (sum(counts) / len(counts)) if counts else 0 for day, counts in weekday_data.items()}
    return weekday_averages


# Function to calculate coefficient of variation
def calculate_coefficient_of_variation(data):
    if len(data) < 2:
        return 0  # Avoid calculation with insufficient data
    mean = statistics.mean(data)
    std_dev = statistics.stdev(data)
    if mean == 0:
        return 0  # Avoid division by zero
    return std_dev / mean


# Function to calculate interquartile range
def calculate_interquartile_range(data):
    if len(data) < 4:
        return 0, 0, 0  # Avoid calculation with insufficient data
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    return q1, q3, iqr


# Function to verify article count against frequency distribution
def check_frequency_distribution(data, count):
    freq_dist = Counter(data)
    most_common_count, _ = freq_dist.most_common(1)[0]
    return count == most_common_count, most_common_count


# Function to check if today's articles are below 80% or above the average for the same day of the week
def check_article_count(today, diary_name, count):
    weekday_averages = calculate_weekday_averages(diary_name)
    today_weekday = today.weekday()
    average = weekday_averages.get(today_weekday, 0)

    if count < 0.8 * average:
        return "under 80% of the average", average
    elif count > average:
        return "above the average", average
    else:
        return "within 80% of the average", average


# Function to get a summary of the last week's article counts for a specific diary, based on the date entered by the user
def get_last_week_summary(date, diary_name):
    last_week_data = {}

    # Calculate the last 7 days from the entered date
    for i in range(7):
        day = date - timedelta(days=i)
        last_week_data[day] = historical_data[day].get(diary_name, 0) if day in historical_data else 0

    return last_week_data


# Function to display the weekday averages for the past 6 months for a specific diary
def show_weekday_averages(diary_name):
    weekday_averages = calculate_weekday_averages(diary_name)
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Create a string that displays each day of the week with its average
    averages_str = f"Averages for {diary_name} for each day of the week (last 6 months):\n"
    for i, day_name in enumerate(days_of_week):
        averages_str += f"{day_name}: {weekday_averages.get(i, 0):.2f} articles\n"

    # Show the averages in a messagebox
    messagebox.showinfo("Weekday Averages", averages_str)


# GUI Application
class ArticleTrackerApp:
    def __init__(self, root, data_file):
        self.root = root
        self.data_file = data_file

        # Set the window size and center it
        window_width = 500
        window_height = 350

        # Get the screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate position x and y to center the window
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)

        # Set the geometry of the window
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        self.root.title("Article Tracker")

        # Use ttk for modern styling
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TButton", font=("Arial", 12))

        self.create_widgets()

        # Load data from file
        load_data_from_file(self.data_file)

    def create_widgets(self):
        # Create frame for inputs
        input_frame = ttk.Frame(self.root, padding="10 10 10 10")
        input_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Create date picker using tkcalendar's DateEntry
        ttk.Label(input_frame, text="Select Date:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = DateEntry(input_frame, width=20, year=datetime.now().year, month=datetime.now().month,
                                    day=datetime.now().day,
                                    background="darkblue", foreground="white", borderwidth=2)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Create diary name input
        ttk.Label(input_frame, text="Diary Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.diary_name_entry = ttk.Entry(input_frame, width=20)
        self.diary_name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Create article count input
        ttk.Label(input_frame, text="Number of Articles:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.article_count_entry = ttk.Entry(input_frame, width=20)
        self.article_count_entry.grid(row=2, column=1, padx=5, pady=5)

        # Submit button
        submit_button = ttk.Button(input_frame, text="Submit", command=self.submit_data)
        submit_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Button to show weekday averages
        avg_button = ttk.Button(input_frame, text="Show Weekday Averages", command=self.show_averages)
        avg_button.grid(row=4, column=0, columnspan=2, pady=5)

        # Summary label
        self.summary_label = ttk.Label(self.root, text="", padding="10 10 10 10", anchor="center")
        self.summary_label.grid(row=1, column=0, columnspan=1)  # Adjusted columnspan to 1 to fit layout

    def submit_data(self):
        # Get date from DateEntry
        date = self.date_entry.get_date()

        diary_name = self.diary_name_entry.get()
        article_count_str = self.article_count_entry.get()

        # Input validation
        try:
            article_count = int(article_count_str)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid article count.")
            return

        if not diary_name:
            messagebox.showerror("Input Error", "Please enter a valid diary name.")
            return

        # Add the article count to the historical data
        add_article_count(date, diary_name, article_count)

        # Check if the article count is below 80% or above the average
        status, average = check_article_count(date, diary_name, article_count)

        # Update summary label
        self.summary_label.config(
            text=f"Articles for {date} from {diary_name}: {article_count}\nAverage for this weekday: {average:.2f}\n"
                 f"Today's count is {status}."
        )

        # Get the data for the past 6 months to perform additional statistical analysis
        six_months_data = []
        six_months_ago = datetime.now().date() - timedelta(days=180)
        for day, diaries in historical_data.items():
            if day >= six_months_ago and diary_name in diaries:
                six_months_data.append(diaries[diary_name])

        # Phase 2: Calculate the coefficient of variation
        if len(six_months_data) > 0:
            coef_variation = calculate_coefficient_of_variation(six_months_data)

            # Display the coefficient of variation
            self.summary_label.config(
                text=self.summary_label.cget("text") + f"\nCoefficient of Variation: {coef_variation:.2f}"
            )

            # If high variation, analyze using interquartile range (IQR) or first quartile (Q1)
            if coef_variation > 0.2:  # Assuming 0.2 as threshold for high variation
                q1, q3, iqr = calculate_interquartile_range(six_months_data)
                if article_count < q1:
                    messagebox.showinfo("Result", f"Article count is below the first quartile (Q1={q1:.2f}).")
                else:
                    messagebox.showinfo("Result",
                                        f"Article count is within the interquartile range (Q1={q1:.2f}, Q3={q3:.2f}).")
            else:
                # Phase 3: Check against frequency distribution if variation is low
                is_most_frequent, most_common_count = check_frequency_distribution(six_months_data, article_count)
                if is_most_frequent:
                    messagebox.showinfo("Result",
                                        f"Article count matches the most frequent category ({most_common_count} articles).")
                else:
                    messagebox.showinfo("Result",
                                        f"Article count does not match the most frequent category ({most_common_count} articles).")

        # Show the last week summary based on the entered date
        last_week_summary = get_last_week_summary(date, diary_name)
        summary_str = f"Last week's summary for {diary_name}:\n" + "\n".join(
            [f"{day}: {count}" for day, count in last_week_summary.items()])
        messagebox.showinfo("Last Week Summary", summary_str)

        # Save the updated data to the file
        with open(self.data_file, 'w') as file:
            for date, diaries in historical_data.items():
                for diary, count in diaries.items():
                    file.write(f"{date.strftime('%Y-%m-%d')},{count},{diary}\n")

        print("Data saved to file.")

    def show_averages(self):
        diary_name = self.diary_name_entry.get()
        if not diary_name:
            messagebox.showerror("Input Error", "Please enter a valid diary name.")
            return
        show_weekday_averages(diary_name)


# Main function to run the app
def run_app(data_file):
    root = tk.Tk()
    app = ArticleTrackerApp(root, data_file)
    root.mainloop()


# Run the app with a specified text file for historical data
data_file = 'article_data.txt'  # Replace this with your actual text file
run_app(data_file)