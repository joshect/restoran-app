import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
import io
import time
from PIL import Image
from streamlit_autorefresh import st_autorefresh

def apply_custom_gui():
    st.markdown("""
        <style>
        /* Impor font jika ingin hasil maksimal */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap');

        .stApp {
            background-color: #f8f9fa;
        }
        
        /* Styling Kartu Menu & Container Laporan */
        [data-testid="stVerticalBlock"] > div:has(div.stContainer) {
            background-color: white;
            border-radius: 15px;
            padding: 20px; /* Sedikit lebih lega */
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.3s ease;
            border: 1px solid #f1f3f5;
        }
        
        [data-testid="stVerticalBlock"] > div:has(div.stContainer):hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0,0,0,0.1);
        }

        /* Styling Metrik Laporan (Khusus halaman Owner) */
        /* Membungkus Grafik agar terlihat seperti kartu */
        [data-testid="stChart"] {
            background-color: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #f1f3f5;
            margin-top: 20px;
        }

        /* Merapikan Tab Laporan */
        button[data-baseweb="tab"] {
            font-weight: 600;
            color: #2c3e50;
        }

        button[aria-selected="true"] {
            color: #e67e22 !important;
            border-bottom-color: #e67e22 !important;
        }

        /* Tombol Utama */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            height: 3.5em;
            background-color: #e67e22; 
            color: white;
            font-weight: 600;
            border: none;
            box-shadow: 0 4px 10px rgba(230, 126, 34, 0.3);
        }
        
        .stButton>button:hover {
            background-color: #d35400;
            color: white;
            box-shadow: 0 6px 15px rgba(211, 84, 0, 0.4);
        }

        /* Harga & Header */
        .price-tag {
            color: #27ae60;
            font-weight: bold;
            font-size: 1.2em;
        }

        .main-header {
            font-family: 'Playfair Display', serif;
            text-align: center;
            color: #2c3e50;
            padding: 10px;
            letter-spacing: 1px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_professional_menu(kategori, menus):
    items = [m for m in menus if m['kategori'] == kategori]
    
    if not items:
        st.info(f"Belum ada menu di kategori {kategori}")
        return

    # Membuat grid
    cols = st.columns(4) # 4 kolom agar gambar lebih besar dan jelas
    for idx, m in enumerate(items):
        with cols[idx % 4]:
            with st.container():
                # Tampilkan Gambar
                if m['foto']:
                    try:
                        image_data = io.BytesIO(m['foto'])
                        img = Image.open(image_data)
                        st.image(img, use_container_width=True)
                    except:
                        st.image("https://via.placeholder.com/150", use_container_width=True)
                
                # Nama & Harga
                st.markdown(f"**{m['nama']}**")
                st.markdown(f"<p class='price-tag'>Rp{m['harga']:,}</p>", unsafe_allow_html=True)
                
                # Input Qty dengan desain minimalis
                qty = st.number_input("Jumlah", min_value=0, max_value=50, key=f"gui_q_{m['id']}", label_visibility="collapsed")
                
                # Logika Update Cart
                if qty > 0:
                    st.session_state.cart[m['nama']] = {"id": m['id'], "harga": m['harga'], "qty": qty}
                elif m['nama'] in st.session_state.cart and qty == 0:
                    del st.session_state.cart[m['nama']]

def generate_struk(order_data, items):
    struk_html = f"""
    <div id="struk" style="width: 280px; font-family: 'Courier New', Courier, monospace; padding: 5px; background: white; color: black;">
        <div style="text-align: center; margin-bottom: 8px;">
            <h3 style="margin: 0; font-size: 16px;">VIINMAKAN</h3>
            <p style="font-size: 10px; margin: 2px 0;">Autentik Vietnamese Resto<br>Jakarta, Indonesia</p>
        </div>
        
        <div style="font-size: 11px; border-top: 1px dashed #000; padding-top: 5px;">
            <table style="width: 100%; font-size: 11px; border-collapse: collapse;">
                <tr><td>ID: {order_data['id']}</td><td style="text-align:right;">Meja: {order_data['meja']}</td></tr>
                <tr><td colspan="2">Tgl: {order_data['waktu'].strftime('%d/%m/%Y %H:%M')}</td></tr>
                <tr><td colspan="2">Kasir: Staff VIINMAKAN</td></tr>
            </table>
        </div>

        <div style="border-top: 1px dashed #000; margin: 5px 0;"></div>
        
        <table style="width: 100%; font-size: 11px; border-collapse: collapse;">
    """
    
    for item in items:
        subtotal = item['harga_satuan'] * item['qty']
        struk_html += f"""
            <tr>
                <td colspan="2" style="padding-top: 4px; font-weight: bold;">{item['nama_item']}</td>
            </tr>
            <tr>
                <td style="padding-bottom: 4px;">{item['qty']} x {item['harga_satuan']:,}</td>
                <td style="text-align: right; vertical-align: bottom;">{subtotal:,}</td>
            </tr>
        """
    struk_html += f"""
        </table>
        
        <div style="border-top: 1px dashed #000; margin: 5px 0;"></div>
        
        <table style="width: 100%; font-size: 13px; font-weight: bold;">
            <tr>
                <td>TOTAL</td>
                <td style="text-align: right;">Rp{order_data['total_harga']:,}</td>
            </tr>
        </table>
        
        <div style="border-top: 1px dashed #000; margin: 8px 0;"></div>
        
        <div style="text-align: center; font-size: 10px; line-height: 1.2;">
            <p style="margin: 0;">Terima Kasih Atas Kunjungannya!</p>
            <p style="margin: 0;">Simpan struk ini sebagai bukti.</p>
            <p style="margin: 5px 0 0 0;">*** CHAO MUNG ***</p>
        </div>
    </div>
    """
    return struk_html
# --- 1. KONEKSI DATABASE ---
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        ssl_disabled=False
    )
#def get_connection():
  #  return mysql.connector.connect(
   #     host="localhost",
   #     user="root",
   #     password="",
   #     database="viinmakan"
 #   )

def run_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    result = cursor.fetchall()
    conn.close()
    return result

def run_commit(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    conn.close()

# --- 2. INISIALISASI SESSION STATE ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'no_meja' not in st.session_state:
    st.session_state.no_meja = 0
if 'meja_locked' not in st.session_state:
    st.session_state.meja_locked = False

# --- 3. CONFIG ---
st.set_page_config(page_title="VIINMAKAN Resto System", layout="wide")
st.sidebar.image("VIIN MAKAN Logo.png", width=200)
st.sidebar.title("🍴 VIINMAKAN (TEAM)")
app_mode = st.sidebar.selectbox("Pilih Akses", 
    ["Pelanggan (Order)", "Dapur (Kitchen)", "Kasir (Payment)", "Admin (Manajemen Menu)", "Owner (Laporan)"])

# --- 4. IMPLEMENTASI PER HALAMAN ---

# --- HALAMAN ADMIN ---
if app_mode == "Admin (Manajemen Menu)":
    st.header("⚙️ VIINMAKAN MANAGEMENT")
    tab1, tab2 = st.tabs(["Tambah Menu", "Daftar Menu"])
    
    with tab1:
        with st.form("form_menu"):
            nama = st.text_input("Nama Makanan/Minuman")
            kat = st.selectbox("Kategori", ["Makanan", "Minuman"])
            harga = st.number_input("Harga", min_value=0, step=500)
            foto = st.file_uploader("Upload Foto", type=['jpg', 'png'])
            if st.form_submit_button("Simpan ke Database"):
                foto_bytes = foto.getvalue() if foto else None
                run_commit("INSERT INTO menu (nama, harga, kategori, foto, tersedia) VALUES (%s, %s, %s, %s, 1)", 
                           (nama, harga, kat, foto_bytes))
                st.success("Menu tersimpan di MySQL!")

    with tab2:
        menus = run_query("SELECT * FROM menu")
        for m in menus:
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                if m['foto']: st.image(m['foto'], width=80)
            with col2:
                st.write(f"**{m['nama']}** | Rp{m['harga']:,}")
                status_stok = "✅ Tersedia" if m.get('tersedia', 1) else "❌ Habis"
                st.caption(f"Status: {status_stok}")
            with col3:
                if st.button("Ubah Stok", key=f"stok_{m['id']}"):
                    new_val = 0 if m.get('tersedia', 1) else 1
                    run_commit("UPDATE menu SET tersedia = %s WHERE id = %s", (new_val, m['id']))
                    st.rerun()
                if st.button("Hapus", key=f"del_{m['id']}"):
                    run_commit("DELETE FROM menu WHERE id = %s", (m['id'],))
                    st.rerun()

# --- HALAMAN PELANGGAN (ORDER) ---  
if app_mode == "Pelanggan (Order)":
    apply_custom_gui() # Panggil CSS hanya sekali di sini
    
    # === TAMBAHKAN LOGO DI ATAS SINI ===
    path_logo = "VIIN MAKAN Logo-1.png" # Ganti dengan nama file logo Anda

    # Menampilkan logo di tengah
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1]) # Gunakan kolom untuk tengahkan logo
    with col_logo2: # Letakkan di kolom tengah
        try:
            # use_container_width=True agar logo responsif terhadap lebar kolom
            st.image(path_logo, use_container_width=True) 
        except FileNotFoundError:
            # Jika file tidak ditemukan, tampilkan teks placeholder atau biarkan kosong
            st.error(f"Logo '{path_logo}' tidak ditemukan. Pastikan file ada di folder yang sama.")
    
    # 1. Header Tunggal (Sekarang di bawah logo)
    st.markdown("<h1 class='main-header'>🥢 VIINMAKAN VIETNAMESE RESTO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; margin-top:-20px;'>Autentik, Segar, dan Menyehatkan</p>", unsafe_allow_html=True)
    
    # Ambil Parameter Meja dari URL Otomatis (Scan QR)
    query_params = st.query_params
    meja_otomatis = query_params.get("meja", "0")
    
    # 2. Logika Registrasi / Masuk Meja
    if 'cust_info' not in st.session_state:
        st.session_state.cust_info = None

    if not st.session_state.meja_locked:
        st.write("---")
        with st.container(border=True):
            st.subheader("📝 Data Pemesan")
            col_in1, col_in2 = st.columns(2)
            nama_cust = col_in1.text_input("Nama Anda", placeholder="Contoh: Budi")
            telp_cust = col_in2.text_input("No. WhatsApp", placeholder="0812xxx")
            
            no_meja = st.number_input("📍 Nomor Meja", 0, 50, value=int(meja_otomatis))
            tipe_order = st.radio("Metode Pesanan", ["Dine In", "Take Away"], horizontal=True)
            
            if st.button("🔒 Konfirmasi & Lihat Menu", type="primary"):
                if nama_cust and no_meja > 0:
                    st.session_state.no_meja = no_meja
                    st.session_state.meja_locked = True
                    st.session_state.cust_info = {"nama": nama_cust, "telp": telp_cust, "tipe": tipe_order}
                    st.rerun()
                else:
                    st.warning("Mohon isi nama dan nomor meja untuk melanjutkan.")
    
    # 3. Tampilan Menu (Hanya muncul jika meja sudah terkunci)
    else:
        # Info Pelanggan di Atas Menu
        p = st.session_state.cust_info
        st.success(f"📍 Meja {st.session_state.no_meja} | 👤 {p['nama']} | 🥡 {p['tipe']}")
        
        if st.button("🔓 Ganti Meja / Ubah Data"):
            st.session_state.meja_locked = False
            st.rerun()

        # Ambil Data Menu dari DB
        menus = run_query("SELECT * FROM menu")
        tab1, tab2 = st.tabs(["🍛 Makanan", "🥤 Minuman"])
        
        with tab1:
            render_professional_menu("Makanan", menus)
        with tab2:
            render_professional_menu("Minuman", menus)

        # 4. Keranjang & Checkout
        if st.session_state.cart:
            st.divider()
            with st.form("form_checkout"):
                st.subheader("🛒 Ringkasan Pesanan")
                total_akhir = 0
                catatan_all = {}
                
                for nama, item in st.session_state.cart.items():
                    subtotal = item['harga'] * item['qty']
                    total_akhir += subtotal
                    
                    c1, c2 = st.columns([2, 3])
                    c1.write(f"**{nama}** x{item['qty']}")
                    catatan_all[nama] = c2.text_input(f"Catatan untuk {nama}", key=f"note_{item['id']}")
                
                st.write(f"### Total Bayar: Rp{total_akhir:,}")
                st.info("💡 Silakan lakukan pembayaran di kasir atau scan QRIS yang tersedia.")
                
                if st.form_submit_button("🚀 Kirim Pesanan Sekarang"):
                    try:
                        p = st.session_state.cust_info
                        
                        # 1. Query Insert ke Database
                        query_insert = """
                            INSERT INTO orders (meja, total_harga, status, status_bayar, nama_pelanggan, telp, tipe_pesanan, waktu) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        run_commit(query_insert, (
                            st.session_state.no_meja, 
                            total_akhir, 
                            'Menunggu', 
                            'Belum Bayar', 
                            p['nama'], 
                            p['telp'], 
                            p['tipe'], 
                            datetime.now()
                        ))
                        
                        # 2. Ambil ID Order Terakhir (Penting untuk Detail Pesanan)
                        res = run_query("SELECT id FROM orders ORDER BY id DESC LIMIT 1")
                        order_id = res[0]['id']
                        
                        # 3. Simpan Detail Item (Jika Anda punya loop order_details)
                        for nama_item, detail in st.session_state.cart.items():
                             run_commit("""INSERT INTO order_details (order_id, nama_item, harga_satuan, qty, catatan) 
                                         VALUES (%s, %s, %s, %s, %s)""",
                                       (order_id, nama_item, detail['harga'], detail['qty'], catatan_all[nama_item]))

                        # 4. Feedback & Reset (Harus di dalam blok try)
                        st.balloons()
                        st.success("✅ Pesanan terkirim! Silakan menuju kasir untuk verifikasi.")
                        
                        # Hapus data keranjang & kunci meja
                        st.session_state.cart = {}
                        st.session_state.meja_locked = False
                        st.session_state.cust_info = None # Hapus info pelanggan lama
                        
                        time.sleep(2)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Gagal memproses pesanan: {e}")

# --- HALAMAN DAPUR ---
elif app_mode == "Dapur (Kitchen)":
    st.header("👨‍🍳 Antrian Dapur")
    st_autorefresh(interval=10000, key="f5_dapur")
    
    # Filter: Hanya pesanan yang SUDAH BAYAR tapi BELUM SELESAI dimasak
    orders = run_query("""
        SELECT * FROM orders 
        WHERE status_bayar = 'Sudah Bayar' AND status != 'Selesai' 
        ORDER BY waktu ASC
    """)
    
    if not orders:
        st.info("Tidak ada antrian masak saat ini.")
    else:
        data_tabel = []
        for o in orders:
            details = run_query("SELECT * FROM order_details WHERE order_id = %s", (o['id'],))
            item_list = [f"{d['nama_item']} ({d['qty']}x)" for d in details]
            catatan_list = [f"{d['nama_item']}: {d['catatan']}" for d in details if d['catatan']]
            data_tabel.append({
                "ID": o['id'], "Waktu": o['waktu'].strftime("%H:%M"), "Meja": o['meja'],
                "Pesanan": ", ".join(item_list), "Catatan": " | ".join(catatan_list) if catatan_list else "-", "Status": o['status']
            })
        st.table(pd.DataFrame(data_tabel))
        
        with st.container(border=True):
            col_sel, col_stat, col_btn = st.columns([1, 2, 1])
            with col_sel:
                selected_id = st.selectbox("Pilih ID Order", [o['id'] for o in orders])
            with col_stat:
                new_stat = st.selectbox("Ubah Status", ["Menunggu", "Dimasak", "Selesai"])
            with col_btn:
                st.write("###")
                if st.button("💾 Update", width='stretch'):
                    run_commit("UPDATE orders SET status = %s WHERE id = %s", (new_stat, selected_id))
                    st.rerun()

# --- HALAMAN KASIR ---
elif app_mode == "Kasir (Payment)":
    st.header("💰 Panel Pembayaran Kasir")
    
    # 1. BUAT TAB DI ATAS (Bukan di dalam loop/button)
    tab_bayar, tab_riwayat = st.tabs(["💳 Menunggu Pembayaran", "📜 Cetak Struk (Riwayat)"])

    # --- TAB 1: PROSES PEMBAYARAN ---
    with tab_bayar:
        # Perhatikan: Query harus diapit tanda kutip agar terbaca sebagai string
        query_kasir = """
            SELECT id, meja, total_harga, status, status_bayar, nama_pelanggan, telp, tipe_pesanan, waktu 
            FROM orders 
            WHERE status_bayar = 'Belum Bayar' 
            ORDER BY waktu DESC
        """
        pending_orders = run_query(query_kasir)
        
        if not pending_orders:
            st.info("Tidak ada pesanan yang menunggu pembayaran.")
        else:
            for ro in pending_orders:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        st.markdown(f"### 🪑 Meja {ro['meja']}")
                        st.markdown(f"👤 **{ro['nama_pelanggan'] if ro['nama_pelanggan'] else 'Pelanggan'}**")
                        st.caption(f"📞 {ro['telp'] if ro['telp'] else '-'} | 🥡 {ro['tipe_pesanan']}")
                    
                    with c2:
                        st.write("Total Tagihan:")
                        st.subheader(f"Rp{ro['total_harga']:,}")
                        
                        if ro['telp']:
                            # Bersihkan nomor telp untuk WhatsApp
                            no_wa = ro['telp']
                            if no_wa.startswith('0'): no_wa = '62' + no_wa[1:]
                            pesan = f"Halo {ro['nama_pelanggan']}, tagihan Meja {ro['meja']} sebesar Rp{ro['total_harga']:,}."
                            st.markdown(f"[💬 Kirim WA](https://wa.me/{no_wa}?text={pesan.replace(' ', '%20')})")

                    with c3:
                        st.write("###")
                        if st.button("✅ Konfirmasi Lunas", key=f"pay_{ro['id']}", use_container_width=True):
                            # Simpan history
                            run_commit("INSERT INTO history_sales (waktu, total, meja) VALUES (%s, %s, %s)", 
                                       (datetime.now(), ro['total_harga'], ro['meja']))
                            # Update status
                            run_commit("UPDATE orders SET status_bayar = 'Sudah Bayar' WHERE id = %s", (ro['id'],))
                            st.success("Lunas!")
                            time.sleep(1)
                            st.rerun()

                    with st.expander("🔍 Detail Item"):
                        details = run_query("SELECT * FROM order_details WHERE order_id = %s", (ro['id'],))
                        for d in details:
                            st.write(f"- {d['nama_item']} ({d['qty']}x)")

    # --- TAB 2: RIWAYAT & CETAK STRUK ---
    with tab_riwayat:
        st.subheader("Cetak Struk Terakhir")
        riwayat = run_query("SELECT * FROM orders WHERE status_bayar = 'Sudah Bayar' ORDER BY waktu DESC LIMIT 10")
        
        if not riwayat:
            st.info("Belum ada riwayat lunas.")
        else:
            for r in riwayat:
                with st.expander(f"Struk Meja {r['meja']} - Rp{r['total_harga']:,} (ID: {r['id']})"):
                    details_r = run_query("SELECT * FROM order_details WHERE order_id = %s", (r['id'],))
                    
                    # Generate & Tampilkan Preview Struk
                    html_struk = generate_struk(r, details_r)
                    st.markdown(html_struk, unsafe_allow_html=True)
                    
                    if st.button(f"🖨️ Cetak Struk #{r['id']}", key=f"print_{r['id']}"):
                        st.components.v1.html(f"""
                            <script>
                            var win = window.open('', '', 'height=500,width=500');
                            win.document.write('<html><body style="margin:0;">');
                            win.document.write('{html_struk.replace("'", "\\'").replace("\n", "")}');
                            win.document.write('</body></html>');
                            win.document.close();
                            setTimeout(function(){{ win.print(); }}, 500);
                            </script>
                        """, height=0)
# --- HALAMAN OWNER ---
elif app_mode == "Owner (Laporan)":
    st.header("📊 Laporan Penjualan Strategis")
    
    # --- 1. FILTER SIDEBAR UNTUK PERIODE ---
    st.sidebar.subheader("📅 Pengaturan Laporan")
    opsi_periode = st.sidebar.selectbox(
        "Grup Berdasarkan:", 
        ["Jam", "Hari", "Minggu", "Bulan", "Tahun"]
    )
    
    # Map periode ke format MySQL
    map_sql = {
        "Jam": "%Y-%m-%d %H:00",
        "Hari": "%Y-%m-%d",
        "Minggu": "%x-%v", # Format Tahun-Minggu ke-
        "Bulan": "%Y-%m",
        "Tahun": "%Y"
    }
    format_tgl = map_sql[opsi_periode]

    # --- 2. TABS LAPORAN ---
    tab_keuangan, tab_produk = st.tabs(["💰 Laporan Keuangan", "🍱 Analisis Produk"])

    with tab_keuangan:
        query_finance = f"SELECT DATE_FORMAT(waktu, '{format_tgl}') as periode, SUM(total) as pendapatan_periode FROM history_sales GROUP BY periode ORDER BY periode ASC"
        data_finance = run_query(query_finance)
        
        if data_finance:
            df_fin = pd.DataFrame(data_finance)
            
            # PAKSA KONVERSI KE FLOAT SEBELUM GRAFIK
            df_fin['pendapatan_periode'] = pd.to_numeric(df_fin['pendapatan_periode'], errors='coerce').astype(float)
            st.bar_chart(df_fin.set_index('periode')['pendapatan_periode'])
        
            # --- BAGIAN PERBAIKAN METRIK ---
            pendapatan_terakhir = df_fin['pendapatan_periode'].iloc[-1]
            label_periode = df_fin['periode'].iloc[-1]
            
            # Menghitung Total Akumulasi (untuk perbandingan jika perlu)
            total_akumulasi = df_fin['pendapatan_periode'].sum()

            # Menampilkan Metrik yang Sesuai Pilihan Filter
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric(
                    label=f"💰 Pendapatan {opsi_periode} Ini ({label_periode})", 
                    value=f"Rp{pendapatan_terakhir:,}"
                )
            with col_m2:
                st.metric(
                    label="📊 Total Akumulasi (All Time)", 
                    value=f"Rp{total_akumulasi:,}"
                )
            
            st.divider()
        
            # Menggunakan kolom agar grafik tidak terlalu 'gepeng' di layar lebar
            c_left, c_chart, c_right = st.columns([0.1, 8, 0.1])
            with c_chart:
                st.markdown("### 📈 Tren Pendapatan")
            # Grafik otomatis akan terbungkus kotak putih berkat CSS di atas
            st.bar_chart(df_fin.set_index('periode')['pendapatan_periode'])
            
            # --- BAGIAN GRAFIK ---
            st.subheader(f"📈 Tren Pendapatan per {opsi_periode}")
            # Menggunakan bar_chart agar lebih mudah dibaca untuk per jam/hari
            st.bar_chart(df_fin.set_index('periode')['pendapatan_periode'])
            
            # Tabel Detail
            with st.expander("📝 Lihat Tabel Detail"):
                st.dataframe(df_fin, use_container_width=True)
        else:
            st.info(f"Belum ada data penjualan untuk laporan per {opsi_periode}.")
        
    with tab_produk:
        # Query Produk Terlaris - Perbaikan pada bagian WHERE
        query_item_trend = f"""
            SELECT 
                od.nama_item, 
                SUM(od.qty) as total_qty,
                DATE_FORMAT(o.waktu, '{format_tgl}') as periode
            FROM order_details od
            JOIN orders o ON od.order_id = o.id
            WHERE o.status_bayar = 'Sudah Bayar'  -- Perubahan di sini
            GROUP BY periode, od.nama_item
            ORDER BY periode DESC, total_qty DESC
        """
        data_items = run_query(query_item_trend)
        # ... (sisa kode laporan produk Anda) ...
        data_items = run_query(query_item_trend)
        
        if data_items:
            df_items = pd.DataFrame(data_items)
            
            # Filter Produk (Multiselect)
            list_produk = df_items['nama_item'].unique()
            produk_pilihan = st.multiselect(
                "Filter Produk Terlaris:", 
                list_produk, 
                default=list_produk[:3] if len(list_produk) >= 3 else list_produk
            )
            
            df_filtered = df_items[df_items['nama_item'].isin(produk_pilihan)]
            
            if not df_filtered.empty:
                # Chart Batang Perbandingan
                st.subheader(f"📊 Analisis Kuantitas Produk per {opsi_periode}")
                # Pivot untuk chart agar sumbu X adalah periode dan warna adalah nama produk
                df_pivot = df_filtered.pivot(index='periode', columns='nama_item', values='total_qty').fillna(0)
                st.bar_chart(df_pivot)
                
                st.dataframe(df_filtered, width='stretch')
        else:
            st.info("Data produk belum tersedia.")