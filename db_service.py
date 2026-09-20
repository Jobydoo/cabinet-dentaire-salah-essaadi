import os
import uuid
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

supabase_client = None
USE_SUPABASE = False

if SUPABASE_URL and SUPABASE_KEY and not SUPABASE_URL.startswith("https://votre-projet"):
    try:
        from supabase import create_client, Client
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        USE_SUPABASE = True
        print("[DB] Connecté avec succès à Supabase PostgreSQL.")
    except Exception as e:
        print(f"[DB WARN] Impossible de se connecter à Supabase ({e}). Utilisation du stockage local de démo.")
        USE_SUPABASE = False
else:
    print("[DB INFO] Variables Supabase non configurées ou par défaut. Mode démo autonome activé.")

# ==============================================================================
# BASE DE DONNÉES LOCALE / FALLBACK EN MÉMOIRE
# ==============================================================================
def get_iso_date(days_offset=0):
    return (date.today() + timedelta(days=days_offset)).isoformat()

def get_iso_now():
    return datetime.now().isoformat()

def is_valid_uuid(val):
    if not val:
        return False
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, AttributeError):
        return False

# Données de démonstration réalistes pour laboratoire / cabinet dentaire
_LOCAL_DB = {
    "clients": [
        {
            "id": "c1001-bennani-uuid",
            "first_name": "Karim",
            "last_name": "Bennani",
            "phone": "+212 6 61 23 45 67",
            "email": "k.bennani@email.com",
            "address": "12 Rue Al Massira, Casablanca",
            "medical_notes": "Sensibilité gingivale légère. Préfère les teintes naturelles translucides.",
            "created_at": get_iso_now(),
            "updated_at": get_iso_now()
        },
        {
            "id": "c1002-amrani-uuid",
            "first_name": "Sofia",
            "last_name": "El Amrani",
            "phone": "+212 6 72 89 12 34",
            "email": "sofia.amrani@email.com",
            "address": "45 Boulevard d'Anfa, Casablanca",
            "medical_notes": "Demande esthétique élevée secteur antérieur. Blanchiment préalable réalisé.",
            "created_at": get_iso_now(),
            "updated_at": get_iso_now()
        },
        {
            "id": "c1003-mansouri-uuid",
            "first_name": "Driss",
            "last_name": "Mansouri",
            "phone": "+212 6 50 11 22 33",
            "email": "driss.m@email.com",
            "address": "8 Avenue Hassan II, Rabat",
            "medical_notes": "Bruxisme nocturne sévère. Prévoir gouttière de désocclusion après pose.",
            "created_at": get_iso_now(),
            "updated_at": get_iso_now()
        },
        {
            "id": "c1004-tazi-uuid",
            "first_name": "Nadia",
            "last_name": "Tazi",
            "phone": "+212 6 63 99 88 77",
            "email": "nadia.tazi@gmail.com",
            "address": "24 Rue Moulay Youssef, Casablanca",
            "medical_notes": "Refait son appareil complet du bas. Préférence résine injectée hypoallergénique.",
            "created_at": get_iso_now(),
            "updated_at": get_iso_now()
        }
    ],
    "treatments": [
        {
            "id": "t2001-uuid",
            "client_id": "c1001-bennani-uuid",
            "title": "Couronne Zircone Multicouche Translucide",
            "teeth_numbers": "16",
            "shade": "A2",
            "status": "ceramique_finition", # empreinte, conception_cfao, armature, essayage, ceramique_finition, livre_pose
            "total_cost": 2800.00,
            "delivery_date": get_iso_date(3),
            "notes": "Finition maquillage cervical et glaçage satiné haute brillance.",
            "created_at": get_iso_now(),
            "updated_at": get_iso_now()
        },
        {
            "id": "t2002-uuid",
            "client_id": "c1002-amrani-uuid",
            "title": "Facettes E-Max Céramique Pressée (x4)",
            "teeth_numbers": "12, 11, 21, 22",
            "shade": "Bleach 2",
            "status": "essayage",
            "total_cost": 7200.00,
            "delivery_date": get_iso_date(2),
            "notes": "Morphologie arrondie féminine, translucidité incisale prononcée.",
            "created_at": get_iso_now(),
            "updated_at": get_iso_now()
        },
        {
            "id": "t2003-uuid",
            "client_id": "c1003-mansouri-uuid",
            "title": "Prothèse Squelettique Stellite Cobalt-Chrome",
            "teeth_numbers": "Maxillaire Supérieur",
            "shade": "A3",
            "status": "armature",
            "total_cost": 4500.00,
            "delivery_date": get_iso_date(5),
            "notes": "Châssis métallique allégé avec crochets esthétiques acétal.",
            "created_at": get_iso_now(),
            "updated_at": get_iso_now()
        },
        {
            "id": "t2004-uuid",
            "client_id": "c1004-tazi-uuid",
            "title": "Prothèse Adjointe Complète Résine Mandibulaire",
            "teeth_numbers": "Arcade Inférieure Complète",
            "shade": "A2.5",
            "status": "conception_cfao",
            "total_cost": 3800.00,
            "delivery_date": get_iso_date(7),
            "notes": "Bourrelets d'occlusion à valider avant montage des dents antérieures.",
            "created_at": get_iso_now(),
            "updated_at": get_iso_now()
        }
    ],
    "appointments": [
        {
            "id": "a3001-uuid",
            "client_id": "c1002-amrani-uuid",
            "appointment_date": get_iso_date(1),
            "start_time": "14:00",
            "duration_minutes": 60,
            "act_type": "Essayage biscuit / cire",
            "status": "confirme",
            "notes": "Validation de l'esthétique du sourire et de la ligne bi-pupillaire.",
            "created_at": get_iso_now()
        },
        {
            "id": "a3002-uuid",
            "client_id": "c1003-mansouri-uuid",
            "appointment_date": get_iso_date(2),
            "start_time": "11:15",
            "duration_minutes": 30,
            "act_type": "Essayage armature",
            "status": "planifie",
            "notes": "Vérification de l'assise du squelettique et des appuis cingulaires.",
            "created_at": get_iso_now()
        },
        {
            "id": "a3003-uuid",
            "client_id": "c1001-bennani-uuid",
            "appointment_date": get_iso_date(3),
            "start_time": "10:30",
            "duration_minutes": 45,
            "act_type": "Pose de prothèse finale",
            "status": "confirme",
            "notes": "Scellement définitif sous digue et contrôle des points de contact.",
            "created_at": get_iso_now()
        },
        {
            "id": "a3004-uuid",
            "client_id": "c1004-tazi-uuid",
            "appointment_date": get_iso_date(0),
            "start_time": "16:00",
            "duration_minutes": 40,
            "act_type": "Prise d'empreinte",
            "status": "confirme",
            "notes": "Empreinte secondaire au polyéther pour précision maximale des crêtes.",
            "created_at": get_iso_now()
        }
    ],
    "payments": [
        {
            "id": "p4001-uuid",
            "client_id": "c1001-bennani-uuid",
            "treatment_id": "t2001-uuid",
            "amount": 1500.00,
            "payment_date": get_iso_date(-8),
            "payment_method": "carte",
            "next_payment_date": get_iso_date(3),
            "notes": "Acompte de 50% versé lors de la prise d'empreinte optique.",
            "created_at": get_iso_now()
        },
        {
            "id": "p4002-uuid",
            "client_id": "c1002-amrani-uuid",
            "treatment_id": "t2002-uuid",
            "amount": 3500.00,
            "payment_date": get_iso_date(-5),
            "payment_method": "virement",
            "next_payment_date": get_iso_date(2),
            "notes": "Première tranche validée par virement instantané.",
            "created_at": get_iso_now()
        },
        {
            "id": "p4003-uuid",
            "client_id": "c1003-mansouri-uuid",
            "treatment_id": "t2003-uuid",
            "amount": 2000.00,
            "payment_date": get_iso_date(-3),
            "payment_method": "especes",
            "next_payment_date": get_iso_date(5),
            "notes": "Avance sur devis squelettique métallique.",
            "created_at": get_iso_now()
        },
        {
            "id": "p4004-uuid",
            "client_id": "c1004-tazi-uuid",
            "treatment_id": "t2004-uuid",
            "amount": 1200.00,
            "payment_date": get_iso_date(0),
            "payment_method": "especes",
            "next_payment_date": get_iso_date(7),
            "notes": "Acompte d'engagement pour démarrage maquette cire.",
            "created_at": get_iso_now()
        }
    ]
}

# ==============================================================================
# FONCTIONS DE CALCUL FINANCIER PAR PATIENT
# ==============================================================================
def calculate_financials_for_client(client_id, treatments_list=None, payments_list=None):
    if treatments_list is None:
        treatments_list = get_treatments_by_client(client_id)
    if payments_list is None:
        payments_list = get_payments_by_client(client_id)

    total_quote = sum(float(t.get("total_cost", 0.0)) for t in treatments_list)
    total_paid = sum(float(p.get("amount", 0.0)) for p in payments_list)
    remaining_balance = max(0.0, total_quote - total_paid)

    # Récupérer la date prévisionnelle du prochain versement (la plus récente ou prochaine non nulle)
    future_dates = [p.get("next_payment_date") for p in payments_list if p.get("next_payment_date")]
    next_payment_date = future_dates[-1] if future_dates else None

    # Statut du paiement
    if total_quote == 0.0:
        status_label = "Aucun devis"
        status_badge = "secondary"
    elif remaining_balance <= 0.0:
        status_label = "Soldé / Réglé"
        status_badge = "success"
    elif total_paid > 0.0:
        status_label = "Acompte partiel"
        status_badge = "warning"
    else:
        status_label = "En attente d'acompte"
        status_badge = "danger"

    percentage_paid = (total_paid / total_quote * 100) if total_quote > 0 else 0

    return {
        "client_id": client_id,
        "total_quote": round(total_quote, 2),
        "total_paid": round(total_paid, 2),
        "remaining_balance": round(remaining_balance, 2),
        "next_payment_date": next_payment_date,
        "status_label": status_label,
        "status_badge": status_badge,
        "percentage_paid": min(100, round(percentage_paid, 1))
    }

# ==============================================================================
# GESTION DES CLIENTS / PATIENTS
# ==============================================================================
def get_clients(search_query=None):
    if USE_SUPABASE:
        try:
            query = supabase_client.table("v_client_financial_summary").select("*").order("last_name")
            if search_query:
                search_term = f"%{search_query}%"
                query = query.or_(f"last_name.ilike.{search_term},first_name.ilike.{search_term},phone.ilike.{search_term}")
            res = query.execute()
            raw_clients = res.data or []
            results = []
            for r in raw_clients:
                c = dict(r)
                c["id"] = c.get("client_id")
                t_quote = float(c.get("total_quote") or 0.0)
                t_paid = float(c.get("total_paid") or 0.0)
                rem_bal = float(c.get("remaining_balance") or 0.0)
                c["total_quote"] = round(t_quote, 2)
                c["total_paid"] = round(t_paid, 2)
                c["remaining_balance"] = round(max(0.0, rem_bal), 2)
                c["percentage_paid"] = min(100.0, round((t_paid / t_quote * 100), 1)) if t_quote > 0 else 0
                if t_quote == 0.0:
                    c["status_label"] = "Aucun devis"
                    c["status_badge"] = "secondary"
                elif rem_bal <= 0.0:
                    c["status_label"] = "Soldé / Réglé"
                    c["status_badge"] = "success"
                elif t_paid > 0.0:
                    c["status_label"] = "Acompte partiel"
                    c["status_badge"] = "warning"
                else:
                    c["status_label"] = "En attente d'acompte"
                    c["status_badge"] = "danger"
                results.append(c)
            return sorted(results, key=lambda x: (x.get("last_name", ""), x.get("first_name", "")))
        except Exception as e:
            print(f"[Supabase Error get_clients]: {e}")
            clients = _LOCAL_DB["clients"]
    else:
        clients = _LOCAL_DB["clients"]

    # Filtrer si recherche en mode local
    if not USE_SUPABASE and search_query:
        q = search_query.strip().lower()
        clients = [
            c for c in clients
            if q in c.get("first_name", "").lower()
            or q in c.get("last_name", "").lower()
            or q in c.get("phone", "").lower()
        ]

    # Enrichir chaque client avec ses statistiques financières (mode local)
    results = []
    for c in clients:
        c_copy = dict(c)
        fin = calculate_financials_for_client(c["id"])
        c_copy.update(fin)
        results.append(c_copy)

    return sorted(results, key=lambda x: (x.get("last_name", ""), x.get("first_name", "")))

def get_client_by_id(client_id):
    if USE_SUPABASE and is_valid_uuid(client_id):
        try:
            res = supabase_client.table("clients").select("*").eq("id", client_id).single().execute()
            client = res.data
        except Exception as e:
            print(f"[Supabase Error get_client_by_id]: {e}")
            client = next((c for c in _LOCAL_DB["clients"] if c["id"] == client_id), None)
    else:
        client = next((c for c in _LOCAL_DB["clients"] if c["id"] == client_id), None)

    if client:
        client_copy = dict(client)
        fin = calculate_financials_for_client(client_id)
        client_copy.update(fin)
        return client_copy
    return None

def create_client(data):
    new_id = str(uuid.uuid4())
    client_record = {
        "id": new_id,
        "first_name": data.get("first_name", "").strip(),
        "last_name": data.get("last_name", "").strip(),
        "phone": data.get("phone", "").strip(),
        "email": data.get("email", "").strip(),
        "address": data.get("address", "").strip(),
        "medical_notes": data.get("medical_notes", "").strip(),
        "created_at": get_iso_now(),
        "updated_at": get_iso_now()
    }

    if USE_SUPABASE:
        try:
            res = supabase_client.table("clients").insert(client_record).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"[Supabase Error create_client]: {e}")

    # Fallback local
    _LOCAL_DB["clients"].insert(0, client_record)
    return client_record

def update_client(client_id, data):
    update_data = {
        "first_name": data.get("first_name", "").strip(),
        "last_name": data.get("last_name", "").strip(),
        "phone": data.get("phone", "").strip(),
        "email": data.get("email", "").strip(),
        "address": data.get("address", "").strip(),
        "medical_notes": data.get("medical_notes", "").strip(),
        "updated_at": get_iso_now()
    }

    if USE_SUPABASE and is_valid_uuid(client_id):
        try:
            res = supabase_client.table("clients").update(update_data).eq("id", client_id).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"[Supabase Error update_client]: {e}")

    # Fallback local
    for i, c in enumerate(_LOCAL_DB["clients"]):
        if c["id"] == client_id:
            _LOCAL_DB["clients"][i].update(update_data)
            return _LOCAL_DB["clients"][i]
    return None

def delete_client(client_id):
    if USE_SUPABASE and is_valid_uuid(client_id):
        try:
            supabase_client.table("clients").delete().eq("id", client_id).execute()
        except Exception as e:
            print(f"[Supabase Error delete_client]: {e}")

    # Fallback local
    _LOCAL_DB["clients"] = [c for c in _LOCAL_DB["clients"] if c["id"] != client_id]
    _LOCAL_DB["treatments"] = [t for t in _LOCAL_DB["treatments"] if t["client_id"] != client_id]
    _LOCAL_DB["appointments"] = [a for a in _LOCAL_DB["appointments"] if a["client_id"] != client_id]
    _LOCAL_DB["payments"] = [p for p in _LOCAL_DB["payments"] if p["client_id"] != client_id]
    return True

# ==============================================================================
# GESTION DES TRAITEMENTS & PROTHÈSES
# ==============================================================================
TREATMENT_STATUS_LABELS = {
    "empreinte": {"label": "Empreinte reçue", "color": "purple", "progress": 15},
    "conception_cfao": {"label": "Conception CFAO / Modèle", "color": "indigo", "progress": 35},
    "armature": {"label": "Armature / Coulée", "color": "blue", "progress": 55},
    "essayage": {"label": "Prêt pour essayage", "color": "amber", "progress": 75},
    "ceramique_finition": {"label": "Finition Céramique / Glaçage", "color": "emerald", "progress": 90},
    "livre_pose": {"label": "Livré & Posé", "color": "slate", "progress": 100}
}

def get_treatments_by_client(client_id):
    if USE_SUPABASE and is_valid_uuid(client_id):
        try:
            res = supabase_client.table("treatments").select("*").eq("client_id", client_id).order("created_at", desc=True).execute()
            treatments = res.data or []
        except Exception as e:
            print(f"[Supabase Error get_treatments_by_client]: {e}")
            treatments = [t for t in _LOCAL_DB["treatments"] if t["client_id"] == client_id]
    else:
        treatments = [t for t in _LOCAL_DB["treatments"] if t["client_id"] == client_id]

    for t in treatments:
        status_key = t.get("status", "empreinte")
        meta = TREATMENT_STATUS_LABELS.get(status_key, {"label": status_key, "color": "blue", "progress": 20})
        t["status_label"] = meta["label"]
        t["status_color"] = meta["color"]
        t["progress_percentage"] = meta["progress"]
    return treatments

def get_all_active_treatments():
    if USE_SUPABASE:
        try:
            res = supabase_client.table("treatments").select("*, clients(first_name, last_name, phone)").neq("status", "livre_pose").order("delivery_date").execute()
            treatments = res.data or []
        except Exception as e:
            print(f"[Supabase Error get_all_active_treatments]: {e}")
            treatments = [t for t in _LOCAL_DB["treatments"] if t.get("status") != "livre_pose"]
    else:
        treatments = [t for t in _LOCAL_DB["treatments"] if t.get("status") != "livre_pose"]

    if USE_SUPABASE:
        for t in treatments:
            client = t.get("clients") or {}
            t["client_name"] = f"{client.get('last_name', '')} {client.get('first_name', '')}".strip()
            t["client_phone"] = client.get("phone", "")
            status_key = t.get("status", "empreinte")
            meta = TREATMENT_STATUS_LABELS.get(status_key, {"label": status_key, "color": "blue", "progress": 20})
            t["status_label"] = meta["label"]
            t["status_color"] = meta["color"]
            t["progress_percentage"] = meta["progress"]
    else:
        client_map = {c["id"]: c for c in _LOCAL_DB["clients"]}
        for t in treatments:
            client = client_map.get(t.get("client_id"), {})
            t["client_name"] = f"{client.get('last_name', '')} {client.get('first_name', '')}".strip()
            t["client_phone"] = client.get("phone", "")
            status_key = t.get("status", "empreinte")
            meta = TREATMENT_STATUS_LABELS.get(status_key, {"label": status_key, "color": "blue", "progress": 20})
            t["status_label"] = meta["label"]
            t["status_color"] = meta["color"]
            t["progress_percentage"] = meta["progress"]

    return sorted(treatments, key=lambda x: x.get("delivery_date") or "9999-99-99")

def create_treatment(data):
    new_id = str(uuid.uuid4())
    record = {
        "id": new_id,
        "client_id": data.get("client_id"),
        "title": data.get("title", "").strip(),
        "teeth_numbers": data.get("teeth_numbers", "").strip(),
        "shade": data.get("shade", "").strip(),
        "status": data.get("status", "empreinte"),
        "total_cost": float(data.get("total_cost", 0.0)),
        "delivery_date": data.get("delivery_date") or None,
        "notes": data.get("notes", "").strip(),
        "created_at": get_iso_now(),
        "updated_at": get_iso_now()
    }

    if USE_SUPABASE:
        try:
            res = supabase_client.table("treatments").insert(record).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"[Supabase Error create_treatment]: {e}")

    _LOCAL_DB["treatments"].insert(0, record)
    return record

def update_treatment_status(treatment_id, new_status):
    update_data = {
        "status": new_status,
        "updated_at": get_iso_now()
    }

    if USE_SUPABASE:
        try:
            supabase_client.table("treatments").update(update_data).eq("id", treatment_id).execute()
            return True
        except Exception as e:
            print(f"[Supabase Error update_treatment_status]: {e}")

    for t in _LOCAL_DB["treatments"]:
        if t["id"] == treatment_id:
            t["status"] = new_status
            t["updated_at"] = get_iso_now()
            return True
    return False

def delete_treatment(treatment_id):
    if USE_SUPABASE:
        try:
            supabase_client.table("treatments").delete().eq("id", treatment_id).execute()
        except Exception as e:
            print(f"[Supabase Error delete_treatment]: {e}")

    _LOCAL_DB["treatments"] = [t for t in _LOCAL_DB["treatments"] if t["id"] != treatment_id]
    return True

# ==============================================================================
# GESTION DES RENDEZ-VOUS & SÉANCES
# ==============================================================================
def get_appointments(date_filter=None, upcoming_only=False):
    if USE_SUPABASE:
        try:
            query = supabase_client.table("appointments").select("*, clients(first_name, last_name, phone)").order("appointment_date").order("start_time")
            if date_filter:
                query = query.eq("appointment_date", date_filter)
            elif upcoming_only:
                query = query.gte("appointment_date", date.today().isoformat())
            res = query.execute()
            appointments = res.data or []
            for a in appointments:
                client = a.get("clients") or {}
                a["client_name"] = f"{client.get('last_name', '')} {client.get('first_name', '')}".strip()
                a["client_phone"] = client.get("phone", "")
            return sorted(appointments, key=lambda x: (x.get("appointment_date", ""), x.get("start_time", "")))
        except Exception as e:
            print(f"[Supabase Error get_appointments]: {e}")
            appointments = _LOCAL_DB["appointments"]
    else:
        appointments = _LOCAL_DB["appointments"]

    today_str = date.today().isoformat()
    if date_filter:
        appointments = [a for a in appointments if a.get("appointment_date") == date_filter]
    elif upcoming_only:
        appointments = [a for a in appointments if a.get("appointment_date") >= today_str]

    client_map = {c["id"]: c for c in _LOCAL_DB["clients"]}
    for a in appointments:
        client = client_map.get(a.get("client_id"), {})
        a["client_name"] = f"{client.get('last_name', '')} {client.get('first_name', '')}".strip()
        a["client_phone"] = client.get("phone", "")

    return sorted(appointments, key=lambda x: (x.get("appointment_date", ""), x.get("start_time", "")))

def get_appointments_by_client(client_id):
    if USE_SUPABASE and is_valid_uuid(client_id):
        try:
            res = supabase_client.table("appointments").select("*").eq("client_id", client_id).order("appointment_date", desc=True).order("start_time", desc=True).execute()
            return res.data or []
        except Exception as e:
            print(f"[Supabase Error get_appointments_by_client]: {e}")
            return [a for a in _LOCAL_DB["appointments"] if a["client_id"] == client_id]
    else:
        appts = [a for a in _LOCAL_DB["appointments"] if a["client_id"] == client_id]
        return sorted(appts, key=lambda x: (x.get("appointment_date", ""), x.get("start_time", "")), reverse=True)

def create_appointment(data):
    new_id = str(uuid.uuid4())
    record = {
        "id": new_id,
        "client_id": data.get("client_id"),
        "appointment_date": data.get("appointment_date"),
        "start_time": data.get("start_time"),
        "duration_minutes": int(data.get("duration_minutes", 30)),
        "act_type": data.get("act_type", "Consultation"),
        "status": data.get("status", "planifie"),
        "notes": data.get("notes", "").strip(),
        "created_at": get_iso_now()
    }

    if USE_SUPABASE:
        try:
            res = supabase_client.table("appointments").insert(record).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"[Supabase Error create_appointment]: {e}")

    _LOCAL_DB["appointments"].append(record)
    return record

def update_appointment_status(appointment_id, new_status):
    if USE_SUPABASE:
        try:
            supabase_client.table("appointments").update({"status": new_status}).eq("id", appointment_id).execute()
            return True
        except Exception as e:
            print(f"[Supabase Error update_appointment_status]: {e}")

    for a in _LOCAL_DB["appointments"]:
        if a["id"] == appointment_id:
            a["status"] = new_status
            return True
    return False

def delete_appointment(appointment_id):
    if USE_SUPABASE:
        try:
            supabase_client.table("appointments").delete().eq("id", appointment_id).execute()
        except Exception as e:
            print(f"[Supabase Error delete_appointment]: {e}")

    _LOCAL_DB["appointments"] = [a for a in _LOCAL_DB["appointments"] if a["id"] != appointment_id]
    return True

# ==============================================================================
# GESTION DES PAIEMENTS & FACTURATION ÉCHELONNÉE
# ==============================================================================
def get_payments_by_client(client_id):
    if USE_SUPABASE and is_valid_uuid(client_id):
        try:
            res = supabase_client.table("payments").select("*").eq("client_id", client_id).order("payment_date", desc=True).execute()
            return res.data or []
        except Exception as e:
            print(f"[Supabase Error get_payments_by_client]: {e}")
            return [p for p in _LOCAL_DB["payments"] if p["client_id"] == client_id]
    else:
        pays = [p for p in _LOCAL_DB["payments"] if p["client_id"] == client_id]
        return sorted(pays, key=lambda x: x.get("payment_date", ""), reverse=True)

def get_all_payments(limit=50):
    if USE_SUPABASE:
        try:
            res = supabase_client.table("payments").select("*, clients(first_name, last_name, phone)").order("payment_date", desc=True).limit(limit).execute()
            payments = res.data or []
            for p in payments:
                client = p.get("clients") or {}
                p["client_name"] = f"{client.get('last_name', '')} {client.get('first_name', '')}".strip()
            return payments
        except Exception as e:
            print(f"[Supabase Error get_all_payments]: {e}")
            payments = _LOCAL_DB["payments"][:limit]
    else:
        payments = sorted(_LOCAL_DB["payments"], key=lambda x: x.get("payment_date", ""), reverse=True)[:limit]

    client_map = {c["id"]: c for c in _LOCAL_DB["clients"]}
    for p in payments:
        client = client_map.get(p.get("client_id"), {})
        p["client_name"] = f"{client.get('last_name', '')} {client.get('first_name', '')}".strip()

    return payments

def create_payment(data):
    new_id = str(uuid.uuid4())
    record = {
        "id": new_id,
        "client_id": data.get("client_id"),
        "treatment_id": data.get("treatment_id") or None,
        "amount": float(data.get("amount", 0.0)),
        "payment_date": data.get("payment_date") or date.today().isoformat(),
        "payment_method": data.get("payment_method", "especes"),
        "next_payment_date": data.get("next_payment_date") or None,
        "notes": data.get("notes", "").strip(),
        "created_at": get_iso_now()
    }

    if USE_SUPABASE:
        try:
            res = supabase_client.table("payments").insert(record).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"[Supabase Error create_payment]: {e}")

    _LOCAL_DB["payments"].insert(0, record)
    return record

def delete_payment(payment_id):
    if USE_SUPABASE:
        try:
            supabase_client.table("payments").delete().eq("id", payment_id).execute()
        except Exception as e:
            print(f"[Supabase Error delete_payment]: {e}")

    _LOCAL_DB["payments"] = [p for p in _LOCAL_DB["payments"] if p["id"] != payment_id]
    return True

# ==============================================================================
# STATISTIQUES GLOBALES DU TABLEAU DE BORD
# ==============================================================================
def get_dashboard_metrics():
    clients = get_clients()
    treatments = get_all_active_treatments()
    today_str = date.today().isoformat()
    today_appointments = get_appointments(date_filter=today_str)
    upcoming_appointments = get_appointments(upcoming_only=True)
    recent_payments = get_all_payments(limit=10)

    total_quote_all = sum(c.get("total_quote", 0.0) for c in clients)
    total_paid_all = sum(c.get("total_paid", 0.0) for c in clients)
    total_remaining_balance = sum(c.get("remaining_balance", 0.0) for c in clients)

    # Répartition des prothèses par étape
    status_counts = {
        "empreinte": 0,
        "conception_cfao": 0,
        "armature": 0,
        "essayage": 0,
        "ceramique_finition": 0
    }
    for t in treatments:
        st = t.get("status")
        if st in status_counts:
            status_counts[st] += 1

    return {
        "total_clients": len(clients),
        "active_prosthetics": len(treatments),
        "today_appointments_count": len(today_appointments),
        "upcoming_appointments": upcoming_appointments[:5],
        "today_appointments": today_appointments,
        "urgent_treatments": treatments[:5],
        "recent_payments": recent_payments,
        "financial": {
            "total_quote": round(total_quote_all, 2),
            "total_paid": round(total_paid_all, 2),
            "total_remaining": round(total_remaining_balance, 2),
            "recovery_rate": round((total_paid_all / total_quote_all * 100), 1) if total_quote_all > 0 else 0
        },
        "status_counts": status_counts,
        "status_labels": TREATMENT_STATUS_LABELS,
        "is_supabase_connected": USE_SUPABASE
    }
