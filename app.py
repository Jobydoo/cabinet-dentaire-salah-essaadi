import os
import io
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from dotenv import load_dotenv

import db_service

load_dotenv()

app = Flask(__name__)
secret_key = (os.getenv("FLASK_SECRET_KEY") or "").strip()
if not secret_key:
    secret_key = "cle_secrete_salah_essaadi_dentaire_2026_ultra_secure_pro"
app.secret_key = secret_key
app.config["SECRET_KEY"] = secret_key

# الإعدادات العامة لعيادة طب الأسنان
CABINET_NAME = os.getenv("CABINET_NAME", "عيادة الدكتور صلاح السعدي لطب وجراحة الأسنان")
CABINET_PHONE = os.getenv("CABINET_PHONE", "+212 5 22 00 11 22")
CABINET_ADDRESS = os.getenv("CABINET_ADDRESS", "شارع أنفا، الدار البيضاء")
CABINET_CURRENCY = os.getenv("CABINET_CURRENCY", "درهم")
DEFAULT_GOOGLE_MAPS_URL = os.getenv(
    "GOOGLE_MAPS_REVIEW_URL",
    "https://search.google.com/local/writereview?placeid=ChIJN1t_tDeuEmsRUsoyG83frY4"
)

# قائمة التدخلات الطبية السريرية / أنواع الجلسات
DENTAL_ACTS = [
    "أخذ القياس / طبعة الأسنان",
    "صب وتجهيز قالب الأسنان وتحديد الإطباق",
    "تجربة هيكل التركيبة (معدن / زركونيا)",
    "تجربة الشمع والشكل الجمالي",
    "تركيب وتثبيت التركيبة النهائية",
    "تعديل وضبط الإطباق والعضة",
    "فحص ومتابعة دورية بعد العلاج",
    "تنظيف وتلميع الأسنان وإزالة الجير",
    "خلع سن أو ضرس",
    "استشارة وكشف أولي مع خطة العلاج"
]

@app.context_processor
def inject_global_vars():
    return {
        "cabinet_name": CABINET_NAME,
        "cabinet_phone": CABINET_PHONE,
        "cabinet_address": CABINET_ADDRESS,
        "cabinet_currency": CABINET_CURRENCY,
        "current_date": date.today().isoformat(),
        "current_year": datetime.now().year,
        "google_maps_review_url": DEFAULT_GOOGLE_MAPS_URL,
        "dental_acts": DENTAL_ACTS
    }

@app.errorhandler(500)
def internal_server_error(e):
    return redirect(url_for("dashboard"))

# ==============================================================================
# ROUTE : TABLEAU DE BORD (ACCUEIL)
# ==============================================================================
@app.route("/")
def dashboard():
    metrics = db_service.get_dashboard_metrics()
    return render_template("dashboard.html", metrics=metrics)

# ==============================================================================
# ROUTES : CLIENTS / PATIENTS
# ==============================================================================
@app.route("/clients")
def clients_list():
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    all_clients = db_service.get_clients(search_query)

    if status_filter == "balance_due":
        filtered_clients = [c for c in all_clients if c.get("remaining_balance", 0) > 0]
    elif status_filter == "settled":
        filtered_clients = [c for c in all_clients if c.get("remaining_balance", 0) == 0 and c.get("total_quote", 0) > 0]
    else:
        filtered_clients = all_clients

    return render_template(
        "clients/list.html",
        clients=filtered_clients,
        search_query=search_query,
        status_filter=status_filter,
        total_count=len(all_clients)
    )

@app.route("/clients/new", methods=["GET", "POST"])
def client_create():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        medical_notes = request.form.get("medical_notes", "").strip()

        if not first_name or not last_name or not phone:
            flash("يرجى ملء الاسم الشخصي والعائلي ورقم الهاتف على الأقل.", "danger")
            return render_template("clients/form.html", client={})

        new_client = db_service.create_client({
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
            "address": address,
            "medical_notes": medical_notes
        })
        flash(f"تم تسجيل المريض {first_name} {last_name} بنجاح !", "success")
        return redirect(url_for("client_view", client_id=new_client["id"]))

    return render_template("clients/form.html", client={}, is_edit=False)

@app.route("/clients/<client_id>")
def client_view(client_id):
    client = db_service.get_client_by_id(client_id)
    if not client:
        flash("ملف المريض غير موجود.", "warning")
        return redirect(url_for("clients_list"))

    treatments = db_service.get_treatments_by_client(client_id)
    appointments = db_service.get_appointments_by_client(client_id)
    payments = db_service.get_payments_by_client(client_id)
    financials = db_service.calculate_financials_for_client(client_id, treatments, payments)

    return render_template(
        "clients/view.html",
        client=client,
        treatments=treatments,
        appointments=appointments,
        payments=payments,
        financials=financials,
        status_labels=db_service.TREATMENT_STATUS_LABELS
    )

@app.route("/clients/<client_id>/edit", methods=["GET", "POST"])
def client_edit(client_id):
    client = db_service.get_client_by_id(client_id)
    if not client:
        flash("ملف المريض غير موجود.", "warning")
        return redirect(url_for("clients_list"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        medical_notes = request.form.get("medical_notes", "").strip()

        if not first_name or not last_name or not phone:
            flash("الاسم الشخصي والعائلي ورقم الهاتف معلومات إلزامية.", "danger")
            return render_template("clients/form.html", client=client, is_edit=True)

        db_service.update_client(client_id, {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
            "address": address,
            "medical_notes": medical_notes
        })
        flash("تم تحديث معلومات المريض بنجاح.", "success")
        return redirect(url_for("client_view", client_id=client_id))

    return render_template("clients/form.html", client=client, is_edit=True)

@app.route("/clients/<client_id>/delete", methods=["POST"])
def client_delete(client_id):
    db_service.delete_client(client_id)
    flash("تم حذف ملف المريض.", "info")
    return redirect(url_for("clients_list"))

# ==============================================================================
# ROUTES : PROTHÈSES & TRAITEMENTS (التركيبات وأعمال المختبر)
# ==============================================================================
@app.route("/treatments/add", methods=["POST"])
def treatment_add():
    client_id = request.form.get("client_id")
    title = request.form.get("title", "").strip()
    teeth_numbers = request.form.get("teeth_numbers", "").strip()
    shade = request.form.get("shade", "").strip()
    status = request.form.get("status", "empreinte")
    total_cost = request.form.get("total_cost", "0").replace(",", ".")
    delivery_date = request.form.get("delivery_date", "").strip()
    notes = request.form.get("notes", "").strip()

    try:
        total_cost_val = float(total_cost)
    except ValueError:
        total_cost_val = 0.0

    if not client_id or not title:
        flash("يرجى تحديد مسمى العمل أو التركيبة السنية.", "danger")
        return redirect(url_for("client_view", client_id=client_id))

    db_service.create_treatment({
        "client_id": client_id,
        "title": title,
        "teeth_numbers": teeth_numbers,
        "shade": shade,
        "status": status,
        "total_cost": total_cost_val,
        "delivery_date": delivery_date,
        "notes": notes
    })
    flash(f"تمت إضافة التركيبة '{title}' بنجاح إلى ملف المريض.", "success")
    return redirect(url_for("client_view", client_id=client_id))

@app.route("/treatments/<treatment_id>/status", methods=["GET", "POST"])
def treatment_update_status(treatment_id):
    if request.method == "POST":
        new_status = request.form.get("status")
        client_id = request.form.get("client_id")
        if new_status:
            db_service.update_treatment_status(treatment_id, new_status)
            flash("تم تحديث مرحلة الإنجاز بنجاح.", "success")
        if client_id:
            return redirect(url_for("client_view", client_id=client_id))
    return redirect(url_for("dashboard"))

@app.route("/treatments/<treatment_id>/delete", methods=["POST"])
def treatment_delete(treatment_id):
    client_id = request.form.get("client_id")
    db_service.delete_treatment(treatment_id)
    flash("تم حذف التركيبة السنية.", "info")
    return redirect(url_for("client_view", client_id=client_id))

# ==============================================================================
# ROUTES : SÉANCES & RENDEZ-VOUS (الجلسات والمواعيد)
# ==============================================================================
@app.route("/appointments")
def appointments_list():
    date_filter = request.args.get("date", "").strip()
    all_appointments = db_service.get_appointments(date_filter=date_filter if date_filter else None)
    clients = db_service.get_clients()
    return render_template(
        "appointments/list.html",
        appointments=all_appointments,
        clients=clients,
        date_filter=date_filter,
        today=date.today().isoformat()
    )

@app.route("/appointments/add", methods=["POST"])
def appointment_add():
    client_id = request.form.get("client_id")
    appointment_date = request.form.get("appointment_date")
    start_time = request.form.get("start_time")
    duration_minutes = request.form.get("duration_minutes", "30")
    act_type = request.form.get("act_type", "استشارة وكشف أولي مع خطة العلاج")
    status = request.form.get("status", "planifie")
    notes = request.form.get("notes", "").strip()
    redirect_to = request.form.get("redirect_to", "appointments")

    if not client_id or not appointment_date or not start_time:
        flash("يرجى اختيار المريض وتحديد تاريخ ووقت الموعد.", "danger")
        if redirect_to == "client":
            return redirect(url_for("client_view", client_id=client_id))
        return redirect(url_for("appointments_list"))

    db_service.create_appointment({
        "client_id": client_id,
        "appointment_date": appointment_date,
        "start_time": start_time,
        "duration_minutes": int(duration_minutes),
        "act_type": act_type,
        "status": status,
        "notes": notes
    })
    flash("تم حجز الموعد بنجاح في الأجندة.", "success")
    if redirect_to == "client":
        return redirect(url_for("client_view", client_id=client_id))
    return redirect(url_for("appointments_list"))

@app.route("/appointments/<appointment_id>/status", methods=["GET", "POST"])
def appointment_update_status(appointment_id):
    if request.method == "POST":
        status = request.form.get("status")
        redirect_to = request.form.get("redirect_to", "appointments")
        client_id = request.form.get("client_id")

        if status:
            db_service.update_appointment_status(appointment_id, status)
            flash("تم تحديث حالة الموعد.", "success")

        if redirect_to == "client" and client_id:
            return redirect(url_for("client_view", client_id=client_id))
    return redirect(url_for("appointments_list"))

@app.route("/appointments/<appointment_id>/delete", methods=["POST"])
def appointment_delete(appointment_id):
    client_id = request.form.get("client_id")
    db_service.delete_appointment(appointment_id)
    flash("تم حذف الموعد من الأجندة.", "info")
    if client_id:
        return redirect(url_for("client_view", client_id=client_id))
    return redirect(url_for("appointments_list"))

# ==============================================================================
# ROUTES : PAIEMENTS & FACTURATION ÉCHELONNÉE (المداخيل والدفعات)
# ==============================================================================
@app.route("/payments")
def payments_list():
    payments = db_service.get_all_payments()
    clients = db_service.get_clients()
    metrics = db_service.get_dashboard_metrics()
    return render_template("payments/list.html", payments=payments, clients=clients, financial=metrics["financial"])

@app.route("/payments/add", methods=["POST"])
def payment_add():
    client_id = request.form.get("client_id")
    treatment_id = request.form.get("treatment_id")
    amount = request.form.get("amount", "0").replace(",", ".")
    payment_date = request.form.get("payment_date", date.today().isoformat())
    payment_method = request.form.get("payment_method", "especes")
    next_payment_date = request.form.get("next_payment_date", "").strip()
    notes = request.form.get("notes", "").strip()
    redirect_to = request.form.get("redirect_to", "client")

    try:
        amount_val = float(amount)
    except ValueError:
        amount_val = 0.0

    if not client_id or amount_val <= 0:
        flash("يرجى إدخال مبلغ دفع صالح أكبر من الصفر.", "danger")
        if redirect_to == "client":
            return redirect(url_for("client_view", client_id=client_id))
        return redirect(url_for("payments_list"))

    db_service.create_payment({
        "client_id": client_id,
        "treatment_id": treatment_id,
        "amount": amount_val,
        "payment_date": payment_date,
        "payment_method": payment_method,
        "next_payment_date": next_payment_date,
        "notes": notes
    })
    flash(f"تم تسجيل دفعة بقيمة {amount_val} {CABINET_CURRENCY} بنجاح. تم تحديث الباقي المستحق !", "success")

    if redirect_to == "client":
        return redirect(url_for("client_view", client_id=client_id))
    return redirect(url_for("payments_list"))

@app.route("/payments/<payment_id>/delete", methods=["POST"])
def payment_delete(payment_id):
    client_id = request.form.get("client_id")
    db_service.delete_payment(payment_id)
    flash("تم حذف سجل الدفعة.", "info")
    if client_id:
        return redirect(url_for("client_view", client_id=client_id))
    return redirect(url_for("payments_list"))

# ==============================================================================
# ROUTE : MODULE QR CODE GOOGLE MAPS (AVIS 5 ÉTOILES)
# ==============================================================================
@app.route("/qrcode")
def qrcode_module():
    custom_url = request.args.get("url", DEFAULT_GOOGLE_MAPS_URL).strip()
    client_id = request.args.get("client_id", "").strip()
    client = db_service.get_client_by_id(client_id) if client_id else None
    return render_template("qrcode/index.html", target_url=custom_url, client=client)

@app.route("/qrcode/generate")
def qrcode_generate():
    target_url = request.args.get("url", DEFAULT_GOOGLE_MAPS_URL).strip()
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2
        )
        qr.add_data(target_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")
    except Exception as e:
        # Fallback SVG dynamique si Pillow / qrcode n'est pas encore installé
        print(f"[QR Code Fallback]: {e}")
        import urllib.parse
        encoded_url = urllib.parse.quote(target_url)
        # Redirection vers le générateur d'API QR code universel haute fiabilité
        return redirect(f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_url}&color=0f172a")

# ==============================================================================
# API JSON POUR RECHERCHE RAPIDE
# ==============================================================================
@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    results = db_service.get_clients(q)
    return jsonify([{
        "id": c["id"],
        "name": f"{c.get('last_name', '')} {c.get('first_name', '')}",
        "phone": c.get("phone", ""),
        "remaining_balance": c.get("remaining_balance", 0),
        "url": url_for("client_view", client_id=c["id"])
    } for c in results[:10]])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
