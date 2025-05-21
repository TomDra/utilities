import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def safe_listdir(path):
    try:
        return sorted(os.listdir(path))
    except Exception as e:
        return [f"[Error reading {path}: {e}]"]

def get_folder_tree_raw(path):
    paths = [os.path.join(root_dir, name)
             for root_dir, dirs, files in os.walk(path)
             for name in dirs + files]
    return paths


def get_folder_tree_text(path, indent=""):
    output = []
    items = safe_listdir(path)
    for i, item in enumerate(items):
        full_path = os.path.join(path, item)
        prefix = "└── " if i == len(items) - 1 else "├── "
        output.append(indent + prefix + item)
        if os.path.isdir(full_path):
            extension = "    " if i == len(items) - 1 else "│   "
            output.extend(get_folder_tree_text(full_path, indent + extension))
    return output

def get_folder_tree_markdown(path, level=0):
    md_lines = []
    for item in safe_listdir(path):
        full_path = os.path.join(path, item)
        md_lines.append(f"{'  ' * level}- {item}")
        if os.path.isdir(full_path):
            md_lines.extend(get_folder_tree_markdown(full_path, level + 1))
    return md_lines

def get_folder_tree_json(path):
    tree = {}
    for item in safe_listdir(path):
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            tree[item] = get_folder_tree_json(full_path)
        else:
            tree[item] = None
    return tree

def get_folder_tree_csv(path):
    return [os.path.join(root, name) for root, dirs, files in os.walk(path) for name in dirs + files]

def get_folder_tree_html(path):
    def build_ul(path):
        items = safe_listdir(path)
        html = "<ul>"
        for item in items:
            full_path = os.path.join(path, item)
            html += f"<li>{item}"
            if os.path.isdir(full_path):
                html += build_ul(full_path)
            html += "</li>"
        html += "</ul>"
        return html
    return [build_ul(path)]

def get_folder_tree_xml(path, indent=""):
    lines = []
    for item in safe_listdir(path):
        full_path = os.path.join(path, item)
        tag = "folder" if os.path.isdir(full_path) else "file"
        lines.append(f"{indent}<{tag} name=\"{item}\">")
        if os.path.isdir(full_path):
            lines.extend(get_folder_tree_xml(full_path, indent + "  "))
        lines.append(f"{indent}</{tag}>")
    return lines

def update_output(*args):
    if not selected_folder[0]:
        copy_button.config(state="disabled")
        return

    folder_path = selected_folder[0]
    base_name = os.path.basename(folder_path)
    format_selected = format_var.get()

    if format_selected == "Raw":
        raw_paths = get_folder_tree_raw(folder_path)
        output = "[\n" + ",\n".join(f"    {repr(p)}" for p in raw_paths) + "\n]"
    elif format_selected == "Plaintext":
        tree_lines = [base_name] + get_folder_tree_text(folder_path)
        output = "\n".join(tree_lines)
    elif format_selected == "Markdown":
        md_lines = ["# " + base_name] + get_folder_tree_markdown(folder_path)
        output = "\n".join(md_lines)
    elif format_selected == "JSON":
        tree_dict = {base_name: get_folder_tree_json(folder_path)}
        output = json.dumps(tree_dict, indent=2)
    elif format_selected == "CSV":
        csv_lines = get_folder_tree_csv(folder_path)
        output = "\n".join(csv_lines)
    elif format_selected == "HTML":
        html_lines = get_folder_tree_html(folder_path)
        output = "\n".join(html_lines)
    elif format_selected == "XML":
        xml_lines = [f"<folder name=\"{base_name}\">"] + get_folder_tree_xml(folder_path, "  ") + [f"</folder>"]
        output = "\n".join(xml_lines)
    else:
        output = "Unknown format selected."

    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, output)
    copy_button.config(state="normal")

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        selected_folder[0] = folder_path
        update_output()

def copy_to_clipboard():
    content = text_area.get("1.0", tk.END).strip()
    if content:
        root.clipboard_clear()
        root.clipboard_append(content)
        messagebox.showinfo("Copied", "Text copied to clipboard!")

def save_to_file():
    content = text_area.get("1.0", tk.END).strip()
    if not content:
        messagebox.showwarning("No Content", "There is no content to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Output saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

# GUI Setup
root = tk.Tk()
root.title("Folder Tree Viewer")
root.minsize(700, 600)

selected_folder = [None]  # Mutable container to store folder path

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Button(frame, text="Select Folder", command=select_folder).pack(pady=5)

tk.Label(frame, text="Choose output format:").pack()

format_var = tk.StringVar(value="Plaintext")
formats = ["Raw", "Plaintext", "Markdown", "JSON", "CSV", "HTML", "XML"]
for fmt in formats:
    tk.Radiobutton(frame, text=fmt, variable=format_var, value=fmt, command=update_output).pack(anchor="w")

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=25, font=("Courier", 10))
text_area.pack(padx=20, pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

copy_button = tk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard, state="disabled")
copy_button.pack(side=tk.LEFT, padx=10)

save_button = tk.Button(button_frame, text="Save to File", command=save_to_file)
save_button.pack(side=tk.LEFT, padx=10)

root.mainloop()
