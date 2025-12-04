import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import database as db
import csv
from datetime import datetime
import locale

# Pengaturan Lokasi Waktu (Bahasa Indonesia)
try:
    locale.setlocale(locale.LC_TIME, 'id_ID')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Indonesian')
    except:
        pass

COLORS = {
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
    "neutral": "#64748B",
    "neutral_hover": "#475569",
    "success": "#10B981",
    "success_hover": "#059669",
    "bg_card": "#1E293B",
    "text_light": "#F8FAFC",
    "input_bg": "#334155"
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("inStock - Aplikasi Manajemen Stok Gudang")
        self.geometry("900x650")
        
        ctk.set_appearance_mode("Dark") 
        ctk.set_default_color_theme("dark-blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # --- FRAME INPUT (ATAS) ---
        self.input_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=COLORS["bg_card"])
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.input_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 1. Judul (Kiri Atas)
        self.label_title = ctk.CTkLabel(self.input_frame, text="Input Barang - inStock", 
                                      font=("Roboto", 18, "bold"), text_color=COLORS["text_light"])
        self.label_title.grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=20, sticky="w")

        # 2. Jam & Tanggal (Kanan Atas)
        self.label_waktu = ctk.CTkLabel(self.input_frame, text="...", 
                                      font=("Roboto", 14), text_color=COLORS["primary"])
        self.label_waktu.grid(row=0, column=2, columnspan=2, pady=(15, 10), padx=20, sticky="e")

        # Input Form
        self.nama_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Nama Barang", height=40, fg_color=COLORS["input_bg"])
        self.nama_entry.grid(row=1, column=0, padx=10, pady=(0, 15), sticky="ew")

        self.harga_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Harga (Rp)", height=40, fg_color=COLORS["input_bg"])
        self.harga_entry.grid(row=1, column=1, padx=10, pady=(0, 15), sticky="ew")

        self.stok_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Jumlah Stok", height=40, fg_color=COLORS["input_bg"])
        self.stok_entry.grid(row=1, column=2, padx=10, pady=(0, 15), sticky="ew")

        self.tambah_button = ctk.CTkButton(self.input_frame, text="+ Tambah", height=40,
                                         fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                                         command=self.tambah_barang)
        self.tambah_button.grid(row=1, column=3, padx=10, pady=(0, 15), sticky="ew")

        # Tombol Aksi
        self.action_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, columnspan=4, pady=(0, 15), padx=10, sticky="e")

        self.update_button = ctk.CTkButton(self.action_frame, text="Update Terpilih", 
                                         fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                                         command=self.perbarui_barang)
        self.update_button.pack(side="left", padx=5)

        self.hapus_button = ctk.CTkButton(self.action_frame, text="Hapus Terpilih", 
                                        fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                                        command=self.hapus_barang)
        self.hapus_button.pack(side="left", padx=5)

        self.clear_button = ctk.CTkButton(self.action_frame, text="Reset Form", 
                                        fg_color=COLORS["neutral"], hover_color=COLORS["neutral_hover"],
                                        command=self.clear_input)
        self.clear_button.pack(side="left", padx=5)

        self.laporan_button = ctk.CTkButton(self.action_frame, text="Laporan & Export", 
                                          fg_color=COLORS["success"], hover_color=COLORS["success_hover"],
                                          command=self.buka_laporan_window)
        self.laporan_button.pack(side="left", padx=5)

        # --- FRAME TABEL (TENGAH) ---
        self.tree_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.tree_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")

        self.style_treeview()

        columns = ("id", "nama_barang", "harga", "stok")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nama_barang", text="Nama Barang")
        self.tree.heading("harga", text="Harga (Rp)")
        self.tree.heading("stok", text="Stok")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nama_barang", width=300, anchor="w")
        self.tree.column("harga", width=150, anchor="e")
        self.tree.column("stok", width=100, anchor="center")

        scrollbar = ctk.CTkScrollbar(self.tree_frame, command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.pilih_item)

        self.refresh_tabel()

        # --- FOOTER (BAWAH) ---
        self.footer_label = ctk.CTkLabel(self, text="Albani Computer - 2025", 
                                       font=("Roboto", 12), text_color=COLORS["neutral"])
        self.footer_label.grid(row=2, column=0, pady=(0, 10))

        # Mulai Jam
        self.update_waktu()

    def update_waktu(self):
        # Format: Kamis, 04 Desember 2025 | 18:30:00
        waktu_sekarang = datetime.now().strftime("%A, %d %B %Y | %H:%M:%S")
        self.label_waktu.configure(text=waktu_sekarang)
        self.after(1000, self.update_waktu)

    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
                        background="#0F172A",
                        foreground="white",
                        fieldbackground="#0F172A",
                        rowheight=30,
                        font=("Roboto", 11))
        
        style.configure("Treeview.Heading",
                        background="#334155",
                        foreground="white",
                        font=("Roboto", 12, "bold"))
        
        style.map("Treeview",
                  background=[("selected", COLORS["primary"])],
                  foreground=[("selected", "white")])

    def refresh_tabel(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in db.lihat_semua_barang():
            row_list = list(row)
            row_list[2] = f"{row_list[2]:,}" 
            self.tree.insert("", "end", values=row_list)

    def tambah_barang(self):
        nama = self.nama_entry.get()
        harga = self.harga_entry.get()
        stok = self.stok_entry.get()

        if not nama or not harga or not stok:
            messagebox.showwarning("Peringatan", "Semua kolom harus diisi!")
            return
        
        try:
            harga_int = int(harga)
            stok_int = int(stok)
        except ValueError:
            messagebox.showerror("Error", "Harga dan Stok harus berupa angka!")
            return
        
        db.tambah_barang(nama, harga_int, stok_int)
        self.refresh_tabel()
        self.clear_input()
        messagebox.showinfo("Sukses", "Barang berhasil ditambahkan!")

    def perbarui_barang(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih barang dari tabel untuk diedit.")
            return

        values = self.tree.item(selected_item, "values")
        item_id = values[0]
        
        nama = self.nama_entry.get()
        harga = self.harga_entry.get()
        stok = self.stok_entry.get()

        if not nama or not harga or not stok:
            messagebox.showwarning("Peringatan", "Semua kolom harus diisi!")
            return

        try:
            harga_clean = int(harga.replace(",", "").replace(".", "")) 
            stok_clean = int(stok)
            
            db.perbarui_barang(item_id, nama, harga_clean, stok_clean)
            self.refresh_tabel()
            self.clear_input()
            messagebox.showinfo("Sukses", "Data barang berhasil diperbarui!")
        except ValueError:
             messagebox.showerror("Error", "Harga dan Stok harus berupa angka valid!")

    def hapus_barang(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih barang yang ingin dihapus.")
            return
            
        values = self.tree.item(selected_item, "values")
        item_id = values[0]
        nama_barang = values[1]
        
        if messagebox.askyesno("Konfirmasi Hapus", f"Hapus '{nama_barang}'?"):
            db.hapus_barang(item_id)
            self.refresh_tabel()
            self.clear_input()
            messagebox.showinfo("Sukses", "Barang berhasil dihapus.")

    def pilih_item(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
        
        values = self.tree.item(selected_item, "values")
        
        self.clear_input()
        self.nama_entry.insert(0, values[1])
        harga_raw = str(values[2]).replace(",", "")
        self.harga_entry.insert(0, harga_raw)
        self.stok_entry.insert(0, values[3])

    def clear_input(self):
        self.nama_entry.delete(0, "end")
        self.harga_entry.delete(0, "end")
        self.stok_entry.delete(0, "end")
        self.nama_entry.focus() 
        self.tree.selection_remove(self.tree.selection())

    def buka_laporan_window(self):
        toplevel = ctk.CTkToplevel(self)
        toplevel.title("Laporan Stok")
        toplevel.geometry("400x350")
        toplevel.grab_set() 

        total_jenis, total_stok, total_aset = db.ambil_ringkasan_stok()

        ctk.CTkLabel(toplevel, text="Ringkasan Toko", font=("Roboto", 20, "bold")).pack(pady=20)

        info_frame = ctk.CTkFrame(toplevel, fg_color=COLORS["bg_card"])
        info_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.create_stat_row(info_frame, "Jenis Barang:", str(total_jenis), 0)
        self.create_stat_row(info_frame, "Total Stok Fisik:", str(total_stok), 1)
        self.create_stat_row(info_frame, "Total Aset:", f"Rp {total_aset:,}", 2)

        export_btn = ctk.CTkButton(toplevel, text="Download CSV (Excel)", 
                                 fg_color=COLORS["success"], hover_color=COLORS["success_hover"],
                                 command=self.export_csv)
        export_btn.pack(pady=20)

    def create_stat_row(self, parent, label_text, value_text, row):
        parent.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(parent, text=label_text, anchor="w").grid(row=row, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkLabel(parent, text=value_text, font=("Roboto", 14, "bold"), anchor="e").grid(row=row, column=1, padx=20, pady=10, sticky="e")

    def export_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                initialfile=f"laporan_stok_{datetime.now().strftime('%Y%m%d')}.csv")
        if not filename:
            return

        try:
            data = db.lihat_semua_barang()
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Nama Barang", "Harga", "Stok"])
                writer.writerows(data)
            messagebox.showinfo("Sukses", f"Laporan berhasil disimpan ke:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan file:\n{e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()