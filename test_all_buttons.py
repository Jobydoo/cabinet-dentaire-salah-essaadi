from app import app
import db_service

def test_full_cabinet_flow():
    client = app.test_client()
    print("[1] Test création patient...")
    res = client.post('/clients/new', data={
        'first_name': 'Omar',
        'last_name': 'Benjelloun',
        'phone': '+212 6 12 34 56 78',
        'email': 'omar.ben@email.com',
        'address': 'Gauthier, Casablanca',
        'medical_notes': 'Traitement implant et couronne zircone'
    }, follow_redirects=True)
    assert res.status_code == 200, "Erreur création patient"
    assert b"Benjelloun" in res.data or b"BENJELLOUN" in res.data
    print(" -> Patient cr\u00e9\u00e9 avec succ\u00e8s !")

    # Récupérer le patient
    patients = db_service.get_clients('Benjelloun')
    assert len(patients) > 0
    p = patients[0]
    p_id = p['id']

    print("[2] Test modification patient...")
    res = client.post(f'/clients/{p_id}/edit', data={
        'first_name': 'Omar',
        'last_name': 'Benjelloun',
        'phone': '+212 6 12 34 56 99',
        'email': 'omar.updated@email.com',
        'address': 'Gauthier, Casablanca (Mis à jour)',
        'medical_notes': 'Mis à jour'
    }, follow_redirects=True)
    assert res.status_code == 200
    p_updated = db_service.get_client_by_id(p_id)
    assert p_updated['phone'] == '+212 6 12 34 56 99'
    print(" -> Modification patient valid\u00e9e !")

    print("[3] Test ajout prothèse...")
    res = client.post('/treatments/add', data={
        'client_id': p_id,
        'title': 'Couronne Zircone Haute Translucidité',
        'teeth_numbers': '21',
        'shade': 'A1',
        'status': 'empreinte',
        'total_cost': '3500.00',
        'delivery_date': '2026-10-05',
        'notes': 'Finitions esthétiques'
    }, follow_redirects=True)
    assert res.status_code == 200
    treatments = db_service.get_treatments_by_client(p_id)
    assert len(treatments) == 1
    t_id = treatments[0]['id']
    print(" -> Proth\u00e8se ajout\u00e9e avec succ\u00e8s (Devis: 3500 DH) !")

    print("[4] Test cycle d'étapes de fabrication prothétique...")
    for stage in ['conception_cfao', 'armature', 'essayage', 'ceramique_finition', 'livre_pose']:
        res = client.post(f'/treatments/{t_id}/status', data={'status': stage, 'client_id': p_id}, follow_redirects=True)
        assert res.status_code == 200
    t_final = next(t for t in db_service.get_treatments_by_client(p_id) if t['id'] == t_id)
    assert t_final['status'] == 'livre_pose'
    print(" -> Toutes les \u00e9tapes de fabrication fonctionnent parfaitement !")

    print("[5] Test planification de rendez-vous...")
    res = client.post('/appointments/add', data={
        'client_id': p_id,
        'appointment_date': '2026-09-28',
        'start_time': '15:30',
        'duration_minutes': '45',
        'act_type': "Pose de prothèse finale & scellement",
        'status': 'confirme',
        'notes': 'Scellement',
        'redirect_to': 'client'
    }, follow_redirects=True)
    assert res.status_code == 200
    appts = db_service.get_appointments_by_client(p_id)
    assert len(appts) == 1
    a_id = appts[0]['id']
    print(" -> Rendez-vous planifi\u00e9 avec succ\u00e8s !")

    print("[6] Test mise à jour statut rendez-vous...")
    res = client.post(f'/appointments/{a_id}/status', data={'status': 'termine', 'client_id': p_id, 'redirect_to': 'client'}, follow_redirects=True)
    assert res.status_code == 200
    appts = db_service.get_appointments_by_client(p_id)
    assert appts[0]['status'] == 'termine'
    print(" -> Statut rendez-vous actualis\u00e9 en 'Termin\u00e9' !")

    print("[7] Test encaissement avance 1 (2000 DH)...")
    res = client.post('/payments/add', data={
        'client_id': p_id,
        'amount': '2000.00',
        'payment_date': '2026-09-20',
        'payment_method': 'carte',
        'next_payment_date': '2026-09-28',
        'notes': 'Acompte',
        'redirect_to': 'client'
    }, follow_redirects=True)
    assert res.status_code == 200
    fin1 = db_service.calculate_financials_for_client(p_id)
    assert fin1['total_paid'] == 2000.0
    assert fin1['remaining_balance'] == 1500.0
    print(f" -> Solde restant calcul\u00e9 : {fin1['remaining_balance']} DH (Attendu: 1500 DH) -> OK !")

    print("[8] Test solde complet (1500 DH)...")
    res = client.post('/payments/add', data={
        'client_id': p_id,
        'amount': '1500.00',
        'payment_date': '2026-09-28',
        'payment_method': 'especes',
        'notes': 'Solde final',
        'redirect_to': 'client'
    }, follow_redirects=True)
    assert res.status_code == 200
    fin2 = db_service.calculate_financials_for_client(p_id)
    assert fin2['total_paid'] == 3500.0
    assert fin2['remaining_balance'] == 0.0
    assert fin2['status_label'] == 'Soldé / Réglé'
    print(" -> Dossier patient int\u00e9gralement sold\u00e9 (Solde: 0.0 DH) -> OK !")

    print("[9] Test module QR Code Google Maps...")
    res = client.get(f'/qrcode?client_id={p_id}')
    assert res.status_code == 200
    assert b"Avis Google" in res.data
    res_img = client.get('/qrcode/generate')
    assert res_img.status_code == 200
    assert res_img.content_type == 'image/png'
    print(" -> Module QR Code Google Maps g\u00e9n\u00e9r\u00e9 avec succ\u00e8s !")

    print("\n TOUS LES BOUTONS ET FLUX FONCTIONNENT \u00c0 100% !")

if __name__ == '__main__':
    test_full_cabinet_flow()
