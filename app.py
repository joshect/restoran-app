from flask import Flask, render_template, request

app = Flask(__name__)

# Daftar menu
menu = {
    "Makanan": {
        "Nasi Goreng": 20000,
        "Mie Goreng": 18000,
        "Sate Ayam": 25000
    },
    "Minuman": {
        "Teh": 5000,
        "Kopi": 7000,
        "Jus": 10000
    }
}

@app.route('/')
def index():
    return render_template('index.html', menu=menu)

@app.route('/pesan', methods=['POST'])
def pesan():
    pesanan = request.form.getlist('item')
    total = sum(menu['Makanan'].get(item, 0) for item in pesanan) + sum(menu['Minuman'].get(item, 0) for item in pesanan)
    return render_template('index.html', menu=menu, pesanan=pesanan, total=total)

if __name__ == '__main__':
    app.run(debug=True)