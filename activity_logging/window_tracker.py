import subprocess
import time
import datetime
import csv
import os
import logging
try:
    from AppKit import NSWorkspace # type: ignore
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID, kCGWindowListOptionExcludeDesktopElements # type: ignore
except ImportError:
    print("Error: PyObjC is not installed. Please install it using 'pip install pyobjc-core pyobjc-framework-quartz'")
    exit(1)

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_active_window():
    """
    Returns the name of the active application and the title of its window using pyobjc.
    Returns (None, None) if it fails.
    """
    try:
        # Get the list of all on-screen windows, ordered from front to back
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly | kCGWindowListOptionExcludeDesktopElements,
            kCGNullWindowID
        )

        # The first window in the list with a title and at layer 0 is the active one
        for window in window_list:
            if window.get('kCGWindowLayer') == 0 and window.get('kCGWindowName'):
                app_name = window.get('kCGWindowOwnerName')
                window_title = window.get('kCGWindowName')
                return app_name, window_title
        
        # Fallback for applications that might not have a window with a title
        # but are still the frontmost application (e.g., Finder, Spotlight).
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        if active_app:
            return active_app.localizedName(), ""
        
        return None, None

    except Exception as e:
        logging.error(f"Error getting active window with pyobjc: {e}", exc_info=True)
        return None, None

SLEEP_INTERVAL = 10

def get_idle_time():
    """Returns the user's idle time in seconds."""
    try:
        cmd = "ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print $NF/1000000000; exit}'"
        idle_time_str = subprocess.check_output(cmd, shell=True, text=True).strip()
        if idle_time_str:
            return float(idle_time_str)
        return 0.0
    except Exception as e:
        logging.error(f"Error getting user idle time: {e}")
        return 0.0

# --- Main loop to run the tracker ---
def delete_old_logs(directory, max_age_days=35):
    """Deletes log files older than max_age_days in the given directory."""
    logging.info(f"Checking for log files older than {max_age_days} days in {directory}...")
    today = datetime.date.today()
    for filename in os.listdir(directory):
        if filename.startswith("activity_log_") and filename.endswith(".csv"):
            try:
                # Extract date from filename like 'activity_log_2023-10-27.csv'
                date_str = filename.replace("activity_log_", "").replace(".csv", "")
                file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                age = (today - file_date).days
                if age > max_age_days:
                    file_path = os.path.join(directory, filename)
                    os.remove(file_path)
                    logging.info(f"Deleted old log file: {filename} (age: {age} days)")
            except ValueError:
                # Ignore files that don't match the date format
                logging.warning(f"Could not parse date from filename: {filename}")
            except Exception as e:
                logging.error(f"Error deleting file {filename}: {e}")

if __name__ == "__main__":
    log_directory = "/Users/kwn/the_lab/time-tracker/data"
    delete_old_logs(log_directory)
    print("Starting window tracker. Logs will be saved to daily CSV files.")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            # 1. Determine the filename for the current day
            today = datetime.date.today()
            filename = f"{log_directory}/activity_log_{today.strftime('%Y-%m-%d')}.csv"

            # 2. Get the current activity
            app, title = get_active_window()
            if app:
                idle_time = get_idle_time()
                # 3. Prepare the data row
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                row = [timestamp, SLEEP_INTERVAL, app, title, idle_time]

                # 4. Write the header only if the file is new
                file_exists = os.path.exists(filename)
                
                # Use 'a' for append mode, so we add to the file, not overwrite it
                with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    if not file_exists:
                        writer.writerow(['Timestamp', 'SleepInterval', 'Application', 'WindowTitle', 'IdleTime'])
                    
                    # 5. Write the activity data to the file
                    writer.writerow(row)
            
            # Wait for 10 seconds before checking again
            time.sleep(SLEEP_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nTracker stopped.")