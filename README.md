# Application de Gestion de Cabinet de Prothésiste Dentaire

Solution full-stack conçue pour les cabinets dentaires et laboratoires de prothèses dentaires. Développée avec **Flask (Python)**, **Supabase (PostgreSQL)**, **Tailwind CSS**, et configurée pour un déploiement sans accroc sur **Vercel**.

---

## 🌟 Fonctionnalités Clés

1. **Gestion des Clients / Patients** :
   - Fiches patients 360° avec informations de contact, observations médicales et prothétiques.
   - Moteur de recherche rapide par nom, prénom ou numéro de téléphone.
   - Statut en temps réel du dossier et filtres par solde.

2. **Suivi des Prothèses & Travaux de Laboratoire** :
   - Suivi du pipeline de fabrication : *Empreinte reçue ➔ Modélisation CFAO ➔ Armature / Coulée ➔ Essayage en bouche ➔ Finition Céramique & Glaçage ➔ Livré & Posé*.
   - Spécification des numéros de dents (FDI) et de la teinte dentaire (ex: A2, Bleach).

3. **Planification des Séances & Rendez-vous** :
   - Prise de rendez-vous avec calcul d'horaires et sélection de l'acte dentaire (empreinte, essayage armature, pose, détartrage, extraction, consultation...).
   - Gestion des statuts de séance (planifié, confirmé, terminé, annulé).

4. **Suivi Financier & Facturation Échelonnée** :
   - Montant total du devis / traitement.
   - Enregistrement des tranches et acomptes versés avec mode de règlement (espèces, carte, virement, chèque).
   - **Calcul automatique instantané du solde restant dû** et date prévisionnelle du prochain versement.

5. **Module QR Code Google Maps (Avis 5 Étoiles)** :
   - Génération dynamique de QR Code pointant directement vers la fiche Google Maps du cabinet (`writereview`).
   - Format chevalet de comptoir prêt à être imprimé ou affiché sur tablette à l'accueil pour encourager les patients à déposer leur note 5 étoiles.

---

## 📁 Structure du Projet

```
dental-lab-manager/
├── api/
│   └── index.py            # Point d'entrée WSGI pour Vercel Serverless
├── static/
│   ├── css/custom.css      # Typographie, ombres et règles d'impression
│   └── js/app.js           # Recherche instantanée et modales
├── templates/
│   ├── base.html           # Layout principal responsive avec Tailwind CSS
│   ├── dashboard.html      # Tableau de bord avec KPIs et pipeline prothétique
│   ├── clients/
│   │   ├── list.html       # Liste & recherche des patients
│   │   ├── form.html       # Formulaire ajout/modification patient
│   │   └── view.html       # Fiche patient complète (travaux, séances, solde)
│   ├── appointments/
│   │   └── list.html       # Planning des séances & rendez-vous
│   ├── payments/
│   │   └── list.html       # Journal des encaissements et trésorerie
│   └── qrcode/
│       └── index.html      # Module QR Code Google Maps & Chevalet
├── app.py                  # Application Flask et routes
├── db_service.py           # Service de données (Supabase + fallback local autonome)
├── schema.sql              # Schéma SQL complet pour Supabase PostgreSQL
├── requirements.txt        # Dépendances Python
├── vercel.json             # Fichier de configuration Vercel
└── .env.example            # Variables d'environnement
```

---

## 🚀 Démarrage Rapide en Local

### 1. Cloner ou ouvrir le dossier
```bash
cd dental-lab-manager
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Lancer l'application
```bash
python app.py
```
Accédez à l'application sur : **http://localhost:5000**

> **Note :** L'application dispose d'un **mode autonome de démonstration intégré**. Elle fonctionne immédiatement même sans compte Supabase configuré, avec des données de test réalistes.

---

## 🗄️ Configuration de Supabase (PostgreSQL)

1. Connectez-vous à votre compte [Supabase](https://supabase.com) et créez un nouveau projet.
2. Rendez-vous dans le menu **SQL Editor** de Supabase.
3. Copiez l'intégralité du fichier [`schema.sql`](schema.sql) et cliquez sur **Run**.
   - Cela créera les tables `clients`, `treatments`, `appointments`, `payments`, la vue financière `v_client_financial_summary`, ainsi que les politiques RLS et un jeu de données de test.
4. Dans Supabase, allez dans **Project Settings** > **API** et copiez :
   - Votre **Project URL**
   - Votre **anon public key** (ou **service_role key**)
5. Créez un fichier `.env` à la racine du projet (ou copiez `.env.example`) :
```ini
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre_cle_anon_ou_service_role
GOOGLE_MAPS_REVIEW_URL=https://search.google.com/local/writereview?placeid=VOTRE_PLACE_ID
```

---

## ☁️ Déploiement sur Vercel

Le projet est préconfiguré pour Vercel grâce à [`vercel.json`](vercel.json) et [`api/index.py`](api/index.py).

### Option 1 : Déploiement via Vercel CLI
```bash
npm install -g vercel
vercel
```

### Option 2 : Déploiement via GitHub
1. Poussez votre dépôt sur GitHub.
2. Sur [Vercel](https://vercel.com), cliquez sur **Add New Project** et importez le dépôt.
3. Ajoutez vos variables d'environnement dans les paramètres Vercel (`SUPABASE_URL`, `SUPABASE_KEY`, `GOOGLE_MAPS_REVIEW_URL`).
4. Cliquez sur **Deploy** !
