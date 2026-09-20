-- ==============================================================================
-- SCHEMA SQL POUR SUPABASE (POSTGRESQL)
-- GESTION DE CABINET DE PROTHÉSISTE DENTAIRE & SOINS DENTAIRES
-- ==============================================================================

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================================================================
-- 2. SUPPRESSION PRÉVENTIVE DES TABLES (Optionnel pour réinitialisation propre)
-- ==============================================================================
DROP VIEW IF EXISTS v_client_financial_summary CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS treatments CASCADE;
DROP TABLE IF EXISTS clients CASCADE;

-- ==============================================================================
-- 3. TABLE : CLIENTS / PATIENTS
-- ==============================================================================
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(150),
    address TEXT,
    medical_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour recherche rapide par nom et téléphone
CREATE INDEX idx_clients_name ON clients (last_name, first_name);
CREATE INDEX idx_clients_phone ON clients (phone);

-- ==============================================================================
-- 4. TABLE : TRAITEMENTS / PROTHÈSES & TRAVAUX DE LABORATOIRE
-- ==============================================================================
-- Statuts possibles du flux prothétique :
--   - 'empreinte'           : Prise d'empreinte réalisée / reçue
--   - 'conception_cfao'     : Modélisation 3D / Usinage CFAO
--   - 'armature'            : Coulée ou usinage de l'armature
--   - 'essayage'            : Prêt pour essayage en bouche
--   - 'ceramique_finition'  : Montage céramique, glaçage & finitions
--   - 'livre_pose'          : Prothèse livrée / posée en bouche
CREATE TABLE treatments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,            -- ex: 'Couronne Zircone', 'Bridge 3 éléments', 'Prothèse Squelettique'
    teeth_numbers VARCHAR(100),             -- ex: '16, 17' ou 'Secteur antéro-supérieur'
    shade VARCHAR(50),                      -- Teinte dentaire ex: 'A2', 'A3', 'B1', 'Bleach 3'
    status VARCHAR(50) NOT NULL DEFAULT 'empreinte',
    total_cost NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    delivery_date DATE,                     -- Date d'échéance ou livraison prévue
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_treatments_client_id ON treatments(client_id);
CREATE INDEX idx_treatments_status ON treatments(status);

-- ==============================================================================
-- 5. TABLE : SÉANCES & RENDEZ-VOUS
-- ==============================================================================
-- Types d'actes dentaires / séances :
--   - 'Prise d''empreinte'
--   - 'Essayage armature'
--   - 'Essayage biscuit / cire'
--   - 'Pose de prothèse finale'
--   - 'Ajustement & Retouche'
--   - 'Détartrage & Polissage'
--   - 'Extraction'
--   - 'Consultation & Devis'
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    appointment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    duration_minutes INT NOT NULL DEFAULT 30,
    act_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'planifie', -- 'planifie', 'confirme', 'termine', 'annule'
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_appointments_client_id ON appointments(client_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date, start_time);

-- ==============================================================================
-- 6. TABLE : PAIEMENTS & SUIVI FINANCIER
-- ==============================================================================
-- Enregistrement des avances / tranches versées et calcul du solde
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    treatment_id UUID REFERENCES treatments(id) ON DELETE SET NULL,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_method VARCHAR(50) NOT NULL DEFAULT 'especes', -- 'especes', 'carte', 'virement', 'cheque'
    next_payment_date DATE,                                -- Date prévue pour le prochain versement
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payments_client_id ON payments(client_id);
CREATE INDEX idx_payments_date ON payments(payment_date);

-- ==============================================================================
-- 7. VUE FINANCIÈRE RÉCAPITULATIVE PAR CLIENT
-- ==============================================================================
CREATE OR REPLACE VIEW v_client_financial_summary AS
SELECT 
    c.id AS client_id,
    c.first_name,
    c.last_name,
    c.phone,
    COALESCE(t.total_treatments_cost, 0.00) AS total_quote,
    COALESCE(p.total_paid, 0.00) AS total_paid,
    (COALESCE(t.total_treatments_cost, 0.00) - COALESCE(p.total_paid, 0.00)) AS remaining_balance,
    p.last_payment_date,
    p.next_payment_date,
    COALESCE(t.treatments_count, 0) AS treatments_count,
    COALESCE(t.active_treatments_count, 0) AS active_treatments_count
FROM clients c
LEFT JOIN (
    SELECT 
        client_id,
        SUM(total_cost) AS total_treatments_cost,
        COUNT(id) AS treatments_count,
        COUNT(CASE WHEN status != 'livre_pose' THEN 1 END) AS active_treatments_count
    FROM treatments
    GROUP BY client_id
) t ON c.id = t.client_id
LEFT JOIN (
    SELECT 
        client_id,
        SUM(amount) AS total_paid,
        MAX(payment_date) AS last_payment_date,
        MAX(next_payment_date) AS next_payment_date
    FROM payments
    GROUP BY client_id
) p ON c.id = p.client_id;

-- ==============================================================================
-- 8. POLITIQUES RLS (ROW LEVEL SECURITY)
-- ==============================================================================
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE treatments ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Autorise l'accès pour l'application (utilisateurs anonymes / service role de Supabase)
CREATE POLICY "Allow public read-write for anon" ON clients FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for anon" ON treatments FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for anon" ON appointments FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read-write for anon" ON payments FOR ALL USING (true) WITH CHECK (true);

-- ==============================================================================
-- 9. JEU DE DONNÉES DÉMONSTRATION (SEED DATA)
-- ==============================================================================
DO $$
DECLARE
    client1_id UUID;
    client2_id UUID;
    client3_id UUID;
    treat1_id UUID;
    treat2_id UUID;
    treat3_id UUID;
BEGIN
    -- Client 1
    INSERT INTO clients (first_name, last_name, phone, email, address, medical_notes)
    VALUES ('Karim', 'Bennani', '+212 6 61 23 45 67', 'k.bennani@email.com', '12 Rue Al Massira, Casablanca', 'Sensibilité gingivale légère. Préfère les teintes naturelles.')
    RETURNING id INTO client1_id;

    -- Client 2
    INSERT INTO clients (first_name, last_name, phone, email, address, medical_notes)
    VALUES ('Sofia', 'El Amrani', '+212 6 72 89 12 34', 'sofia.amrani@email.com', '45 Boulevard d''Anfa, Casablanca', 'Demande esthétique élevée. Blanchiment préalable réalisé.')
    RETURNING id INTO client2_id;

    -- Client 3
    INSERT INTO clients (first_name, last_name, phone, email, address, medical_notes)
    VALUES ('Driss', 'Mansouri', '+212 6 50 11 22 33', 'driss.m@email.com', '8 Avenue Hassan II, Rabat', 'Bruxisme nocturne. Prévoir gouttière de protection après pose.')
    RETURNING id INTO client3_id;

    -- Prothèses / Traitements
    INSERT INTO treatments (client_id, title, teeth_numbers, shade, status, total_cost, delivery_date, notes)
    VALUES (client1_id, 'Couronne Zircone Multicouche', '16', 'A2', 'ceramique_finition', 2800.00, CURRENT_DATE + INTERVAL '3 days', 'Finition glaçage haute brillance')
    RETURNING id INTO treat1_id;

    INSERT INTO treatments (client_id, title, teeth_numbers, shade, status, total_cost, delivery_date, notes)
    VALUES (client2_id, 'Facettes E-Max Céramique (x4)', '12, 11, 21, 22', 'Bleach 2', 'essayage', 7200.00, CURRENT_DATE + INTERVAL '5 days', 'Translucidité incisale prononcée demandée')
    RETURNING id INTO treat2_id;

    INSERT INTO treatments (client_id, title, teeth_numbers, shade, status, total_cost, delivery_date, notes)
    VALUES (client3_id, 'Prothèse Adjointe Squelettique Stellite', 'Maxillaire Supérieur', 'A3', 'armature', 4500.00, CURRENT_DATE + INTERVAL '7 days', 'Crochets esthétiques acétal')
    RETURNING id INTO treat3_id;

    -- Rendez-vous
    INSERT INTO appointments (client_id, appointment_date, start_time, duration_minutes, act_type, status, notes)
    VALUES (client1_id, CURRENT_DATE + INTERVAL '3 days', '10:30', 45, 'Pose de prothèse finale', 'confirme', 'Scellement définitif et contrôle de l''occlusion');

    INSERT INTO appointments (client_id, appointment_date, start_time, duration_minutes, act_type, status, notes)
    VALUES (client2_id, CURRENT_DATE + INTERVAL '1 day', '14:00', 60, 'Essayage biscuit / cire', 'confirme', 'Validation esthétique et ligne du sourire avec la patiente');

    INSERT INTO appointments (client_id, appointment_date, start_time, duration_minutes, act_type, status, notes)
    VALUES (client3_id, CURRENT_DATE + INTERVAL '2 days', '11:15', 30, 'Essayage armature', 'planifie', 'Essayage du châssis métallique stellite');

    -- Paiements / Acomptes
    INSERT INTO payments (client_id, treatment_id, amount, payment_date, payment_method, next_payment_date, notes)
    VALUES (client1_id, treat1_id, 1500.00, CURRENT_DATE - INTERVAL '10 days', 'carte', CURRENT_DATE + INTERVAL '3 days', 'Acompte initial à la prise d''empreinte');

    INSERT INTO payments (client_id, treatment_id, amount, payment_date, payment_method, next_payment_date, notes)
    VALUES (client2_id, treat2_id, 3000.00, CURRENT_DATE - INTERVAL '7 days', 'virement', CURRENT_DATE + INTERVAL '5 days', '1ère tranche versée');

    INSERT INTO payments (client_id, treatment_id, amount, payment_date, payment_method, next_payment_date, notes)
    VALUES (client3_id, treat3_id, 2000.00, CURRENT_DATE - INTERVAL '5 days', 'especes', CURRENT_DATE + INTERVAL '7 days', 'Avance sur châssis');
END $$;
