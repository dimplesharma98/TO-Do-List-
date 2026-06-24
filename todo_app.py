import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
#  DATA FILE  (saves your tasks automatically)
# ─────────────────────────────────────────────
DATA_FILE = "tasks.json"
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

# ─────────────────────────────────────────────
#  MAIN APPLICATION CLASS
# ─────────────────────────────────────────────
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 My To-Do List")
        self.root.geometry("900x750")
        self.root.configure(bg="#F8FAFC")
        self.root.resizable(True, True)

        self.tasks = load_tasks()
        self.filter_mode = "All"

        self.build_ui()
        self.refresh_list()

    # ──────────────────────────────────────────
    #  BUILD UI
    # ──────────────────────────────────────────
    def build_ui(self):
        # ── Title Bar ──
        title_frame = tk.Frame(self.root, bg="#7C3AED", pady=14)
        title_frame.pack(fill="x")

        tk.Label(
            title_frame, text="📝 My To-Do List",
            font=("Segoe UI", 18, "bold"),
            bg="#7C3AED", fg="white"
        ).pack()

        tk.Label(
            title_frame, text="Organize • Prioritize • Achieve",
            font=("Segoe UI", 10),
          bg="#7C3AED", fg="#FFFFFF"
        ).pack()

        # ── Stats Bar ──
        self.stats_frame = tk.Frame(self.root, bg="#8B5CF6", pady=8)
        self.stats_frame.pack(fill="x")

        self.lbl_total   = self._stat_label("Total: 0")
        self.lbl_done    = self._stat_label("Done: 0")
        self.lbl_pending = self._stat_label("Pending: 0")

        # ── Input Area ──
        input_frame = tk.Frame(self.root, bg="#F0F4F8", pady=14, padx=16)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="Task:", font=("Segoe UI", 11),
                 bg="#F0F4F8", fg="#333").grid(row=0, column=0, padx=(0,6))

        self.task_entry = tk.Entry(
            input_frame, font=("Segoe UI", 12), width=32,
            relief="flat", bd=0, bg="white", fg="#222",
            highlightthickness=1, highlightbackground="#CBD5E0",
            highlightcolor="#378ADD"
        )
        self.task_entry.grid(row=0, column=1, ipady=6, padx=(0,8))
        self.task_entry.bind("<Return>", lambda e: self.add_task())

        tk.Label(input_frame, text="Priority:", font=("Segoe UI", 11),
                 bg="#F0F4F8", fg="#333").grid(row=0, column=2, padx=(0,6))

        self.priority_var = tk.StringVar(value="Medium")
        priority_menu = ttk.Combobox(
            input_frame, textvariable=self.priority_var,
            values=["High", "Medium", "Low"],
            state="readonly", width=9, font=("Segoe UI", 11)
        )
        priority_menu.grid(row=0, column=3, ipady=4, padx=(0,10))

        add_btn = tk.Button(
            input_frame, text="+ Add Task",
            font=("Segoe UI", 11, "bold"),
            bg="#6D28D9", fg="white", relief="flat",
            padx=14, pady=6, cursor="hand2",
            command=self.add_task,
            activebackground="#5B21B6", activeforeground="white"
        )
        add_btn.grid(row=0, column=4)

        # ── Filter Buttons ──
        filter_frame = tk.Frame(self.root, bg="#F0F4F8", padx=16)
        filter_frame.pack(fill="x", pady=(0, 8))

        tk.Label(filter_frame, text="Filter:", font=("Segoe UI", 10),
                 bg="#F0F4F8", fg="#666").pack(side="left", padx=(0,8))

        self.filter_buttons = {}
        for label in ["All", "Pending", "Done", "High", "Medium", "Low"]:
            btn = tk.Button(
                filter_frame, text=label,
                font=("Segoe UI", 10),
                relief="flat", padx=10, pady=4,
                cursor="hand2",
                command=lambda l=label: self.set_filter(l)
            )
            btn.pack(side="left", padx=3)
            self.filter_buttons[label] = btn

        self._highlight_filter("All")

        # ── Task List ──
        list_frame = tk.Frame(self.root, bg="#F0F4F8", padx=16)
        list_frame.pack(fill="both", expand=True, pady=(0,8))

        columns = ("status", "task", "priority", "date")
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="headings",
            selectmode="browse", height=10
        )

        self.tree.heading("status",   text="✓")
        self.tree.heading("task",     text="Task")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("date",     text="Added On")

        self.tree.column("status",   width=40,  anchor="center", stretch=False)
        self.tree.column("task",     width=300, anchor="w")
        self.tree.column("priority", width=90,  anchor="center", stretch=False)
        self.tree.column("date",     width=120, anchor="center", stretch=False)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         font=("Segoe UI", 11),
                         rowheight=30,
                         background="white",
                         fieldbackground="white",
                         foreground="#222")
        style.configure("Treeview.Heading",
                         font=("Segoe UI", 11, "bold"),
                         background="#7C3AED",
                         foreground="white",
                         relief="flat")
        style.map("Treeview", background=[("selected", "#D0E8FF")])

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # colour tags
        self.tree.tag_configure("done",   foreground="#999", font=("Segoe UI", 11, "overstrike"))
        self.tree.tag_configure("high",   foreground="#A32D2D")
        self.tree.tag_configure("medium", foreground="#94960B")
        self.tree.tag_configure("low",    foreground="#3B6D11")

        # ── Action Buttons ──
        btn_frame = tk.Frame(self.root, bg="#F0F4F8", pady=10, padx=16)
        btn_frame.pack(fill="x")

        for text, cmd, color in [
            ("✅  Mark Done",    self.mark_done,    "#1D9E75"),
            ("🗑️  Delete Task",  self.delete_task,  "#C0392B"),
            ("🧹  Clear Done",   self.clear_done,   "#8E44AD"),
            ("✏️  Edit Task",    self.edit_task,    "#2980B9"),
        ]:
            tk.Button(
                btn_frame, text=text,
                font=("Segoe UI", 10, "bold"),
                bg=color, fg="white", relief="flat",
                padx=12, pady=7, cursor="hand2",
                command=cmd,
                activeforeground="white"
            ).pack(side="left", padx=5)

    # ──────────────────────────────────────────
    #  STAT LABELS HELPER
    # ──────────────────────────────────────────
    def _stat_label(self, text):
        lbl = tk.Label(self.stats_frame, text=text,
                       font=("Segoe UI", 11, "bold"),
                      bg="#8B5CF6", fg="white", padx=20)
        lbl.pack(side="left")
        return lbl

    # ──────────────────────────────────────────
    #  FILTER HIGHLIGHT
    # ──────────────────────────────────────────
    def _highlight_filter(self, active):
        for label, btn in self.filter_buttons.items():
            if label == active:
                btn.config(bg="#6D28D9", fg="white")
            else:
                btn.config(bg="#E2E8F0", fg="#444")

    def set_filter(self, mode):
        self.filter_mode = mode
        self._highlight_filter(mode)
        self.refresh_list()

    # ──────────────────────────────────────────
    #  CRUD OPERATIONS
    # ──────────────────────────────────────────
    def add_task(self):
        text = self.task_entry.get().strip()
        if not text:
            messagebox.showwarning("Empty Task", "Please type a task first!")
            return
        task = {
            "text":     text,
            "priority": self.priority_var.get(),
            "done":     False,
            "date":     datetime.now().strftime("%d %b %Y")
        }
        self.tasks.append(task)
        save_tasks(self.tasks)
        self.task_entry.delete(0, tk.END)
        self.refresh_list()

    def mark_done(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Task", "Please select a task first.")
            return
        idx = self.tree.index(selected[0])
        visible = self._filtered_tasks()
        task = visible[idx]
        task["done"] = not task["done"]
        save_tasks(self.tasks)
        self.refresh_list()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Task", "Please select a task to delete.")
            return
        idx = self.tree.index(selected[0])
        visible = self._filtered_tasks()
        task = visible[idx]
        if messagebox.askyesno("Delete", f'Delete "{task["text"]}"?'):
            self.tasks.remove(task)
            save_tasks(self.tasks)
            self.refresh_list()

    def clear_done(self):
        done_count = sum(1 for t in self.tasks if t["done"])
        if done_count == 0:
            messagebox.showinfo("Nothing to Clear", "No completed tasks found.")
            return
        if messagebox.askyesno("Clear Done", f"Remove all {done_count} completed task(s)?"):
            self.tasks = [t for t in self.tasks if not t["done"]]
            save_tasks(self.tasks)
            self.refresh_list()

    def edit_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Task", "Please select a task to edit.")
            return
        idx = self.tree.index(selected[0])
        visible = self._filtered_tasks()
        task = visible[idx]

        win = tk.Toplevel(self.root)
        win.title("Edit Task")
        win.geometry("400x160")
        win.configure(bg="#F0F4F8")
        win.grab_set()

        tk.Label(win, text="Edit Task:", font=("Segoe UI", 11),
                 bg="#F0F4F8").pack(pady=(16,4))

        entry = tk.Entry(win, font=("Segoe UI", 12), width=36,
                         relief="flat", highlightthickness=1,
                         highlightbackground="#CBD5E0")
        entry.insert(0, task["text"])
        entry.pack(ipady=6, padx=20)
        entry.focus()

        def save_edit():
            new_text = entry.get().strip()
            if not new_text:
                messagebox.showwarning("Empty", "Task cannot be empty!", parent=win)
                return
            task["text"] = new_text
            save_tasks(self.tasks)
            self.refresh_list()
            win.destroy()

        tk.Button(win, text="Save", font=("Segoe UI", 11, "bold"),
                  bg="#185FA5", fg="white", relief="flat",
                  padx=20, pady=6, cursor="hand2",
                  command=save_edit).pack(pady=12)
        entry.bind("<Return>", lambda e: save_edit())

    # ──────────────────────────────────────────
    #  HELPERS
    # ──────────────────────────────────────────
    def _filtered_tasks(self):
        f = self.filter_mode
        if f == "All":     return list(self.tasks)
        if f == "Pending": return [t for t in self.tasks if not t["done"]]
        if f == "Done":    return [t for t in self.tasks if t["done"]]
        return [t for t in self.tasks if t["priority"] == f]

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        visible = self._filtered_tasks()
        for task in visible:
            status = "✅" if task["done"] else "⬜"
            tag = "done" if task["done"] else task["priority"].lower()
            self.tree.insert("", "end",
                             values=(status, task["text"], task["priority"], task["date"]),
                             tags=(tag,))

        total   = len(self.tasks)
        done    = sum(1 for t in self.tasks if t["done"])
        pending = total - done
        self.lbl_total.config(  text=f"  Total: {total}  ")
        self.lbl_done.config(   text=f"  Done: {done}  ")
        self.lbl_pending.config(text=f"  Pending: {pending}  ")


# ─────────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()