import threading
import time
from monitor import SelectionMonitor
from ui import PopDoBar

def main():
    # Initialize UI
    app = PopDoBar()
    
    # Define callback for the monitor
    def on_selection_detected(text, x, y):
        # Schedule UI update on main thread
        app.after(0, lambda: app.show_at(text, x, y))

    # Initialize Monitor
    monitor = SelectionMonitor(on_selection_detected)
    monitor.start()
    
    # Run UI Loop
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop()

if __name__ == "__main__":
    main()
