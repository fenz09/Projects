import time
import random
import tkinter as tk
WORD_BANK = [
    "the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "time",
    "space", "light", "water", "fire", "earth", "wind", "music", "art",
    "science", "history", "future", "past", "present", "code", "computer",
    "language", "speed", "test", "type", "write", "read", "learn", "grow",
    "change", "world", "people", "place", "thing", "idea", "story", "book",
    "page", "word", "letter", "number", "system", "process", "result",
    "value", "data", "network", "signal", "energy", "matter", "force",
    "motion", "sound", "color", "shape", "size", "shape", "form", "structure",
    "function", "purpose", "reason", "cause", "effect", "action", "reaction",
    "question", "answer", "problem", "solution", "challenge", "goal",
    "success", "failure", "effort", "practice", "skill", "talent", "focus",
]


def generate_passage(word_count=200):
    """Return a random passage of roughly word_count words."""
    words = random.choices(WORD_BANK, k=word_count)
    return " ".join(words)




class WordSpeedApp:
    TEST_DURATION = 30 

    def __init__(self, root):
        self.root = root
        self.root.title("Word Speed Test")
        self.root.geometry("1920x1080")

        self.passage = ""
        self.start_time = None
        self.typed_index = 0
        self.remaining = self.TEST_DURATION
        self.timer_job = None

        # --- start screen ---
        self.start_frame = tk.Frame(root)
        self.start_frame.pack(expand=True)

        tk.Label(self.start_frame, text="Typing Speed Test", font=("Rubik", 28, "bold")).pack(pady=(150, 10))
        tk.Label(self.start_frame, text="Press Start to begin. Each test lasts 30 seconds.",
                 font=("Rubik", 14)).pack(pady=(0, 30))
        tk.Button(self.start_frame, text="Start", font=("Rubik", 14), width=14,
                  command=self.begin_test).pack()

        # --- test screen (built but not shown until Start is pressed) ---
        self.test_frame = tk.Frame(root)

        self.timer_label = tk.Label(self.test_frame, text="Time left: 30s", font=("Rubik", 14, "bold"))
        self.timer_label.pack(pady=(10, 0))

        tk.Label(self.test_frame, text="Type this passage:", font=("Rubik", 12, "bold")).pack(pady=(10, 0))

        self.passage_box = tk.Text(self.test_frame, height=8, wrap="word", font=("Rubik", 11))
        self.passage_box.config(state="disabled")
        self.passage_box.pack(padx=10, pady=10, fill="both", expand=False)
        self.passage_box.tag_config("correct", foreground="#2ecc71")
        self.passage_box.tag_config("incorrect", foreground="#e74c3c", underline=True)

        self.entry = tk.Text(self.test_frame, height=8, wrap="word", font=("Rubik", 11))
        self.entry.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        self.entry.config(state="disabled")
        self.entry.bind("<KeyPress>", self.on_key)

        btn_frame = tk.Frame(self.test_frame)
        btn_frame.pack(pady=(0, 10))

        self.new_btn = tk.Button(btn_frame, text="Try Again", command=self.begin_test, width=12)
        self.new_btn.pack(side="left", padx=5)

        self.result_label = tk.Label(self.test_frame, text="", font=("Rubik", 11))
        self.result_label.pack(pady=(0, 10))

    def begin_test(self):
        self.start_frame.pack_forget()
        self.test_frame.pack(fill="both", expand=True)

        self.passage = generate_passage()
        self.passage_box.config(state="normal")
        self.passage_box.delete("1.0", "end")
        self.passage_box.insert("1.0", self.passage)
        self.passage_box.config(state="disabled")

        self.entry.config(state="normal")
        self.entry.delete("1.0", "end")
        self.typed_index = 0
        self.result_label.config(text="")

        self.remaining = self.TEST_DURATION
        self.timer_label.config(text=f"Time left: {self.remaining}s")
        self.start_time = time.time()
        self.entry.focus_set()
        self.tick()

    def tick(self):
        if self.remaining <= 0:
            self.stop()
            return
        self.timer_label.config(text=f"Time left: {self.remaining}s")
        self.remaining -= 1
        self.timer_job = self.root.after(1000, self.tick)

    def on_key(self, event):
        if self.start_time is None:
            return "break"
        if event.keysym == "BackSpace":
            if self.typed_index > 0:
                self.typed_index -= 1
                self.clear_highlight(self.typed_index)
            return None
        if not event.char or len(event.char) != 1:
            return "break"  # block arrows, tab, etc.
        if self.typed_index >= len(self.passage):
            return "break"
        expected_char = self.passage[self.typed_index]
        start = f"1.{self.typed_index}"
        end = f"1.{self.typed_index + 1}"
        if event.char == expected_char:
            self.passage_box.tag_remove("incorrect", start, end)
            self.passage_box.tag_add("correct", start, end)
            self.typed_index += 1
            if self.typed_index >= len(self.passage):
                self.stop()
            return None
        self.passage_box.tag_add("incorrect", start, end)
        return "break"  # wrong letter: block it from being typed

    def clear_highlight(self, index):
        start = f"1.{index}"
        end = f"1.{index + 1}"
        self.passage_box.tag_remove("correct", start, end)
        self.passage_box.tag_remove("incorrect", start, end)

    def stop(self):
        if self.start_time is None:
            return
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        elapsed = time.time() - self.start_time
        typed = self.entry.get("1.0", "end").strip()
        word_count = len(typed.split())
        wpm = word_count / (elapsed / 60) if elapsed > 0 else 0
        self.result_label.config(text=f"Elapsed: {elapsed:.2f}s | Words typed: {word_count} | WPM: {wpm:.1f}")
        self.start_time = None
        self.entry.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = WordSpeedApp(root)
    root.mainloop()

