# database.py
# File ini berfungsi sebagai "otak" untuk semua urusan database.

import sqlite3

def init_db():
    """Membuat koneksi dan tabel jika belum ada."""
    conn = sqlite3.connect('toko.db')
    cursor = conn.cursor()
    # Membuat tabel 'barang' dengan kolom id, nama, harga, dan stok
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS barang (
            id INTEGER PRIMARY KEY,
            nama_barang TEXT NOT NULL,
            harga INTEGER NOT NULL,
            stok INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def tambah_barang(nama, harga, stok):
    """Menambahkan barang baru ke database."""
    conn = sqlite3.connect('toko.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO barang (nama_barang, harga, stok) VALUES (?, ?, ?)", (nama, harga, stok))
    conn.commit()
    conn.close()

def lihat_semua_barang():
    """Mengambil semua data barang dari database."""
    conn = sqlite3.connect('toko.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama_barang, harga, stok FROM barang")
    semua_barang = cursor.fetchall()
    conn.close()
    return semua_barang

def perbarui_barang(id, nama, harga, stok):
    """Memperbarui data barang berdasarkan ID-nya."""
    conn = sqlite3.connect('toko.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE barang SET nama_barang = ?, harga = ?, stok = ? WHERE id = ?", (nama, harga, stok, id))
    conn.commit()
    conn.close()

def hapus_barang(id):
    """Menghapus barang dari database berdasarkan ID-nya."""
    conn = sqlite3.connect('toko.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM barang WHERE id = ?", (id,))
    conn.commit()
    conn.close()

init_db()

def ambil_ringkasan_stok():
    """Menghitung total jenis barang, total stok fisik, dan total nilai aset."""
    conn = sqlite3.connect('toko.db')
    cursor = conn.cursor()
    
    # Query SQL untuk menghitung statistik sekaligus
    cursor.execute("SELECT COUNT(*), SUM(stok), SUM(harga * stok) FROM barang")
    result = cursor.fetchone()
    
    conn.close()
    
    total_jenis = result[0] if result[0] else 0
    total_stok = result[1] if result[1] else 0
    total_aset = result[2] if result[2] else 0
    
    return total_jenis, total_stok, total_aset