import json
import tkinter as tk
from tkinter import messagebox

books_file = 'books.json'
borrows_file = 'borrows.json'

class Library:
    def __init__(self):
        self._books = []
        self._borrows = []
        self.load_data()
        self.borrow_queue = []
        self.return_stack = []
        self._last_book_id = self.get_last_book_id()

    def books(self):
        return self._books

    def set_books(self, value):
        self._books = value
        self.save()

    def borrows(self):
        return self._borrows

    def set_borrows(self, value):
        self._borrows = value
        self.save()

    def load_data(self):
        try:
            with open(books_file, 'r') as f:
                self._books = json.load(f)
        except FileNotFoundError:
            self._books = []

        try:
            with open(borrows_file, 'r') as f:
                self._borrows = json.load(f)
        except FileNotFoundError:
            self._borrows = []

    def save(self):
        with open(books_file, 'w') as f:
            json.dump(self._books, f, indent=4)
        with open(borrows_file, 'w') as f:
            json.dump(self._borrows, f, indent=4)

    def get_last_book_id(self):
        if not self._books:
            return 0
        return max(book["id"] for book in self._books)

    def addbook(self, title):
        for book in self._books:
            if book["title"].lower() == title.lower():
                return False
        self._last_book_id += 1
        self._books.append({"id": self._last_book_id, "title": title, "available": True})
        self.save()
        return True

    def borrowbook(self, book_id, borrower_name):
        for book in self._books:
            if book["id"] == book_id:
                if book["available"]:
                    self._borrows.append({"book_id": book_id, "borrower_name": borrower_name})
                    book["available"] = False
                    self.save()
                    self.borrow_queue.append(book_id)
                    return True
                else:
                    return False
        return False

    def returnbook(self, book_id):
        for borrow in self._borrows:
            if borrow["book_id"] == book_id:
                self._borrows.remove(borrow)
                for book in self._books:
                    if book["id"] == book_id:
                        book["available"] = True
                        self.save()
                        self.return_stack.append(book_id)
                        return True
        return False

    def removebook(self, book_id):
        for book in self._books:
            if book["id"] == book_id:
                self._books.remove(book)
                self.save()
                return True
        return False

def refreshbook(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    for book in library.books():
        status = 'Yes' if book['available'] else 'No'
        borrows_list = [borrow for borrow in library.borrows() if borrow['book_id'] == book['id']]
        borrower_name = f", Borrowed by: {borrows_list[0]['borrower_name']}" if borrows_list else ''
        tk.Label(frame, text=f"ID: {book['id']}, Title: {book['title']}, Available: {status}{borrower_name}", bg="lightgreen").pack(pady=2)

def booklist():
    list_window = tk.Toplevel(window)
    list_window.geometry("400x400")
    list_window.title("Daftar Buku")
    list_window.configure(bg="lightgreen")

    canvas = tk.Canvas(list_window, bg="lightgreen")
    framebook = tk.Frame(canvas, bg="lightgreen")
    scrollbar = tk.Scrollbar(list_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=framebook, anchor="nw")

    framebook.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
    
    refreshbook(framebook)

def buttonclick(action):
    if action == 'add':
        title = entry_title.get()
        if title:
            if library.addbook(title):
                entry_title.delete(0, tk.END)
                messagebox.showinfo("Success", "Book added successfully!")
            else:
                messagebox.showerror("Error", "Book with this title already exists!")
        else:
            messagebox.showerror("Error", "Title field must be filled!")
    elif action == 'borrow':
        book_id = entry_borrow_id.get()
        borrower_name = entry_borrower_name.get()
        if book_id and borrower_name:
            if not book_id.isdigit():
                messagebox.showerror("Error", "Book ID must be a number!")
            elif library.borrowbook(int(book_id), borrower_name):
                messagebox.showinfo("Success", "Book borrowed successfully!")
            else:
                messagebox.showerror("Error", "Book is not available or Book ID not found!")
            entry_borrow_id.delete(0, tk.END)
            entry_borrower_name.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Both Book ID and Borrower Name fields must be filled!")
    elif action == 'return':
        book_id = entry_return_id.get()
        if book_id:
            if not book_id.isdigit():
                messagebox.showerror("Error", "Book ID must be a number!")
            elif library.returnbook(int(book_id)):
                messagebox.showinfo("Success", "Book returned successfully!")
            else:
                messagebox.showerror("Error", "Book was not borrowed or Book ID not found!")
            entry_return_id.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Book ID field must be filled!")
    elif action == 'remove':
        book_id = entry_remove_id.get()
        if book_id:
            if not book_id.isdigit():
                messagebox.showerror("Error", "Book ID must be a number!")
            elif library.removebook(int(book_id)):
                messagebox.showinfo("Success", "Book removed successfully!")
            else:
                messagebox.showerror("Error", "Book ID not found!")
            entry_remove_id.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Book ID field must be filled!")

library = Library()

window = tk.Tk()
window.geometry("400x600")
window.title("Peminjaman Buku Online")
window.configure(bg="lightgreen")
window.resizable(width=0, height=0)

tk.Label(window, text="Peminjaman Buku", font=("Georgia", 16, "bold"), bg="lightgreen").pack(pady=1)

framebook = tk.Frame(window, bg="lightgreen")
framebook.pack(pady=1)

tk.Button(window, text="List Buku", bg="lightblue", command=booklist).pack(pady=8)

tk.Label(window, text="Add Book", font=("Georgia", 12, "bold"), bg="lightgreen").pack(pady=3)  
tk.Label(window, text="Title:", bg="lightgreen").pack(pady=1)
entry_title = tk.Entry(window)
entry_title.pack(pady=1)
tk.Button(window, text="Add", bg="lightblue", command=lambda: buttonclick('add')).pack(pady=3)

tk.Label(window, text="Borrow Book", font=("Georgia", 12, "bold"), bg="lightgreen").pack(pady=3)  
tk.Label(window, text="Book ID:", bg="lightgreen").pack(pady=1)
entry_borrow_id = tk.Entry(window)
entry_borrow_id.pack(pady=1)
tk.Label(window, text="Borrower Name:", bg="lightgreen").pack(pady=1)
entry_borrower_name = tk.Entry(window)
entry_borrower_name.pack(pady=1)
tk.Button(window, text="Borrow", bg="lightblue", command=lambda: buttonclick('borrow')).pack(pady=3)

tk.Label(window, text="Return Book", font=("Georgia", 12, "bold"), bg="lightgreen").pack(pady=3) 
tk.Label(window, text="Book ID:", bg="lightgreen").pack(pady=1)
entry_return_id = tk.Entry(window)
entry_return_id.pack(pady=1)
tk.Button(window, text="Return", bg="lightblue", command=lambda: buttonclick('return')).pack(pady=3)

tk.Label(window, text="Remove Book", font=("Georgia", 12, "bold"), bg="lightgreen").pack(pady=3) 
tk.Label(window, text="Book ID:", bg="lightgreen").pack(pady=1)
entry_remove_id = tk.Entry(window)
entry_remove_id.pack(pady=1)
tk.Button(window, text="Remove", bg="lightblue", command=lambda: buttonclick('remove')).pack(pady=3)

window.mainloop()