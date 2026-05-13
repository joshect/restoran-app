import streamlit as st
import pandas as pd
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Resto Streamlit System", layout="wide")

# Inisialisasi State Global (Penyimpanan Data Sementara)
if 'orders' not in st.session_state:
    st.session_state.orders = []

# Data Menu Restoran
MENU = {
    "Nasi Goreng Spesial": 25000,
    "Mie Ayam Jamur": 20000,
    "Ayam Bakar Taliwang": 35000,
    "Es Teh Manis": 5000,
    "Jus Jeruk": 12000
}

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("Sistem Restoran Digital")
app_mode = st.sidebar.selectbox("Pilih Akses Akun", ["Pelanggan (Order)", "Dapur (Kitchen)", "Kasir (Payment)"])

# --- 1. HALAMAN PELANGGAN (ORDER) ---
if app_mode == "Pelanggan (Order)":
    st.header("🍴 Silahkan Pesan Menu Anda")
    
    col1, col2 = st.columns(2)
    with col1:
        no_meja = st.number_input("Nomor Meja", min_value=1, max_value=50, step=1)
        item_pesanan = st.multiselect("Pilih Menu", list(MENU.keys()))
    
    with col2:
        st.write("**Daftar Harga:**")
        for k, v in MENU.items():
            st.write(f"- {k}: Rp{v:,}")

    if st.button("Kirim Pesanan ke Dapur"):
        if item_pesanan:
            new_order = {
                "id": len(st.session_state.orders) + 1,
                "meja": no_meja,
                "items": item_pesanan,
                "total_harga": sum(MENU[item] for item in item_pesanan),
                "status": "Menunggu", # Status: Menunggu, Dimasak, Selesai, Dibayar
                "waktu": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.orders.append(new_order)
            st.success(f"Pesanan Meja {no_meja} berhasil dikirim!")
        else:
            st.error("Pilih menu terlebih dahulu!")

# --- 2. HALAMAN DAPUR (KITCHEN) ---
elif app_mode == "Dapur (Kitchen)":
    st.header("👨‍🍳 Pesanan Masuk (Kitchen)")
    
    pending_orders = [o for o in st.session_state.orders if o['status'] in ["Menunggu", "Dimasak"]]
    
    if not pending_orders:
        st.info("Belum ada pesanan yang perlu dimasak.")
    else:
        for idx, order in enumerate(st.session_state.orders):
            if order['status'] in ["Menunggu", "Dimasak"]:
                with st.expander(f"Pesanan Meja {order['meja']} - {order['waktu']}"):
                    st.write(f"**Menu:** {', '.join(order['items'])}")
                    st.write(f"**Status Saat Ini:** {order['status']}")
                    
                    if order['status'] == "Menunggu":
                        if st.button(f"Mulai Masak (Meja {order['meja']})", key=f"cook_{idx}"):
                            st.session_state.orders[idx]['status'] = "Dimasak"
                            st.rerun()
                    
                    if order['status'] == "Dimasak":
                        if st.button(f"Selesaikan Pesanan (Meja {order['meja']})", key=f"done_{idx}"):
                            st.session_state.orders[idx]['status'] = "Selesai"
                            st.rerun()

# --- 3. HALAMAN KASIR (PAYMENT) ---
elif app_mode == "Kasir (Payment)":
    st.header("💰 Pembayaran Kasir")
    
    ready_to_pay = [o for o in st.session_state.orders if o['status'] == "Selesai"]
    
    if not ready_to_pay:
        st.info("Tidak ada pesanan yang menunggu pembayaran.")
    else:
        df_pay = pd.DataFrame(ready_to_pay)
        st.table(df_pay[['meja', 'items', 'total_harga', 'waktu']])
        
        target_meja = st.selectbox("Pilih Meja untuk Bayar", [o['meja'] for o in ready_to_pay])
        
        if st.button("Proses Pembayaran & Cetak Struk"):
            for idx, order in enumerate(st.session_state.orders):
                if order['meja'] == target_meja and order['status'] == "Selesai":
                    st.session_state.orders[idx]['status'] = "Dibayar"
                    st.balloons()
                    st.success(f"Pembayaran Meja {target_meja} sebesar Rp{order['total_harga']:,} Berhasil!")
                    st.rerun()