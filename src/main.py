import threading
import time
from PIL import Image, ImageDraw
import pystray
from monitor import SelectionMonitor
from ui import PopDoBar

def create_icon():
    # Generate a simple icon with an initial
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color=(43, 43, 43))
    dc = ImageDraw.Draw(image)
    dc.rectangle([16, 16, 48, 48], fill=(62, 126, 230))
    return image

def run_tray(app, monitor):
    def on_quit(icon, item):
        icon.stop()
        app.quit()
        # monitor.stop() is called in finally block of main

    icon = pystray.Icon("PopDo", create_icon(), "PopDo", menu=pystray.Menu(
        pystray.MenuItem("Quit", on_quit)
    ))
    icon.run()

def main():
    # Initialize UI
    app = PopDoBar()
    
    # Define callback for the monitor
    def on_selection_detected(text, x, y):
        # Schedule UI update on main thread
        app.after(0, lambda: app.show_at(text, x, y))

    def on_global_click(x, y):
        # Handle click on main thread
        app.after(0, lambda: app.handle_external_click(x, y))

    # Initialize Monitor
    monitor = SelectionMonitor(on_selection_detected, on_global_click)
    monitor.start()
    
    # Start Tray Icon in background thread
    tray_thread = threading.Thread(target=run_tray, args=(app, monitor), daemon=True)
    tray_thread.start()

    # Run UI Loop
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop()

if __name__ == "__main__":
    main()
