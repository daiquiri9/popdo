import customtkinter as ctk
import webbrowser
import urllib.parse
import re
import threading

class PopDoBar(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PopDo")
        
        # Hide window initially
        self.withdraw()
        
        # Window settings
        self.overrideredirect(True) # Frameless
        self.attributes('-topmost', True)
        self.resizable(False, False)
        
        # Visual styling
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.configure(fg_color="#2b2b2b")
        
        # State
        self.current_text = ""
        
        # Layout container
        self.frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=10)
        self.frame.pack(padx=2, pady=2)
        
        # Buttons
        self.btn_google = self._create_btn("G", self.search_google, "Search Google")
        self.btn_baidu = self._create_btn("B", self.search_baidu, "Search Baidu")
        self.btn_link = self._create_btn("🔗", self.open_link, "Open URL")
        
        # Hide link button by default
        self.btn_link.pack_forget()

        # Auto-hide timer
        self.hide_timer = None

        # Bind focus out to hide (clicks outside)
        self.bind("<FocusOut>", self._on_focus_out)

    def _create_btn(self, text, command, tooltip):
        btn = ctk.CTkButton(
            self.frame,
            text=text,
            width=40,
            height=40,
            command=command,
            corner_radius=8,
            fg_color="#3a3a3a",
            hover_color="#505050",
            font=("Arial", 16, "bold")
        )
        btn.pack(side="left", padx=2)
        return btn

    def show_at(self, text, x, y):
        self.current_text = text
        
        # Check if text contains URL
        url_match = self._extract_url(text)
        if url_match:
            self.btn_link.pack(side="left", padx=2)
            self.current_url = url_match
        else:
            self.btn_link.pack_forget()
            self.current_url = None
            
        # Position window slightly offset from mouse to avoid covering text
        offset_x = 10
        offset_y = 20
        self.geometry(f"+{int(x + offset_x)}+{int(y + offset_y)}")
        
        self.deiconify()
        self.lift()
        # self.focus_force() # Removed to prevent stealing focus from text editor
        
        # Reset hide timer if exists
        self._cancel_timer()

    def handle_external_click(self, x, y):
        if self.state() == "withdrawn":
            return

        # Check if click is inside the window
        wx = self.winfo_rootx()
        wy = self.winfo_rooty()
        ww = self.winfo_width()
        wh = self.winfo_height()

        if wx <= x <= wx + ww and wy <= y <= wy + wh:
            # Inside, do nothing (let button click handle it)
            return
        
        # Outside, hide
        self.hide()

    def hide(self):
        self.withdraw()
        self._cancel_timer()

    def _on_focus_out(self, event):
        # Small delay to allow clicking buttons (which might steal focus temporarily or valid clicks)
        # Actually clicking a button stays within the app usually, but clicking outside should hide.
        # But if we click the button, focus might shift to the button widget.
        # Let's use a robust method: if the new focus is not one of our children, hide.
        # Simpler for now: just hide. Button clicks execute before visual hide typically?
        # No, button click needs to run. 
        # Let's rely on the button command hiding the window, and FocusOut hiding it if missed.
        self.hide()

    def search_google(self):
        query = urllib.parse.quote(self.current_text)
        webbrowser.open(f"https://www.google.com/search?q={query}")
        self.hide()

    def search_baidu(self):
        query = urllib.parse.quote(self.current_text)
        webbrowser.open(f"https://www.baidu.com/s?wd={query}")
        self.hide()
        
    def open_link(self):
        if self.current_url:
            target = self.current_url
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
            webbrowser.open(target)
        self.hide()

    def _extract_url(self, text):
        # Simple regex for URL
        pattern = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def _cancel_timer(self):
        if self.hide_timer:
            self.after_cancel(self.hide_timer)
            self.hide_timer = None

