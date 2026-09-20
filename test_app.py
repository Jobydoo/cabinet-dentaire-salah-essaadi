import unittest
from app import app
import db_service

class DentalLabTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.client.testing = True

    def test_01_dashboard(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Tableau de bord", response.data)
        self.assertIn(b"Pipeline de fabrication", response.data)

    def test_02_clients_list(self):
        response = self.client.get('/clients')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Fichier des Patients", response.data)
        self.assertIn(b"BENNANI", response.data)

    def test_03_client_view_and_financials(self):
        response = self.client.get('/clients/c1001-bennani-uuid')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"BENNANI", response.data)
        self.assertIn(b"Couronne Zircone", response.data)
        self.assertIn(b"Solde Restant", response.data)

    def test_04_appointments(self):
        response = self.client.get('/appointments')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Planning des S", response.data)

    def test_05_payments(self):
        response = self.client.get('/payments')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Journal des R", response.data)

    def test_06_qrcode_module_and_image(self):
        response = self.client.get('/qrcode')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Avis Google", response.data)

        # Tester la génération dynamique de l'image QR Code
        img_response = self.client.get('/qrcode/generate')
        self.assertEqual(img_response.status_code, 200)
        self.assertEqual(img_response.content_type, 'image/png')
        self.assertGreater(len(img_response.data), 100)

    def test_07_search_api(self):
        response = self.client.get('/api/search?q=Bennani')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data[0]['name'], 'Bennani Karim')

    def test_08_crud_flow_and_balance_calculation(self):
        import uuid
        test_lastname = f"Test_{uuid.uuid4().hex[:6]}"
        # 1. Créer un nouveau patient
        create_res = self.client.post('/clients/new', data={
            'first_name': 'Amine',
            'last_name': test_lastname,
            'phone': '+212 6 65 44 33 22',
            'email': 'amine.test@email.com',
            'address': 'Maarif, Casablanca',
            'medical_notes': 'Pose bridge 3 éléments'
        }, follow_redirects=True)
        self.assertEqual(create_res.status_code, 200)

        # Récupérer l'ID du nouveau patient
        clients = db_service.get_clients(test_lastname)
        self.assertTrue(len(clients) > 0)
        client_id = clients[0]['id']

        try:
            # 2. Ajouter une prothèse (Devis: 6000 DH)
            treat_res = self.client.post('/treatments/add', data={
                'client_id': client_id,
                'title': 'Bridge Céramo-Métallique 3 éléments',
                'teeth_numbers': '14, 15, 16',
                'shade': 'A2',
                'status': 'empreinte',
                'total_cost': '6000.00',
                'delivery_date': '2026-10-01',
                'notes': 'Empreinte double mélange'
            }, follow_redirects=True)
            self.assertEqual(treat_res.status_code, 200)

            # Vérifier solde initial: 6000 DH restant dû
            fin_initial = db_service.calculate_financials_for_client(client_id)
            self.assertEqual(fin_initial['total_quote'], 6000.0)
            self.assertEqual(fin_initial['total_paid'], 0.0)
            self.assertEqual(fin_initial['remaining_balance'], 6000.0)

            # 3. Enregistrer un premier acompte de 2500 DH
            pay_res = self.client.post('/payments/add', data={
                'client_id': client_id,
                'amount': '2500.00',
                'payment_date': '2026-09-20',
                'payment_method': 'carte',
                'next_payment_date': '2026-10-01',
                'notes': 'Acompte initial',
                'redirect_to': 'client'
            }, follow_redirects=True)
            self.assertEqual(pay_res.status_code, 200)

            # 4. Vérifier calcul automatique du solde: 6000 - 2500 = 3500 DH restant dû
            fin_after = db_service.calculate_financials_for_client(client_id)
            self.assertEqual(fin_after['total_paid'], 2500.0)
            self.assertEqual(fin_after['remaining_balance'], 3500.0)
            self.assertEqual(fin_after['next_payment_date'], '2026-10-01')

            # 5. Planifier un rendez-vous
            appt_res = self.client.post('/appointments/add', data={
                'client_id': client_id,
                'appointment_date': '2026-09-25',
                'start_time': '11:00',
                'duration_minutes': '45',
                'act_type': 'Essayage armature (métal / zircone)',
                'status': 'confirme',
                'notes': 'Essayage de la chape métallique',
                'redirect_to': 'client'
            }, follow_redirects=True)
            self.assertEqual(appt_res.status_code, 200)

            appts = db_service.get_appointments_by_client(client_id)
            self.assertEqual(len(appts), 1)
            self.assertEqual(appts[0]['act_type'], 'Essayage armature (métal / zircone)')
        finally:
            db_service.delete_client(client_id)

    def test_09_vercel_wsgi_entrypoint(self):
        from api.index import app as vercel_app
        self.assertIsNotNone(vercel_app)

if __name__ == '__main__':
    unittest.main()
