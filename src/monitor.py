import threading
import time
import pyperclip
import pyautogui
from pynput import mouse
from pynput.keyboard import Key, Controller

class SelectionMonitor:
    def __init__(self, on_selection_callback):
        self.on_selection = on_selection_callback
        self.keyboard = Controller()
        self.mouse_listener = None
        self.start_pos = None
        self.is_monitoring = False
        self._last_process_time = 0
        self.last_click_time = 0
        self.click_count = 0

    def start(self):
        self.is_monitoring = True
        self.mouse_listener = mouse.Listener(
            on_click=self._on_click
        )
        self.mouse_listener.start()

    def stop(self):
        self.is_monitoring = False
        if self.mouse_listener:
            self.mouse_listener.stop()

    def _on_click(self, x, y, button, pressed):
        if not self.is_monitoring:
            return

        if button != mouse.Button.left:
            return

        if pressed:
            self.start_pos = (x, y)
        else:
            is_drag = False
            if self.start_pos:
                # Calculate distance
                dx = abs(x - self.start_pos[0])
                dy = abs(y - self.start_pos[1])
                dist = (dx**2 + dy**2)**0.5
                
                # If drag distance is significant (e.g., > 10 pixels), check for text
                if dist > 5:
                    is_drag = True
            
            if is_drag:
                self.click_count = 0
                # Run checkout in a separate thread to not block the mouse listener
                threading.Thread(target=self._check_selection, args=(x, y)).start()
            else:
                # Potential multi-click (Double/Triple)
                now = time.time()
                # Windows default double click speed is usually ~500ms
                if (now - self.last_click_time) < 0.5:
                    self.click_count += 1
                else:
                    self.click_count = 1
                
                self.last_click_time = now

                if self.click_count >= 2:
                    # Double click (2) or Triple click (3) detected
                    # Run check
                    threading.Thread(target=self._check_selection, args=(x, y)).start()

            self.start_pos = None

    def _check_selection(self, mouse_x, mouse_y):
        # Debounce to prevent double triggering
        now = time.time()
        if now - self._last_process_time < 0.5:
            return
        self._last_process_time = now

        # Wait a brief moment for the application to register the selection release
        time.sleep(0.1)

        # Store current clipboard to restore later (optional, but polite)
        # For this MVP, we might skip full restore complexity as it can be flaky,
        # but let's at least grab the new text.
        
        try:
            # Get current clipboard content
            old_text = pyperclip.paste()
            
            # Send Ctrl+C
            with self.keyboard.pressed(Key.ctrl):
                self.keyboard.press('c')
                self.keyboard.release('c')
            
            # Tiny wait for clipboard to update
            time.sleep(0.1)
            
            new_text = pyperclip.paste()
            new_text = new_text.strip()
            
            # Only trigger if text changed and is valid
            # This prevents window dragging (which triggers Ctrl+C but doesn't change clipboard)
            # from showing the popup with old clipboard data.
            if new_text and new_text != old_text:
                # Valid text found, trigger UI
                # We pass the mouse position to spawn the window there
                self.on_selection(new_text, mouse_x, mouse_y)
                
        except Exception as e:
            print(f"Error checking selection: {e}")

