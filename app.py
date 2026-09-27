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
        paid_amount_str = request.form.get("paid_amount", "").strip().replace(",", ".")
        remaining_amount_str = request.form.get("remaining_amount", "").strip().replace(",", ".")

        if not first_name or not last_name or not phone:
            flash("يرجى ملء الاسم الشخصي والعائلي ورقم الهاتف على الأقل.", "danger")
            return render_template("clients/form.html", client={})

        try:
            paid_amount = max(0.0, float(paid_amount_str)) if paid_amount_str else 0.0
        except ValueError:
            paid_amount = 0.0

        try:
            remaining_amount = max(0.0, float(remaining_amount_str)) if remaining_amount_str else 0.0
        except ValueError:
            remaining_amount = 0.0

        new_client = db_service.create_client({
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
            "address": address,
            "medical_notes": medical_notes
        })
        client_id = new_client["id"]

        total_cost = paid_amount + remaining_amount
        if total_cost > 0:
            treatment_record = db_service.create_treatment({
                "client_id": client_id,
                "title": "كشف وعلاج أسنان",
                "teeth_numbers": "",
                "shade": "",
                "status": "empreinte",
                "total_cost": total_cost,
                "delivery_date": None,
                "notes": f"تم تسجيل الحساب عند فتح الملف: مدفوع ({paid_amount})، باقي ({remaining_amount})"
            })

            if paid_amount > 0:
                db_service.create_payment({
                    "client_id": client_id,
                    "treatment_id": treatment_record.get("id") if treatment_record else None,
                    "amount": paid_amount,
                    "payment_date": date.today().isoformat(),
                    "payment_method": "especes",
                    "next_payment_date": None,
                    "notes": "دفعة أولى عند فتح الملف"
                })

        flash(f"تم تسجيل المريض {first_name} {last_name} بنجاح !", "success")
        return redirect(url_for("client_view", client_id=client_id))

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
    invoices = [inv for inv in db_service.get_invoices() if str(inv.get("client_id")) == str(client_id)]
    financials = db_service.calculate_financials_for_client(client_id, treatments, payments)

    return render_template(
        "clients/view.html",
        client=client,
        treatments=treatments,
        appointments=appointments,
        payments=payments,
        invoices=invoices,
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
        paid_amount_str = request.form.get("paid_amount", "").strip().replace(",", ".")
        remaining_amount_str = request.form.get("remaining_amount", "").strip().replace(",", ".")

        if not first_name or not last_name or not phone:
            flash("الاسم الشخصي والعائلي ورقم الهاتف معلومات إلزامية.", "danger")
            return render_template("clients/form.html", client=client, is_edit=True)

        try:
            paid_amount = max(0.0, float(paid_amount_str)) if paid_amount_str else 0.0
        except ValueError:
            paid_amount = 0.0

        try:
            remaining_amount = max(0.0, float(remaining_amount_str)) if remaining_amount_str else 0.0
        except ValueError:
            remaining_amount = 0.0

        db_service.update_client(client_id, {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
            "address": address,
            "medical_notes": medical_notes
        })

        treatments = db_service.get_treatments_by_client(client_id)
        payments = db_service.get_payments_by_client(client_id)
        total_cost = paid_amount + remaining_amount

        if not treatments and total_cost > 0:
            treatment_record = db_service.create_treatment({
                "client_id": client_id,
                "title": "كشف وعلاج أسنان",
                "teeth_numbers": "",
                "shade": "",
                "status": "empreinte",
                "total_cost": total_cost,
                "delivery_date": None,
                "notes": f"تم تسجيل الحساب عند تعديل الملف: مدفوع ({paid_amount})، باقي ({remaining_amount})"
            })
            if paid_amount > 0:
                db_service.create_payment({
                    "client_id": client_id,
                    "treatment_id": treatment_record.get("id") if treatment_record else None,
                    "amount": paid_amount,
                    "payment_date": date.today().isoformat(),
                    "payment_method": "especes",
                    "next_payment_date": None,
                    "notes": "دفعة أولى عند تعديل الملف"
                })
        elif len(treatments) == 1 and len(payments) <= 1 and total_cost > 0:
            db_service.update_treatment(treatments[0]["id"], {"total_cost": total_cost})
            if payments:
                if paid_amount > 0:
                    db_service.update_payment(payments[0]["id"], {"amount": paid_amount})
                else:
                    db_service.delete_payment(payments[0]["id"])
            elif paid_amount > 0:
                db_service.create_payment({
                    "client_id": client_id,
                    "treatment_id": treatments[0]["id"],
                    "amount": paid_amount,
                    "payment_date": date.today().isoformat(),
                    "payment_method": "especes",
                    "next_payment_date": None,
                    "notes": "دفعة مسجلة عند تعديل الملف"
                })

        flash("تم تحديث معلومات المريض بنجاح.", "success")
        return redirect(url_for("client_view", client_id=client_id))

    return render_template("clients/form.html", client=client, is_edit=True)

@app.route("/clients/<client_id>/delete", methods=["POST"])
def client_delete(client_id):
    db_service.delete_client(client_id)
    flash("تم حذف ملف المريض.", "info")
    return redirect(url_for("clients_list"))

@app.route("/clients/<client_id>/duplicate", methods=["GET", "POST"])
def client_duplicate(client_id):
    dup = db_service.duplicate_client(client_id)
    if dup:
        flash(f"تم نسخ ملف المريض بنجاح: {dup.get('first_name')} {dup.get('last_name')}", "success")
        return redirect(url_for("client_view", client_id=dup["id"]))
    flash("تعذر تكرار ملف المريض.", "danger")
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

@app.route("/treatments/<treatment_id>/edit", methods=["POST"])
def treatment_edit(treatment_id):
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

    db_service.update_treatment(treatment_id, {
        "title": title,
        "teeth_numbers": teeth_numbers,
        "shade": shade,
        "status": status,
        "total_cost": total_cost_val,
        "delivery_date": delivery_date,
        "notes": notes
    })
    flash("تم تعديل بيانات التركيبة السنية بنجاح.", "success")
    if client_id:
        return redirect(url_for("client_view", client_id=client_id))
    return redirect(url_for("dashboard"))

@app.route("/treatments/<treatment_id>/duplicate", methods=["GET", "POST"])
def treatment_duplicate(treatment_id):
    client_id = request.args.get("client_id") or request.form.get("client_id")
    dup = db_service.duplicate_treatment(treatment_id)
    if dup:
        flash("تم تكرار التركيبة السنية بنجاح.", "success")
        cid = dup.get("client_id") or client_id
        if cid:
            return redirect(url_for("client_view", client_id=cid))
    flash("تعذر تكرار التركيبة.", "danger")
    return redirect(url_for("clients_list"))


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

@app.route("/appointments/<appointment_id>/edit", methods=["POST"])
def appointment_edit(appointment_id):
    client_id = request.form.get("client_id")
    appointment_date = request.form.get("appointment_date")
    start_time = request.form.get("start_time")
    duration_minutes = request.form.get("duration_minutes", "30")
    act_type = request.form.get("act_type", "استشارة وكشف أولي مع خطة العلاج")
    status = request.form.get("status", "planifie")
    notes = request.form.get("notes", "").strip()
    redirect_to = request.form.get("redirect_to", "appointments")

    try:
        duration_val = int(duration_minutes)
    except ValueError:
        duration_val = 30

    db_service.update_appointment(appointment_id, {
        "client_id": client_id,
        "appointment_date": appointment_date,
        "start_time": start_time,
        "duration_minutes": duration_val,
        "act_type": act_type,
        "status": status,
        "notes": notes
    })
    flash("تم تحديث الموعد بنجاح.", "success")
    if redirect_to == "client" and client_id:
        return redirect(url_for("client_view", client_id=client_id))
    return redirect(url_for("appointments_list"))

@app.route("/appointments/<appointment_id>/duplicate", methods=["GET", "POST"])
def appointment_duplicate(appointment_id):
    redirect_to = request.args.get("redirect_to") or request.form.get("redirect_to", "appointments")
    dup = db_service.duplicate_appointment(appointment_id)
    if dup:
        flash("تم تكرار الموعد بنجاح.", "success")
        if redirect_to == "client" and dup.get("client_id"):
            return redirect(url_for("client_view", client_id=dup["client_id"]))
    else:
        flash("تعذر تكرار الموعد.", "danger")
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

@app.route("/payments/<payment_id>/edit", methods=["POST"])
def payment_edit(payment_id):
    client_id = request.form.get("client_id")
    amount = request.form.get("amount", "0").replace(",", ".")
    payment_date = request.form.get("payment_date")
    payment_method = request.form.get("payment_method", "especes")
    next_payment_date = request.form.get("next_payment_date", "").strip()
    notes = request.form.get("notes", "").strip()
    redirect_to = request.form.get("redirect_to", "client")

    try:
        amount_val = float(amount)
    except ValueError:
        amount_val = 0.0

    db_service.update_payment(payment_id, {
        "amount": amount_val,
        "payment_date": payment_date,
        "payment_method": payment_method,
        "next_payment_date": next_payment_date,
        "notes": notes
    })
    flash("تم تعديل بيانات الدفعة بنجاح.", "success")
    if redirect_to == "client" and client_id:
        return redirect(url_for("client_view", client_id=client_id))
    return redirect(url_for("payments_list"))

@app.route("/payments/<payment_id>/duplicate", methods=["GET", "POST"])
def payment_duplicate(payment_id):
    redirect_to = request.args.get("redirect_to") or request.form.get("redirect_to", "payments")
    dup = db_service.duplicate_payment(payment_id)
    if dup:
        flash("تم نسخ الدفعة بنجاح.", "success")
        if redirect_to == "client" and dup.get("client_id"):
            return redirect(url_for("client_view", client_id=dup["client_id"]))
    else:
        flash("تعذر نسخ الدفعة.", "danger")
    return redirect(url_for("payments_list"))

@app.route("/payments/<payment_id>/print")
def payment_print(payment_id):
    payment = db_service.get_payment_by_id(payment_id)
    if not payment:
        flash("سجل الدفعة غير موجود.", "warning")
        return redirect(url_for("payments_list"))
    client = db_service.get_client_by_id(payment.get("client_id"))
    treatment = db_service.get_treatment_by_id(payment.get("treatment_id")) if payment.get("treatment_id") else None
    return render_template("payments/print_receipt.html", payment=payment, client=client, treatment=treatment)

# ==============================================================================
# ROUTES : FACTURATION & DEVIS (الفواتير والمقايسات)
# ==============================================================================
@app.route("/invoices")
def invoices_list():
    status_filter = request.args.get("status", "").strip()
    type_filter = request.args.get("type", "").strip()
    search_query = request.args.get("q", "").strip()
    all_invoices = db_service.get_invoices(
        status=status_filter if status_filter else None,
        invoice_type=type_filter if type_filter else None
    )
    if search_query:
        q_lower = search_query.lower()
        all_invoices = [
            inv for inv in all_invoices
            if q_lower in inv.get("invoice_number", "").lower()
            or q_lower in inv.get("client_name", "").lower()
        ]
    clients = db_service.get_clients()

    total_invoiced = sum(float(inv.get("total_amount", 0)) for inv in all_invoices if inv.get("type") == "facture")
    total_paid = sum(float(inv.get("paid_amount", 0)) for inv in all_invoices if inv.get("type") == "facture")
    total_remaining = sum(float(inv.get("remaining_amount", 0)) for inv in all_invoices if inv.get("type") == "facture")

    return render_template(
        "invoices/list.html",
        invoices=all_invoices,
        clients=clients,
        status_filter=status_filter,
        type_filter=type_filter,
        search_query=search_query,
        total_invoiced=total_invoiced,
        total_paid=total_paid,
        total_remaining=total_remaining
    )

@app.route("/invoices/new", methods=["GET", "POST"])
def invoice_create():
    clients = db_service.get_clients()
    selected_client_id = request.args.get("client_id", "").strip()
    client = db_service.get_client_by_id(selected_client_id) if selected_client_id else None
    treatments = db_service.get_treatments_by_client(selected_client_id) if selected_client_id else []

    if request.method == "POST":
        client_id = request.form.get("client_id")
        inv_type = request.form.get("type", "facture")
        invoice_date = request.form.get("date", date.today().isoformat())
        due_date = request.form.get("due_date", "").strip()
        status = request.form.get("status", "non_payee")
        notes = request.form.get("notes", "").strip()

        item_descriptions = request.form.getlist("item_description[]")
        item_quantities = request.form.getlist("item_quantity[]")
        item_unit_prices = request.form.getlist("item_unit_price[]")

        items = []
        total_amount = 0.0
        for desc, qty_str, price_str in zip(item_descriptions, item_quantities, item_unit_prices):
            desc = desc.strip()
            if not desc:
                continue
            try:
                qty = int(qty_str) if qty_str else 1
            except ValueError:
                qty = 1
            try:
                unit_price = float(price_str.replace(",", ".")) if price_str else 0.0
            except ValueError:
                unit_price = 0.0
            total_line = round(qty * unit_price, 2)
            items.append({
                "description": desc,
                "quantity": qty,
                "unit_price": unit_price,
                "total": total_line
            })
            total_amount += total_line

        paid_str = request.form.get("paid_amount", "0").replace(",", ".")
        try:
            paid_amount = float(paid_str) if paid_str else 0.0
        except ValueError:
            paid_amount = 0.0

        discount_str = request.form.get("discount", "0").replace(",", ".")
        try:
            discount = float(discount_str) if discount_str else 0.0
        except ValueError:
            discount = 0.0

        net_total = max(0.0, total_amount - discount)
        remaining_amount = max(0.0, net_total - paid_amount)

        new_inv = db_service.create_invoice({
            "client_id": client_id,
            "type": inv_type,
            "date": invoice_date,
            "due_date": due_date,
            "status": status,
            "items": items,
            "total_amount": net_total,
            "paid_amount": paid_amount,
            "remaining_amount": remaining_amount,
            "discount": discount,
            "notes": notes
        })
        flash(f"تم إنشاء {'الفاتورة' if inv_type == 'facture' else 'المقايسة'} بنجاح رقم {new_inv.get('invoice_number')} !", "success")
        return redirect(url_for("invoice_view", invoice_id=new_inv["id"]))

    return render_template("invoices/form.html", clients=clients, selected_client=client, treatments=treatments, is_edit=False)

@app.route("/invoices/<invoice_id>")
def invoice_view(invoice_id):
    inv = db_service.get_invoice_by_id(invoice_id)
    if not inv:
        flash("الفاتورة غير موجودة.", "warning")
        return redirect(url_for("invoices_list"))
    client = db_service.get_client_by_id(inv.get("client_id"))
    return render_template("invoices/view.html", invoice=inv, client=client)

@app.route("/invoices/<invoice_id>/edit", methods=["GET", "POST"])
def invoice_edit(invoice_id):
    inv = db_service.get_invoice_by_id(invoice_id)
    if not inv:
        flash("الفاتورة غير موجودة.", "warning")
        return redirect(url_for("invoices_list"))
    clients = db_service.get_clients()
    client = db_service.get_client_by_id(inv.get("client_id"))

    if request.method == "POST":
        client_id = request.form.get("client_id")
        inv_type = request.form.get("type", "facture")
        invoice_date = request.form.get("date", date.today().isoformat())
        due_date = request.form.get("due_date", "").strip()
        status = request.form.get("status", "non_payee")
        notes = request.form.get("notes", "").strip()

        item_descriptions = request.form.getlist("item_description[]")
        item_quantities = request.form.getlist("item_quantity[]")
        item_unit_prices = request.form.getlist("item_unit_price[]")

        items = []
        total_amount = 0.0
        for desc, qty_str, price_str in zip(item_descriptions, item_quantities, item_unit_prices):
            desc = desc.strip()
            if not desc:
                continue
            try:
                qty = int(qty_str) if qty_str else 1
            except ValueError:
                qty = 1
            try:
                unit_price = float(price_str.replace(",", ".")) if price_str else 0.0
            except ValueError:
                unit_price = 0.0
            total_line = round(qty * unit_price, 2)
            items.append({
                "description": desc,
                "quantity": qty,
                "unit_price": unit_price,
                "total": total_line
            })
            total_amount += total_line

        paid_str = request.form.get("paid_amount", "0").replace(",", ".")
        try:
            paid_amount = float(paid_str) if paid_str else 0.0
        except ValueError:
            paid_amount = 0.0

        discount_str = request.form.get("discount", "0").replace(",", ".")
        try:
            discount = float(discount_str) if discount_str else 0.0
        except ValueError:
            discount = 0.0

        net_total = max(0.0, total_amount - discount)
        remaining_amount = max(0.0, net_total - paid_amount)

        db_service.update_invoice(invoice_id, {
            "client_id": client_id,
            "type": inv_type,
            "date": invoice_date,
            "due_date": due_date,
            "status": status,
            "items": items,
            "total_amount": net_total,
            "paid_amount": paid_amount,
            "remaining_amount": remaining_amount,
            "discount": discount,
            "notes": notes
        })
        flash("تم تحديث الفاتورة بنجاح.", "success")
        return redirect(url_for("invoice_view", invoice_id=invoice_id))

    return render_template("invoices/form.html", invoice=inv, clients=clients, selected_client=client, is_edit=True)

@app.route("/invoices/<invoice_id>/duplicate", methods=["GET", "POST"])
def invoice_duplicate(invoice_id):
    dup = db_service.duplicate_invoice(invoice_id)
    if dup:
        flash(f"تم تكرار الفاتورة بنجاح، رقم النسخة: {dup.get('invoice_number')}", "success")
        return redirect(url_for("invoice_view", invoice_id=dup["id"]))
    flash("تعذر تكرار الفاتورة.", "danger")
    return redirect(url_for("invoices_list"))

@app.route("/invoices/<invoice_id>/delete", methods=["POST"])
def invoice_delete(invoice_id):
    db_service.delete_invoice(invoice_id)
    flash("تم حذف الفاتورة بنجاح.", "info")
    return redirect(url_for("invoices_list"))

@app.route("/invoices/<invoice_id>/print")
def invoice_print(invoice_id):
    inv = db_service.get_invoice_by_id(invoice_id)
    if not inv:
        flash("الفاتورة غير موجودة.", "warning")
        return redirect(url_for("invoices_list"))
    client = db_service.get_client_by_id(inv.get("client_id"))
    return render_template("invoices/print.html", invoice=inv, client=client)


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
