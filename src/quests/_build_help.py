import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import uuid


class DataEntryForm:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Entry Form")
        self.root.geometry("850x750")

        # Main container
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Data storage
        self.data = {
            "id": "",
            "name": "",
            "description": "",
            "content": "",
            "pos": 0,
            "father_id": "",
            "disp": "",
            "prerequisites": [],
            "requirements": []
        }

        self.create_widgets(main_frame)

    def create_widgets(self, parent):
        row = 0

        # ID field
        ttk.Label(parent, text="ID:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))

        id_frame = ttk.Frame(parent)
        id_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        self.id_var = tk.StringVar()
        self.id_entry = ttk.Entry(id_frame, textvariable=self.id_var, width=40)
        self.id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(id_frame, text="Generate", command=self.generate_id,
                   width=10).pack(side=tk.RIGHT, padx=(5, 0))
        row += 1

        # Father ID field (optional parent reference)
        ttk.Label(parent, text="Father ID:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        self.father_id_var = tk.StringVar()
        self.father_id_entry = ttk.Entry(parent, textvariable=self.father_id_var, width=50)
        self.father_id_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1



        # Father ID field (optional parent reference)
        ttk.Label(parent, text="Display", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        self.disp_var = tk.StringVar()
        self.disp_entry = ttk.Entry(parent, textvariable=self.disp_var, width=50)
        self.disp_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1

        # Position field
        ttk.Label(parent, text="PositionX:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))

        pos_frame = ttk.Frame(parent)
        pos_frame.grid(row=row, column=1, sticky=(tk.W), pady=(0, 5))

        self.pos_var = tk.IntVar(value=0)
        self.pos_spinbox = ttk.Spinbox(pos_frame, from_=-10000, to=10000,
                                       textvariable=self.pos_var, width=10)
        self.pos_spinbox.pack(side=tk.LEFT)

        row += 1

        # Position field
        ttk.Label(parent, text="PositionY:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))

        posy_frame = ttk.Frame(parent)
        posy_frame.grid(row=row, column=1, sticky=(tk.W), pady=(0, 5))

        self.posy_var = tk.IntVar(value=0)
        self.posy_spinbox = ttk.Spinbox(posy_frame, from_=-10000, to=10000,
                                       textvariable=self.posy_var, width=10)
        self.posy_spinbox.pack(side=tk.RIGHT)

        ttk.Label(pos_frame, text=" (Order/sequence number)").pack(side=tk.LEFT, padx=(5, 0))
        row += 1

        # Separator
        ttk.Separator(parent, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Name field
        ttk.Label(parent, text="Name:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(parent, textvariable=self.name_var, width=50)
        self.name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1

        # Description field
        ttk.Label(parent, text="Description:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.NW, pady=(0, 5))
        self.desc_text = scrolledtext.ScrolledText(parent, width=50, height=4)
        self.desc_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1

        # Content field
        ttk.Label(parent, text="Content:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.NW, pady=(0, 5))
        self.content_text = scrolledtext.ScrolledText(parent, width=50, height=6)
        self.content_text.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1

        # Prerequisites section
        ttk.Label(parent, text="Prerequisites:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.NW, pady=(0, 5))

        pre_frame = ttk.Frame(parent)
        pre_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        self.pre_listbox = tk.Listbox(pre_frame, height=4, width=40)
        self.pre_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        pre_btn_frame = ttk.Frame(pre_frame)
        pre_btn_frame.pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(pre_btn_frame, text="Add", command=self.add_prerequisite,
                   width=10).pack(pady=(0, 5))
        ttk.Button(pre_btn_frame, text="Remove", command=self.remove_prerequisite,
                   width=10).pack(pady=(0, 5))
        ttk.Button(pre_btn_frame, text="Clear All", command=self.clear_prerequisites,
                   width=10).pack()

        self.pre_entry = ttk.Entry(pre_frame, width=30)
        self.pre_entry.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        self.pre_entry.bind('<Return>', lambda e: self.add_prerequisite())

        row += 1

        # Requirements section
        ttk.Label(parent, text="Requirements:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.NW, pady=(0, 5))

        req_frame = ttk.Frame(parent)
        req_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        self.req_listbox = tk.Listbox(req_frame, height=4, width=40)
        self.req_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        req_btn_frame = ttk.Frame(req_frame)
        req_btn_frame.pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(req_btn_frame, text="Add", command=self.add_requirement,
                   width=10).pack(pady=(0, 5))
        ttk.Button(req_btn_frame, text="Remove", command=self.remove_requirement,
                   width=10).pack(pady=(0, 5))
        ttk.Button(req_btn_frame, text="Clear All", command=self.clear_requirements,
                   width=10).pack()

        self.req_entry = ttk.Entry(req_frame, width=30)
        self.req_entry.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        self.req_entry.bind('<Return>', lambda e: self.add_requirement())

        row += 1

        # Action buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Save Data", command=self.save_data,
                   width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Data", command=self.load_data,
                   width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form,
                   width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Show Data", command=self.show_data,
                   width=15).pack(side=tk.LEFT, padx=5)

    def generate_id(self):
        """Generate a unique ID"""
        new_id = str(uuid.uuid4())[:8]  # First 8 chars of UUID
        self.id_var.set(new_id)

    def add_prerequisite(self):
        pre = self.pre_entry.get().strip()
        if pre:
            self.pre_listbox.insert(tk.END, pre)
            self.pre_entry.delete(0, tk.END)

    def remove_prerequisite(self):
        selection = self.pre_listbox.curselection()
        if selection:
            self.pre_listbox.delete(selection[0])

    def clear_prerequisites(self):
        self.pre_listbox.delete(0, tk.END)

    def add_requirement(self):
        req = self.req_entry.get().strip()
        if req:
            self.req_listbox.insert(tk.END, req)
            self.req_entry.delete(0, tk.END)

    def remove_requirement(self):
        selection = self.req_listbox.curselection()
        if selection:
            self.req_listbox.delete(selection[0])

    def clear_requirements(self):
        self.req_listbox.delete(0, tk.END)

    def collect_data(self):
        """Collect all form data into dictionary"""
        self.data["id"] = self.id_var.get()
        self.data["father_id"] = self.father_id_var.get()
        self.data["pos"] = self.pos_var.get()
        self.data["posy"] = self.posy_var.get()
        self.data["name"] = self.name_var.get()
        self.data["disp"] = self.disp_var.get()
        self.data["description"] = self.desc_text.get("1.0", tk.END).strip().replace('\n', '\\n')
        self.data["content"] = self.content_text.get("1.0", tk.END).strip().replace('\n', '\\n')

        # Get prerequisites as list
        self.data["prerequisites"] = list(self.pre_listbox.get(0, tk.END))

        # Get requirements as list
        self.data["requirements"] = list(self.req_listbox.get(0, tk.END))

        return self.data

    def save_data(self):
        """Save data to JSON file"""
        data = self.collect_data()

        # Check if ID is provided
        if not data["id"]:
            messagebox.showwarning("Warning", "Please enter or generate an ID")
            return

        try:

            dt = (f'single.QUEST_NAME["{self.data['father_id']}"].add_child(single.QuestBlock(qid="{self.data['id']}",'
                  f' name="{self.data['name']}", desc="{self.data['description']}", content="{self.data['content']}",'
                  f' reqs=[{", ".join(self.data["requirements"])}], req_num={len(self.data["requirements"])}, '
                  f'pos={(self.data['pos'], self.data['posy'])}, disp="{self.data['disp']}", '
                  f'pre=[{", ".join(self.data["prerequisites"])}],))')
            dt += "\n# insert"

            with open("./build.py") as f:
                st = f.read()
                f.close()
                with open('./build.py', "w") as f2:
                    f2.write(st.replace("# insert", dt))
                    f2.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

    def load_data(self):
        """Load data from JSON file"""
        from tkinter import filedialog

        filename = filedialog.askopenfilename(
            title="Select data file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, "r") as f:
                    data = json.load(f)

                # Populate form fields
                self.id_var.set(data.get("id", ""))
                self.father_id_var.set(data.get("father_id", ""))
                self.pos_var.set(data.get("pos", 0))
                self.name_var.set(data.get("name", ""))

                self.desc_text.delete("1.0", tk.END)
                self.desc_text.insert("1.0", data.get("description", ""))

                self.content_text.delete("1.0", tk.END)
                self.content_text.insert("1.0", data.get("content", ""))

                # Clear and repopulate prerequisites
                self.clear_prerequisites()
                for pre in data.get("prerequisites", []):
                    self.pre_listbox.insert(tk.END, pre)

                # Clear and repopulate requirements
                self.clear_requirements()
                for req in data.get("requirements", []):
                    self.req_listbox.insert(tk.END, req)

                messagebox.showinfo("Success", f"Loaded data from {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")

    def clear_form(self):
        """Clear all form fields"""
        self.id_var.set("")
        self.father_id_var.set("")
        self.pos_var.set(0)
        self.name_var.set("")
        self.desc_text.delete("1.0", tk.END)
        self.content_text.delete("1.0", tk.END)
        self.clear_prerequisites()
        self.clear_requirements()
        self.pre_entry.delete(0, tk.END)
        self.req_entry.delete(0, tk.END)

    def show_data(self):
        """Display collected data in a new window"""
        data = self.collect_data()

        # Create new window
        data_window = tk.Toplevel(self.root)
        data_window.title("Collected Data")
        data_window.geometry("600x500")

        # Create text widget to display data
        text_widget = scrolledtext.ScrolledText(data_window, width=70, height=25)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Format and display data
        formatted_data = f"ID: {data['id']}\n"
        formatted_data += f"Father ID: {data['father_id']}\n"
        formatted_data += f"Position: {data['pos']}\n"
        formatted_data += "=" * 50 + "\n\n"
        formatted_data += f"Name: {data['name']}\n\n"
        formatted_data += f"Description:\n{data['description']}\n\n"
        formatted_data += f"Content:\n{data['content']}\n\n"

        formatted_data += "Prerequisites:\n"
        if data['prerequisites']:
            for i, pre in enumerate(data['prerequisites'], 1):
                formatted_data += f"  {i}. {pre}\n"
        else:
            formatted_data += "  (None)\n"

        formatted_data += "\nRequirements:\n"
        if data['requirements']:
            for i, req in enumerate(data['requirements'], 1):
                formatted_data += f"  {i}. {req}\n"
        else:
            formatted_data += "  (None)\n"

        text_widget.insert("1.0", formatted_data)
        text_widget.configure(state='disabled')


def main():
    root = tk.Tk()
    app = DataEntryForm(root)
    root.mainloop()


if __name__ == "__main__":
    main()