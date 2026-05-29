# Se-Aa-Achievement-monitoring-tool
Made with the help of AI for a jonior developer to make his life easier and encorage him to work hard.
And it worked! I've tried it and it really helped me alot and encoraged me to work, I've witnessed 20% more productivity + it makes it so easy to monitor what you did,
currently it is a raw python code sadly and the interface all in Arabic, but I will continue to improve it if god wills




## 1. Technical Requirements

* **Programming Language:** Python 3[cite: 1]
* **External Libraries:**[cite: 1]
    * `customtkinter`: For building the advanced dark mode Graphical User Interface (GUI)[cite: 1].
* **Python Standard Libraries:**[cite: 1]
    * `json`: For processing data pasted from the clipboard[cite: 1].
    * `os`: For handling system paths and opening exported files[cite: 1].
    * `time` & `datetime`: For calculating focus session durations, dates, and weekly alerts[cite: 1].
* **Local Dependencies:**[cite: 1]
    * `database.py`: Must contain the `Database` class responsible for database operations (CRUD)[cite: 1].
    * `vfx.py`: Must contain the `play_sound` function for interactive sound effects[cite: 1].

---

## 2. Functional Requirements

### I. Main Dashboard
* **Top Performance Cards:** Real-time statistics displaying: Remaining weekly hours, total hours this week, total archived hours, and the current streak[cite: 1].
* **Smart Alert System:** A distinct purple warning banner that appears exclusively on Thursdays (Weekday 3) to calculate remaining hours before the week ends, motivating the user[cite: 1].

### II. Task Management
* **Add New Task:** A pop-up dialog to input the task name, weekly target hours, and specify if the goal is temporary or permanent[cite: 1].
* **Edit/Delete Tasks:** Ability to modify task details or delete them completely via a dedicated settings button on each task card[cite: 1].
* **Undo Feature:** Instantly revert the last task deletion or bulk addition[cite: 1].
* **Paste from Clipboard (Bulk Add):** Read JSON formatted data directly from the clipboard and add them as multiple tasks at once[cite: 1].

### III. Time Tracking & Logging
* **Focus Session Timer:** Opens an independent, topmost window calculating actual focus time in a `HH:MM:SS` format, with an option to stop and automatically log the session[cite: 1].
* **Manual Time Logging:** A button to manually add completed hours to any task, with an option to include a comment or note[cite: 1].

### IV. Debts Page
* **Visibility Condition:** This tab appears automatically **only** if the user has accumulated debt hours[cite: 1].
* **Pay Debts:** Displays overdue hours for each task and provides an option to pay off a portion of the debt via a custom logging window[cite: 1].

### V. Advanced Statistics
* **Weekly Bar Chart:** A Canvas-based bar chart displaying the daily activity volume for the last 7 days along with dates[cite: 1].
* **Time Distribution (Top 5):** Displays the top 5 most time-consuming tasks using colored progress bars corresponding to each task's assigned color[cite: 1].

### VI. Data Management & Archive
* **Export Archive:** Export all logged data into a CSV file automatically saved to the Desktop as `TaskFlow_Archive.csv`[cite: 1].
* **System Integration:** Automatically open the Desktop folder and highlight the exported file upon completion (specifically using the `open -R` command for macOS)[cite: 1].
