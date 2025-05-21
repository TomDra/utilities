import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import hashlib

def safe_listdir(path):
    try:
        return sorted(os.listdir(path))
    except Exception as e:
        return [f"[Error reading {path}: {e}]"]

def get_folder_tree_raw(path):
    return [os.path.join(root, name) for root, dirs, files in os.walk(path) for name in dirs + files]

def build_tree_json(path):
    tree = {}
    for item in safe_listdir(path):
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            tree[item] = build_tree_json(full_path)
        else:
            tree[item] = None
    return tree

def hash_folder_content(path):
    """
    Generate a hash representing the folder content for change detection.
    It walks the folder and hashes paths + file modification times.
    """
    hash_md5 = hashlib.md5()
    for root, dirs, files in os.walk(path):
        for name in sorted(dirs + files):
            full_path = os.path.join(root, name)
            try:
                stat = os.stat(full_path)
                hash_md5.update(full_path.encode('utf-8'))
                hash_md5.update(str(stat.st_mtime).encode('utf-8'))
                hash_md5.update(str(stat.st_size).encode('utf-8'))
            except Exception:
                continue
    return hash_md5.hexdigest()

def update_output(*args):
    if not selected_folder[0]:
        copy_button.config(state="disabled")
        return

    folder_path = selected_folder[0]
    base_name = os.path.basename(folder_path)
    format_selected = format_var.get()

    raw_paths = folder_tree_cache["raw"]
    tree_json = folder_tree_cache["json"]

    if format_selected == "Raw":
        output = "[\n" + ",\n".join(f"    {repr(p)}" for p in raw_paths) + "\n]"
    elif format_selected == "Plaintext":
        def text_tree(json_tree, indent=""):
            lines = []
            items = list(json_tree.items())
            for i, (name, subtree) in enumerate(items):
                prefix = "└── " if i == len(items) - 1 else "├── "
                lines.append(indent + prefix + name)
                if subtree is not None:
                    extension = "    " if i == len(items) - 1 else "│   "
                    lines.extend(text_tree(subtree, indent + extension))
            return lines
        output = "\n".join([base_name] + text_tree(tree_json))
    elif format_selected == "Markdown":
        def md_tree(json_tree, level=0):
            lines = []
            for name, subtree in json_tree.items():
                lines.append(f"{'  ' * level}- {name}")
                if subtree is not None:
                    lines.extend(md_tree(subtree, level + 1))
            return lines
        output = "\n".join(["# " + base_name] + md_tree(tree_json))
    elif format_selected == "JSON":
        output = json.dumps({base_name: tree_json}, indent=2)
    elif format_selected == "CSV":
        output = "\n".join(raw_paths)
    elif format_selected == "HTML":
        # Faster HTML generation using list append and join
        def html_tree(json_tree):
            html_parts = ["<ul>"]
            for name, subtree in json_tree.items():
                html_parts.append(f"<li>{name}")
                if subtree is not None:
                    html_parts.append(html_tree(subtree))
                html_parts.append("</li>")
            html_parts.append("</ul>")
            return "".join(html_parts)
        output = html_tree(tree_json)
    elif format_selected == "XML":
        def xml_tree(name, subtree, indent="  "):
            lines = [f'{indent}<folder name="{name}">']
            for child_name, child_tree in subtree.items():
                if child_tree is None:
                    lines.append(f'{indent}  <file name="{child_name}" />')
                else:
                    lines.extend(xml_tree(child_name, child_tree, indent + "  "))
            lines.append(f'{indent}</folder>')
            return lines
        output = "\n".join([f'<folder name="{base_name}">'] + xml_tree(base_name, tree_json, "  ")[1:])
    else:
        output = "Unknown format selected."

    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, output)
    copy_button.config(state="normal")

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        selected_folder[0] = folder_path
        refresh_cache()
        update_output()
        start_auto_refresh()  # start auto-refresh timer

def refresh_cache():
    folder_path = selected_folder[0]
    if folder_path:
        folder_tree_cache["raw"] = get_folder_tree_raw(folder_path)
        folder_tree_cache["json"] = build_tree_json(folder_path)
        folder_tree_cache["hash"] = hash_folder_content(folder_path)

def auto_refresh_check():
    folder_path = selected_folder[0]
    if folder_path:
        current_hash = hash_folder_content(folder_path)
        if current_hash != folder_tree_cache.get("hash"):
            # Folder changed — refresh cache and update output
            refresh_cache()
            update_output()
    # Schedule next check in 5 seconds
    root.after(5000, auto_refresh_check)

def start_auto_refresh():
    # Start the periodic auto-refresh loop if not already running
    if not getattr(root, "_auto_refresh_running", False):
        root._auto_refresh_running = True
        root.after(5000, auto_refresh_check)

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
folder_tree_cache = {"raw": [], "json": {}, "hash": None}  # Cache including content hash

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
