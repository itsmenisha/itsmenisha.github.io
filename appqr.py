from flask import Flask, render_template, request
import qrcode
import io
import base64

app = Flask(__name__)

# Bank options (you can keep the same list or import from a module)
banks = [
    ("ADBLNPKA", "Agricultural Development Bank Limited"),
    ("CTZNNPKA", "Citizens Bank International Limited"),
    ("EVBLNPKA", "Everest Bank Limited"),
    ("GLBBNPKA", "Global IME Bank Limited"),
    ("HIMALNPKA", "Himalayan Bank Limited"),
    ("KMBLNPKA", "Kumari Bank Limited"),
    ("LXBLNPKA", "Laxmi Sunrise Bank Limited"),
    ("MBLNNPKA", "Machhapuchchhre Bank Limited"),
    ("NARBNPKA", "Nabil Bank Limited"),
    ("NEBLNPKA", "Nepal Bank Limited"),
    ("NIFRANPKA", "Nepal Infrastructure Bank Limited"),
    ("NIMBNPKA", "Nepal Investment Mega Bank Limited"),
    ("NRBLNPKA", "Nepal Rastra Bank"),
    ("NSBINPKA", "Nepal SBI Bank Limited"),
    ("NICENPKA", "NIC Asia Bank Limited"),
    ("NMBBNPKA", "NMB Bank Limited"),
    ("PRBHNPKA", "Prabhu Bank Limited"),
    ("PCBLNPKA", "Prime Commercial Bank Limited"),
    ("RBBANPKA", "Rastriya Banijya Bank Limited"),
    ("SNMANPKA", "Sanima Bank Limited"),
    ("SIDDNPKA", "Siddhartha Bank Limited"),
    ("SCBLNPKA", "Standard Chartered Bank Nepal Limited"),
    ("SRDBNPKA", "Shine Resunga Development Bank Limited"),
    ("NABBC", "Narayani Development Bank Ltd."),
    ("KDBL", "Karnali Development Bank Ltd."),
    ("EDBL", "Excel Development Bank Ltd."),
    ("MDBL", "Miteri Development Bank Ltd."),
    ("MNBBL", "Muktinath Bikas Bank Ltd."),
    ("CORBL", "Corporate Development Bank Ltd."),
    ("SBBL", "Sindhu Bikas Bank Ltd."),
    ("SALBL", "Salapa Bikas Bank Ltd."),
    ("GRDBL", "Green Development Bank Ltd."),
    ("SADBL", "Shangrila Development Bank Ltd."),
    ("JBBL", "Jyoti Bikas Bank Ltd."),
    ("GBBL", "Garima Bikas Bank Ltd."),
    ("MLBL", "Mahalaxmi Bikas Bank Ltd."),
    ("LBBL", "Lumbini Bikas Bank Ltd."),
    ("KSBBL", "Kamana Sewa Bikas Bank Ltd."),
    ("SAPDBL", "Saptakoshi Development Bank Ltd."),
]


@app.route("/", methods=["GET", "POST"])
def index():
    qr_img = None
    if request.method == "POST":
        name = request.form.get("name")
        bank_code = request.form.get("bank")
        account_number = request.form.get("accountNumber")

        # Find bank name from code
        bank_name = next(
            (bname for bcode, bname in banks if bcode == bank_code), "Unknown Bank")

        # Compose text to encode in QR
        qr_data = f"Name: {name}\nBank: {bank_name} ({bank_code})\nAccount Number: {account_number}"

        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")

        # Convert PIL image to base64 string to embed in HTML
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        qr_img = f"data:image/png;base64,{img_str}"

    return render_template("qr.html", banks=banks, qr_img=qr_img)


if __name__ == "__main__":
    app.run(debug=True)
