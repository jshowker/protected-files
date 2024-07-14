import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import crypting
import json
from Main import recognize_face_with_camera

STATE_FILE = "app_state.json"

def save_state(tree):
    state = []
    for item in tree.get_children():
        item_text = tree.item(item, "text")
        item_values = tree.item(item, "values")
        state.append((item_text, item_values))
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def load_state(tree):
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            for item_text, item_values in state:
                tree.insert("", "end", text=item_text, values=item_values)

def open_new_window():
    if not recognize_face_with_camera("known_faces", "Timur"):
        return

    root.destroy()

    new_window = ttk.Window(themename="vapor")
    new_window.title("New Window")
    new_window.geometry("700x600")
    new_window.configure(background='#D8BFD8')

    style = ttk.Style()
    style.configure('Dark.TFrame', background='#CDA1C1')

    top_frame = ttk.Frame(new_window, style='Dark.TFrame', height=50)
    top_frame.pack(side=TOP, fill=X)

    bottom_frame = ttk.Frame(new_window, style='Dark.TFrame', height=50)
    bottom_frame.pack(side=BOTTOM, fill=X)

    add_file_button = ttk.Button(top_frame, text="Add File", bootstyle=SUCCESS,
                                 command=lambda: add_file(file_tree))
    add_file_button.pack(side=LEFT, padx=5, pady=5)

    create_folder_button = ttk.Button(top_frame, text="Create Folder", bootstyle=SUCCESS,
                                      command=lambda: create_folder(file_tree))
    create_folder_button.pack(side=LEFT, padx=5, pady=5)

    delete_item_button = ttk.Button(top_frame, text="Delete", bootstyle=DANGER, command=lambda: delete_item(file_tree))
    delete_item_button.pack(side=LEFT, padx=5, pady=5)

    generate_keys_button = ttk.Button(top_frame, text="Generate Keys", bootstyle=INFO, command=generate_keys)
    generate_keys_button.pack(side=LEFT, padx=5, pady=5)

    file_tree = ttk.Treeview(new_window)
    file_tree.pack(side=TOP, fill=BOTH, expand=True, padx=5, pady=5)

    file_tree.heading("#0", text="Files and Folders", anchor='w')

    load_state(file_tree)  # Load the saved state

    def on_double_click(event):
        item_id = file_tree.selection()[0]
        item_path = file_tree.item(item_id, "values")[0]
        if item_path.endswith('.bin'):
            temp_path = item_path[:-4]
            crypting.decrypt(item_path, temp_path)
            try:
                if temp_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    show_image(temp_path)
                else:
                    with open(temp_path, "r", encoding="utf-8") as file:
                        content = file.read()
                    messagebox.showinfo("Open File", content)
                os.remove(temp_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
        else:
            messagebox.showerror("Error", "File is not encrypted.")

    file_tree.bind("<Double-1>", on_double_click)

    def show_image(image_path):
        image_window = tk.Toplevel()
        image_window.title("Image Viewer")

        img = Image.open(image_path)
        photo = ImageTk.PhotoImage(img)
        label = ttk.Label(image_window, image=photo)
        label.image = photo
        label.pack()

    def on_item_edit(event):
        item_id = file_tree.selection()[0]
        old_name = file_tree.item(item_id, "text")
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
        if new_name:
            file_tree.item(item_id, text=new_name)
            save_state(file_tree)  # Save the state after renaming

    new_window.bind('<F2>', on_item_edit)

    def on_start_drag(event):
        selected_items = file_tree.selection()
        if not selected_items:
            return
        selected_item = selected_items[0]
        file_tree.dragged_item = selected_item

    def on_drop(event):
        drop_target = file_tree.identify_row(event.y)
        dragged_item = getattr(file_tree, 'dragged_item', None)

        if drop_target and dragged_item and drop_target != dragged_item and not is_descendant(dragged_item, drop_target):
            drop_target_values = file_tree.item(drop_target, "values")
            dragged_item_values = file_tree.item(dragged_item, "values")
            if drop_target_values and drop_target_values[0] == "folder":
                if dragged_item_values and dragged_item_values[0] != "folder":
                    file_tree.move(dragged_item, drop_target, 'end')
                    save_state(file_tree)  # Save the state after moving item
                else:
                    messagebox.showerror("Error", "Cannot place a folder inside another object.")
            else:
                messagebox.showerror("Error", "You can only place items inside folders.")

    file_tree.bind('<ButtonPress-1>', on_start_drag)
    file_tree.bind('<ButtonRelease-1>', on_drop)

    def is_descendant(item, target):
        while item:
            if item == target:
                return True
            item = file_tree.parent(item)
        return False

    new_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(new_window, file_tree))
    new_window.mainloop()

def add_file(tree):
    file_path = filedialog.askopenfilename()
    if file_path:
        encrypted_path = file_path + ".bin"
        if crypting.encrypt(file_path, encrypted_path):
            tree.insert("", "end", text=os.path.basename(encrypted_path), values=(encrypted_path,))
            save_state(tree)  # Save the state after adding a file

def create_folder(tree):
    folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
    if folder_name:
        tree.insert("", "end", text=folder_name, values=("folder",))
        save_state(tree)  # Save the state after creating a folder

def delete_item(tree):
    selected_items = tree.selection()
    for item in selected_items:
        item_path = tree.item(item, "values")[0]
        tree.delete(item)
        crypting.decrypt(item_path, item_path[:-4])
    save_state(tree)  # Save the state after deleting items

def generate_keys():
    crypting.generate_keys()
    messagebox.showinfo("Keys Generated", "Public and private keys have been generated successfully.")

def on_closing(window, tree):
    save_state(tree)
    window.destroy()

root = ttk.Window(themename="vapor")
root.title("Empty Window")
root.geometry("700x600")
root.configure(background='#D8BFD8')

style = ttk.Style()
style.configure('Dark.TFrame', background='#CDA1C1')

top_frame = ttk.Frame(root, style='Dark.TFrame', height=50)
top_frame.pack(side=TOP, fill=X)

bottom_frame = ttk.Frame(root, style='Dark.TFrame', height=50)
bottom_frame.pack(side=BOTTOM, fill=X)

b1 = ttk.Button(root, text="Unlock", bootstyle=SUCCESS, width=10, command=open_new_window)
b1.place(relx=0.5, rely=0.5, anchor='center')

root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, None))
root.mainloop()
