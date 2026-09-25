# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
# tkinter = Python's built-in GUI library. We nickname it "tk".
import tkinter as tk

# ttk = themed widgets (Frame, Label, Button, Scrollbar).
from tkinter import ttk

# Text shown at the start of each new input line (like a real console prompt).
PROMPT = "> "


def main() -> None:
    """
    Build a console-style window:
      - File menu at the TOP (dropdown -> Clear Console)
      - type commands DIRECTLY inside the console (cursor lives in the console)
      - two buttons on the RIGHT (each prints a message into the console)
    """

    # -----------------------------------------------------------------------
    # WINDOW SETUP (same size as before)
    # -----------------------------------------------------------------------
    root = tk.Tk()                          # create the main window
    root.title("Welcome to Syamel's UI")    # title bar text
    root.geometry("960x480")                # wider so canvas + console fit side by side
    root.minsize(720, 320)                  # do not allow shrinking too small

    # Outer padding so widgets are not stuck to the window edges.
    frame = ttk.Frame(root, padding=12)
    frame.pack(fill=tk.BOTH, expand=True)   # fill the whole window

    # -----------------------------------------------------------------------
    # MAIN AREA: console | canvas | buttons  (left -> right)
    # -----------------------------------------------------------------------
    content_row = ttk.Frame(frame)
    content_row.pack(fill=tk.BOTH, expand=True)

    # Pack BUTTONS FIRST on the RIGHT so they always keep their width.
    button_frame = ttk.Frame(content_row)
    button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 0))

    # Console container (text + scrollbar) — LEFT side, equal expand with canvas.
    console_frame = ttk.Frame(content_row)
    console_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

    # -----------------------------------------------------------------------
    # CANVAS — RIGHT of the console, same proportional size (side by side)
    # -----------------------------------------------------------------------
    # Pack canvas AFTER the console so it sits to the right of the console
    # (and still LEFT of the buttons). fill=BOTH + expand=True keeps canvas
    # the SAME share of width/height as the console next to it.
    canvas = tk.Canvas(
        content_row,
        bg="white",                         # white drawing surface
        highlightthickness=1,               # thin border so the canvas edge is visible
        highlightbackground="#3c3c3c",
        cursor="crosshair",                 # shows you’re aimed at a clickable canvas
    )
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Vertical scrollbar for the console.
    scrollbar = ttk.Scrollbar(console_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # -----------------------------------------------------------------------
    # CONSOLE — type here with a real blinking cursor (no separate text field)
    # -----------------------------------------------------------------------
    # state stays NORMAL so the caret (cursor) is visible and you can type.
    console = tk.Text(
        console_frame,
        wrap=tk.WORD,                       # wrap long lines at word breaks
        yscrollcommand=scrollbar.set,       # keep scrollbar in sync while scrolling
        font=("Consolas", 11),              # monospace font = classic console look
        bg="#1e1e1e",                       # dark background
        fg="#d4d4d4",                       # light gray text
        insertbackground="#ffffff",         # white blinking caret inside the console
        padx=8,
        pady=8,
        width=40,                           # preferred width in characters
        height=20,                          # preferred height in lines
    )
    console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=console.yview)  # dragging scrollbar scrolls the console

    # "input_start" marks where the current command begins (right after "> ").
    # Everything AFTER line 1 is history and should not be edited.
    # Prompt lives on line 1 (TOP) so the latest input stays visible.
    console.mark_set("input_start", "1.0")
    console.mark_gravity("input_start", tk.LEFT)  # mark stays put when we type after it

    # -----------------------------------------------------------------------
    # SIMPLE METHODS
    # -----------------------------------------------------------------------
    def show_prompt() -> None:
        """
        Put a fresh '> ' prompt on LINE 1 (the TOP of the console).

        Notes:
          - Keeping the input line at the top means you always see what you type,
            even after lots of output fills the console.
          - console.see("1.0") scrolls the view to the TOP (not the bottom).
        """
        # Wipe line 1 if it already has text, then write a clean prompt.
        console.delete("1.0", "1.end")
        console.insert("1.0", PROMPT)                       # "> " at the very top
        console.mark_set("input_start", f"1.0 + {len(PROMPT)}c")  # after "> "
        console.mark_set(tk.INSERT, "input_start")          # blinking cursor after "> "
        console.see("1.0")                                  # stay scrolled to the TOP

    def console_print(message: str) -> None:
        """
        Print text under the prompt (starting at line 2).

        Notes:
          - Inserting at "2.0" puts each NEW message right under the prompt,
            so the latest text stays near the top (older lines get pushed down).
          - We scroll to "1.0" so the view stays at the top (input + latest text).
        """
        # Right under the prompt line = newest message near the top.
        console.insert("2.0", message + "\n")
        console.see("1.0")  # keep TOP visible (do NOT jump to the bottom)

    def clear_console() -> None:
        """Erase the console and show a new prompt at the top."""
        console.delete("1.0", tk.END)   # delete everything
        show_prompt()                   # start a fresh input line at the top

    def get_command() -> str:
        """Read only the text the user typed after '> ' on line 1."""
        # Line 1 only — history below must not be part of the command.
        return console.get("input_start", "1.end").strip()

    def run_command(_event: tk.Event | None = None) -> str:
        """
        When Enter is pressed: take the typed command, print a result, reset prompt.

        Special commands:
          clear / cls  -> wipe the console
          loop N       -> print N lines in a loop (example: loop 20)
          help         -> show a short help message

        Anything else is echoed as output.
        Returns "break" so Enter does not also insert a normal blank line.
        """
        command = get_command()

        # Clear what was typed on the prompt line (keep the prompt via show_prompt later).
        console.delete("input_start", "1.end")

        if not command:
            # Empty Enter -> just keep the prompt ready.
            console.mark_set(tk.INSERT, "input_start")
            console.see("1.0")
            return "break"

        lower = command.lower()

        if lower in ("clear", "cls"):
            clear_console()
            console_print("Console cleared.")
            # Prompt is already on line 1; put the cursor back after "> ".
            console.mark_set(tk.INSERT, "input_start")

        elif lower.startswith("loop"):
            parts = command.split()
            try:
                count = int(parts[1]) if len(parts) > 1 else 10
            except ValueError:
                count = 10
            # Cap so a huge number does not freeze the window for too long.
            count = max(1, min(count, 10000))
            for i in range(1, count + 1):
                console_print(f"loop line {i}")
            console.mark_set(tk.INSERT, "input_start")
            console.see("1.0")

        elif lower == "help":
            console_print("Commands:")
            console_print("  help          - show this help")
            console_print("  clear / cls   - clear the console")
            console_print("  loop N        - print N lines (e.g. loop 20)")
            console_print("  anything else - print it to the console")
            console.mark_set(tk.INSERT, "input_start")
            console.see("1.0")

        else:
            console_print(command)
            console.mark_set(tk.INSERT, "input_start")
            console.see("1.0")

        return "break"  # stop the default Text widget Enter behavior

    def protect_history(event: tk.Event) -> str | None:
        """
        Stop the user from deleting or typing inside old console history.

        Only the text AFTER the '> ' prompt on LINE 1 (top) is editable.
        """
        # Keys that only move the cursor — always allow.
        if event.keysym in {
            "Left", "Right", "Up", "Down", "Home", "End",
            "Prior", "Next", "Escape", "Return",
        }:
            return None

        # If the cursor left the prompt line (line 1), jump it back to the input.
        # "2.0" = start of line 2 = beginning of history under the prompt.
        if console.compare(tk.INSERT, ">=", "2.0") or console.compare(tk.INSERT, "<", "input_start"):
            console.mark_set(tk.INSERT, "1.end")  # back to the end of the input line
            return "break"

        # Block Backspace if it would erase into the prompt itself.
        if event.keysym == "BackSpace" and console.compare(tk.INSERT, "==", "input_start"):
            return "break"

        return None

    def on_button1() -> None:
        """Button 1 click -> print a message into the console."""
        console_print("Button 1 pressed")
        console.mark_set(tk.INSERT, "1.end")  # keep the cursor on the top input line
        console.focus_set()

    def on_button2() -> None:
        """Button 2 click -> print a message into the console."""
        console_print("Button 2 pressed")
        console.mark_set(tk.INSERT, "1.end")
        console.focus_set()

    def on_file_clear() -> None:
        """
        File menu -> Clear Console.

        Wipes all console text, shows a fresh prompt at the top, and puts the cursor back.
        """
        clear_console()                         # erase everything + new "> " at top
        console_print("Console cleared.")       # confirm message under the prompt
        console.mark_set(tk.INSERT, "1.end")    # cursor stays on the top input line
        console.focus_set()

    def on_canvas_click(event: tk.Event) -> None:
        """
        Mouse listener for the canvas (left button push / click).

        Every time you click any point on the canvas, this runs and prints
        the click's x and y coordinates into the console.

        Notes:
          - event.x = horizontal pixel from the canvas LEFT edge (0 = left)
          - event.y = vertical pixel from the canvas TOP edge (0 = top)
          - Bound with <Button-1>, which means the left mouse button.
        """
        # Print coordinates into the console (same helper the buttons use).
        console_print(f"Canvas click: x={event.x}, y={event.y}")
        console.mark_set(tk.INSERT, "1.end")  # keep the cursor on the top input line
        console.focus_set()

    # -----------------------------------------------------------------------
    # MENU BAR — File tab at the top with a dropdown
    # -----------------------------------------------------------------------
    # Menu() with tearoff=0 builds a menu. tearoff=0 removes the old dotted
    # "----" tear-off line at the top of dropdowns (cleaner look).
    menu_bar = tk.Menu(root, tearoff=0)

    # Attach this menu bar to the window (shows across the top of the app).
    root.config(menu=menu_bar)

    # The File dropdown itself (another Menu attached under "File").
    file_menu = tk.Menu(menu_bar, tearoff=0)

    # add_cascade = put a top-level tab named "File" that opens file_menu.
    # Click "File" -> dropdown appears underneath.
    menu_bar.add_cascade(label="File", menu=file_menu)

    # add_command = one clickable item inside the File dropdown.
    # When pressed, it runs on_file_clear() which clears the console.
    file_menu.add_command(label="Clear Console", command=on_file_clear)

    # -----------------------------------------------------------------------
    # KEY BINDINGS — type and run commands inside the console
    # -----------------------------------------------------------------------
    # Enter runs the command typed after "> ".
    console.bind("<Return>", run_command)

    # Block edits that would mess up old output / the prompt.
    console.bind("<Key>", protect_history)

    # -----------------------------------------------------------------------
    # THE TWO BUTTONS (RIGHT SIDE)
    # -----------------------------------------------------------------------
    # command= is the function called when the button is clicked (no arguments).
    ttk.Button(
        button_frame,
        text="Button 1",
        width=12,
        command=on_button1,                 # click -> on_button1() -> console_print(...)
    ).pack(pady=(0, 8), fill=tk.X)

    ttk.Button(
        button_frame,
        text="Button 2",
        width=12,
        command=on_button2,                 # click -> on_button2() -> console_print(...)
    ).pack(fill=tk.X)

    # Mouse listener: left-button push on the canvas -> on_canvas_click(event)
    # <Button-1> = left mouse button (Button-2 = middle, Button-3 = right).
    # Bound here (after on_canvas_click exists); canvas itself is created above.
    canvas.bind("<Button-1>", on_canvas_click)

    # -----------------------------------------------------------------------
    # STARTUP MESSAGE + CURSOR INSIDE THE CONSOLE
    # -----------------------------------------------------------------------
    # Prompt first (line 1 at the TOP), then messages under it (latest near top).
    show_prompt()                           # show "> " on line 1 and put the cursor after it
    console_print("Console ready. Type here and press Enter.")
    console_print("Try: help  |  loop 20  |  clear")
    console_print("Or click Button 1 / Button 2.")
    console.mark_set(tk.INSERT, "1.end")    # cursor stays on the top input line

    console.focus_set()                     # keyboard focus goes straight into the console

    # Start the GUI event loop (keeps the window open and handles clicks/keys).
    root.mainloop()


# ---------------------------------------------------------------------------
# SCRIPT ENTRY POINT
# ---------------------------------------------------------------------------
# Run main() only when this file is executed directly (not when imported).
if __name__ == "__main__":
    main()
