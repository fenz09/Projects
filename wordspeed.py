import time
import random
import tkinter as tk
import pandas as pd
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
    BG = "#2b2b2b"
    FG = "#dddddd"

    def __init__(self, root):
        self.root = root
        self.root.title("Word Speed Test")
        self.root.geometry("1920x1080")
        self.root.config(bg=self.BG)

        self.passage = ""
        self.start_time = None
        self.typed_index = 0
        self.remaining = self.TEST_DURATION
        self.timer_job = None
        self.results = []

        # --- start screen ---
        self.start_frame = tk.Frame(root, bg=self.BG)
        self.start_frame.pack(expand=True)

        tk.Label(self.start_frame, text="Typing Speed Test", font=("Rubik", 28, "bold"),
                 bg=self.BG, fg=self.FG).pack(pady=(150, 10))
        tk.Label(self.start_frame, text="Choose a test length, then press Start.",
                 font=("Rubik", 14), bg=self.BG, fg=self.FG).pack(pady=(0, 30))
        self.duration_var = tk.IntVar(value=self.TEST_DURATION)
        tk.OptionMenu(self.start_frame, self.duration_var, 30, 60, 90).pack(pady=(0, 20))
        tk.Button(self.start_frame, text="Start", font=("Rubik", 14), width=14,
                  command=self.begin_test).pack()

        # --- test screen (built but not shown until Start is pressed) ---
        self.test_frame = tk.Frame(root, bg=self.BG)
        self.timer_label = tk.Label(self.test_frame, text="Time left: 30s", font=("Rubik", 14, "bold"),
                                     bg=self.BG, fg=self.FG)
        self.timer_label.pack(pady=(0, 20))

        # passage is shown centered on screen; the user types directly, no visible input box
        self.passage_box = tk.Text(self.test_frame, height=10, width=70, wrap="word", font=("Rubik", 16),
                                    bg=self.BG, fg=self.FG, insertwidth=0, relief="flat",
                                    highlightthickness=0, cursor="arrow", padx=20, pady=20)
        self.passage_box.config(state="disabled")
        tk.Label(
            self.test_frame,
            text="Type the passage below as quickly and accurately as you can:",
            font=("Rubik", 14),
            bg=self.BG,
            fg=self.FG
        ).pack(pady=(0, 20))
        self.passage_box.pack()
        self.passage_box.tag_config("correct", foreground="#2ecc71")
        self.passage_box.tag_config("incorrect", foreground="#e74c3c", underline=True)

        self.result_label = tk.Label(self.test_frame, text="", font=("Rubik", 12), bg=self.BG, fg=self.FG)
        self.result_label.pack(pady=(20, 10))

        self.results_box = tk.Text(self.test_frame, height=5, width=85, font=("Courier New", 11),
                       bg="#202020", fg=self.FG, relief="flat", state="disabled")
        self.results_box.pack(pady=(0, 15))

        self.new_btn = tk.Button(self.test_frame, text="Try Again?", command=self.begin_test, width=12)
        self.new_btn.pack()

        self.end_frame = tk.Frame(root, bg=self.BG)
        self.end_frame.pack(expand=True)


    def begin_test(self):
        self.start_frame.pack_forget()
        self.test_frame.pack(expand=True)
        self.passage = generate_passage()#
        self.passage_box.config(foreground = "#DBDB10")
        self.passage_box.config(state="normal")
        self.passage_box.delete("1.0", "end")
        self.passage_box.insert("1.0", self.passage)
        self.passage_box.config(state="disabled")

        self.typed_index = 0
        self.result_label.config(text="")

        self.remaining = self.duration_var.get()
        self.timer_label.config(text=f"Time left: {self.remaining}s")
        self.start_time = time.time()
        self.root.bind("<KeyPress>", self.on_key)
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
            return "break"  # ignore arrows, tab, etc.
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
        return "break"

    def clear_highlight(self, index):
        start = f"1.{index}"
        end = f"1.{index + 1}"
        self.passage_box.tag_remove("correct", start, end)
        self.passage_box.tag_remove("incorrect", start, end)

    def stop(self):
        if self.start_time is None:
            return
        self.root.unbind("<KeyPress>")
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        elapsed = time.time() - self.start_time
        word_count = len(self.passage[:self.typed_index].split())
        wpm = word_count / (elapsed / 60) if elapsed > 0 else 0
        accuracy = (self.typed_index / len(self.passage) * 100) if self.passage else 0
        self.results.append({
            "Attempt": len(self.results) + 1,
            "Time (s)": self.duration_var.get(),
            "Elapsed (s)": round(elapsed, 2),
            "Words": word_count,
            "Accuracy (%)": round(accuracy, 1),
            "WPM": round(wpm, 1),
        })
        results_df = pd.DataFrame(self.results)
        self.result_label.config(text=f"Elapsed: {elapsed:.2f}s | Words typed: {word_count} | WPM: {wpm:.1f}")
        self.results_box.config(state="normal")
        self.results_box.delete("1.0", "end")
        self.results_box.insert("1.0", results_df.to_string(index=False))
        self.results_box.config(state="disabled")
        self.start_time = None


if __name__ == "__main__":
    root = tk.Tk()
    app = WordSpeedApp(root)
    root.mainloop()


