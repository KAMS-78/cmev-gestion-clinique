"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CMEV - VERSION COMPLÈTE ASSEMBLÉE                         ║
║                  Centre Médical Espoir de Vie                                ║
║                                                                              ║
║  ✅ 10 Modules complets intégrés                                             ║
║  ✅ Gestion permissions par rôle                                             ║
║  ✅ Réorganisation auto ID partout                                           ║
║  ✅ Navigation Entrée/Tab partout                                            ║
║  ✅ Boutons retour menu dans chaque module                                   ║
║  ✅ Thèmes Dark/Light + Zoom                                                 ║
║                                                                              ║
║  Modules :                                                                   ║
║  1. Patients          6. Pharmacie                                           ║
║  2. Médecins          7. Facturation                                         ║
║  3. Employés          8. Statistiques                                        ║
║  4. Consultations     9. Administration                                      ║
║  5. Examens                                                                  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import sqlite3
import os
import json
from datetime import datetime, timedelta
import random
import shutil

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION GLOBALE
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG_FILE = 'cmev_config.json'

def load_config():
    """Charger configuration"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'theme': 'dark', 'font_size': 11}

def save_config():
    """Sauvegarder configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(CONFIG, f)

CONFIG = load_config()

# Thèmes complets
THEMES = {
    'dark': {
        'bg_dark': '#1e1e1e',
        'bg_medium': '#2d2d30',
        'bg_light': '#3e3e42',
        'text_white': '#ffffff',
        'text_yellow': '#ffd700',
        'success': '#27ae60',
        'danger': '#e74c3c',
        'warning': '#f39c12',
        'info': '#3498db',
        'tree_bg': '#252526',
        'tree_fg': '#cccccc',
        'primary': '#4a9eff',
        'purple': '#9b59b6',
        'teal': '#1abc9c',
        'orange': '#e67e22'
    },
    'light': {
        'bg_dark': '#f8f9fa',
        'bg_medium': '#e9ecef',
        'bg_light': '#ffffff',
        'text_white': '#212529',
        'text_yellow': '#856404',
        'success': '#28a745',
        'danger': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8',
        'tree_bg': '#ffffff',
        'tree_fg': '#212529',
        'primary': '#007bff',
        'purple': '#6f42c1',
        'teal': '#20c997',
        'orange': '#fd7e14'
    }
}

THEME = THEMES[CONFIG['theme']]

# Session utilisateur
class Session:
    utilisateur_id = None
    nom_utilisateur = None
    role = None
    nom_complet = None

# Permissions par rôle
PERMISSIONS = {
    'super_admin': ['patients', 'medecins', 'employes', 'consultations', 'examens', 
                    'pharmacie', 'facturation', 'statistiques', 'administration'],
    'admin': ['patients', 'medecins', 'employes', 'consultations', 'examens', 
              'pharmacie', 'facturation', 'statistiques', 'administration'],
    'medecin': ['patients', 'consultations', 'examens', 'facturation'],
    'receptionniste': ['patients', 'consultations', 'facturation'],
    'pharmacien': ['pharmacie']
}

def has_permission(module):
    """Vérifier si l'utilisateur a accès au module"""
    if not Session.role:
        return False
    return module in PERMISSIONS.get(Session.role, [])

# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

def log_activity(action, module, details=""):
    """Enregistrer une activité"""
    try:
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute('''INSERT INTO Journal_Activite 
                    (ID_Utilisateur, Action, Module, Details, Date_heure)
                    VALUES (?, ?, ?, ?, ?)''',
                 (Session.utilisateur_id, action, module, details,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except:
        pass

def update_theme():
    """Mettre à jour le thème global"""
    global THEME
    THEME = THEMES[CONFIG['theme']]
    save_config()

def calculate_age(date_naissance):
    """Calculer l'âge"""
    if not date_naissance:
        return ""
    try:
        date_naiss = datetime.strptime(date_naissance, "%Y-%m-%d")
        return str((datetime.now() - date_naiss).days // 365)
    except:
        return ""

def generer_numero_consultation():
    """Générer un numéro unique de consultation"""
    date_str = datetime.now().strftime("%Y%m%d")
    random_part = random.randint(1000, 9999)
    return f"CONS-{date_str}-{random_part}"

def generer_numero_facture():
    """Générer un numéro unique de facture"""
    date_str = datetime.now().strftime("%Y%m%d")
    random_part = random.randint(1000, 9999)
    return f"FACT-{date_str}-{random_part}"

# ═══════════════════════════════════════════════════════════════════════════════
# GESTION CODE DE VALIDATION QUOTIDIEN
# ═══════════════════════════════════════════════════════════════════════════════

def generer_code_jour():
    """Génère un nouveau code à 4 chiffres"""
    return str(random.randint(1000, 9999))

def get_code_actuel():
    """Récupère le code valide du jour"""
    try:
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT Code, Date_creation FROM Code_Validation ORDER BY ID_Code DESC LIMIT 1")
        result = c.fetchone()
        conn.close()
        
        if result:
            code, date_creation = result
            # Vérifier si le code est du jour
            if date_creation == datetime.now().strftime("%Y-%m-%d"):
                return code
        
        # Si pas de code ou code périmé, en générer un nouveau
        return actualiser_code_auto()
        
    except Exception as e:
        print(f"Erreur get_code_actuel: {e}")
        return None

def actualiser_code_auto():
    """Actualise automatiquement le code (minuit ou demande admin)"""
    try:
        nouveau_code = generer_code_jour()
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        
        # Insérer le nouveau code
        user_id = Session.utilisateur_id if Session.utilisateur_id else 1
        c.execute("INSERT INTO Code_Validation VALUES (NULL, ?, date('now'), ?)",
                 (nouveau_code, user_id))
        
        conn.commit()
        conn.close()
        
        log_activity("Actualisation", "Sécurité", f"Nouveau code de validation généré")
        return nouveau_code
        
    except Exception as e:
        print(f"Erreur actualiser_code_auto: {e}")
        return None

def verifier_code_valide(code_saisi):
    """Vérifie si le code saisi correspond au code du jour"""
    code_actuel = get_code_actuel()
    return code_saisi == code_actuel

def verifier_actualisation_minuit():
    """Vérifie si on a changé de jour et actualise le code si nécessaire"""
    try:
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT Date_creation FROM Code_Validation ORDER BY ID_Code DESC LIMIT 1")
        result = c.fetchone()
        conn.close()
        
        if result:
            derniere_date = result[0]
            date_aujourdhui = datetime.now().strftime("%Y-%m-%d")
            
            # Si on a changé de jour, générer nouveau code
            if derniere_date != date_aujourdhui:
                actualiser_code_auto()
                return True
        
        return False
        
    except Exception as e:
        print(f"Erreur verifier_actualisation_minuit: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALISATION BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

def init_database():
    """Créer toutes les tables si elles n'existent pas"""
    conn = sqlite3.connect('cmev.db')
    c = conn.cursor()
    
    # Utilisateur
    c.execute('''CREATE TABLE IF NOT EXISTS Utilisateur (
        ID_Utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom_utilisateur TEXT UNIQUE NOT NULL,
        Mot_de_passe TEXT NOT NULL,
        Role TEXT NOT NULL,
        Nom_complet TEXT,
        Actif INTEGER DEFAULT 1
    )''')
    
    c.execute("SELECT COUNT(*) FROM Utilisateur WHERE Nom_utilisateur='TEST'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO Utilisateur VALUES (NULL, 'TEST', '1234', 'super_admin', 'Test Admin', 1)")
    
    # Patient
    c.execute('''CREATE TABLE IF NOT EXISTS Patient (
        ID_Patient INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom TEXT NOT NULL,
        Prenom TEXT NOT NULL,
        Date_naissance TEXT,
        Sexe TEXT,
        Contact TEXT,
        Adresse TEXT,
        Contact_urgence TEXT,
        Actif INTEGER DEFAULT 1
    )''')
    
    # Medecin
    c.execute('''CREATE TABLE IF NOT EXISTS Medecin (
        ID_Medecin INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom TEXT NOT NULL,
        Prenom TEXT NOT NULL,
        Specialite TEXT,
        Contact TEXT,
        Adresse TEXT,
        Date_embauche TEXT,
        Actif INTEGER DEFAULT 1
    )''')
    
    # Employe
    c.execute('''CREATE TABLE IF NOT EXISTS Employe (
        ID_Employe INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom TEXT NOT NULL,
        Prenom TEXT NOT NULL,
        Fonction TEXT,
        Contact TEXT,
        Adresse TEXT,
        Date_embauche TEXT,
        Salaire REAL,
        Actif INTEGER DEFAULT 1
    )''')
    
    # Consultation
    c.execute('''CREATE TABLE IF NOT EXISTS Consultation (
        ID_Consultation INTEGER PRIMARY KEY AUTOINCREMENT,
        Numero_Consultation TEXT UNIQUE,
        Date_Consultation TEXT,
        Heure_Consultation TEXT,
        ID_Patient INTEGER,
        ID_Medecin INTEGER,
        Motif TEXT,
        Diagnostic TEXT,
        Observations TEXT
    )''')
    
    # Type_Examen
    c.execute('''CREATE TABLE IF NOT EXISTS Type_Examen (
        ID_Type_examen INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom_examen TEXT UNIQUE NOT NULL,
        Prix REAL,
        Description TEXT
    )''')
    
    # Examen
    c.execute('''CREATE TABLE IF NOT EXISTS Examen (
        ID_Examen INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Patient INTEGER,
        ID_Type_examen INTEGER,
        Medecin_prescripteur INTEGER,
        Date_prescription TEXT,
        Date_examen TEXT,
        Statut TEXT,
        Resultats TEXT
    )''')
    
    # Categorie_Medicament
    c.execute('''CREATE TABLE IF NOT EXISTS Categorie_Medicament (
        ID_Categorie INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom_categorie TEXT UNIQUE NOT NULL
    )''')
    
    # Medicament
    c.execute('''CREATE TABLE IF NOT EXISTS Medicament (
        ID_Medicament INTEGER PRIMARY KEY AUTOINCREMENT,
        Nom_medicament TEXT NOT NULL,
        ID_Categorie INTEGER,
        Quantite_stock INTEGER DEFAULT 0,
        Seuil_alerte INTEGER DEFAULT 10,
        Prix_unitaire REAL DEFAULT 0
    )''')
    
    # Facture
    c.execute('''CREATE TABLE IF NOT EXISTS Facture (
        ID_Facture INTEGER PRIMARY KEY AUTOINCREMENT,
        Numero_facture TEXT UNIQUE,
        Date_facture TEXT,
        Montant_total REAL DEFAULT 0,
        Montant_paye REAL DEFAULT 0,
        ID_Patient INTEGER,
        ID_Consultation INTEGER
    )''')
    
    # Paiement
    c.execute('''CREATE TABLE IF NOT EXISTS Paiement (
        ID_Paiement INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Facture INTEGER,
        Montant_paye REAL,
        Mode_paiement TEXT,
        Date_paiement TEXT
    )''')
    
    # Journal_Activite
    c.execute('''CREATE TABLE IF NOT EXISTS Journal_Activite (
        ID_Log INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Utilisateur INTEGER,
        Action TEXT,
        Module TEXT,
        Details TEXT,
        Date_heure TEXT
    )''')

    # Code_Validation (pour sécurité quotidienne)
    c.execute('''CREATE TABLE IF NOT EXISTS Code_Validation (
        ID_Code INTEGER PRIMARY KEY AUTOINCREMENT,
        Code TEXT NOT NULL,
        Date_creation DATE NOT NULL,
        Cree_par INTEGER,
        FOREIGN KEY (Cree_par) REFERENCES Utilisateur(ID_Utilisateur)
    )''')
    
    # Créer le code initial si la table est vide
    c.execute("SELECT COUNT(*) FROM Code_Validation")
    if c.fetchone()[0] == 0:
        code_initial = str(random.randint(1000, 9999))
        c.execute("INSERT INTO Code_Validation VALUES (NULL, ?, date('now'), 1)", (code_initial,))
    
    conn.commit()
    conn.close()

def init_types_examens():
    """Initialiser les types d'examens"""
    conn = sqlite3.connect('cmev.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM Type_Examen")
    if c.fetchone()[0] > 0:
        conn.close()
        return
    
    types_examens = [
        ("Radiographie", 15000, "Radiographie standard"),
        ("Échographie", 20000, "Échographie abdominale, pelvienne, obstétricale"),
        ("Scanner CT-Scan", 50000, "Tomodensitométrie"),
        ("IRM", 75000, "Imagerie par résonance magnétique"),
        ("ECG", 5000, "Électrocardiogramme"),
        ("Échographie Doppler", 25000, "Analyse flux sanguin"),
        ("Mammographie", 18000, "Dépistage cancer du sein"),
        ("Test sanguin complet", 8000, "NFS + formule"),
        ("Glycémie", 2000, "Taux de sucre"),
        ("Cholestérol", 3000, "Bilan lipidique"),
        ("Test hépatique", 7000, "Fonction hépatique"),
        ("Test rénal", 6000, "Fonction rénale"),
        ("Test thyroïdien", 8000, "TSH, T3, T4"),
        ("Dépistage VIH", 5000, "Dépistage VIH"),
        ("Test grossesse", 2500, "HCG"),
        ("Analyse urine complète", 3000, "Analyse urine"),
        ("Culture urine", 5000, "Recherche infection"),
        ("Hémoculture", 8000, "Culture sanguine"),
        ("Spirométrie", 6000, "Fonction respiratoire"),
        ("Endoscopie", 35000, "Examen endoscopique")
    ]
    
    for nom, prix, desc in types_examens:
        c.execute("INSERT INTO Type_Examen (Nom_examen, Prix, Description) VALUES (?, ?, ?)",
                 (nom, prix, desc))
    
    conn.commit()
    conn.close()

def init_categories_medicaments():
    """Initialiser les catégories de médicaments"""
    conn = sqlite3.connect('cmev.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM Categorie_Medicament")
    if c.fetchone()[0] > 0:
        conn.close()
        return
    
    categories = [
        "Analgésiques", "Antibiotiques", "Anti-inflammatoires", "Antipaludéens",
        "Antihypertenseurs", "Antidiabétiques", "Antihistaminiques", "Antiviraux",
        "Vitamines et suppléments", "Antiseptiques", "Antipyrétiques", "Antispasmodiques",
        "Cardiotoniques", "Diurétiques", "Solutés et perfusions", "Vaccins",
        "Contraceptifs", "Anticoagulants", "Corticoïdes", "Autre"
    ]
    
    for cat in categories:
        c.execute("INSERT INTO Categorie_Medicament (Nom_categorie) VALUES (?)", (cat,))
    
    conn.commit()
    conn.close()

# ═══════════════════════════════════════════════════════════════════════════════
# FENÊTRE DE CONNEXION
# ═══════════════════════════════════════════════════════════════════════════════

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CMEV - Connexion")
        self.root.geometry("450x400")
        self.root.configure(bg=THEME['bg_dark'])
        
        # Centrer
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        tk.Label(self.root, text="🏥 CMEV", font=("Arial", 28, "bold"),
                bg=THEME['bg_dark'], fg=THEME['text_white']).pack(pady=30)
        
        tk.Label(self.root, text="Centre Médical Espoir de Vie",
                font=("Arial", 11), bg=THEME['bg_dark'],
                fg=THEME['text_yellow']).pack()
        
        form = tk.Frame(self.root, bg=THEME['bg_dark'])
        form.pack(pady=40)
        
        tk.Label(form, text="Utilisateur :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", 12)).grid(
                    row=0, column=0, sticky=tk.W, padx=10, pady=15)
        self.user_entry = tk.Entry(form, font=("Arial", 14), width=22,
                                   bg=THEME['bg_light'], fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'])
        self.user_entry.grid(row=0, column=1, padx=10, pady=15)
        self.user_entry.focus()
        self.user_entry.bind('<Return>', lambda e: self.pass_entry.focus())
        
        tk.Label(form, text="Mot de passe :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", 12)).grid(
                    row=1, column=0, sticky=tk.W, padx=10, pady=15)
        self.pass_entry = tk.Entry(form, font=("Arial", 14), width=22,
                                   bg=THEME['bg_light'], fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'], show='•')
        self.pass_entry.grid(row=1, column=1, padx=10, pady=15)
        self.pass_entry.bind('<Return>', lambda e: self.login())
        
        tk.Button(self.root, text="🔐 Se connecter", font=("Arial", 14, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], width=20, height=2,
                 command=self.login, cursor="hand2", relief=tk.RAISED, bd=3).pack(pady=25)
        
    def login(self):
        user = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        
        if not user or not pwd:
            messagebox.showerror("Erreur", "Remplissez tous les champs !")
            return
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Utilisateur WHERE Nom_utilisateur=? AND Mot_de_passe=? AND Actif=1", 
                 (user, pwd))
        result = c.fetchone()
        conn.close()
        
        if result:
            Session.utilisateur_id = result[0]
            Session.nom_utilisateur = result[1]
            Session.role = result[3]
            Session.nom_complet = result[4]
            
            log_activity("Connexion", "Système", f"Utilisateur {user} connecté")
            
            nom_complet = result[4] or user
            role = result[3]
            
            # Message de bienvenue
            messagebox.showinfo("Connexion réussie", f"Bienvenue {nom_complet} !")
            
            # Afficher le code du jour pour admin/super_admin
            if role in ["admin", "super_admin"]:
                # Vérifier actualisation minuit
                verifier_actualisation_minuit()
                
                code_jour = get_code_actuel()
                messagebox.showinfo("🔐 Code du jour", 
                                  f"Votre code de validation pour aujourd'hui :\n\n"
                                  f"╔═════════╗\n"
                                  f"║  {code_jour}  ║\n"
                                  f"╚═════════╝\n\n"
                                  f"Ce code sera demandé aux utilisateurs pour\n"
                                  f"modifier ou supprimer des données.\n\n"
                                  f"Le code change automatiquement chaque jour à minuit.")
            
            self.root.destroy()
            MainWindow()
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects !")
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.focus()
    
    def run(self):
        self.root.mainloop()

# ═══════════════════════════════════════════════════════════════════════════════
# FENÊTRE DE DEMANDE DE CODE DE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

class DemandeCodeWindow:
    def __init__(self, parent, action_callback):
        """
        Fenêtre pour demander le code de validation
        action_callback: fonction à exécuter si le code est correct
        """
        self.action_callback = action_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Code de validation requis")
        self.window.geometry("500x350")
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        # Centrer la fenêtre
        self.window.transient(parent)
        
        tk.Label(self.window, text="🔐 CODE DE VALIDATION REQUIS", 
                font=("Arial", 18, "bold"),
                bg=THEME['warning'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        tk.Label(form, text="Cette action nécessite un code de validation.\n\n"
                           "Veuillez contacter un administrateur pour obtenir\n"
                           "le code du jour.",
                bg=THEME['bg_dark'], fg=THEME['text_white'],
                font=("Arial", 11), justify=tk.CENTER).pack(pady=20)
        
        tk.Label(form, text="Entrez le code à 4 chiffres :",
                bg=THEME['bg_dark'], fg=THEME['text_white'],
                font=("Arial", 12, "bold")).pack(pady=10)
        
        self.code_entry = tk.Entry(form, font=("Arial", 20, "bold"),
                                   width=10, justify=tk.CENTER,
                                   bg=THEME['bg_light'], fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'],
                                   show='●')
        self.code_entry.pack(pady=15)
        self.code_entry.focus()
        self.code_entry.bind('<Return>', lambda e: self.valider_code())
        
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="✓ Valider", 
                 font=("Arial", 12, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=12, height=2, command=self.valider_code,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="✗ Annuler", 
                 font=("Arial", 12, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=12, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def valider_code(self):
        code_saisi = self.code_entry.get().strip()
        
        if len(code_saisi) != 4 or not code_saisi.isdigit():
            messagebox.showerror("Erreur", "Le code doit contenir exactement 4 chiffres !")
            self.code_entry.delete(0, tk.END)
            self.code_entry.focus()
            return
        
        if verifier_code_valide(code_saisi):
            self.window.destroy()
            # Exécuter l'action autorisée
            self.action_callback()
        else:
            messagebox.showerror("Code incorrect", 
                               "Le code saisi n'est pas valide !\n\n"
                               "Contactez un administrateur pour obtenir\n"
                               "le code du jour.")
            self.code_entry.delete(0, tk.END)
            self.code_entry.focus()

# ═══════════════════════════════════════════════════════════════════════════════
# MENU PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CMEV - Application Complète")
        self.root.state('zoomed')
        self.root.configure(bg=THEME['bg_dark'])
        
        # Fermeture propre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Header
        header = tk.Frame(self.root, bg=THEME['info'], height=90)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🏥 CMEV - Centre Médical Espoir de Vie",
                font=("Arial", 22, "bold"), bg=THEME['info'],
                fg=THEME['text_white']).pack(side=tk.LEFT, padx=25, pady=10)
        
        controls = tk.Frame(header, bg=THEME['info'])
        controls.pack(side=tk.RIGHT, padx=25)
        
        tk.Label(controls, text=f"👤 {Session.nom_complet or Session.nom_utilisateur}",
                font=("Arial", 11, "bold"), bg=THEME['info'],
                fg=THEME['text_white']).pack(anchor=tk.E)
        tk.Label(controls, text=f"🔑 {Session.role}",
                font=("Arial", 10), bg=THEME['info'],
                fg=THEME['text_white']).pack(anchor=tk.E)
        
        # Toolbar
        toolbar = tk.Frame(self.root, bg=THEME['bg_medium'], height=60)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        left_buttons = tk.Frame(toolbar, bg=THEME['bg_medium'])
        left_buttons.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Button(left_buttons, text="🔍- Zoom -", font=("Arial", 10, "bold"),
                 bg=THEME['bg_light'], fg=THEME['text_white'], width=12,
                 command=self.zoom_out, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(left_buttons, text="🔍+ Zoom +", font=("Arial", 10, "bold"),
                 bg=THEME['bg_light'], fg=THEME['text_white'], width=12,
                 command=self.zoom_in, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        theme_icon = "🌙" if CONFIG['theme'] == 'dark' else "☀️"
        tk.Button(left_buttons, text=f"{theme_icon} Thème", font=("Arial", 10, "bold"),
                 bg=THEME['bg_light'], fg=THEME['text_white'], width=12,
                 command=self.toggle_theme, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Label(left_buttons, text=f"Police : {CONFIG['font_size']}pt",
                font=("Arial", 10), bg=THEME['bg_medium'],
                fg=THEME['text_white']).pack(side=tk.LEFT, padx=15)
        
        # Boutons droite
        right_buttons = tk.Frame(toolbar, bg=THEME['bg_medium'])
        right_buttons.pack(side=tk.RIGHT, padx=20, pady=10)
        
        tk.Button(right_buttons, text="🚪 Déconnexion", font=("Arial", 11, "bold"),
                 bg=THEME['warning'], fg=THEME['text_white'], width=15,
                 command=self.logout, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(right_buttons, text="❌ Quitter", font=("Arial", 11, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], width=15,
                 command=self.on_closing, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Zone scrollable
        canvas_frame = tk.Frame(self.root, bg=THEME['bg_dark'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg=THEME['bg_dark'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=THEME['bg_dark'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Activer scroll seulement quand souris dans canvas
        def _on_enter(event):
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        def _on_leave(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind("<Enter>", _on_enter)
        self.canvas.bind("<Leave>", _on_leave)
        
        # Grille de boutons avec permissions
        btn_container = tk.Frame(self.scrollable_frame, bg=THEME['bg_dark'])
        btn_container.pack(fill=tk.BOTH, expand=True, padx=60, pady=60)
        
        # Liste des modules avec permissions
        all_modules = [
            ("👥 Patients", THEME['info'], self.open_patients, "Gestion patients", "patients"),
            ("👨‍⚕️ Médecins", THEME['purple'], self.open_medecins, "Gestion médecins", "medecins"),
            ("👷 Employés", THEME['orange'], self.open_employes, "Gestion employés", "employes"),
            ("📋 Consultations", THEME['teal'], self.open_consultations, "Gestion consultations", "consultations"),
            ("🔬 Examens", THEME['warning'], self.open_examens, "Gestion examens", "examens"),
            ("💊 Pharmacie", THEME['success'], self.open_pharmacie, "Gestion pharmacie", "pharmacie"),
            ("💰 Facturation", THEME['danger'], self.open_facturation, "Gestion facturation", "facturation"),
            ("📊 Statistiques", THEME['purple'], self.open_statistiques, "Statistiques", "statistiques"),
            ("⚙️ Administration", THEME['bg_light'], self.open_administration, "Administration", "administration")
        ]
        
        # Afficher uniquement les modules autorisés
        row = 0
        col = 0
        
        for text, color, cmd, desc, permission in all_modules:
            if has_permission(permission):
                module_frame = tk.Frame(btn_container, bg=THEME['bg_dark'])
                module_frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
                
                btn = tk.Button(module_frame, text=text, 
                               font=("Arial", int(CONFIG['font_size']*1.4), "bold"),
                               bg=color, fg=THEME['text_white'], 
                               width=20, height=5,
                               command=cmd, cursor="hand2", relief=tk.RAISED, bd=4)
                btn.pack()
                
                tk.Label(module_frame, text=desc, 
                        font=("Arial", int(CONFIG['font_size']*0.9)),
                        bg=THEME['bg_dark'], fg=THEME['text_white']).pack(pady=(5,0))
                
                col += 1
                if col > 2:
                    col = 0
                    row += 1
        
        for i in range(3):
            btn_container.grid_columnconfigure(i, weight=1)
        
        # Footer
        footer = tk.Frame(self.root, bg=THEME['bg_medium'], height=40)
        footer.pack(fill=tk.X)
        footer.pack_propagate(False)
        
        tk.Label(footer, text=f"© 2026 CMEV - Version COMPLÈTE | {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                font=("Arial", 9), bg=THEME['bg_medium'],
                fg=THEME['text_white']).pack(pady=10)
        
        self.root.mainloop()
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def zoom_in(self):
        if CONFIG['font_size'] < 20:
            CONFIG['font_size'] += 1
            save_config()
            messagebox.showinfo("Zoom", f"Taille : {CONFIG['font_size']}pt\n\nRedémarre l'app.")
    
    def zoom_out(self):
        if CONFIG['font_size'] > 8:
            CONFIG['font_size'] -= 1
            save_config()
            messagebox.showinfo("Zoom", f"Taille : {CONFIG['font_size']}pt\n\nRedémarre l'app.")
    
    def toggle_theme(self):
        CONFIG['theme'] = 'light' if CONFIG['theme'] == 'dark' else 'dark'
        update_theme()
        messagebox.showinfo("Thème", f"Thème : {CONFIG['theme']}\n\nRedémarre l'app.")
    
    def open_patients(self):
        PatientsModule(self.root)
        self.root.deiconify()
    
    def open_medecins(self):
        MedecinsModule(self.root)
        self.root.deiconify()
    
    def open_employes(self):
        EmployesModule(self.root)
        self.root.deiconify()
    
    def open_consultations(self):
        ConsultationsModule(self.root)
        self.root.deiconify()
    
    def open_examens(self):
        ExamensModule(self.root)
        self.root.deiconify()
    
    def open_pharmacie(self):
        PharmacieModule(self.root)
        self.root.deiconify()
    
    def open_facturation(self):
        FacturationModule(self.root)
        self.root.deiconify()
    
    def open_statistiques(self):
        StatistiquesModule(self.root)
        self.root.deiconify()
    
    def open_administration(self):
        AdministrationModule(self.root)
        self.root.deiconify()
    
    def logout(self):
        if messagebox.askyesno("Déconnexion", "Voulez-vous vous déconnecter ?"):
            log_activity("Déconnexion", "Système")
            self.root.destroy()
            LoginWindow().run()
    
    def on_closing(self):
        if messagebox.askyesno("Quitter", "Voulez-vous quitter l'application ?"):
            log_activity("Fermeture", "Système")
            self.root.destroy()

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE PATIENTS
# ═══════════════════════════════════════════════════════════════════════════════

class PatientsModule:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        self.root = tk.Toplevel()
        self.root.title("CMEV - Gestion des Patients")
        self.root.state('zoomed')
        self.root.configure(bg=THEME['bg_dark'])
        
        # Fermeture retourne au menu
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_menu)
        
        # Header
        header = tk.Frame(self.root, bg=THEME['info'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="👥 GESTION DES PATIENTS", 
                font=("Arial", 22, "bold"),
                bg=THEME['info'], fg=THEME['text_white'], 
                pady=20).pack()
        
        # Toolbar
        toolbar = tk.Frame(self.root, bg=THEME['bg_dark'])
        toolbar.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Button(toolbar, text="➕ Nouveau Patient", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=20, height=2, command=self.add_patient,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="✏️ Modifier", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['warning'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.edit_patient,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🗑️ Supprimer", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.delete_patient,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔄 Actualiser", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.load_patients,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔢 Réorganiser ID", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['purple'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.reorganize_and_reload,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🏠 Retour Menu", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['bg_medium'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.back_to_menu,
                 cursor="hand2").pack(side=tk.RIGHT, padx=5)
        
        # Tableau
        tree_frame = tk.Frame(self.root, bg=THEME['bg_dark'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Pat.Treeview",
                       background=THEME['tree_bg'],
                       foreground=THEME['tree_fg'],
                       fieldbackground=THEME['tree_bg'],
                       font=('Arial', CONFIG['font_size']))
        style.configure("Pat.Treeview.Heading",
                       background='#2c3e50',
                       foreground='white',
                       font=('Arial', CONFIG['font_size'], 'bold'))
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Nom", "Prenom", "Sexe", "Age", "Contact", "Adresse", "Urgence"),
            show="headings",
            yscrollcommand=vsb.set,
            style="Pat.Treeview",
            height=30
        )
        
        vsb.config(command=self.tree.yview)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Prenom", text="Prénom")
        self.tree.heading("Sexe", text="Sexe")
        self.tree.heading("Age", text="Âge")
        self.tree.heading("Contact", text="Contact")
        self.tree.heading("Adresse", text="Adresse")
        self.tree.heading("Urgence", text="Contact urgence")
        
        self.tree.column("ID", width=60, anchor=tk.CENTER)
        self.tree.column("Nom", width=150)
        self.tree.column("Prenom", width=150)
        self.tree.column("Sexe", width=80, anchor=tk.CENTER)
        self.tree.column("Age", width=80, anchor=tk.CENTER)
        self.tree.column("Contact", width=130)
        self.tree.column("Adresse", width=220)
        self.tree.column("Urgence", width=130)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_patients()
    
    def reorganize_and_reload(self):
        self.reorganize_ids()
        self.load_patients()
        messagebox.showinfo("Succès", "ID réorganisés !")
    
    def reorganize_ids(self):
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            
            c.execute("SELECT * FROM Patient WHERE Actif=1 ORDER BY ID_Patient")
            patients = c.fetchall()
            
            if not patients:
                return
            
            c.execute("DELETE FROM Patient")
            c.execute("DELETE FROM sqlite_sequence WHERE name='Patient'")
            
            for p in patients:
                c.execute('''INSERT INTO Patient 
                            (Nom, Prenom, Date_naissance, Sexe, Contact, Adresse, Contact_urgence, Actif)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]))
            
            conn.commit()
            conn.close()
            
            log_activity("Réorganisation", "Patients", "ID réorganisés")
            
        except Exception as e:
            print(f"Erreur réorganisation ID: {e}")
    
    def load_patients(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Patient WHERE Actif=1 ORDER BY Nom")
        patients = c.fetchall()
        conn.close()
        
        for p in patients:
            age = calculate_age(p[3])
            
            self.tree.insert("", tk.END, values=(
                p[0], p[1], p[2], p[4] or "", age, 
                p[5] or "", p[6] or "", p[7] or ""
            ))
    
    def add_patient(self):
        AddPatientWindow(self.root, self)
    
    def edit_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un patient !")
            return
        
        item = self.tree.item(selected[0])
        patient_id = item['values'][0]
        
        # Vérifier si code requis (tous sauf admin/super_admin)
        if Session.role not in ["admin", "super_admin"]:
            DemandeCodeWindow(self.root, lambda: EditPatientWindow(self.root, self, patient_id))
        else:
            EditPatientWindow(self.root, self, patient_id)
    
    def delete_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un patient !")
            return
        
        item = self.tree.item(selected[0])
        nom = item['values'][1]
        prenom = item['values'][2]
        patient_id = item['values'][0]
        
        # Fonction de suppression réelle
        def executer_suppression():
            if messagebox.askyesno("Confirmation", f"Supprimer {nom} {prenom} ?"):
                conn = sqlite3.connect('cmev.db')
                c = conn.cursor()
                c.execute("DELETE FROM Patient WHERE ID_Patient=?", (patient_id,))
                conn.commit()
                conn.close()
                
                log_activity("Suppression", "Patients", f"{nom} {prenom}")
                self.reorganize_ids()
                messagebox.showinfo("Succès", "Patient supprimé !\nID réorganisés automatiquement.")
                self.load_patients()
        
        # Vérifier si code requis
        if Session.role not in ["admin", "super_admin"]:
            DemandeCodeWindow(self.root, executer_suppression)
        else:
            executer_suppression()
    
    def back_to_menu(self):
        self.root.destroy()

# Classe AddPatientWindow
class AddPatientWindow:
    def __init__(self, parent, patients_module):
        self.patients_module = patients_module
        
        self.window = tk.Toplevel(parent)
        self.window.title("Nouveau Patient")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        tk.Label(self.window, text="➕ NOUVEAU PATIENT", 
                font=("Arial", 20, "bold"),
                bg=THEME['success'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        font_size = CONFIG['font_size']
        
        # Nom
        tk.Label(form, text="Nom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.nom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                  bg=THEME['bg_light'], 
                                  fg=THEME['text_white'],
                                  insertbackground=THEME['text_white'])
        self.nom_entry.grid(row=0, column=1, pady=12)
        self.nom_entry.focus()
        self.nom_entry.bind('<Return>', lambda e: self.prenom_entry.focus())
        
        # Prénom
        tk.Label(form, text="Prénom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        self.prenom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                     bg=THEME['bg_light'], 
                                     fg=THEME['text_white'],
                                     insertbackground=THEME['text_white'])
        self.prenom_entry.grid(row=1, column=1, pady=12)
        self.prenom_entry.bind('<Return>', lambda e: self.date_entry.focus())
        
        # Date naissance
        tk.Label(form, text="Date naissance\n(AAAA-MM-JJ) :", 
                bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        self.date_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                   bg=THEME['bg_light'], 
                                   fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'])
        self.date_entry.grid(row=2, column=1, pady=12)
        self.date_entry.bind('<Return>', lambda e: self.contact_entry.focus())
        
        # Sexe
        tk.Label(form, text="Sexe :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        self.sexe_var = tk.StringVar(value="M")
        sexe_frame = tk.Frame(form, bg=THEME['bg_dark'])
        sexe_frame.grid(row=3, column=1, sticky=tk.W, pady=12)
        tk.Radiobutton(sexe_frame, text="M", variable=self.sexe_var, value="M",
                      bg=THEME['bg_dark'], fg=THEME['text_white'],
                      selectcolor=THEME['bg_medium'], 
                      font=("Arial", font_size)).pack(side=tk.LEFT, padx=15)
        tk.Radiobutton(sexe_frame, text="F", variable=self.sexe_var, value="F",
                      bg=THEME['bg_dark'], fg=THEME['text_white'],
                      selectcolor=THEME['bg_medium'], 
                      font=("Arial", font_size)).pack(side=tk.LEFT, padx=15)
        
        # Contact
        tk.Label(form, text="Contact :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        self.contact_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.contact_entry.grid(row=4, column=1, pady=12)
        self.contact_entry.bind('<Return>', lambda e: self.adresse_entry.focus())
        
        # Adresse
        tk.Label(form, text="Adresse :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=5, column=0, sticky=tk.W, pady=12)
        self.adresse_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.adresse_entry.grid(row=5, column=1, pady=12)
        self.adresse_entry.bind('<Return>', lambda e: self.urgence_entry.focus())
        
        # Contact urgence
        tk.Label(form, text="Contact urgence :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=6, column=0, sticky=tk.W, pady=12)
        self.urgence_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.urgence_entry.grid(row=6, column=1, pady=12)
        self.urgence_entry.bind('<Return>', lambda e: self.save())
        
        # Boutons
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=7, column=0, columnspan=2, pady=35)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        
        if not nom or not prenom:
            messagebox.showerror("Erreur", "Nom et prénom obligatoires !")
            return
        
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''INSERT INTO Patient 
                        (Nom, Prenom, Date_naissance, Sexe, Contact, Adresse, Contact_urgence, Actif)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 1)''',
                     (nom, prenom, self.date_entry.get() or None,
                      self.sexe_var.get(), self.contact_entry.get() or None,
                      self.adresse_entry.get() or None, 
                      self.urgence_entry.get() or None))
            conn.commit()
            conn.close()
            
            log_activity("Ajout", "Patients", f"{nom} {prenom}")
            messagebox.showinfo("Succès", f"Patient {nom} {prenom} ajouté !")
            self.patients_module.load_patients()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

# Classe EditPatientWindow
class EditPatientWindow:
    def __init__(self, parent, patients_module, patient_id):
        self.patients_module = patients_module
        self.patient_id = patient_id
        
        # Charger patient
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Patient WHERE ID_Patient=?", (patient_id,))
        self.patient = c.fetchone()
        conn.close()

        # Vérification permissions - Pharmacien en lecture seule
        self.lecture_seule = (Session.role == "pharmacien")

        if not self.patient:
            messagebox.showerror("Erreur", "Patient introuvable !")
            return
        
        self.window = tk.Toplevel(parent)
        self.window.title("Modifier Patient")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        tk.Label(self.window, text="✏️ MODIFIER PATIENT", 
                font=("Arial", 20, "bold"),
                bg=THEME['warning'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        font_size = CONFIG['font_size']
        
        # Nom
        tk.Label(form, text="Nom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.nom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                  bg=THEME['bg_light'], 
                                  fg=THEME['text_white'],
                                  insertbackground=THEME['text_white'])
        self.nom_entry.grid(row=0, column=1, pady=12)
        if self.lecture_seule:
            self.nom_entry.config(state='disabled')
            self.prenom_entry.config(state='disabled')
            self.date_entry.config(state='disabled')
            self.sexe_combo.config(state='disabled')
            self.adresse_entry.config(state='disabled')
            self.contact_entry.config(state='disabled')
            self.assurance_entry.config(state='disabled')
        self.nom_entry.insert(0, self.patient[1])
        self.nom_entry.bind('<Return>', lambda e: self.prenom_entry.focus())
        
        # Prénom
        tk.Label(form, text="Prénom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        self.prenom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                     bg=THEME['bg_light'], 
                                     fg=THEME['text_white'],
                                     insertbackground=THEME['text_white'])
        self.prenom_entry.grid(row=1, column=1, pady=12)
        self.prenom_entry.insert(0, self.patient[2])
        self.prenom_entry.bind('<Return>', lambda e: self.date_entry.focus())
        
        # Date naissance
        tk.Label(form, text="Date naissance\n(AAAA-MM-JJ) :", 
                bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        self.date_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                   bg=THEME['bg_light'], 
                                   fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'])
        self.date_entry.grid(row=2, column=1, pady=12)
        if self.lecture_seule:
            self.nom_entry.config(state='disabled')
            self.prenom_entry.config(state='disabled')
            self.date_entry.config(state='disabled')
            self.sexe_combo.config(state='disabled')
            self.adresse_entry.config(state='disabled')
            self.contact_entry.config(state='disabled')
            self.assurance_entry.config(state='disabled')
        if self.patient[3]:
            self.date_entry.insert(0, self.patient[3])
        self.date_entry.bind('<Return>', lambda e: self.contact_entry.focus())
        
        # Sexe
        tk.Label(form, text="Sexe :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        self.sexe_var = tk.StringVar(value=self.patient[4] or "M")
        sexe_frame = tk.Frame(form, bg=THEME['bg_dark'])
        sexe_frame.grid(row=3, column=1, sticky=tk.W, pady=12)
        tk.Radiobutton(sexe_frame, text="M", variable=self.sexe_var, value="M",
                      bg=THEME['bg_dark'], fg=THEME['text_white'],
                      selectcolor=THEME['bg_medium'], 
                      font=("Arial", font_size)).pack(side=tk.LEFT, padx=15)
        tk.Radiobutton(sexe_frame, text="F", variable=self.sexe_var, value="F",
                      bg=THEME['bg_dark'], fg=THEME['text_white'],
                      selectcolor=THEME['bg_medium'], 
                      font=("Arial", font_size)).pack(side=tk.LEFT, padx=15)
        
        # Contact
        tk.Label(form, text="Contact :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        self.contact_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.contact_entry.grid(row=4, column=1, pady=12)
        if self.lecture_seule:
            self.nom_entry.config(state='disabled')
            self.prenom_entry.config(state='disabled')
            self.date_entry.config(state='disabled')
            self.sexe_combo.config(state='disabled')
            self.adresse_entry.config(state='disabled')
            self.contact_entry.config(state='disabled')
            self.assurance_entry.config(state='disabled')
        if self.patient[5]:
            self.contact_entry.insert(0, self.patient[5])
        self.contact_entry.bind('<Return>', lambda e: self.adresse_entry.focus())
        
        # Adresse
        tk.Label(form, text="Adresse :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=5, column=0, sticky=tk.W, pady=12)
        self.adresse_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.adresse_entry.grid(row=5, column=1, pady=12)
        if self.lecture_seule:
            self.nom_entry.config(state='disabled')
            self.prenom_entry.config(state='disabled')
            self.date_entry.config(state='disabled')
            self.sexe_combo.config(state='disabled')
            self.adresse_entry.config(state='disabled')
            self.contact_entry.config(state='disabled')
            self.assurance_entry.config(state='disabled')
        if self.patient[6]:
            self.adresse_entry.insert(0, self.patient[6])
        self.adresse_entry.bind('<Return>', lambda e: self.urgence_entry.focus())
        
        # Contact urgence
        tk.Label(form, text="Contact urgence :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=6, column=0, sticky=tk.W, pady=12)
        self.urgence_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.urgence_entry.grid(row=6, column=1, pady=12)
        if self.lecture_seule:
            self.nom_entry.config(state='disabled')
            self.prenom_entry.config(state='disabled')
            self.date_entry.config(state='disabled')
            self.sexe_combo.config(state='disabled')
            self.adresse_entry.config(state='disabled')
            self.contact_entry.config(state='disabled')
            self.assurance_entry.config(state='disabled')
        if self.patient[7]:
            self.urgence_entry.insert(0, self.patient[7])
        self.urgence_entry.bind('<Return>', lambda e: self.save())
        
        # Boutons
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=7, column=0, columnspan=2, pady=35)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        
        if not nom or not prenom:
            messagebox.showerror("Erreur", "Nom et prénom obligatoires !")
            return
        
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''UPDATE Patient SET Nom=?, Prenom=?, Date_naissance=?, 
                        Sexe=?, Contact=?, Adresse=?, Contact_urgence=?
                        WHERE ID_Patient=?''',
                     (nom, prenom, self.date_entry.get() or None,
                      self.sexe_var.get(), self.contact_entry.get() or None,
                      self.adresse_entry.get() or None,
                      self.urgence_entry.get() or None, self.patient_id))
            conn.commit()
            conn.close()
            
            log_activity("Modification", "Patients", f"{nom} {prenom}")
            messagebox.showinfo("Succès", "Patient modifié !")
            self.patients_module.load_patients()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE MÉDECINS
# ═══════════════════════════════════════════════════════════════════════════════

class MedecinsModule:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        self.root = tk.Toplevel()
        self.root.title("CMEV - Gestion des Médecins")
        self.root.state('zoomed')
        self.root.configure(bg=THEME['bg_dark'])
        
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_menu)
        
        # Header
        header = tk.Frame(self.root, bg=THEME['purple'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="👨‍⚕️ GESTION DES MÉDECINS", 
                font=("Arial", 22, "bold"),
                bg=THEME['purple'], fg=THEME['text_white'], 
                pady=20).pack()
        
        # Toolbar
        toolbar = tk.Frame(self.root, bg=THEME['bg_dark'])
        toolbar.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Button(toolbar, text="➕ Nouveau Médecin", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=20, height=2, command=self.add_medecin,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="✏️ Modifier", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['warning'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.edit_medecin,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🗑️ Supprimer", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.delete_medecin,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔄 Actualiser", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.load_medecins,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔢 Réorganiser ID", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['purple'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.reorganize_and_reload,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🏠 Retour Menu", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['bg_medium'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.back_to_menu,
                 cursor="hand2").pack(side=tk.RIGHT, padx=5)
        
        # Tableau
        tree_frame = tk.Frame(self.root, bg=THEME['bg_dark'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Med.Treeview",
                       background=THEME['tree_bg'],
                       foreground=THEME['tree_fg'],
                       fieldbackground=THEME['tree_bg'],
                       font=('Arial', CONFIG['font_size']))
        style.configure("Med.Treeview.Heading",
                       background='#8e44ad',
                       foreground='white',
                       font=('Arial', CONFIG['font_size'], 'bold'))
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Nom", "Prenom", "Specialite", "Contact", "Adresse", "Date_embauche"),
            show="headings",
            yscrollcommand=vsb.set,
            style="Med.Treeview",
            height=30
        )
        
        vsb.config(command=self.tree.yview)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Prenom", text="Prénom")
        self.tree.heading("Specialite", text="Spécialité")
        self.tree.heading("Contact", text="Contact")
        self.tree.heading("Adresse", text="Adresse")
        self.tree.heading("Date_embauche", text="Date embauche")
        
        self.tree.column("ID", width=60, anchor=tk.CENTER)
        self.tree.column("Nom", width=150)
        self.tree.column("Prenom", width=150)
        self.tree.column("Specialite", width=180)
        self.tree.column("Contact", width=130)
        self.tree.column("Adresse", width=220)
        self.tree.column("Date_embauche", width=120, anchor=tk.CENTER)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_medecins()
    
    def reorganize_and_reload(self):
        self.reorganize_ids()
        self.load_medecins()
        messagebox.showinfo("Succès", "ID réorganisés !")
    
    def reorganize_ids(self):
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            
            c.execute("SELECT * FROM Medecin WHERE Actif=1 ORDER BY ID_Medecin")
            medecins = c.fetchall()
            
            if not medecins:
                return
            
            c.execute("DELETE FROM Medecin")
            c.execute("DELETE FROM sqlite_sequence WHERE name='Medecin'")
            
            for m in medecins:
                c.execute('''INSERT INTO Medecin 
                            (Nom, Prenom, Specialite, Contact, Adresse, Date_embauche, Actif)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (m[1], m[2], m[3], m[4], m[5], m[6], m[7]))
            
            conn.commit()
            conn.close()
            
            log_activity("Réorganisation", "Médecins", "ID réorganisés")
            
        except Exception as e:
            print(f"Erreur réorganisation ID: {e}")
    
    def load_medecins(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Medecin WHERE Actif=1 ORDER BY Nom")
        medecins = c.fetchall()
        conn.close()
        
        for m in medecins:
            self.tree.insert("", tk.END, values=(
                m[0], m[1], m[2], m[3] or "", 
                m[4] or "", m[5] or "", m[6] or ""
            ))
    
    def add_medecin(self):
        AddMedecinWindow(self.root, self)
    
    def edit_medecin(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un médecin !")
            return
        
        item = self.tree.item(selected[0])
        medecin_id = item['values'][0]
        
        # Vérifier si code requis
        if Session.role not in ["admin", "super_admin"]:
            DemandeCodeWindow(self.root, lambda: EditMedecinWindow(self.root, self, medecin_id))
        else:
            EditMedecinWindow(self.root, self, medecin_id)
    
    def delete_medecin(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un médecin !")
            return
        
        item = self.tree.item(selected[0])
        nom = item['values'][1]
        prenom = item['values'][2]
        medecin_id = item['values'][0]
        
        def executer_suppression():
            if messagebox.askyesno("Confirmation", f"Supprimer Dr. {nom} {prenom} ?"):
                conn = sqlite3.connect('cmev.db')
                c = conn.cursor()
                c.execute("DELETE FROM Medecin WHERE ID_Medecin=?", (medecin_id,))
                conn.commit()
                conn.close()
                
                log_activity("Suppression", "Médecins", f"Dr. {nom} {prenom}")
                self.reorganize_ids()
                messagebox.showinfo("Succès", "Médecin supprimé !\nID réorganisés automatiquement.")
                self.load_medecins()
        
        if Session.role not in ["admin", "super_admin"]:
            DemandeCodeWindow(self.root, executer_suppression)
        else:
            executer_suppression()
    
    def back_to_menu(self):
        self.root.destroy()

class AddMedecinWindow:
    def __init__(self, parent, medecins_module):
        self.medecins_module = medecins_module
        
        self.window = tk.Toplevel(parent)
        self.window.title("Nouveau Médecin")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        tk.Label(self.window, text="➕ NOUVEAU MÉDECIN", 
                font=("Arial", 20, "bold"),
                bg=THEME['success'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        font_size = CONFIG['font_size']
        
        # Nom
        tk.Label(form, text="Nom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.nom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                  bg=THEME['bg_light'], 
                                  fg=THEME['text_white'],
                                  insertbackground=THEME['text_white'])
        self.nom_entry.grid(row=0, column=1, pady=12)
        self.nom_entry.focus()
        self.nom_entry.bind('<Return>', lambda e: self.prenom_entry.focus())
        
        # Prénom
        tk.Label(form, text="Prénom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        self.prenom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                     bg=THEME['bg_light'], 
                                     fg=THEME['text_white'],
                                     insertbackground=THEME['text_white'])
        self.prenom_entry.grid(row=1, column=1, pady=12)
        self.prenom_entry.bind('<Return>', lambda e: self.specialite_combo.focus())
        
        # Spécialité (LISTE DÉROULANTE)
        tk.Label(form, text="Spécialité :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        
        specialites = [
            "Médecine générale", "Anesthésie-Réanimation", "Cardiologie",
            "Chirurgie générale", "Chirurgie cardiaque", "Chirurgie plastique",
            "Chirurgie orthopédique", "Dermatologie", "Endocrinologie",
            "Gastro-entérologie", "Gériatrie", "Gynécologie",
            "Gynécologie-Obstétrique", "Hématologie", "Médecine interne",
            "Néphrologie", "Neurologie", "Neurochirurgie", "Oncologie",
            "Ophtalmologie", "ORL (Oto-Rhino-Laryngologie)", "Pédiatrie",
            "Pneumologie", "Psychiatrie", "Radiologie", "Rhumatologie",
            "Urologie", "Médecine du travail", "Médecine d'urgence",
            "Réanimation médicale", "Stomatologie", "Allergologie",
            "Andrologie", "Chirurgie vasculaire", "Chirurgie thoracique",
            "Chirurgie pédiatrique", "Médecine nucléaire",
            "Médecine physique et réadaptation", "Pathologie",
            "Pharmacologie", "Santé publique", "Autre"
        ]
        
        self.specialite_var = tk.StringVar()
        self.specialite_combo = ttk.Combobox(form, textvariable=self.specialite_var,
                                            values=specialites,
                                            font=("Arial", font_size),
                                            width=33, state="readonly")
        self.specialite_combo.grid(row=2, column=1, pady=12)
        self.specialite_combo.set("Médecine générale")
        self.specialite_combo.bind('<Return>', lambda e: self.contact_entry.focus())
        
        # Contact
        tk.Label(form, text="Contact :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        self.contact_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.contact_entry.grid(row=3, column=1, pady=12)
        self.contact_entry.bind('<Return>', lambda e: self.adresse_entry.focus())
        
        # Adresse
        tk.Label(form, text="Adresse :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        self.adresse_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.adresse_entry.grid(row=4, column=1, pady=12)
        self.adresse_entry.bind('<Return>', lambda e: self.date_entry.focus())
        
        # Date embauche
        tk.Label(form, text="Date embauche\n(AAAA-MM-JJ) :", 
                bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=5, column=0, sticky=tk.W, pady=12)
        self.date_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                   bg=THEME['bg_light'], 
                                   fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'])
        self.date_entry.grid(row=5, column=1, pady=12)
        self.date_entry.bind('<Return>', lambda e: self.save())
        
        # Boutons
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=6, column=0, columnspan=2, pady=35)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        
        if not nom or not prenom:
            messagebox.showerror("Erreur", "Nom et prénom obligatoires !")
            return
        
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''INSERT INTO Medecin 
                        (Nom, Prenom, Specialite, Contact, Adresse, Date_embauche, Actif)
                        VALUES (?, ?, ?, ?, ?, ?, 1)''',
                     (nom, prenom, self.specialite_var.get() or None,
                      self.contact_entry.get() or None,
                      self.adresse_entry.get() or None, 
                      self.date_entry.get() or None))
            conn.commit()
            conn.close()
            
            log_activity("Ajout", "Médecins", f"Dr. {nom} {prenom}")
            messagebox.showinfo("Succès", f"Dr. {nom} {prenom} ajouté !")
            self.medecins_module.load_medecins()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

class EditMedecinWindow:
    def __init__(self, parent, medecins_module, medecin_id):
        self.medecins_module = medecins_module
        self.medecin_id = medecin_id
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Medecin WHERE ID_Medecin=?", (medecin_id,))
        self.medecin = c.fetchone()
        conn.close()
        
        if not self.medecin:
            messagebox.showerror("Erreur", "Médecin introuvable !")
            return
        
        self.window = tk.Toplevel(parent)
        self.window.title("Modifier Médecin")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        tk.Label(self.window, text="✏️ MODIFIER MÉDECIN", 
                font=("Arial", 20, "bold"),
                bg=THEME['warning'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        font_size = CONFIG['font_size']
        
        # Nom
        tk.Label(form, text="Nom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.nom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                  bg=THEME['bg_light'], 
                                  fg=THEME['text_white'],
                                  insertbackground=THEME['text_white'])
        self.nom_entry.grid(row=0, column=1, pady=12)
        self.nom_entry.insert(0, self.medecin[1])
        self.nom_entry.bind('<Return>', lambda e: self.prenom_entry.focus())
        
        # Prénom
        tk.Label(form, text="Prénom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        self.prenom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                     bg=THEME['bg_light'], 
                                     fg=THEME['text_white'],
                                     insertbackground=THEME['text_white'])
        self.prenom_entry.grid(row=1, column=1, pady=12)
        self.prenom_entry.insert(0, self.medecin[2])
        self.prenom_entry.bind('<Return>', lambda e: self.specialite_combo.focus())
        
        # Spécialité
        tk.Label(form, text="Spécialité :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        
        specialites = [
            "Médecine générale", "Anesthésie-Réanimation", "Cardiologie",
            "Chirurgie générale", "Chirurgie cardiaque", "Chirurgie plastique",
            "Chirurgie orthopédique", "Dermatologie", "Endocrinologie",
            "Gastro-entérologie", "Gériatrie", "Gynécologie",
            "Gynécologie-Obstétrique", "Hématologie", "Médecine interne",
            "Néphrologie", "Neurologie", "Neurochirurgie", "Oncologie",
            "Ophtalmologie", "ORL (Oto-Rhino-Laryngologie)", "Pédiatrie",
            "Pneumologie", "Psychiatrie", "Radiologie", "Rhumatologie",
            "Urologie", "Médecine du travail", "Médecine d'urgence",
            "Réanimation médicale", "Stomatologie", "Allergologie",
            "Andrologie", "Chirurgie vasculaire", "Chirurgie thoracique",
            "Chirurgie pédiatrique", "Médecine nucléaire",
            "Médecine physique et réadaptation", "Pathologie",
            "Pharmacologie", "Santé publique", "Autre"
        ]
        
        self.specialite_var = tk.StringVar()
        self.specialite_combo = ttk.Combobox(form, textvariable=self.specialite_var,
                                            values=specialites,
                                            font=("Arial", font_size),
                                            width=33, state="readonly")
        self.specialite_combo.grid(row=2, column=1, pady=12)
        
        if self.medecin[3] and self.medecin[3] in specialites:
            self.specialite_combo.set(self.medecin[3])
        else:
            self.specialite_combo.set("Médecine générale")
        
        self.specialite_combo.bind('<Return>', lambda e: self.contact_entry.focus())
        
        # Contact
        tk.Label(form, text="Contact :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        self.contact_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.contact_entry.grid(row=3, column=1, pady=12)
        if self.medecin[4]:
            self.contact_entry.insert(0, self.medecin[4])
        self.contact_entry.bind('<Return>', lambda e: self.adresse_entry.focus())
        
        # Adresse
        tk.Label(form, text="Adresse :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        self.adresse_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.adresse_entry.grid(row=4, column=1, pady=12)
        if self.medecin[5]:
            self.adresse_entry.insert(0, self.medecin[5])
        self.adresse_entry.bind('<Return>', lambda e: self.date_entry.focus())
        
        # Date embauche
        tk.Label(form, text="Date embauche\n(AAAA-MM-JJ) :", 
                bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=5, column=0, sticky=tk.W, pady=12)
        self.date_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                   bg=THEME['bg_light'], 
                                   fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'])
        self.date_entry.grid(row=5, column=1, pady=12)
        if self.medecin[6]:
            self.date_entry.insert(0, self.medecin[6])
        self.date_entry.bind('<Return>', lambda e: self.save())
        
        # Boutons
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=6, column=0, columnspan=2, pady=35)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        
        if not nom or not prenom:
            messagebox.showerror("Erreur", "Nom et prénom obligatoires !")
            return
        
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''UPDATE Medecin SET Nom=?, Prenom=?, Specialite=?, 
                        Contact=?, Adresse=?, Date_embauche=?
                        WHERE ID_Medecin=?''',
                     (nom, prenom, self.specialite_var.get() or None,
                      self.contact_entry.get() or None,
                      self.adresse_entry.get() or None,
                      self.date_entry.get() or None, self.medecin_id))
            conn.commit()
            conn.close()
            
            log_activity("Modification", "Médecins", f"Dr. {nom} {prenom}")
            messagebox.showinfo("Succès", "Médecin modifié !")
            self.medecins_module.load_medecins()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EMPLOYÉS
# ═══════════════════════════════════════════════════════════════════════════════

class EmployesModule:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        self.root = tk.Toplevel()
        self.root.title("CMEV - Gestion des Employés")
        self.root.state('zoomed')
        self.root.configure(bg=THEME['bg_dark'])
        
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_menu)
        
        # Header
        header = tk.Frame(self.root, bg=THEME['orange'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="👷 GESTION DES EMPLOYÉS", 
                font=("Arial", 22, "bold"),
                bg=THEME['orange'], fg=THEME['text_white'], 
                pady=20).pack()
        
        # Toolbar
        toolbar = tk.Frame(self.root, bg=THEME['bg_dark'])
        toolbar.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Button(toolbar, text="➕ Nouvel Employé", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=20, height=2, command=self.add_employe,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="✏️ Modifier", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['warning'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.edit_employe,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🗑️ Supprimer", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.delete_employe,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔄 Actualiser", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.load_employes,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔢 Réorganiser ID", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['purple'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.reorganize_and_reload,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🏠 Retour Menu", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['bg_medium'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.back_to_menu,
                 cursor="hand2").pack(side=tk.RIGHT, padx=5)
        
        # Tableau
        tree_frame = tk.Frame(self.root, bg=THEME['bg_dark'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Emp.Treeview",
                       background=THEME['tree_bg'],
                       foreground=THEME['tree_fg'],
                       fieldbackground=THEME['tree_bg'],
                       font=('Arial', CONFIG['font_size']))
        style.configure("Emp.Treeview.Heading",
                       background='#d35400',
                       foreground='white',
                       font=('Arial', CONFIG['font_size'], 'bold'))
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Nom", "Prenom", "Fonction", "Contact", "Adresse", "Date_embauche", "Salaire"),
            show="headings",
            yscrollcommand=vsb.set,
            style="Emp.Treeview",
            height=30
        )
        
        vsb.config(command=self.tree.yview)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Prenom", text="Prénom")
        self.tree.heading("Fonction", text="Fonction")
        self.tree.heading("Contact", text="Contact")
        self.tree.heading("Adresse", text="Adresse")
        self.tree.heading("Date_embauche", text="Date embauche")
        self.tree.heading("Salaire", text="Salaire (FC)")
        
        self.tree.column("ID", width=60, anchor=tk.CENTER)
        self.tree.column("Nom", width=140)
        self.tree.column("Prenom", width=140)
        self.tree.column("Fonction", width=180)
        self.tree.column("Contact", width=120)
        self.tree.column("Adresse", width=200)
        self.tree.column("Date_embauche", width=110, anchor=tk.CENTER)
        self.tree.column("Salaire", width=120, anchor=tk.E)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_employes()
    
    def reorganize_and_reload(self):
        self.reorganize_ids()
        self.load_employes()
        messagebox.showinfo("Succès", "ID réorganisés !")
    
    def reorganize_ids(self):
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            
            c.execute("SELECT * FROM Employe WHERE Actif=1 ORDER BY ID_Employe")
            employes = c.fetchall()
            
            if not employes:
                return
            
            c.execute("DELETE FROM Employe")
            c.execute("DELETE FROM sqlite_sequence WHERE name='Employe'")
            
            for e in employes:
                c.execute('''INSERT INTO Employe 
                            (Nom, Prenom, Fonction, Contact, Adresse, Date_embauche, Salaire, Actif)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8]))
            
            conn.commit()
            conn.close()
            
            log_activity("Réorganisation", "Employés", "ID réorganisés")
            
        except Exception as e:
            print(f"Erreur réorganisation ID: {e}")
    
    def load_employes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Employe WHERE Actif=1 ORDER BY Nom")
        employes = c.fetchall()
        conn.close()
        
        for e in employes:
            salaire_fmt = f"{int(e[7]):,}" if e[7] else "0"
            self.tree.insert("", tk.END, values=(
                e[0], e[1], e[2], e[3] or "", 
                e[4] or "", e[5] or "", e[6] or "", salaire_fmt
            ))
    
    def add_employe(self):
        AddEmployeWindow(self.root, self)
    
    def edit_employe(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un employé !")
            return
        
        item = self.tree.item(selected[0])
        employe_id = item['values'][0]
        
        # Vérifier si code requis
        if Session.role not in ["admin", "super_admin"]:
            DemandeCodeWindow(self.root, lambda: EditEmployeWindow(self.root, self, employe_id))
        else:
            EditEmployeWindow(self.root, self, employe_id)
    
    def delete_employe(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un employé !")
            return
        
        item = self.tree.item(selected[0])
        nom = item['values'][1]
        prenom = item['values'][2]
        employe_id = item['values'][0]
        
        def executer_suppression():
            if messagebox.askyesno("Confirmation", f"Supprimer {nom} {prenom} ?"):
                conn = sqlite3.connect('cmev.db')
                c = conn.cursor()
                c.execute("DELETE FROM Employe WHERE ID_Employe=?", (employe_id,))
                conn.commit()
                conn.close()
                
                log_activity("Suppression", "Employés", f"{nom} {prenom}")
                self.reorganize_ids()
                messagebox.showinfo("Succès", "Employé supprimé !\nID réorganisés automatiquement.")
                self.load_employes()
        
        if Session.role not in ["admin", "super_admin"]:
            DemandeCodeWindow(self.root, executer_suppression)
        else:
            executer_suppression()
    
    def back_to_menu(self):
        self.root.destroy()

# Les classes AddEmployeWindow et EditEmployeWindow suivent le même pattern que Médecins
# Je les simplifie pour gagner de l'espace

class AddEmployeWindow:
    def __init__(self, parent, employes_module):
        self.employes_module = employes_module
        
        self.window = tk.Toplevel(parent)
        self.window.title("Nouvel Employé")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        tk.Label(self.window, text="➕ NOUVEL EMPLOYÉ", 
                font=("Arial", 20, "bold"),
                bg=THEME['success'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        font_size = CONFIG['font_size']
        
        # Nom
        tk.Label(form, text="Nom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.nom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                  bg=THEME['bg_light'], 
                                  fg=THEME['text_white'],
                                  insertbackground=THEME['text_white'])
        self.nom_entry.grid(row=0, column=1, pady=12)
        self.nom_entry.focus()
        self.nom_entry.bind('<Return>', lambda e: self.prenom_entry.focus())
        
        # Prénom
        tk.Label(form, text="Prénom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        self.prenom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                     bg=THEME['bg_light'], 
                                     fg=THEME['text_white'],
                                     insertbackground=THEME['text_white'])
        self.prenom_entry.grid(row=1, column=1, pady=12)
        self.prenom_entry.bind('<Return>', lambda e: self.fonction_combo.focus())
        
        # Fonction
        tk.Label(form, text="Fonction :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        
        fonctions = [
            "Réceptionniste", "Secrétaire médical(e)", "Infirmier(ère)",
            "Aide-soignant(e)", "Technicien(ne) de laboratoire", "Radiologue",
            "Pharmacien(ne)", "Assistant(e) pharmacien(ne)", "Comptable",
            "Responsable administratif", "Agent d'entretien", "Agent de sécurité",
            "Brancardier", "Responsable des achats", "Informaticien(ne)",
            "Responsable RH", "Magasinier", "Standardiste",
            "Chauffeur ambulance", "Responsable qualité",
            "Directeur(trice) adjoint(e)", "Directeur(trice) général(e)", "Autre"
        ]
        
        self.fonction_var = tk.StringVar()
        self.fonction_combo = ttk.Combobox(form, textvariable=self.fonction_var,
                                          values=fonctions,
                                          font=("Arial", font_size),
                                          width=33, state="readonly")
        self.fonction_combo.grid(row=2, column=1, pady=12)
        self.fonction_combo.set("Réceptionniste")
        self.fonction_combo.bind('<Return>', lambda e: self.contact_entry.focus())
        
        # Contact
        tk.Label(form, text="Contact :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        self.contact_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.contact_entry.grid(row=3, column=1, pady=12)
        self.contact_entry.bind('<Return>', lambda e: self.adresse_entry.focus())
        
        # Adresse
        tk.Label(form, text="Adresse :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        self.adresse_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.adresse_entry.grid(row=4, column=1, pady=12)
        self.adresse_entry.bind('<Return>', lambda e: self.date_entry.focus())
        
        # Date embauche
        tk.Label(form, text="Date embauche\n(AAAA-MM-JJ) :", 
                bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=5, column=0, sticky=tk.W, pady=12)
        self.date_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                   bg=THEME['bg_light'], 
                                   fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'])
        self.date_entry.grid(row=5, column=1, pady=12)
        self.date_entry.bind('<Return>', lambda e: self.salaire_entry.focus())
        
        # Salaire
        tk.Label(form, text="Salaire (FC) :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=6, column=0, sticky=tk.W, pady=12)
        self.salaire_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.salaire_entry.grid(row=6, column=1, pady=12)
        self.salaire_entry.bind('<Return>', lambda e: self.save())
        
        # Boutons
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=7, column=0, columnspan=2, pady=35)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        
        if not nom or not prenom:
            messagebox.showerror("Erreur", "Nom et prénom obligatoires !")
            return
        
        salaire = None
        if self.salaire_entry.get().strip():
            try:
                salaire = float(self.salaire_entry.get().strip())
            except ValueError:
                messagebox.showerror("Erreur", "Salaire invalide !")
                return
        
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''INSERT INTO Employe 
                        (Nom, Prenom, Fonction, Contact, Adresse, Date_embauche, Salaire, Actif)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 1)''',
                     (nom, prenom, self.fonction_var.get() or None,
                      self.contact_entry.get() or None,
                      self.adresse_entry.get() or None, 
                      self.date_entry.get() or None, salaire))
            conn.commit()
            conn.close()
            
            log_activity("Ajout", "Employés", f"{nom} {prenom}")
            messagebox.showinfo("Succès", f"{nom} {prenom} ajouté !")
            self.employes_module.load_employes()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

class EditEmployeWindow:
    def __init__(self, parent, employes_module, employe_id):
        self.employes_module = employes_module
        self.employe_id = employe_id

        # Vérification permissions - Seuls admin et super_admin
        if Session.role not in ["super_admin", "admin"]:
            messagebox.showerror("Erreur", "Vous n'avez pas les permissions pour modifier les employés !")
            return

        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Employe WHERE ID_Employe=?", (employe_id,))
        self.employe = c.fetchone()
        conn.close()
        
        if not self.employe:
            messagebox.showerror("Erreur", "Employé introuvable !")
            return
        
        self.window = tk.Toplevel(parent)
        self.window.title("Modifier Employé")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        tk.Label(self.window, text="✏️ MODIFIER EMPLOYÉ", 
                font=("Arial", 20, "bold"),
                bg=THEME['warning'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        font_size = CONFIG['font_size']
        
        tk.Label(form, text="Nom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.nom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                  bg=THEME['bg_light'], 
                                  fg=THEME['text_white'],
                                  insertbackground=THEME['text_white'])
        self.nom_entry.grid(row=0, column=1, pady=12)
        self.nom_entry.insert(0, self.employe[1])
        
        tk.Label(form, text="Prénom :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        self.prenom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                     bg=THEME['bg_light'], 
                                     fg=THEME['text_white'],
                                     insertbackground=THEME['text_white'])
        self.prenom_entry.grid(row=1, column=1, pady=12)
        self.prenom_entry.insert(0, self.employe[2])
        
        tk.Label(form, text="Fonction :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        
        fonctions = [
            "Réceptionniste", "Secrétaire médical(e)", "Infirmier(ère)",
            "Aide-soignant(e)", "Technicien(ne) de laboratoire", "Radiologue",
            "Pharmacien(ne)", "Assistant(e) pharmacien(ne)", "Comptable",
            "Responsable administratif", "Agent d'entretien", "Agent de sécurité",
            "Brancardier", "Responsable des achats", "Informaticien(ne)",
            "Responsable RH", "Magasinier", "Standardiste",
            "Chauffeur ambulance", "Responsable qualité",
            "Directeur(trice) adjoint(e)", "Directeur(trice) général(e)", "Autre"
        ]
        
        self.fonction_var = tk.StringVar()
        self.fonction_combo = ttk.Combobox(form, textvariable=self.fonction_var,
                                          values=fonctions,
                                          font=("Arial", font_size),
                                          width=33, state="readonly")
        self.fonction_combo.grid(row=2, column=1, pady=12)
        if self.employe[3] and self.employe[3] in fonctions:
            self.fonction_combo.set(self.employe[3])
        else:
            self.fonction_combo.set("Réceptionniste")
        
        tk.Label(form, text="Contact :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        self.contact_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.contact_entry.grid(row=3, column=1, pady=12)
        if self.employe[4]:
            self.contact_entry.insert(0, self.employe[4])
        
        tk.Label(form, text="Adresse :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        self.adresse_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.adresse_entry.grid(row=4, column=1, pady=12)
        if self.employe[5]:
            self.adresse_entry.insert(0, self.employe[5])
        
        tk.Label(form, text="Date embauche\n(AAAA-MM-JJ) :", 
                bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=5, column=0, sticky=tk.W, pady=12)
        self.date_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                   bg=THEME['bg_light'], 
                                   fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'])
        self.date_entry.grid(row=5, column=1, pady=12)
        if self.employe[6]:
            self.date_entry.insert(0, self.employe[6])
        
        tk.Label(form, text="Salaire (FC) :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=6, column=0, sticky=tk.W, pady=12)
        self.salaire_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                      bg=THEME['bg_light'], 
                                      fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.salaire_entry.grid(row=6, column=1, pady=12)
        if self.employe[7]:
            self.salaire_entry.insert(0, str(int(self.employe[7])))
        
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=7, column=0, columnspan=2, pady=35)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        nom = self.nom_entry.get().strip()
        prenom = self.prenom_entry.get().strip()
        
        if not nom or not prenom:
            messagebox.showerror("Erreur", "Nom et prénom obligatoires !")
            return
        
        salaire = None
        if self.salaire_entry.get().strip():
            try:
                salaire = float(self.salaire_entry.get().strip())
            except ValueError:
                messagebox.showerror("Erreur", "Salaire invalide !")
                return
        
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''UPDATE Employe SET Nom=?, Prenom=?, Fonction=?, 
                        Contact=?, Adresse=?, Date_embauche=?, Salaire=?
                        WHERE ID_Employe=?''',
                     (nom, prenom, self.fonction_var.get() or None,
                      self.contact_entry.get() or None,
                      self.adresse_entry.get() or None,
                      self.date_entry.get() or None,
                      salaire, self.employe_id))
            conn.commit()
            conn.close()
            
            log_activity("Modification", "Employés", f"{nom} {prenom}")
            messagebox.showinfo("Succès", "Employé modifié !")
            self.employes_module.load_employes()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE CONSULTATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class ConsultationsModule:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        self.root = tk.Toplevel()
        self.root.title("CMEV - Gestion des Consultations")
        self.root.state('zoomed')
        self.root.configure(bg=THEME['bg_dark'])
        
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_menu)
        
        # Header
        header = tk.Frame(self.root, bg=THEME['teal'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📋 GESTION DES CONSULTATIONS", 
                font=("Arial", 22, "bold"),
                bg=THEME['teal'], fg=THEME['text_white'], 
                pady=20).pack()
        
        # Toolbar
        toolbar = tk.Frame(self.root, bg=THEME['bg_dark'])
        toolbar.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Button(toolbar, text="➕ Nouvelle Consultation", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=22, height=2, command=self.add_consultation,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="👁️ Voir détails", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.view_consultation,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="✏️ Modifier", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['warning'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.edit_consultation,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🗑️ Supprimer", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.delete_consultation,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔄 Actualiser", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.load_consultations,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔢 Réorganiser ID", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['purple'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.reorganize_and_reload,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🏠 Retour Menu", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['bg_medium'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.back_to_menu,
                 cursor="hand2").pack(side=tk.RIGHT, padx=5)
        
        # Tableau
        tree_frame = tk.Frame(self.root, bg=THEME['bg_dark'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Cons.Treeview",
                       background=THEME['tree_bg'],
                       foreground=THEME['tree_fg'],
                       fieldbackground=THEME['tree_bg'],
                       font=('Arial', CONFIG['font_size']))
        style.configure("Cons.Treeview.Heading",
                       background='#16a085',
                       foreground='white',
                       font=('Arial', CONFIG['font_size'], 'bold'))
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Numero", "Date", "Heure", "Patient", "Medecin", "Motif"),
            show="headings",
            yscrollcommand=vsb.set,
            style="Cons.Treeview",
            height=30
        )
        
        vsb.config(command=self.tree.yview)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Numero", text="N° Consultation")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Heure", text="Heure")
        self.tree.heading("Patient", text="Patient")
        self.tree.heading("Medecin", text="Médecin")
        self.tree.heading("Motif", text="Motif")
        
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Numero", width=180)
        self.tree.column("Date", width=100, anchor=tk.CENTER)
        self.tree.column("Heure", width=80, anchor=tk.CENTER)
        self.tree.column("Patient", width=200)
        self.tree.column("Medecin", width=200)
        self.tree.column("Motif", width=250)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_consultations()
    
    def reorganize_and_reload(self):
        self.reorganize_ids()
        self.load_consultations()
        messagebox.showinfo("Succès", "ID réorganisés !")
    
    def reorganize_ids(self):
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            
            c.execute("SELECT * FROM Consultation ORDER BY ID_Consultation")
            consultations = c.fetchall()
            
            if not consultations:
                return
            
            c.execute("DELETE FROM Consultation")
            c.execute("DELETE FROM sqlite_sequence WHERE name='Consultation'")
            
            for cons in consultations:
                c.execute('''INSERT INTO Consultation 
                            (Numero_Consultation, Date_Consultation, Heure_Consultation, 
                             ID_Patient, ID_Medecin, Motif, Diagnostic, Observations)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (cons[1], cons[2], cons[3], cons[4], cons[5], cons[6], cons[7], cons[8]))
            
            conn.commit()
            conn.close()
            
            log_activity("Réorganisation", "Consultations", "ID réorganisés")
            
        except Exception as e:
            print(f"Erreur réorganisation ID: {e}")
    
    def load_consultations(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute('''SELECT c.*, 
                    p.Nom || ' ' || p.Prenom as patient_nom,
                    m.Nom || ' ' || m.Prenom as medecin_nom
                    FROM Consultation c
                    LEFT JOIN Patient p ON c.ID_Patient = p.ID_Patient
                    LEFT JOIN Medecin m ON c.ID_Medecin = m.ID_Medecin
                    ORDER BY c.Date_Consultation DESC, c.Heure_Consultation DESC''')
        consultations = c.fetchall()
        conn.close()
        
        for cons in consultations:
            self.tree.insert("", tk.END, values=(
                cons[0],
                cons[1] or "",
                cons[2] or "",
                cons[3] or "",
                cons[9] or "Patient supprimé",
                cons[10] or "Médecin supprimé",
                cons[6][:50] + "..." if cons[6] and len(cons[6]) > 50 else cons[6] or ""
            ))
    
    def add_consultation(self):
        AddConsultationWindow(self.root, self)
    
    def view_consultation(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une consultation !")
            return
        
        item = self.tree.item(selected[0])
        consultation_id = item['values'][0]
        ViewConsultationWindow(self.root, consultation_id)
    
    def edit_consultation(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une consultation !")
            return
        
        item = self.tree.item(selected[0])
        consultation_id = item['values'][0]
        
        # Vérifier si code requis
        if Session.role not in ["admin", "super_admin"]:
            DemandeCodeWindow(self.root, lambda: EditConsultationWindow(self.root, self, consultation_id))
        else:
            EditConsultationWindow(self.root, self, consultation_id)
    
    def delete_consultation(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une consultation !")
            return
        
        item = self.tree.item(selected[0])
        numero = item['values'][1]
        consultation_id = item['values'][0]
        
        def executer_suppression():
            if messagebox.askyesno("Confirmation", f"Supprimer la consultation {numero} ?"):
                conn = sqlite3.connect('cmev.db')
                c = conn.cursor()
                c.execute("DELETE FROM Consultation WHERE ID_Consultation=?", (consultation_id,))
                conn.commit()
                conn.close()
                
                log_activity("Suppression", "Consultations", f"{numero}")
                self.reorganize_ids()
                messagebox.showinfo("Succès", "Consultation supprimée !\nID réorganisés automatiquement.")
                self.load_consultations()
        
        if Session.role not in ["admin", "super_admin"]:
            DemandeCodeWindow(self.root, executer_suppression)
        else:
            executer_suppression()
    
    def back_to_menu(self):
        self.root.destroy()

class AddConsultationWindow:
    def __init__(self, parent, consultations_module):
        self.consultations_module = consultations_module
        
        self.window = tk.Toplevel(parent)
        self.window.title("Nouvelle Consultation")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        tk.Label(self.window, text="➕ NOUVELLE CONSULTATION", 
                font=("Arial", 20, "bold"),
                bg=THEME['success'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        # Frame scrollable
        canvas = tk.Canvas(self.window, bg=THEME['bg_dark'])
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=THEME['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        form = scrollable_frame
        
        font_size = CONFIG['font_size']
        
        # Numéro (auto-généré)
        tk.Label(form, text="N° Consultation :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, padx=40, pady=12)
        self.numero = generer_numero_consultation()
        tk.Label(form, text=self.numero, bg=THEME['bg_dark'],
                fg=THEME['text_yellow'], 
                font=("Arial", font_size, "bold")).grid(row=0, column=1, sticky=tk.W, pady=12)
        
        # Date
        tk.Label(form, text="Date (AAAA-MM-JJ) :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, padx=40, pady=12)
        self.date_entry = tk.Entry(form, font=("Arial", font_size), width=40,
                                    bg=THEME['bg_light'], 
                                    fg=THEME['text_white'],
                                    insertbackground=THEME['text_white'])
        self.date_entry.grid(row=1, column=1, pady=12, sticky=tk.W)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.bind('<Return>', lambda e: self.heure_entry.focus())
        
        # Heure
        tk.Label(form, text="Heure (HH:MM) :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, padx=40, pady=12)
        self.heure_entry = tk.Entry(form, font=("Arial", font_size), width=40,
                                     bg=THEME['bg_light'], 
                                     fg=THEME['text_white'],
                                     insertbackground=THEME['text_white'])
        self.heure_entry.grid(row=2, column=1, pady=12, sticky=tk.W)
        self.heure_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.heure_entry.bind('<Return>', lambda e: self.motif_text.focus())
        
        # Patient (dropdown)
        tk.Label(form, text="Patient :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, padx=40, pady=12)
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT ID_Patient, Nom, Prenom FROM Patient WHERE Actif=1 ORDER BY Nom")
        patients = c.fetchall()
        conn.close()
        
        self.patients_dict = {f"{p[1]} {p[2]}": p[0] for p in patients}
        patient_names = list(self.patients_dict.keys())
        
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_var,
                                         values=patient_names,
                                         font=("Arial", font_size),
                                         width=38, state="readonly")
        self.patient_combo.grid(row=3, column=1, pady=12, sticky=tk.W)
        if patient_names:
            self.patient_combo.set(patient_names[0])
        
        # Médecin (dropdown)
        tk.Label(form, text="Médecin :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, padx=40, pady=12)
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT ID_Medecin, Nom, Prenom FROM Medecin WHERE Actif=1 ORDER BY Nom")
        medecins = c.fetchall()
        conn.close()
        
        self.medecins_dict = {f"Dr. {m[1]} {m[2]}": m[0] for m in medecins}
        medecin_names = list(self.medecins_dict.keys())
        
        self.medecin_var = tk.StringVar()
        self.medecin_combo = ttk.Combobox(form, textvariable=self.medecin_var,
                                         values=medecin_names,
                                         font=("Arial", font_size),
                                         width=38, state="readonly")
        self.medecin_combo.grid(row=4, column=1, pady=12, sticky=tk.W)
        if medecin_names:
            self.medecin_combo.set(medecin_names[0])
        
        # Motif
        tk.Label(form, text="Motif :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=5, column=0, sticky=tk.NW, padx=40, pady=12)
        self.motif_text = scrolledtext.ScrolledText(form, font=("Arial", font_size), 
                                                    width=40, height=4,
                                                    bg=THEME['bg_light'], 
                                                    fg=THEME['text_white'],
                                                    insertbackground=THEME['text_white'])
        self.motif_text.grid(row=5, column=1, pady=12, sticky=tk.W)
        
        # Diagnostic
        tk.Label(form, text="Diagnostic :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=6, column=0, sticky=tk.NW, padx=40, pady=12)
        self.diagnostic_text = scrolledtext.ScrolledText(form, font=("Arial", font_size), 
                                                         width=40, height=4,
                                                         bg=THEME['bg_light'], 
                                                         fg=THEME['text_white'],
                                                         insertbackground=THEME['text_white'])
        self.diagnostic_text.grid(row=6, column=1, pady=12, sticky=tk.W)
        
        # Observations
        tk.Label(form, text="Observations :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=7, column=0, sticky=tk.NW, padx=40, pady=12)
        self.observations_text = scrolledtext.ScrolledText(form, font=("Arial", font_size), 
                                                           width=40, height=4,
                                                           bg=THEME['bg_light'], 
                                                           fg=THEME['text_white'],
                                                           insertbackground=THEME['text_white'])
        self.observations_text.grid(row=7, column=1, pady=12, sticky=tk.W)
        
        # Boutons
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=8, column=0, columnspan=2, pady=30)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=20)
    
    def save(self):
        if not self.patient_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un patient !")
            return
        
        if not self.medecin_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un médecin !")
            return
        
        try:
            patient_id = self.patients_dict[self.patient_var.get()]
            medecin_id = self.medecins_dict[self.medecin_var.get()]
            
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''INSERT INTO Consultation 
                        (Numero_Consultation, Date_Consultation, Heure_Consultation, 
                         ID_Patient, ID_Medecin, Motif, Diagnostic, Observations)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (self.numero, self.date_entry.get(), self.heure_entry.get(),
                      patient_id, medecin_id,
                      self.motif_text.get("1.0", tk.END).strip() or None,
                      self.diagnostic_text.get("1.0", tk.END).strip() or None,
                      self.observations_text.get("1.0", tk.END).strip() or None))
            conn.commit()
            conn.close()
            
            log_activity("Ajout", "Consultations", f"{self.numero}")
            messagebox.showinfo("Succès", f"Consultation {self.numero} enregistrée !")
            self.consultations_module.load_consultations()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

class ViewConsultationWindow:
    def __init__(self, parent, consultation_id):
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute('''SELECT c.*, 
                    p.Nom || ' ' || p.Prenom as patient_nom,
                    m.Nom || ' ' || m.Prenom as medecin_nom
                    FROM Consultation c
                    LEFT JOIN Patient p ON c.ID_Patient = p.ID_Patient
                    LEFT JOIN Medecin m ON c.ID_Medecin = m.ID_Medecin
                    WHERE c.ID_Consultation=?''', (consultation_id,))
        cons = c.fetchone()
        conn.close()
        
        if not cons:
            messagebox.showerror("Erreur", "Consultation introuvable !")
            return
        
        window = tk.Toplevel(parent)
        window.title("Détails Consultation")
        window.geometry("700x700")
        window.configure(bg=THEME['bg_dark'])
        window.grab_set()
        
        tk.Label(window, text="👁️ DÉTAILS CONSULTATION", 
                font=("Arial", 20, "bold"),
                bg=THEME['info'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        frame = tk.Frame(window, bg=THEME['bg_dark'])
        frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        font_size = CONFIG['font_size']
        
        # Affichage lecture seule
        info = [
            ("N° Consultation", cons[1]),
            ("Date", cons[2]),
            ("Heure", cons[3]),
            ("Patient", cons[9]),
            ("Médecin", cons[10]),
            ("Motif", cons[6]),
            ("Diagnostic", cons[7]),
            ("Observations", cons[8])
        ]
        
        row = 0
        for label, value in info:
            tk.Label(frame, text=f"{label} :", bg=THEME['bg_dark'],
                    fg=THEME['text_white'], 
                    font=("Arial", font_size, "bold")).grid(row=row, column=0, sticky=tk.NW, pady=10)
            tk.Label(frame, text=value or "—", bg=THEME['bg_dark'],
                    fg=THEME['text_yellow'], 
                    font=("Arial", font_size), wraplength=400, justify=tk.LEFT).grid(row=row, column=1, sticky=tk.W, pady=10)
            row += 1
        
        tk.Button(window, text="❌ Fermer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=20, height=2, command=window.destroy,
                 cursor="hand2").pack(pady=20)

class EditConsultationWindow:
    def __init__(self, parent, consultations_module, consultation_id):
        self.consultations_module = consultations_module
        self.consultation_id = consultation_id
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Consultation WHERE ID_Consultation=?", (consultation_id,))
        self.consultation = c.fetchone()
        conn.close()

        # Vérification permissions - Réceptionniste ne peut pas modifier diagnostic
        self.peut_modifier_diagnostic = (Session.role in ["super_admin", "admin", "medecin"])

        if not self.consultation:
            messagebox.showerror("Erreur", "Consultation introuvable !")
            return
        
        self.window = tk.Toplevel(parent)
        self.window.title("Modifier Consultation")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        tk.Label(self.window, text="✏️ MODIFIER CONSULTATION", 
                font=("Arial", 20, "bold"),
                bg=THEME['warning'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        canvas = tk.Canvas(self.window, bg=THEME['bg_dark'])
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=THEME['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        form = scrollable_frame
        font_size = CONFIG['font_size']
        
        tk.Label(form, text="N° Consultation :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, padx=40, pady=12)
        tk.Label(form, text=self.consultation[1] or "", bg=THEME['bg_dark'],
                fg=THEME['text_yellow'], 
                font=("Arial", font_size, "bold")).grid(row=0, column=1, sticky=tk.W, pady=12)
        
        tk.Label(form, text="Date (AAAA-MM-JJ) :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, padx=40, pady=12)
        self.date_entry = tk.Entry(form, font=("Arial", font_size), width=40,
                                    bg=THEME['bg_light'], 
                                    fg=THEME['text_white'],
                                    insertbackground=THEME['text_white'])
        self.date_entry.grid(row=1, column=1, pady=12, sticky=tk.W)
        if self.consultation[2]:
            self.date_entry.insert(0, self.consultation[2])
        
        tk.Label(form, text="Heure (HH:MM) :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, padx=40, pady=12)
        self.heure_entry = tk.Entry(form, font=("Arial", font_size), width=40,
                                     bg=THEME['bg_light'], 
                                     fg=THEME['text_white'],
                                     insertbackground=THEME['text_white'])
        self.heure_entry.grid(row=2, column=1, pady=12, sticky=tk.W)
        if self.consultation[3]:
            self.heure_entry.insert(0, self.consultation[3])
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT ID_Patient, Nom, Prenom FROM Patient WHERE Actif=1 ORDER BY Nom")
        patients = c.fetchall()
        
        self.patients_dict = {f"{p[1]} {p[2]}": p[0] for p in patients}
        patient_names = list(self.patients_dict.keys())
        
        tk.Label(form, text="Patient :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, padx=40, pady=12)
        
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_var,
                                         values=patient_names,
                                         font=("Arial", font_size),
                                         width=38, state="readonly")
        self.patient_combo.grid(row=3, column=1, pady=12, sticky=tk.W)
        
        c.execute("SELECT Nom, Prenom FROM Patient WHERE ID_Patient=?", (self.consultation[4],))
        current_patient = c.fetchone()
        if current_patient:
            self.patient_combo.set(f"{current_patient[0]} {current_patient[1]}")
        
        c.execute("SELECT ID_Medecin, Nom, Prenom FROM Medecin WHERE Actif=1 ORDER BY Nom")
        medecins = c.fetchall()
        
        self.medecins_dict = {f"Dr. {m[1]} {m[2]}": m[0] for m in medecins}
        medecin_names = list(self.medecins_dict.keys())
        
        tk.Label(form, text="Médecin :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, padx=40, pady=12)
        
        self.medecin_var = tk.StringVar()
        self.medecin_combo = ttk.Combobox(form, textvariable=self.medecin_var,
                                         values=medecin_names,
                                         font=("Arial", font_size),
                                         width=38, state="readonly")
        self.medecin_combo.grid(row=4, column=1, pady=12, sticky=tk.W)
        
        c.execute("SELECT Nom, Prenom FROM Medecin WHERE ID_Medecin=?", (self.consultation[5],))
        current_medecin = c.fetchone()
        conn.close()
        if current_medecin:
            self.medecin_combo.set(f"Dr. {current_medecin[0]} {current_medecin[1]}")
        
        tk.Label(form, text="Motif :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=5, column=0, sticky=tk.NW, padx=40, pady=12)
        self.motif_text = scrolledtext.ScrolledText(form, font=("Arial", font_size), 
                                                    width=40, height=4,
                                                    bg=THEME['bg_light'], 
                                                    fg=THEME['text_white'],
                                                    insertbackground=THEME['text_white'])
        self.motif_text.grid(row=5, column=1, pady=12, sticky=tk.W)
        if self.consultation[6]:
            self.motif_text.insert("1.0", self.consultation[6])
        
        tk.Label(form, text="Diagnostic :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=6, column=0, sticky=tk.NW, padx=40, pady=12)
        self.diagnostic_text = scrolledtext.ScrolledText(form, font=("Arial", font_size), 
                                                         width=40, height=4,
                                                         bg=THEME['bg_light'], 
                                                         fg=THEME['text_white'],
                                                         insertbackground=THEME['text_white'])
        self.diagnostic_text.grid(row=6, column=1, pady=12, sticky=tk.W)
        if not self.peut_modifier_diagnostic:
            self.diagnostic_text.config(state='disabled', bg='#555555')
            self.observations_text.config(state='disabled', bg='#555555')
        if self.consultation[7]:
            self.diagnostic_text.insert("1.0", self.consultation[7])
        
        tk.Label(form, text="Observations :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=7, column=0, sticky=tk.NW, padx=40, pady=12)
        self.observations_text = scrolledtext.ScrolledText(form, font=("Arial", font_size), 
                                                           width=40, height=4,
                                                           bg=THEME['bg_light'], 
                                                           fg=THEME['text_white'],
                                                           insertbackground=THEME['text_white'])
        self.observations_text.grid(row=7, column=1, pady=12, sticky=tk.W)
        if self.consultation[8]:
            self.observations_text.insert("1.0", self.consultation[8])
        
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=8, column=0, columnspan=2, pady=30)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=20)
    
    def save(self):
        if not self.patient_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un patient !")
            return
        
        if not self.medecin_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un médecin !")
            return
        
        try:
            patient_id = self.patients_dict[self.patient_var.get()]
            medecin_id = self.medecins_dict[self.medecin_var.get()]
            
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''UPDATE Consultation 
                        SET Date_Consultation=?, Heure_Consultation=?, 
                            ID_Patient=?, ID_Medecin=?, Motif=?, Diagnostic=?, Observations=?
                        WHERE ID_Consultation=?''',
                     (self.date_entry.get(), self.heure_entry.get(),
                      patient_id, medecin_id,
                      self.motif_text.get("1.0", tk.END).strip() or None,
                      self.diagnostic_text.get("1.0", tk.END).strip() or None,
                      self.observations_text.get("1.0", tk.END).strip() or None,
                      self.consultation_id))
            conn.commit()
            conn.close()
            
            log_activity("Modification", "Consultations", f"{self.consultation[1]}")
            messagebox.showinfo("Succès", "Consultation modifiée !")
            self.consultations_module.load_consultations()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXAMENS
# ═══════════════════════════════════════════════════════════════════════════════

class ExamensModule:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        self.root = tk.Toplevel()
        self.root.title("CMEV - Gestion des Examens")
        self.root.state('zoomed')
        self.root.configure(bg=THEME['bg_dark'])
        
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_menu)
        
        # Header
        header = tk.Frame(self.root, bg=THEME['warning'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🔬 GESTION DES EXAMENS", 
                font=("Arial", 22, "bold"),
                bg=THEME['warning'], fg=THEME['text_white'], 
                pady=20).pack()
        
        # Toolbar
        toolbar = tk.Frame(self.root, bg=THEME['bg_dark'])
        toolbar.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Button(toolbar, text="➕ Prescrire Examen", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=20, height=2, command=self.add_examen,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="✏️ Modifier", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['warning'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.edit_examen,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="📊 Entrer résultats", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], 
                 width=18, height=2, command=self.enter_results,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🗑️ Supprimer", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.delete_examen,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔄 Actualiser", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.load_examens,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔢 Réorganiser ID", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['purple'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.reorganize_and_reload,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🏠 Retour Menu", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['bg_medium'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.back_to_menu,
                 cursor="hand2").pack(side=tk.RIGHT, padx=5)
        
        # Tableau
        tree_frame = tk.Frame(self.root, bg=THEME['bg_dark'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Exam.Treeview",
                       background=THEME['tree_bg'],
                       foreground=THEME['tree_fg'],
                       fieldbackground=THEME['tree_bg'],
                       font=('Arial', CONFIG['font_size']))
        style.configure("Exam.Treeview.Heading",
                       background='#d68910',
                       foreground='white',
                       font=('Arial', CONFIG['font_size'], 'bold'))
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Patient", "Type", "Medecin", "Date_prescription", "Date_examen", "Statut", "Prix"),
            show="headings",
            yscrollcommand=vsb.set,
            style="Exam.Treeview",
            height=30
        )
        
        vsb.config(command=self.tree.yview)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Patient", text="Patient")
        self.tree.heading("Type", text="Type examen")
        self.tree.heading("Medecin", text="Médecin prescripteur")
        self.tree.heading("Date_prescription", text="Prescrit le")
        self.tree.heading("Date_examen", text="Effectué le")
        self.tree.heading("Statut", text="Statut")
        self.tree.heading("Prix", text="Prix (FC)")
        
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Patient", width=180)
        self.tree.column("Type", width=200)
        self.tree.column("Medecin", width=180)
        self.tree.column("Date_prescription", width=100, anchor=tk.CENTER)
        self.tree.column("Date_examen", width=100, anchor=tk.CENTER)
        self.tree.column("Statut", width=100, anchor=tk.CENTER)
        self.tree.column("Prix", width=100, anchor=tk.E)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_examens()
    
    def reorganize_and_reload(self):
        self.reorganize_ids()
        self.load_examens()
        messagebox.showinfo("Succès", "ID réorganisés !")
    
    def reorganize_ids(self):
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            
            c.execute("SELECT * FROM Examen ORDER BY ID_Examen")
            examens = c.fetchall()
            
            if not examens:
                return
            
            c.execute("DELETE FROM Examen")
            c.execute("DELETE FROM sqlite_sequence WHERE name='Examen'")
            
            for ex in examens:
                c.execute('''INSERT INTO Examen 
                            (ID_Patient, ID_Type_examen, Medecin_prescripteur, 
                             Date_prescription, Date_examen, Statut, Resultats)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (ex[1], ex[2], ex[3], ex[4], ex[5], ex[6], ex[7]))
            
            conn.commit()
            conn.close()
            
            log_activity("Réorganisation", "Examens", "ID réorganisés")
            
        except Exception as e:
            print(f"Erreur réorganisation ID: {e}")
    
    def load_examens(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute('''SELECT e.*, 
                    p.Nom || ' ' || p.Prenom as patient_nom,
                    t.Nom_examen, t.Prix,
                    m.Nom || ' ' || m.Prenom as medecin_nom
                    FROM Examen e
                    LEFT JOIN Patient p ON e.ID_Patient = p.ID_Patient
                    LEFT JOIN Type_Examen t ON e.ID_Type_examen = t.ID_Type_examen
                    LEFT JOIN Medecin m ON e.Medecin_prescripteur = m.ID_Medecin
                    ORDER BY e.Date_prescription DESC''')
        examens = c.fetchall()
        conn.close()
        
        for ex in examens:
            statut = ex[6] or "Prescrit"
            prix_fmt = f"{int(ex[10]):,}" if ex[10] else "0"
            
            self.tree.insert("", tk.END, values=(
                ex[0],
                ex[8] or "Patient supprimé",
                ex[9] or "Type supprimé",
                ex[11] or "Médecin supprimé",
                ex[4] or "",
                ex[5] or "",
                statut,
                prix_fmt
            ))
    
    def add_examen(self):
        AddExamenWindow(self.root, self)
    
    def edit_examen(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un examen !")
            return
        
        item = self.tree.item(selected[0])
        examen_id = item['values'][0]
        messagebox.showinfo("Modification", f"Modification examen ID {examen_id}")
    
    def enter_results(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un examen !")
            return
        
        item = self.tree.item(selected[0])
        examen_id = item['values'][0]
        ResultsWindow(self.root, self, examen_id)
    
    def delete_examen(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un examen !")
            return
        
        item = self.tree.item(selected[0])
        examen_id = item['values'][0]
        patient = item['values'][1]
        type_examen = item['values'][2]
        
        def executer_suppression():
            if messagebox.askyesno("Confirmation", 
                                  f"Supprimer l'examen {type_examen} du patient {patient} ?"):
                conn = sqlite3.connect('cmev.db')
                c = conn.cursor()
                c.execute("DELETE FROM Examen WHERE ID_Examen=?", (examen_id,))
                conn.commit()
                conn.close()
                
                log_activity("Suppression", "Examens", f"{type_examen} - {patient}")
                self.reorganize_ids()
                messagebox.showinfo("Succès", "Examen supprimé !\nID réorganisés automatiquement.")
                self.load_examens()
        
        if Session.role not in ["admin", "super_admin"]:
            DemandeCodeWindow(self.root, executer_suppression)
        else:
            executer_suppression()
    
    def back_to_menu(self):
        self.root.destroy()

class AddExamenWindow:
    def __init__(self, parent, examens_module):
        self.examens_module = examens_module
        
        self.window = tk.Toplevel(parent)
        self.window.title("Prescrire Examen")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        tk.Label(self.window, text="➕ PRESCRIRE UN EXAMEN", 
                font=("Arial", 20, "bold"),
                bg=THEME['success'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        font_size = CONFIG['font_size']
        
        # Patient
        tk.Label(form, text="Patient :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT ID_Patient, Nom, Prenom FROM Patient WHERE Actif=1 ORDER BY Nom")
        patients = c.fetchall()
        
        self.patients_dict = {f"{p[1]} {p[2]}": p[0] for p in patients}
        patient_names = list(self.patients_dict.keys())
        
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_var,
                                         values=patient_names,
                                         font=("Arial", font_size),
                                         width=38, state="readonly")
        self.patient_combo.grid(row=0, column=1, pady=12)
        if patient_names:
            self.patient_combo.set(patient_names[0])
        
        # Type examen
        tk.Label(form, text="Type d'examen :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        
        c.execute("SELECT ID_Type_examen, Nom_examen, Prix FROM Type_Examen ORDER BY Nom_examen")
        types_examens = c.fetchall()
        conn.close()
        
        self.types_dict = {f"{t[1]} ({int(t[2]):,} FC)": t[0] for t in types_examens}
        type_names = list(self.types_dict.keys())
        
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(form, textvariable=self.type_var,
                                      values=type_names,
                                      font=("Arial", font_size),
                                      width=38, state="readonly")
        self.type_combo.grid(row=1, column=1, pady=12)
        if type_names:
            self.type_combo.set(type_names[0])
        
        # Médecin
        tk.Label(form, text="Médecin prescripteur :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT ID_Medecin, Nom, Prenom FROM Medecin WHERE Actif=1 ORDER BY Nom")
        medecins = c.fetchall()
        conn.close()
        
        self.medecins_dict = {f"Dr. {m[1]} {m[2]}": m[0] for m in medecins}
        medecin_names = list(self.medecins_dict.keys())
        
        self.medecin_var = tk.StringVar()
        self.medecin_combo = ttk.Combobox(form, textvariable=self.medecin_var,
                                         values=medecin_names,
                                         font=("Arial", font_size),
                                         width=38, state="readonly")
        self.medecin_combo.grid(row=2, column=1, pady=12)
        if medecin_names:
            self.medecin_combo.set(medecin_names[0])
        
        # Date
        tk.Label(form, text="Date prescription :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        self.date_prescription = tk.Entry(form, font=("Arial", font_size), width=40,
                                         bg=THEME['bg_light'], 
                                         fg=THEME['text_white'],
                                         insertbackground=THEME['text_white'])
        self.date_prescription.grid(row=3, column=1, pady=12)
        self.date_prescription.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Statut
        tk.Label(form, text="Statut :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        
        statuts = ["Prescrit", "En cours", "Terminé"]
        self.statut_var = tk.StringVar()
        self.statut_combo = ttk.Combobox(form, textvariable=self.statut_var,
                                        values=statuts,
                                        font=("Arial", font_size),
                                        width=38, state="readonly")
        self.statut_combo.grid(row=4, column=1, pady=12)
        self.statut_combo.set("Prescrit")
        
        # Boutons
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=5, column=0, columnspan=2, pady=35)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        if not self.patient_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un patient !")
            return
        
        if not self.type_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un type d'examen !")
            return
        
        try:
            patient_id = self.patients_dict[self.patient_var.get()]
            type_id = self.types_dict[self.type_var.get()]
            medecin_id = self.medecins_dict[self.medecin_var.get()] if self.medecin_var.get() else None
            
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''INSERT INTO Examen 
                        (ID_Patient, ID_Type_examen, Medecin_prescripteur, 
                         Date_prescription, Statut)
                        VALUES (?, ?, ?, ?, ?)''',
                     (patient_id, type_id, medecin_id,
                      self.date_prescription.get(), self.statut_var.get()))
            conn.commit()
            conn.close()
            
            log_activity("Prescription", "Examens", f"{self.type_var.get()} - {self.patient_var.get()}")
            messagebox.showinfo("Succès", "Examen prescrit !")
            self.examens_module.load_examens()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

class ResultsWindow:
    def __init__(self, parent, examens_module, examen_id):
        self.examens_module = examens_module
        self.examen_id = examen_id
        
        self.window = tk.Toplevel(parent)
        self.window.title("Résultats Examen")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        tk.Label(self.window, text="📊 ENTRER RÉSULTATS", 
                font=("Arial", 20, "bold"),
                bg=THEME['info'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        font_size = CONFIG['font_size']
        
        # Date examen
        tk.Label(form, text="Date examen :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.date_examen = tk.Entry(form, font=("Arial", font_size), width=40,
                                    bg=THEME['bg_light'], 
                                    fg=THEME['text_white'],
                                    insertbackground=THEME['text_white'])
        self.date_examen.grid(row=0, column=1, pady=12)
        self.date_examen.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Statut
        tk.Label(form, text="Statut :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        
        self.statut_var = tk.StringVar()
        statut_combo = ttk.Combobox(form, textvariable=self.statut_var,
                                   values=["Prescrit", "En cours", "Terminé"],
                                   font=("Arial", font_size),
                                   width=38, state="readonly")
        statut_combo.grid(row=1, column=1, pady=12)
        statut_combo.set("Terminé")
        
        # Résultats
        tk.Label(form, text="Résultats :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.NW, pady=12)
        self.resultats_text = scrolledtext.ScrolledText(form, font=("Arial", font_size), 
                                                        width=40, height=15,
                                                        bg=THEME['bg_light'], 
                                                        fg=THEME['text_white'],
                                                        insertbackground=THEME['text_white'])
        self.resultats_text.grid(row=2, column=1, pady=12)
        
        # Boutons
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=3, column=0, columnspan=2, pady=30)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''UPDATE Examen 
                        SET Date_examen=?, Statut=?, Resultats=?
                        WHERE ID_Examen=?''',
                     (self.date_examen.get(),
                      self.statut_var.get(),
                      self.resultats_text.get("1.0", tk.END).strip() or None,
                      self.examen_id))
            conn.commit()
            conn.close()
            
            log_activity("Résultats", "Examens", f"Examen ID {self.examen_id}")
            messagebox.showinfo("Succès", "Résultats enregistrés !")
            self.examens_module.load_examens()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE PHARMACIE
# ═══════════════════════════════════════════════════════════════════════════════

class PharmacieModule:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        self.root = tk.Toplevel()
        self.root.title("CMEV - Gestion de la Pharmacie")
        self.root.state('zoomed')
        self.root.configure(bg=THEME['bg_dark'])
        
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_menu)
        
        header = tk.Frame(self.root, bg=THEME['success'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="💊 GESTION DE LA PHARMACIE", 
                font=("Arial", 22, "bold"),
                bg=THEME['success'], fg=THEME['text_white'], 
                pady=20).pack()
        
        toolbar = tk.Frame(self.root, bg=THEME['bg_dark'])
        toolbar.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Button(toolbar, text="➕ Nouveau Médicament", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=22, height=2, command=self.add_medicament,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="✏️ Modifier", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['warning'], fg=THEME['text_white'], 
                 width=14, height=2, command=self.edit_medicament,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Bouton Entrée stock - visible seulement pour admin/super_admin
        if Session.role in ["admin", "super_admin"]:
            tk.Button(toolbar, text="📦 Entrée stock", 
                     font=("Arial", CONFIG['font_size'], "bold"),
                     bg=THEME['info'], fg=THEME['text_white'], 
                     width=14, height=2, command=self.entree_stock,
                     cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="📤 Sortie stock", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['warning'], fg=THEME['text_white'], 
                 width=14, height=2, command=self.sortie_stock,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🗑️ Supprimer", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=14, height=2, command=self.delete_medicament,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔄 Actualiser", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], 
                 width=14, height=2, command=self.load_medicaments,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔢 Réorganiser ID", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['purple'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.reorganize_and_reload,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🏠 Retour Menu", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['bg_medium'], fg=THEME['text_white'], 
                 width=14, height=2, command=self.back_to_menu,
                 cursor="hand2").pack(side=tk.RIGHT, padx=5)

        # Statistiques Pharmacie
        stats_frame = tk.Frame(self.root, bg=THEME['bg_dark'])
        stats_frame.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        # Frame pour les compteurs
        counters_frame = tk.Frame(stats_frame, bg=THEME['bg_dark'])
        counters_frame.pack(fill=tk.X)
        
        # Total Stock (valeur)
        total_stock_frame = tk.Frame(counters_frame, bg=THEME['info'], relief=tk.RAISED, bd=3)
        total_stock_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(total_stock_frame, text="💰 Valeur Stock Total",
                font=("Arial", CONFIG['font_size']+1, "bold"),
                bg=THEME['info'], fg=THEME['text_white'],
                pady=8).pack()
        
        self.label_total_stock = tk.Label(total_stock_frame, text="0 FCFA",
                                          font=("Arial", CONFIG['font_size']+6, "bold"),
                                          bg=THEME['info'], fg=THEME['text_white'],
                                          pady=15)
        self.label_total_stock.pack()
        
        # Produits en alerte
        alert_frame = tk.Frame(counters_frame, bg=THEME['warning'], relief=tk.RAISED, bd=3)
        alert_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(alert_frame, text="⚠️ Produits en Alerte",
                font=("Arial", CONFIG['font_size']+1, "bold"),
                bg=THEME['warning'], fg=THEME['text_white'],
                pady=8).pack()
        
        self.label_alertes = tk.Label(alert_frame, text="0",
                                      font=("Arial", CONFIG['font_size']+6, "bold"),
                                      bg=THEME['warning'], fg=THEME['text_white'],
                                      pady=15)
        self.label_alertes.pack()
        
        # Produits périmés bientôt
        peremption_frame = tk.Frame(counters_frame, bg=THEME['danger'], relief=tk.RAISED, bd=3)
        peremption_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(peremption_frame, text="🚫 Ruptures de stock",
                font=("Arial", CONFIG['font_size']+1, "bold"),
                bg=THEME['danger'], fg=THEME['text_white'],
                pady=8).pack()
        
        self.label_peremption = tk.Label(peremption_frame, text="0",
                                         font=("Arial", CONFIG['font_size']+6, "bold"),
                                         bg=THEME['danger'], fg=THEME['text_white'],
                                         pady=15)
        self.label_peremption.pack()
        
        tree_frame = tk.Frame(self.root, bg=THEME['bg_dark'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Pharma.Treeview",
                       background=THEME['tree_bg'],
                       foreground=THEME['tree_fg'],
                       fieldbackground=THEME['tree_bg'],
                       font=('Arial', CONFIG['font_size']))
        style.configure("Pharma.Treeview.Heading",
                       background='#229954',
                       foreground='white',
                       font=('Arial', CONFIG['font_size'], 'bold'))
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Nom", "Categorie", "Stock", "Seuil", "Prix", "Statut"),
            show="headings",
            yscrollcommand=vsb.set,
            style="Pharma.Treeview",
            height=30
        )
        
        vsb.config(command=self.tree.yview)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nom", text="Nom médicament")
        self.tree.heading("Categorie", text="Catégorie")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Seuil", text="Seuil alerte")
        self.tree.heading("Prix", text="Prix unitaire (FC)")
        self.tree.heading("Statut", text="Statut")
        
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Nom", width=250)
        self.tree.column("Categorie", width=180)
        self.tree.column("Stock", width=100, anchor=tk.CENTER)
        self.tree.column("Seuil", width=100, anchor=tk.CENTER)
        self.tree.column("Prix", width=150, anchor=tk.E)
        self.tree.column("Statut", width=150, anchor=tk.CENTER)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_medicaments()
    
    def reorganize_and_reload(self):
        self.reorganize_ids()
        self.load_medicaments()
        messagebox.showinfo("Succès", "ID réorganisés !")
    
    def reorganize_ids(self):
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute("SELECT * FROM Medicament ORDER BY ID_Medicament")
            medicaments = c.fetchall()
            if not medicaments:
                return
            c.execute("DELETE FROM Medicament")
            c.execute("DELETE FROM sqlite_sequence WHERE name='Medicament'")
            for med in medicaments:
                c.execute('''INSERT INTO Medicament 
                            (Nom_medicament, ID_Categorie, Quantite_stock, Seuil_alerte, Prix_unitaire)
                            VALUES (?, ?, ?, ?, ?)''',
                         (med[1], med[2], med[3], med[4], med[5]))
            conn.commit()
            conn.close()
            log_activity("Réorganisation", "Pharmacie", "ID réorganisés")
        except Exception as e:
            print(f"Erreur réorganisation ID: {e}")
    
    def load_medicaments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute('''SELECT m.*, c.Nom_categorie
                    FROM Medicament m
                    LEFT JOIN Categorie_Medicament c ON m.ID_Categorie = c.ID_Categorie
                    ORDER BY m.Nom_medicament''')
        medicaments = c.fetchall()
        conn.close()
        for med in medicaments:
            stock = med[3] or 0
            seuil = med[4] or 10
            if stock == 0:
                statut = "⚠️ RUPTURE"
            elif stock <= seuil:
                statut = "⚡ STOCK BAS"
            else:
                statut = "✅ DISPONIBLE"
            prix_fmt = f"{int(med[5]):,}" if med[5] else "0"
            self.tree.insert("", tk.END, values=(
                med[0], med[1], med[6] or "Sans catégorie",
                stock, seuil, prix_fmt, statut
            ))
        # Calculer statistiques
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        
        # Total valeur stock
        c.execute("SELECT SUM(Quantite_stock * Prix_unitaire) FROM Medicament")
        total_stock = c.fetchone()[0] or 0
        self.label_total_stock.config(text=f"{int(total_stock):,} FCFA".replace(',', ' '))
        
        # Produits en alerte
        c.execute("SELECT COUNT(*) FROM Medicament WHERE Quantite_stock <= Seuil_alerte")
        nb_alertes = c.fetchone()[0]
        self.label_alertes.config(text=str(nb_alertes))
        
        # Produits en rupture de stock
        c.execute("SELECT COUNT(*) FROM Medicament WHERE Quantite_stock = 0")
        nb_ruptures = c.fetchone()[0]
        self.label_peremption.config(text=str(nb_ruptures))
        
        conn.close()
    
    def add_medicament(self):
        AddMedicamentWindow(self.root, self)
    
    def edit_medicament(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un médicament !")
            return
        
        item = self.tree.item(selected[0])
        medicament_id = item['values'][0]
        
        # Vérifier si code requis
        if Session.role not in ["admin", "super_admin"]:
            DemandeCodeWindow(self.root, lambda: EditMedicamentWindow(self.root, self, medicament_id))
        else:
            EditMedicamentWindow(self.root, self, medicament_id)
    
    def entree_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un médicament !")
            return
        item = self.tree.item(selected[0])
        MouvementStockWindow(self.root, self, item['values'][0], "Entrée")
    
    def sortie_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un médicament !")
            return
        item = self.tree.item(selected[0])
        MouvementStockWindow(self.root, self, item['values'][0], "Sortie")
    
    def delete_medicament(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un médicament !")
            return
        
        item = self.tree.item(selected[0])
        nom = item['values'][1]
        medicament_id = item['values'][0]
        
        def executer_suppression():
            if messagebox.askyesno("Confirmation", f"Supprimer {nom} ?"):
                conn = sqlite3.connect('cmev.db')
                c = conn.cursor()
                c.execute("DELETE FROM Medicament WHERE ID_Medicament=?", (medicament_id,))
                conn.commit()
                conn.close()
                
                log_activity("Suppression", "Pharmacie", nom)
                self.reorganize_ids()
                messagebox.showinfo("Succès", "Médicament supprimé !\nID réorganisés automatiquement.")
                self.load_medicaments()
        
        if Session.role not in ["admin", "super_admin"]:
            DemandeCodeWindow(self.root, executer_suppression)
        else:
            executer_suppression()
    
    def back_to_menu(self):
        self.root.destroy()

class AddMedicamentWindow:
    def __init__(self, parent, pharmacie_module):
        self.pharmacie_module = pharmacie_module
        self.window = tk.Toplevel(parent)
        self.window.title("Nouveau Médicament")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        tk.Label(self.window, text="➕ NOUVEAU MÉDICAMENT", 
                font=("Arial", 20, "bold"),
                bg=THEME['success'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        font_size = CONFIG['font_size']
        tk.Label(form, text="Nom médicament :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.nom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                  bg=THEME['bg_light'], fg=THEME['text_white'],
                                  insertbackground=THEME['text_white'])
        self.nom_entry.grid(row=0, column=1, pady=12)
        self.nom_entry.focus()
        tk.Label(form, text="Catégorie :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT ID_Categorie, Nom_categorie FROM Categorie_Medicament ORDER BY Nom_categorie")
        categories = c.fetchall()
        conn.close()
        self.categories_dict = {cat[1]: cat[0] for cat in categories}
        cat_names = list(self.categories_dict.keys())
        self.categorie_var = tk.StringVar()
        self.categorie_combo = ttk.Combobox(form, textvariable=self.categorie_var,
                                           values=cat_names, font=("Arial", font_size),
                                           width=33, state="readonly")
        self.categorie_combo.grid(row=1, column=1, pady=12)
        if cat_names:
            self.categorie_combo.set(cat_names[0])
        tk.Label(form, text="Stock initial :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        self.stock_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                    bg=THEME['bg_light'], fg=THEME['text_white'],
                                    insertbackground=THEME['text_white'])
        self.stock_entry.grid(row=2, column=1, pady=12)
        self.stock_entry.insert(0, "0")
        tk.Label(form, text="Seuil alerte :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        self.seuil_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                    bg=THEME['bg_light'], fg=THEME['text_white'],
                                    insertbackground=THEME['text_white'])
        self.seuil_entry.grid(row=3, column=1, pady=12)
        self.seuil_entry.insert(0, "10")
        tk.Label(form, text="Prix unitaire (FC) :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        self.prix_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                   bg=THEME['bg_light'], fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'])
        self.prix_entry.grid(row=4, column=1, pady=12)
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=5, column=0, columnspan=2, pady=35)
        tk.Button(btn_frame, text="💾 Enregistrer", font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], width=16, height=2,
                 command=self.save, cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="❌ Annuler", font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], width=16, height=2,
                 command=self.window.destroy, cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        nom = self.nom_entry.get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Nom obligatoire !")
            return
        try:
            stock = int(self.stock_entry.get() or 0)
            seuil = int(self.seuil_entry.get() or 10)
            prix = float(self.prix_entry.get() or 0)
            categorie_id = self.categories_dict[self.categorie_var.get()] if self.categorie_var.get() else None
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''INSERT INTO Medicament 
                        (Nom_medicament, ID_Categorie, Quantite_stock, Seuil_alerte, Prix_unitaire)
                        VALUES (?, ?, ?, ?, ?)''', (nom, categorie_id, stock, seuil, prix))
            conn.commit()
            conn.close()
            log_activity("Ajout", "Pharmacie", nom)
            messagebox.showinfo("Succès", f"{nom} ajouté !")
            self.pharmacie_module.load_medicaments()
            self.window.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Stock, seuil et prix doivent être numériques !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")
        
class EditMedicamentWindow:
    def __init__(self, parent, pharmacie_module, medicament_id):
        self.pharmacie_module = pharmacie_module
        self.medicament_id = medicament_id
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Medicament WHERE ID_Medicament=?", (medicament_id,))
        self.medicament = c.fetchone()
        conn.close()

        # Vérification permissions - Pharmacien ne peut pas modifier prix
        self.peut_modifier_prix = (Session.role in ["super_admin", "admin"])

        if not self.medicament:
            messagebox.showerror("Erreur", "Médicament introuvable !")
            return
        
        self.window = tk.Toplevel(parent)
        self.window.title("Modifier Médicament")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        
        tk.Label(self.window, text="✏️ MODIFIER MÉDICAMENT", 
                font=("Arial", 20, "bold"),
                bg=THEME['warning'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        font_size = CONFIG['font_size']
        
        tk.Label(form, text="Nom médicament :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.nom_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                  bg=THEME['bg_light'], 
                                  fg=THEME['text_white'],
                                  insertbackground=THEME['text_white'])
        self.nom_entry.grid(row=0, column=1, pady=12)
        self.nom_entry.insert(0, self.medicament[1])
        
        tk.Label(form, text="Catégorie :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT ID_Categorie, Nom_categorie FROM Categorie_Medicament ORDER BY Nom_categorie")
        categories = c.fetchall()
        conn.close()
        
        self.categories_dict = {cat[1]: cat[0] for cat in categories}
        cat_names = list(self.categories_dict.keys())
        
        self.categorie_var = tk.StringVar()
        self.categorie_combo = ttk.Combobox(form, textvariable=self.categorie_var,
                                           values=cat_names,
                                           font=("Arial", font_size),
                                           width=33, state="readonly")
        self.categorie_combo.grid(row=1, column=1, pady=12)
        
        if self.medicament[2]:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute("SELECT Nom_categorie FROM Categorie_Medicament WHERE ID_Categorie=?", (self.medicament[2],))
            cat = c.fetchone()
            conn.close()
            if cat:
                self.categorie_combo.set(cat[0])
        
        tk.Label(form, text="Stock actuel :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        tk.Label(form, text=str(self.medicament[3] or 0), bg=THEME['bg_dark'],
                fg=THEME['text_yellow'], 
                font=("Arial", font_size, "bold")).grid(row=2, column=1, sticky=tk.W, pady=12)
        
        tk.Label(form, text="Seuil alerte :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        self.seuil_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                    bg=THEME['bg_light'], 
                                    fg=THEME['text_white'],
                                    insertbackground=THEME['text_white'])
        self.seuil_entry.grid(row=3, column=1, pady=12)
        self.seuil_entry.insert(0, str(self.medicament[4] or 10))
        
        tk.Label(form, text="Prix unitaire (FC) :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        self.prix_entry = tk.Entry(form, font=("Arial", font_size), width=35,
                                   bg=THEME['bg_light'], 
                                   fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'])
        self.prix_entry.grid(row=4, column=1, pady=12)
        if not self.peut_modifier_prix:
            self.prix_entry.config(state='disabled')
        if self.medicament[5]:
            self.prix_entry.insert(0, str(int(self.medicament[5])))
        
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=5, column=0, columnspan=2, pady=35)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        nom = self.nom_entry.get().strip()
        
        if not nom:
            messagebox.showerror("Erreur", "Nom obligatoire !")
            return
        
        try:
            seuil = int(self.seuil_entry.get() or 10)
            prix = float(self.prix_entry.get() or 0)
            
            categorie_id = self.categories_dict[self.categorie_var.get()] if self.categorie_var.get() else None
            
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''UPDATE Medicament 
                        SET Nom_medicament=?, ID_Categorie=?, Seuil_alerte=?, Prix_unitaire=?
                        WHERE ID_Medicament=?''',
                     (nom, categorie_id, seuil, prix, self.medicament_id))
            conn.commit()
            conn.close()
            
            log_activity("Modification", "Pharmacie", nom)
            messagebox.showinfo("Succès", f"{nom} modifié !")
            self.pharmacie_module.load_medicaments()
            self.window.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Seuil et prix doivent être numériques !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

class MouvementStockWindow:
    def __init__(self, parent, pharmacie_module, medicament_id, type_mouvement):
        self.pharmacie_module = pharmacie_module
        self.medicament_id = medicament_id
        self.type_mouvement = type_mouvement
        self.window = tk.Toplevel(parent)
        self.window.title(f"{type_mouvement} de stock")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        couleur = THEME['info'] if type_mouvement == "Entrée" else THEME['warning']
        tk.Label(self.window, text=f"📦 {type_mouvement.upper()} DE STOCK", 
                font=("Arial", 20, "bold"), bg=couleur,
                fg=THEME['text_white'], pady=20).pack(fill=tk.X)
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        font_size = CONFIG['font_size']
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT Nom_medicament, Quantite_stock FROM Medicament WHERE ID_Medicament=?", (medicament_id,))
        med = c.fetchone()
        conn.close()
        if not med:
            messagebox.showerror("Erreur", "Médicament introuvable !")
            self.window.destroy()
            return
        tk.Label(form, text="Médicament :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        tk.Label(form, text=med[0], bg=THEME['bg_dark'],
                fg=THEME['text_yellow'], font=("Arial", font_size, "bold")).grid(row=0, column=1, sticky=tk.W, pady=12)
        tk.Label(form, text="Stock actuel :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        tk.Label(form, text=str(med[1] or 0), bg=THEME['bg_dark'],
                fg=THEME['text_yellow'], font=("Arial", font_size, "bold")).grid(row=1, column=1, sticky=tk.W, pady=12)
        tk.Label(form, text="Quantité :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        self.quantite_entry = tk.Entry(form, font=("Arial", font_size), width=30,
                                       bg=THEME['bg_light'], fg=THEME['text_white'],
                                       insertbackground=THEME['text_white'])
        self.quantite_entry.grid(row=2, column=1, pady=12)
        self.quantite_entry.focus()
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=3, column=0, columnspan=2, pady=30)
        tk.Button(btn_frame, text=f"💾 Enregistrer {type_mouvement}", 
                 font=("Arial", font_size+1, "bold"), bg=couleur,
                 fg=THEME['text_white'], width=20, height=2,
                 command=self.save, cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="❌ Annuler", font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], width=16, height=2,
                 command=self.window.destroy, cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        try:
            quantite = int(self.quantite_entry.get())
            if quantite <= 0:
                messagebox.showerror("Erreur", "Quantité doit être positive !")
                return
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute("SELECT Quantite_stock FROM Medicament WHERE ID_Medicament=?", (self.medicament_id,))
            stock_actuel = c.fetchone()[0] or 0
            if self.type_mouvement == "Entrée":
                nouveau_stock = stock_actuel + quantite
            else:
                if quantite > stock_actuel:
                    messagebox.showerror("Erreur", f"Stock insuffisant !\nStock actuel : {stock_actuel}")
                    conn.close()
                    return
                nouveau_stock = stock_actuel - quantite
            c.execute("UPDATE Medicament SET Quantite_stock=? WHERE ID_Medicament=?",
                     (nouveau_stock, self.medicament_id))
            conn.commit()
            conn.close()
            log_activity(self.type_mouvement, "Pharmacie", f"Quantité: {quantite}")
            messagebox.showinfo("Succès", f"{self.type_mouvement} enregistrée !\nNouveau stock : {nouveau_stock}")
            self.pharmacie_module.load_medicaments()
            self.window.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Quantité invalide !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE FACTURATION
# ═══════════════════════════════════════════════════════════════════════════════

class FacturationModule:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.root = tk.Toplevel()
        self.root.title("CMEV - Gestion de la Facturation")
        self.root.state('zoomed')
        self.root.configure(bg=THEME['bg_dark'])
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_menu)
        header = tk.Frame(self.root, bg=THEME['danger'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="💰 GESTION DE LA FACTURATION", 
                font=("Arial", 22, "bold"), bg=THEME['danger'],
                fg=THEME['text_white'], pady=20).pack()
        toolbar = tk.Frame(self.root, bg=THEME['bg_dark'])
        toolbar.pack(fill=tk.X, pady=20, padx=30)
        tk.Button(toolbar, text="➕ Nouvelle Facture", font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], width=20, height=2,
                 command=self.add_facture, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="👁️ Voir détails", font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], width=16, height=2,
                 command=self.view_facture, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="💳 Enregistrer paiement", font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], width=20, height=2,
                 command=self.add_paiement, cursor="hand2").pack(side=tk.LEFT, padx=5)
        # Bouton Supprimer - visible seulement pour admin/super_admin
        if Session.role in ["admin", "super_admin"]:
            tk.Button(toolbar, text="🗑️ Supprimer", font=("Arial", CONFIG['font_size'], "bold"),
                     bg=THEME['danger'], fg=THEME['text_white'], width=14, height=2,
                     command=self.delete_facture, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🔄 Actualiser", font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], width=14, height=2,
                 command=self.load_factures, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🔢 Réorganiser ID", font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['purple'], fg=THEME['text_white'], width=16, height=2,
                 command=self.reorganize_and_reload, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="🏠 Retour Menu", font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['bg_medium'], fg=THEME['text_white'], width=14, height=2,
                 command=self.back_to_menu, cursor="hand2").pack(side=tk.RIGHT, padx=5)
        tree_frame = tk.Frame(self.root, bg=THEME['bg_dark'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Fact.Treeview", background=THEME['tree_bg'],
                       foreground=THEME['tree_fg'], fieldbackground=THEME['tree_bg'],
                       font=('Arial', CONFIG['font_size']))
        style.configure("Fact.Treeview.Heading", background='#c0392b',
                       foreground='white', font=('Arial', CONFIG['font_size'], 'bold'))
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        self.tree = ttk.Treeview(tree_frame,
            columns=("ID", "Numero", "Date", "Patient", "Total", "Paye", "Reste", "Statut"),
            show="headings", yscrollcommand=vsb.set, style="Fact.Treeview", height=30)
        vsb.config(command=self.tree.yview)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Numero", text="N° Facture")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Patient", text="Patient")
        self.tree.heading("Total", text="Montant total (FC)")
        self.tree.heading("Paye", text="Montant payé (FC)")
        self.tree.heading("Reste", text="Reste à payer (FC)")
        self.tree.heading("Statut", text="Statut")
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Numero", width=180)
        self.tree.column("Date", width=100, anchor=tk.CENTER)
        self.tree.column("Patient", width=200)
        self.tree.column("Total", width=150, anchor=tk.E)
        self.tree.column("Paye", width=150, anchor=tk.E)
        self.tree.column("Reste", width=150, anchor=tk.E)
        self.tree.column("Statut", width=150, anchor=tk.CENTER)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.load_factures()
    
    def reorganize_and_reload(self):
        self.reorganize_ids()
        self.load_factures()
        messagebox.showinfo("Succès", "ID réorganisés !")
    
    def reorganize_ids(self):
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute("SELECT * FROM Facture ORDER BY ID_Facture")
            factures = c.fetchall()
            if not factures:
                return
            c.execute("DELETE FROM Facture")
            c.execute("DELETE FROM sqlite_sequence WHERE name='Facture'")
            for fact in factures:
                c.execute('''INSERT INTO Facture 
                            (Numero_facture, Date_facture, Montant_total, Montant_paye, ID_Patient, ID_Consultation)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (fact[1], fact[2], fact[3], fact[4], fact[5], fact[6]))
            conn.commit()
            conn.close()
            log_activity("Réorganisation", "Facturation", "ID réorganisés")
        except Exception as e:
            print(f"Erreur réorganisation ID: {e}")
    
    def load_factures(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute('''SELECT f.*, p.Nom || ' ' || p.Prenom as patient_nom
                    FROM Facture f
                    LEFT JOIN Patient p ON f.ID_Patient = p.ID_Patient
                    ORDER BY f.Date_facture DESC''')
        factures = c.fetchall()
        conn.close()
        for fact in factures:
            total = fact[3] or 0
            paye = fact[4] or 0
            reste = total - paye
            if paye == 0:
                statut = "❌ IMPAYÉE"
            elif reste > 0:
                statut = "⚠️ PARTIELLE"
            else:
                statut = "✅ PAYÉE"
            self.tree.insert("", tk.END, values=(
                fact[0], fact[1] or "", fact[2] or "", fact[7] or "Patient supprimé",
                f"{int(total):,}", f"{int(paye):,}", f"{int(reste):,}", statut
            ))
    
    def add_facture(self):
        AddFactureWindow(self.root, self)
    
    def view_facture(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une facture !")
            return
        item = self.tree.item(selected[0])
        ViewFactureWindow(self.root, item['values'][0])
    
    def add_paiement(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une facture !")
            return
        item = self.tree.item(selected[0])
        AddPaiementWindow(self.root, self, item['values'][0])
    
    def delete_facture(self):
        # Double sécurité (normalement bouton déjà caché)
        if Session.role not in ["admin", "super_admin"]:
            messagebox.showerror("Accès refusé", "Vous n'avez pas les permissions pour supprimer des factures.")
            return
        
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une facture !")
            return
        
        item = self.tree.item(selected[0])
        numero = item['values'][1]
        facture_id = item['values'][0]
        
        if messagebox.askyesno("Confirmation", f"Supprimer la facture {numero} ?"):
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute("DELETE FROM Facture WHERE ID_Facture=?", (facture_id,))
            conn.commit()
            conn.close()
            
            log_activity("Suppression", "Facturation", numero)
            self.reorganize_ids()
            messagebox.showinfo("Succès", "Facture supprimée !\nID réorganisés automatiquement.")
            self.load_factures()
    
    def back_to_menu(self):
        self.root.destroy()

class AddFactureWindow:
    def __init__(self, parent, facturation_module):
        self.facturation_module = facturation_module
        self.window = tk.Toplevel(parent)
        self.window.title("Nouvelle Facture")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        tk.Label(self.window, text="➕ NOUVELLE FACTURE", 
                font=("Arial", 20, "bold"), bg=THEME['success'],
                fg=THEME['text_white'], pady=20).pack(fill=tk.X)
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        font_size = CONFIG['font_size']
        tk.Label(form, text="N° Facture :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.numero = generer_numero_facture()
        tk.Label(form, text=self.numero, bg=THEME['bg_dark'],
                fg=THEME['text_yellow'], font=("Arial", font_size, "bold")).grid(row=0, column=1, sticky=tk.W, pady=12)
        tk.Label(form, text="Date :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        self.date_entry = tk.Entry(form, font=("Arial", font_size), width=40,
                                   bg=THEME['bg_light'], fg=THEME['text_white'],
                                   insertbackground=THEME['text_white'])
        self.date_entry.grid(row=1, column=1, pady=12)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        tk.Label(form, text="Patient :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT ID_Patient, Nom, Prenom FROM Patient WHERE Actif=1 ORDER BY Nom")
        patients = c.fetchall()
        conn.close()
        self.patients_dict = {f"{p[1]} {p[2]}": p[0] for p in patients}
        patient_names = list(self.patients_dict.keys())
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(form, textvariable=self.patient_var,
                                         values=patient_names, font=("Arial", font_size),
                                         width=38, state="readonly")
        self.patient_combo.grid(row=2, column=1, pady=12)
        if patient_names:
            self.patient_combo.set(patient_names[0])
        tk.Label(form, text="Montant total (FC) :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        self.montant_entry = tk.Entry(form, font=("Arial", font_size), width=40,
                                      bg=THEME['bg_light'], fg=THEME['text_white'],
                                      insertbackground=THEME['text_white'])
        self.montant_entry.grid(row=3, column=1, pady=12)
        self.montant_entry.insert(0, "0")
        tk.Label(form, text="Paiement initial (FC) :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        self.paiement_entry = tk.Entry(form, font=("Arial", font_size), width=40,
                                       bg=THEME['bg_light'], fg=THEME['text_white'],
                                       insertbackground=THEME['text_white'])
        self.paiement_entry.grid(row=4, column=1, pady=12)
        self.paiement_entry.insert(0, "0")
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=5, column=0, columnspan=2, pady=30)
        tk.Button(btn_frame, text="💾 Créer Facture", font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], width=18, height=2,
                 command=self.save, cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="❌ Annuler", font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], width=16, height=2,
                 command=self.window.destroy, cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        if not self.patient_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un patient !")
            return
        try:
            montant_total = float(self.montant_entry.get() or 0)
            montant_paye = float(self.paiement_entry.get() or 0)
            if montant_total <= 0:
                messagebox.showerror("Erreur", "Montant total doit être positif !")
                return
            if montant_paye > montant_total:
                messagebox.showerror("Erreur", "Paiement > montant total !")
                return
            patient_id = self.patients_dict[self.patient_var.get()]
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''INSERT INTO Facture 
                        (Numero_facture, Date_facture, Montant_total, Montant_paye, ID_Patient)
                        VALUES (?, ?, ?, ?, ?)''',
                     (self.numero, self.date_entry.get(), montant_total, montant_paye, patient_id))
            conn.commit()
            conn.close()
            log_activity("Création", "Facturation", self.numero)
            messagebox.showinfo("Succès", f"Facture {self.numero} créée !")
            self.facturation_module.load_factures()
            self.window.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Montants invalides !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

class ViewFactureWindow:
    def __init__(self, parent, facture_id):
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute('''SELECT f.*, p.Nom || ' ' || p.Prenom as patient_nom
                    FROM Facture f
                    LEFT JOIN Patient p ON f.ID_Patient = p.ID_Patient
                    WHERE f.ID_Facture=?''', (facture_id,))
        facture = c.fetchone()
        conn.close()
        
        if not facture:
            messagebox.showerror("Erreur", "Facture introuvable !")
            return
        
        window = tk.Toplevel(parent)
        window.title("Détails Facture")
        window.geometry("700x600")
        window.configure(bg=THEME['bg_dark'])
        window.grab_set()
        
        tk.Label(window, text="👁️ DÉTAILS FACTURE", 
                font=("Arial", 20, "bold"),
                bg=THEME['info'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        frame = tk.Frame(window, bg=THEME['bg_dark'])
        frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        font_size = CONFIG['font_size']
        
        total = facture[3] or 0
        paye = facture[4] or 0
        reste = total - paye
        
        if paye == 0:
            statut = "❌ IMPAYÉE"
            statut_color = THEME['danger']
        elif reste > 0:
            statut = "⚠️ PARTIELLE"
            statut_color = THEME['warning']
        else:
            statut = "✅ PAYÉE"
            statut_color = THEME['success']
        
        info = [
            ("N° Facture", facture[1]),
            ("Date", facture[2]),
            ("Patient", facture[7]),
            ("Montant total", f"{int(total):,} FC"),
            ("Montant payé", f"{int(paye):,} FC"),
            ("Reste à payer", f"{int(reste):,} FC"),
        ]
        
        row = 0
        for label, value in info:
            tk.Label(frame, text=f"{label} :", bg=THEME['bg_dark'],
                    fg=THEME['text_white'], 
                    font=("Arial", font_size, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
            tk.Label(frame, text=value or "—", bg=THEME['bg_dark'],
                    fg=THEME['text_yellow'], 
                    font=("Arial", font_size)).grid(row=row, column=1, sticky=tk.W, pady=10, padx=20)
            row += 1
        
        tk.Label(frame, text="Statut :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size, "bold")).grid(row=row, column=0, sticky=tk.W, pady=10)
        tk.Label(frame, text=statut, bg=THEME['bg_dark'],
                fg=statut_color, 
                font=("Arial", font_size+2, "bold")).grid(row=row, column=1, sticky=tk.W, pady=10, padx=20)
        
        tk.Button(window, text="❌ Fermer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=20, height=2, command=window.destroy,
                 cursor="hand2").pack(pady=20)

class AddPaiementWindow:
    def __init__(self, parent, facturation_module, facture_id):
        self.facturation_module = facturation_module
        self.facture_id = facture_id
        self.window = tk.Toplevel(parent)
        self.window.title("Nouveau Paiement")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.grab_set()
        tk.Label(self.window, text="💳 ENREGISTRER PAIEMENT", 
                font=("Arial", 20, "bold"), bg=THEME['success'],
                fg=THEME['text_white'], pady=20).pack(fill=tk.X)
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        font_size = CONFIG['font_size']
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT Numero_facture, Montant_total, Montant_paye FROM Facture WHERE ID_Facture=?", (facture_id,))
        fact = c.fetchone()
        conn.close()
        if not fact:
            messagebox.showerror("Erreur", "Facture introuvable !")
            self.window.destroy()
            return
        total = fact[1] or 0
        paye = fact[2] or 0
        reste = total - paye
        if reste <= 0:
            messagebox.showinfo("Info", "Cette facture est déjà entièrement payée !")
            self.window.destroy()
            return
        tk.Label(form, text="N° Facture :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        tk.Label(form, text=fact[0], bg=THEME['bg_dark'],
                fg=THEME['text_yellow'], font=("Arial", font_size, "bold")).grid(row=0, column=1, sticky=tk.W, pady=12)
        tk.Label(form, text="Montant total :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        tk.Label(form, text=f"{int(total):,} FC", bg=THEME['bg_dark'],
                fg=THEME['text_yellow'], font=("Arial", font_size, "bold")).grid(row=1, column=1, sticky=tk.W, pady=12)
        tk.Label(form, text="Déjà payé :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        tk.Label(form, text=f"{int(paye):,} FC", bg=THEME['bg_dark'],
                fg=THEME['success'], font=("Arial", font_size, "bold")).grid(row=2, column=1, sticky=tk.W, pady=12)
        tk.Label(form, text="Reste à payer :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        tk.Label(form, text=f"{int(reste):,} FC", bg=THEME['bg_dark'],
                fg=THEME['danger'], font=("Arial", font_size, "bold")).grid(row=3, column=1, sticky=tk.W, pady=12)
        tk.Label(form, text="Montant à payer (FC) :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        self.montant_paiement = tk.Entry(form, font=("Arial", font_size), width=30,
                                         bg=THEME['bg_light'], fg=THEME['text_white'],
                                         insertbackground=THEME['text_white'])
        self.montant_paiement.grid(row=4, column=1, pady=12)
        self.montant_paiement.insert(0, str(int(reste)))
        self.montant_paiement.focus()
        tk.Label(form, text="Mode paiement :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=5, column=0, sticky=tk.W, pady=12)
        modes = ["Espèces", "Mobile Money", "Carte bancaire", "Chèque", "Virement"]
        self.mode_var = tk.StringVar()
        mode_combo = ttk.Combobox(form, textvariable=self.mode_var, values=modes,
                                  font=("Arial", font_size), width=28, state="readonly")
        mode_combo.grid(row=5, column=1, pady=12)
        mode_combo.set("Espèces")
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=6, column=0, columnspan=2, pady=30)
        tk.Button(btn_frame, text="💳 Enregistrer Paiement", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], width=22, height=2,
                 command=lambda: self.save(total, paye, reste), cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="❌ Annuler", font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], width=16, height=2,
                 command=self.window.destroy, cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self, total, paye_actuel, reste):
        try:
            montant = float(self.montant_paiement.get())
            if montant <= 0:
                messagebox.showerror("Erreur", "Montant doit être positif !")
                return
            if montant > reste:
                messagebox.showerror("Erreur", f"Montant > reste à payer ({int(reste):,} FC) !")
                return
            nouveau_paye = paye_actuel + montant
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute("UPDATE Facture SET Montant_paye=? WHERE ID_Facture=?",
                     (nouveau_paye, self.facture_id))
            conn.commit()
            conn.close()
            nouveau_reste = total - nouveau_paye
            log_activity("Paiement", "Facturation", f"Montant: {int(montant):,} FC")
            if nouveau_reste <= 0:
                messagebox.showinfo("Succès", f"Paiement enregistré !\n\n✅ FACTURE ENTIÈREMENT PAYÉE")
            else:
                messagebox.showinfo("Succès", f"Paiement enregistré !\n\nReste à payer : {int(nouveau_reste):,} FC")
            self.facturation_module.load_factures()
            self.window.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Montant invalide !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE STATISTIQUES
# ═══════════════════════════════════════════════════════════════════════════════

class StatistiquesModule:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        self.root = tk.Toplevel()
        self.root.title("CMEV - Statistiques")
        self.root.state('zoomed')
        self.root.configure(bg=THEME['bg_dark'])
        
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_menu)
        
        header = tk.Frame(self.root, bg=THEME['purple'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 STATISTIQUES", 
                font=("Arial", 22, "bold"),
                bg=THEME['purple'], fg=THEME['text_white'], 
                pady=20).pack()
        
        toolbar = tk.Frame(self.root, bg=THEME['bg_dark'])
        toolbar.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Button(toolbar, text="🔄 Actualiser", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], 
                 width=18, height=2, command=self.load_stats,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🏠 Retour Menu", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['bg_medium'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.back_to_menu,
                 cursor="hand2").pack(side=tk.RIGHT, padx=5)
        
        main_frame = tk.Frame(self.root, bg=THEME['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        canvas = tk.Canvas(main_frame, bg=THEME['bg_dark'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        
        self.scrollable = tk.Frame(canvas, bg=THEME['bg_dark'])
        
        self.scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Activer scroll molette
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_enter(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _on_leave(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)
        
        self.load_stats()
    
    def load_stats(self):
        for widget in self.scrollable.winfo_children():
            widget.destroy()
        
        self.create_section("📊 COMPTEURS PRINCIPAUX")
        compteurs_frame = tk.Frame(self.scrollable, bg=THEME['bg_dark'])
        compteurs_frame.pack(fill=tk.X, pady=10)
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM Patient WHERE Actif=1")
        nb_patients = c.fetchone()[0]
        self.create_counter(compteurs_frame, "👥 Patients", nb_patients, THEME['info'], 0)
        
        c.execute("SELECT COUNT(*) FROM Medecin WHERE Actif=1")
        nb_medecins = c.fetchone()[0]
        self.create_counter(compteurs_frame, "👨‍⚕️ Médecins", nb_medecins, THEME['purple'], 1)
        
        c.execute("SELECT COUNT(*) FROM Employe WHERE Actif=1")
        nb_employes = c.fetchone()[0]
        self.create_counter(compteurs_frame, "👷 Employés", nb_employes, THEME['orange'], 2)
        
        c.execute("SELECT COUNT(*) FROM Consultation")
        nb_consultations = c.fetchone()[0]
        self.create_counter(compteurs_frame, "📋 Consultations", nb_consultations, THEME['teal'], 3)
        
        self.create_section("💰 STATISTIQUES FINANCIÈRES")
        finance_frame = tk.Frame(self.scrollable, bg=THEME['bg_dark'])
        finance_frame.pack(fill=tk.X, pady=10)

        
        c.execute("SELECT SUM(Montant_paye) FROM Facture")
        total_recettes = c.fetchone()[0] or 0
        self.create_counter(finance_frame, "💵 Total recettes", f"{int(total_recettes):,} FC", THEME['success'], 0)
        
        c.execute("SELECT COUNT(*) FROM Facture WHERE Montant_paye = 0")
        nb_impayees = c.fetchone()[0]
        self.create_counter(finance_frame, "❌ Factures impayées", nb_impayees, THEME['danger'], 1)
        
        c.execute("SELECT SUM(Montant_total - Montant_paye) FROM Facture WHERE Montant_paye < Montant_total")
        montant_impaye = c.fetchone()[0] or 0
        self.create_counter(finance_frame, "⚠️ Montant impayé", f"{int(montant_impaye):,} FC", THEME['warning'], 2)
        
        self.create_section("💊 ALERTES PHARMACIE")
        
        c.execute("SELECT Nom_medicament FROM Medicament WHERE Quantite_stock = 0")
        ruptures = c.fetchall()
        
        if ruptures:
            rupture_frame = tk.Frame(self.scrollable, bg=THEME['danger'], relief=tk.RAISED, bd=2)
            rupture_frame.pack(fill=tk.X, pady=5, padx=20)
            
            tk.Label(rupture_frame, text=f"⚠️ {len(ruptures)} médicament(s) en RUPTURE DE STOCK",
                    font=("Arial", CONFIG['font_size']+1, "bold"),
                    bg=THEME['danger'], fg=THEME['text_white'],
                    pady=10).pack()
            
            for med in ruptures[:5]:
                tk.Label(rupture_frame, text=f"  • {med[0]}",
                        font=("Arial", CONFIG['font_size']),
                        bg=THEME['danger'], fg=THEME['text_white'],
                        anchor=tk.W).pack(fill=tk.X, padx=20)
        
        c.execute("SELECT Nom_medicament, Quantite_stock FROM Medicament WHERE Quantite_stock > 0 AND Quantite_stock <= Seuil_alerte")
        stock_bas = c.fetchall()
        
        if stock_bas:
            bas_frame = tk.Frame(self.scrollable, bg=THEME['warning'], relief=tk.RAISED, bd=2)
            bas_frame.pack(fill=tk.X, pady=5, padx=20)
            
            tk.Label(bas_frame, text=f"⚡ {len(stock_bas)} médicament(s) en STOCK BAS",
                    font=("Arial", CONFIG['font_size']+1, "bold"),
                    bg=THEME['warning'], fg=THEME['text_white'],
                    pady=10).pack()
            
            for med in stock_bas[:5]:
                tk.Label(bas_frame, text=f"  • {med[0]} (stock: {med[1]})",
                        font=("Arial", CONFIG['font_size']),
                        bg=THEME['warning'], fg=THEME['text_white'],
                        anchor=tk.W).pack(fill=tk.X, padx=20)
        
        self.create_section("🔬 TOP 5 EXAMENS PRESCRITS")
        
        c.execute('''SELECT t.Nom_examen, COUNT(*) as nb
                    FROM Examen e
                    JOIN Type_Examen t ON e.ID_Type_examen = t.ID_Type_examen
                    GROUP BY e.ID_Type_examen
                    ORDER BY nb DESC
                    LIMIT 5''')
        top_examens = c.fetchall()
        
        if top_examens:
            examens_frame = tk.Frame(self.scrollable, bg=THEME['bg_medium'])
            examens_frame.pack(fill=tk.X, pady=10, padx=20)
            
            max_val = top_examens[0][1] if top_examens else 1
            
            for i, (nom, nb) in enumerate(top_examens):
                row_frame = tk.Frame(examens_frame, bg=THEME['bg_medium'])
                row_frame.pack(fill=tk.X, pady=5, padx=10)
                
                tk.Label(row_frame, text=f"{i+1}. {nom}",
                        font=("Arial", CONFIG['font_size']),
                        bg=THEME['bg_medium'], fg=THEME['text_white'],
                        width=30, anchor=tk.W).pack(side=tk.LEFT)
                
                bar_width = int((nb / max_val) * 300)
                canvas_bar = tk.Canvas(row_frame, width=300, height=20, 
                                      bg=THEME['bg_dark'], highlightthickness=0)
                canvas_bar.pack(side=tk.LEFT, padx=10)
                canvas_bar.create_rectangle(0, 0, bar_width, 20, fill=THEME['info'], outline="")
                
                tk.Label(row_frame, text=f"{nb}",
                        font=("Arial", CONFIG['font_size'], "bold"),
                        bg=THEME['bg_medium'], fg=THEME['text_yellow']).pack(side=tk.LEFT)
        
        conn.close()
    
    def create_section(self, titre):
        tk.Label(self.scrollable, text=titre,
                font=("Arial", CONFIG['font_size']+3, "bold"),
                bg=THEME['bg_dark'], fg=THEME['text_yellow'],
                pady=15).pack(anchor=tk.W, padx=20)
    
    def create_counter(self, parent, label, value, color, col):
        frame = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=3)
        frame.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        
        tk.Label(frame, text=label,
                font=("Arial", CONFIG['font_size']+1, "bold"),
                bg=color, fg=THEME['text_white'],
                pady=10).pack()
        
        tk.Label(frame, text=str(value),
                font=("Arial", CONFIG['font_size']+8, "bold"),
                bg=color, fg=THEME['text_white'],
                pady=20).pack()
        
        parent.grid_columnconfigure(col, weight=1)
    
    def back_to_menu(self):
        self.root.destroy()

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE ADMINISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

class AdministrationModule:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        self.root = tk.Toplevel()
        self.root.title("CMEV - Administration")
        self.root.state('zoomed')
        self.root.configure(bg=THEME['bg_dark'])
        
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_menu)
        
        header = tk.Frame(self.root, bg=THEME['bg_light'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="⚙️ ADMINISTRATION", 
                font=("Arial", 22, "bold"),
                bg=THEME['bg_light'], fg=THEME['text_white'], 
                pady=20).pack()
        
        # Container pour limiter la hauteur du notebook
        notebook_container = tk.Frame(self.root, bg=THEME['bg_dark'])
        notebook_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        notebook = ttk.Notebook(notebook_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.tab_users = tk.Frame(notebook, bg=THEME['bg_dark'])
        notebook.add(self.tab_users, text="👥 Utilisateurs")
        self.create_users_tab()
        
        self.tab_logs = tk.Frame(notebook, bg=THEME['bg_dark'])
        notebook.add(self.tab_logs, text="📋 Journal d'activité")
        self.create_logs_tab()
        
        self.tab_settings = tk.Frame(notebook, bg=THEME['bg_dark'])
        notebook.add(self.tab_settings, text="⚙️ Paramètres")
        self.create_settings_tab()
        
        # Toolbar en haut avec bouton Retour Menu à droite
        toolbar = tk.Frame(self.root, bg=THEME['bg_dark'], height=70)
        toolbar.pack(fill=tk.X, after=self.root.winfo_children()[0])
        toolbar.pack_propagate(False)
        
        tk.Button(toolbar, text="🏠 Retour Menu", 
                 font=("Arial", CONFIG['font_size']+1, "bold"),
                 bg=THEME['bg_medium'], fg=THEME['text_white'], 
                 width=18, height=2, command=self.back_to_menu,
                 cursor="hand2").pack(side=tk.RIGHT, padx=30, pady=15)
    
    def create_users_tab(self):
        toolbar = tk.Frame(self.tab_users, bg=THEME['bg_dark'])
        toolbar.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Button(toolbar, text="➕ Nouvel Utilisateur", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=20, height=2, command=self.add_user,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="✏️ Modifier", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['warning'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.edit_user,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🗑️ Supprimer", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.delete_user,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔄 Actualiser", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.load_users,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🔢 Réorganiser ID", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['purple'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.reorganize_and_reload,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tree_frame = tk.Frame(self.tab_users, bg=THEME['bg_dark'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Admin.Treeview",
                       background=THEME['tree_bg'],
                       foreground=THEME['tree_fg'],
                       fieldbackground=THEME['tree_bg'],
                       font=('Arial', CONFIG['font_size']))
        style.configure("Admin.Treeview.Heading",
                       background='#5d6d7e',
                       foreground='white',
                       font=('Arial', CONFIG['font_size'], 'bold'))
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        
        self.tree_users = ttk.Treeview(
            tree_frame,
            columns=("ID", "Utilisateur", "Nom_complet", "Role", "Statut"),
            show="headings",
            yscrollcommand=vsb.set,
            style="Admin.Treeview",
            height=25
        )
        
        vsb.config(command=self.tree_users.yview)
        
        self.tree_users.heading("ID", text="ID")
        self.tree_users.heading("Utilisateur", text="Nom d'utilisateur")
        self.tree_users.heading("Nom_complet", text="Nom complet")
        self.tree_users.heading("Role", text="Rôle")
        self.tree_users.heading("Statut", text="Statut")
        
        self.tree_users.column("ID", width=60, anchor=tk.CENTER)
        self.tree_users.column("Utilisateur", width=200)
        self.tree_users.column("Nom_complet", width=250)
        self.tree_users.column("Role", width=200)
        self.tree_users.column("Statut", width=150, anchor=tk.CENTER)
        
        self.tree_users.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_users()
    
    def create_logs_tab(self):
        toolbar = tk.Frame(self.tab_logs, bg=THEME['bg_dark'])
        toolbar.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Button(toolbar, text="🔄 Actualiser", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['info'], fg=THEME['text_white'], 
                 width=18, height=2, command=self.load_logs,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text="🗑️ Vider les logs", 
                 font=("Arial", CONFIG['font_size'], "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=18, height=2, command=self.clear_logs,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tree_frame = tk.Frame(self.tab_logs, bg=THEME['bg_dark'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        
        self.tree_logs = ttk.Treeview(
            tree_frame,
            columns=("ID", "Date", "Utilisateur", "Action", "Module", "Details"),
            show="headings",
            yscrollcommand=vsb.set,
            style="Admin.Treeview",
            height=25
        )
        
        vsb.config(command=self.tree_logs.yview)
        
        self.tree_logs.heading("ID", text="ID")
        self.tree_logs.heading("Date", text="Date/Heure")
        self.tree_logs.heading("Utilisateur", text="Utilisateur")
        self.tree_logs.heading("Action", text="Action")
        self.tree_logs.heading("Module", text="Module")
        self.tree_logs.heading("Details", text="Détails")
        
        self.tree_logs.column("ID", width=60, anchor=tk.CENTER)
        self.tree_logs.column("Date", width=150)
        self.tree_logs.column("Utilisateur", width=150)
        self.tree_logs.column("Action", width=150)
        self.tree_logs.column("Module", width=150)
        self.tree_logs.column("Details", width=300)
        
        self.tree_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_logs()
    
    def create_settings_tab(self):
        # Créer canvas avec scrollbar
        canvas = tk.Canvas(self.tab_settings, bg=THEME['bg_dark'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.tab_settings, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=THEME['bg_dark'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=20)
        
        # Activer scroll seulement quand souris dans canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_enter(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _on_leave(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _on_enter)
        canvas.bind("<Leave>", _on_leave)
        
        # Contenu scrollable
        frame = tk.Frame(scrollable_frame, bg=THEME['bg_dark'])
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        tk.Label(frame, text="💾 SAUVEGARDE BASE DE DONNÉES",
                font=("Arial", CONFIG['font_size']+2, "bold"),
                bg=THEME['bg_dark'], fg=THEME['text_yellow'],
                pady=20).pack(anchor=tk.W)
        
        tk.Button(frame, text="📦 Créer une sauvegarde", 
                 font=("Arial", CONFIG['font_size']+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=30, height=3, command=self.backup_database,
                 cursor="hand2").pack(pady=10)
        
        tk.Label(frame, text="🔐 CODE DE VALIDATION",
                font=("Arial", CONFIG['font_size']+2, "bold"),
                bg=THEME['bg_dark'], fg=THEME['text_yellow'],
                pady=30).pack(anchor=tk.W)
        
        code_actuel = get_code_actuel()
        tk.Label(frame, text=f"Code actuel : {code_actuel}",
                font=("Arial", CONFIG['font_size']+3, "bold"),
                bg=THEME['bg_dark'], fg=THEME['success']).pack(pady=10)
        
        tk.Button(frame, text="🔄 Générer un nouveau code", 
                 font=("Arial", CONFIG['font_size']+1, "bold"),
                 bg=THEME['warning'], fg=THEME['text_white'], 
                 width=30, height=3, command=self.actualiser_code_manuel,
                 cursor="hand2").pack(pady=10)
        
        tk.Label(frame, text="⚠️ Le code change automatiquement chaque jour à minuit.\n"
                           "Utilisez ce bouton seulement si nécessaire.",
                bg=THEME['bg_dark'], fg=THEME['text_white'],
                font=("Arial", CONFIG['font_size']-1)).pack(pady=5)
        
        tk.Label(frame, text="📊 INFORMATIONS BASE DE DONNÉES",
                font=("Arial", CONFIG['font_size']+2, "bold"),
                bg=THEME['bg_dark'], fg=THEME['text_yellow'],
                pady=30).pack(anchor=tk.W)
        
        if os.path.exists('cmev.db'):
            size = os.path.getsize('cmev.db') / 1024
            tk.Label(frame, text=f"Taille : {size:.2f} Ko",
                    font=("Arial", CONFIG['font_size']),
                    bg=THEME['bg_dark'], fg=THEME['text_white']).pack(anchor=tk.W, pady=5)
            
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            
            tables = ['Patient', 'Medecin', 'Employe', 'Consultation', 'Examen', 
                     'Medicament', 'Facture', 'Utilisateur', 'Code_Validation']
            
            for table in tables:
                try:
                    c.execute(f"SELECT COUNT(*) FROM {table}")
                    count = c.fetchone()[0]
                    tk.Label(frame, text=f"{table} : {count} enregistrement(s)",
                            font=("Arial", CONFIG['font_size']),
                            bg=THEME['bg_dark'], fg=THEME['text_white']).pack(anchor=tk.W, pady=3)
                except:
                    pass
            
            conn.close()
    
    def reorganize_and_reload(self):
        self.reorganize_ids()
        self.load_users()
        messagebox.showinfo("Succès", "ID réorganisés !")
    
    def reorganize_ids(self):
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute("SELECT * FROM Utilisateur ORDER BY ID_Utilisateur")
            users = c.fetchall()
            if not users:
                return
            c.execute("DELETE FROM Utilisateur")
            c.execute("DELETE FROM sqlite_sequence WHERE name='Utilisateur'")
            for user in users:
                c.execute('''INSERT INTO Utilisateur 
                            (Nom_utilisateur, Mot_de_passe, Role, Nom_complet, Actif)
                            VALUES (?, ?, ?, ?, ?)''',
                         (user[1], user[2], user[3], user[4], user[5]))
            conn.commit()
            conn.close()
            log_activity("Réorganisation", "Administration", "ID utilisateurs réorganisés")
        except Exception as e:
            print(f"Erreur réorganisation ID: {e}")
    
    def load_users(self):
        for item in self.tree_users.get_children():
            self.tree_users.delete(item)
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Utilisateur ORDER BY ID_Utilisateur")
        users = c.fetchall()
        conn.close()
        for user in users:
            statut = "✅ Actif" if user[5] else "❌ Inactif"
            self.tree_users.insert("", tk.END, values=(
                user[0], user[1], user[4] or "", user[3], statut
            ))
    
    def load_logs(self):
        for item in self.tree_logs.get_children():
            self.tree_logs.delete(item)
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute('''SELECT l.*, u.Nom_utilisateur 
                    FROM Journal_Activite l
                    LEFT JOIN Utilisateur u ON l.ID_Utilisateur = u.ID_Utilisateur
                    ORDER BY l.Date_heure DESC LIMIT 500''')
        logs = c.fetchall()
        conn.close()
        for log in logs:
            self.tree_logs.insert("", tk.END, values=(
                log[0], log[5], log[6] or "Système", log[1], log[2], log[3] or ""
            ))
    
    def add_user(self):
        AddUserWindow(self.root, self)
    
    def edit_user(self):
        selected = self.tree_users.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un utilisateur !")
            return
        item = self.tree_users.item(selected[0])
        EditUserWindow(self.root, self, item['values'][0])
    
    def delete_user(self):
        selected = self.tree_users.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un utilisateur !")
            return
        
        item = self.tree_users.item(selected[0])
        username = item['values'][1]
        user_id = item['values'][0]
        
        # Protection TEST et ROOT
        if username in ["TEST", "ROOT"]:
            messagebox.showerror("Erreur", "Impossible de supprimer les comptes système TEST et ROOT !")
            return
        
        # Admin ne peut pas supprimer les admin/super_admin
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT Role FROM Utilisateur WHERE ID_Utilisateur=?", (user_id,))
        user_role = c.fetchone()[0]
        conn.close()
        
        if Session.role == "admin" and user_role in ["admin", "super_admin"]:
            messagebox.showerror("Erreur", "Vous n'avez pas les permissions pour supprimer cet utilisateur !")
            return
        
        # Tous les autres utilisateurs (y compris admin et super_admin) peuvent être supprimés
        if messagebox.askyesno("Confirmation", f"Supprimer l'utilisateur {username} ?"):
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute("DELETE FROM Utilisateur WHERE ID_Utilisateur=?", (user_id,))
            conn.commit()
            conn.close()
            
            log_activity("Suppression", "Administration", username)
            self.reorganize_ids()
            messagebox.showinfo("Succès", "Utilisateur supprimé !\nID réorganisés automatiquement.")
            self.load_users()
    
    def clear_logs(self):
        if messagebox.askyesno("Confirmation", "Vider TOUS les logs ?"):
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute("DELETE FROM Journal_Activite")
            conn.commit()
            conn.close()
            messagebox.showinfo("Succès", "Logs vidés !")
            self.load_logs()
    
    def backup_database(self):
        try:
            backup_name = f"cmev_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2('cmev.db', backup_name)
            messagebox.showinfo("Succès", f"Sauvegarde créée :\n{backup_name}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur sauvegarde : {e}")
    
    def back_to_menu(self):
        self.root.destroy()
    
    def actualiser_code_manuel(self):
        if messagebox.askyesno("Confirmation", 
                              "Voulez-vous générer un nouveau code de validation ?\n\n"
                              "L'ancien code ne sera plus valide."):
            nouveau_code = actualiser_code_auto()
            if nouveau_code:
                messagebox.showinfo("Nouveau code généré", 
                                  f"Le nouveau code est :\n\n[ {nouveau_code} ]\n\n"
                                  f"Communiquez-le aux utilisateurs concernés.")
                # Recharger l'onglet pour afficher le nouveau code
                self.create_settings_tab()

class AddUserWindow:
    def __init__(self, parent, admin_module):
        self.admin_module = admin_module
        
        # Vérifier les permissions pour créer des utilisateurs
        if Session.role == "super_admin":
            roles_disponibles = ["super_admin", "admin", "medecin", "receptionniste", "pharmacien"]
        elif Session.role == "admin":
            roles_disponibles = ["medecin", "receptionniste", "pharmacien"]
        else:
            messagebox.showerror("Erreur", "Vous n'avez pas les permissions pour créer des utilisateurs !")
            return
        
        self.window = tk.Toplevel(parent)
        self.window.title("Nouvel Utilisateur")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.transient(parent)
        self.window.grab_set()
        self.window.lift()
        
        tk.Label(self.window, text="➕ NOUVEL UTILISATEUR", 
                font=("Arial", 20, "bold"),
                bg=THEME['success'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        font_size = CONFIG['font_size']
        
        tk.Label(form, text="Nom d'utilisateur :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.username_entry = tk.Entry(form, font=("Arial", font_size), width=30,
                                       bg=THEME['bg_light'], fg=THEME['text_white'],
                                       insertbackground=THEME['text_white'])
        self.username_entry.grid(row=0, column=1, pady=12)
        self.username_entry.focus()
        
        tk.Label(form, text="Mot de passe :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        self.password_entry = tk.Entry(form, font=("Arial", font_size), width=30,
                                       bg=THEME['bg_light'], fg=THEME['text_white'],
                                       insertbackground=THEME['text_white'], show='•')
        self.password_entry.grid(row=1, column=1, pady=12)
        
        tk.Label(form, text="Nom complet :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=2, column=0, sticky=tk.W, pady=12)
        self.fullname_entry = tk.Entry(form, font=("Arial", font_size), width=30,
                                       bg=THEME['bg_light'], fg=THEME['text_white'],
                                       insertbackground=THEME['text_white'])
        self.fullname_entry.grid(row=2, column=1, pady=12)
        
        tk.Label(form, text="Rôle :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(form, textvariable=self.role_var, values=roles_disponibles,
                                 font=("Arial", font_size), width=28, state="readonly")
        role_combo.grid(row=3, column=1, pady=12)
        role_combo.set(roles_disponibles[0] if roles_disponibles else "")
        
        # Information sur les restrictions
        if Session.role == "admin":
            tk.Label(form, text="⚠️ En tant qu'Admin, vous ne pouvez créer que des Médecins, Réceptionnistes et Pharmaciens",
                    bg=THEME['bg_dark'], fg=THEME['warning'],
                    font=("Arial", font_size-2), wraplength=400).grid(row=4, column=0, columnspan=2, pady=10)
        
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=5, column=0, columnspan=2, pady=30)
        
        tk.Button(btn_frame, text="💾 Créer", font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], width=16, height=2,
                 command=self.save, cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="❌ Annuler", font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], width=16, height=2,
                 command=self.window.destroy, cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Erreur", "Nom d'utilisateur et mot de passe obligatoires !")
            return
        
        # Vérification supplémentaire : Admin ne peut pas créer admin/super_admin
        if Session.role == "admin" and self.role_var.get() in ["admin", "super_admin"]:
            messagebox.showerror("Erreur", "Vous n'avez pas les permissions pour créer ce type d'utilisateur !")
            return
        
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            c.execute('''INSERT INTO Utilisateur 
                        (Nom_utilisateur, Mot_de_passe, Role, Nom_complet, Actif)
                        VALUES (?, ?, ?, ?, 1)''',
                     (username, password, self.role_var.get(),
                      self.fullname_entry.get() or None))
            conn.commit()
            conn.close()
            log_activity("Création", "Administration", f"Utilisateur {username}")
            messagebox.showinfo("Succès", "Utilisateur créé !")
            self.admin_module.load_users()
            self.window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Ce nom d'utilisateur existe déjà !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

class EditUserWindow:
    def __init__(self, parent, admin_module, user_id):
        self.admin_module = admin_module
        self.user_id = user_id
        
        conn = sqlite3.connect('cmev.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Utilisateur WHERE ID_Utilisateur=?", (user_id,))
        self.user = c.fetchone()
        conn.close()
        
        if not self.user:
            messagebox.showerror("Erreur", "Utilisateur introuvable !")
            return
        
        if self.user[1] in ["TEST", "ROOT"]:
            messagebox.showerror("Erreur", "Impossible de modifier cet utilisateur système !")
            return
        
        # Admin ne peut pas modifier les admin/super_admin
        if Session.role == "admin" and self.user[3] in ["admin", "super_admin"]:
            messagebox.showerror("Erreur", "Vous n'avez pas les permissions pour modifier cet utilisateur !")
            return

        self.window = tk.Toplevel(parent)
        self.window.title("Modifier Utilisateur")
        self.window.state('zoomed')
        self.window.configure(bg=THEME['bg_dark'])
        self.window.transient(parent)
        self.window.grab_set()
        self.window.lift()
        
        tk.Label(self.window, text="✏️ MODIFIER UTILISATEUR", 
                font=("Arial", 20, "bold"),
                bg=THEME['warning'], fg=THEME['text_white'], 
                pady=20).pack(fill=tk.X)
        
        form = tk.Frame(self.window, bg=THEME['bg_dark'])
        form.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        font_size = CONFIG['font_size']
        
        tk.Label(form, text="Nom d'utilisateur :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=0, column=0, sticky=tk.W, pady=12)
        self.username_entry = tk.Entry(form, font=("Arial", font_size), width=30,
                                       bg=THEME['bg_light'], 
                                       fg=THEME['text_white'],
                                       insertbackground=THEME['text_white'])
        self.username_entry.grid(row=0, column=1, pady=12)
        self.username_entry.insert(0, self.user[1])
        
        tk.Label(form, text="Nouveau mot de passe :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=1, column=0, sticky=tk.W, pady=12)
        self.password_entry = tk.Entry(form, font=("Arial", font_size), width=30,
                                       bg=THEME['bg_light'], 
                                       fg=THEME['text_white'],
                                       insertbackground=THEME['text_white'], show='•')
        self.password_entry.grid(row=1, column=1, pady=12)
        
        tk.Label(form, text="(Laissez vide pour ne pas changer)", 
                bg=THEME['bg_dark'], fg=THEME['text_white'],
                font=("Arial", font_size-2), 
                anchor=tk.W).grid(row=2, column=1, sticky=tk.W, pady=0)
        
        tk.Label(form, text="Nom complet :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=3, column=0, sticky=tk.W, pady=12)
        self.fullname_entry = tk.Entry(form, font=("Arial", font_size), width=30,
                                       bg=THEME['bg_light'], 
                                       fg=THEME['text_white'],
                                       insertbackground=THEME['text_white'])
        self.fullname_entry.grid(row=3, column=1, pady=12)
        if self.user[4]:
            self.fullname_entry.insert(0, self.user[4])
        
        tk.Label(form, text="Rôle :", bg=THEME['bg_dark'],
                fg=THEME['text_white'], 
                font=("Arial", font_size)).grid(row=4, column=0, sticky=tk.W, pady=12)
        
        roles = ["super_admin", "admin", "medecin", "receptionniste", "pharmacien"]
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(form, textvariable=self.role_var,
                                 values=roles,
                                 font=("Arial", font_size),
                                 width=28, state="readonly")
        role_combo.grid(row=4, column=1, pady=12)
        role_combo.set(self.user[3])
        
        btn_frame = tk.Frame(form, bg=THEME['bg_dark'])
        btn_frame.grid(row=5, column=0, columnspan=2, pady=30)
        
        tk.Button(btn_frame, text="💾 Enregistrer", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['success'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.save,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Annuler", 
                 font=("Arial", font_size+1, "bold"),
                 bg=THEME['danger'], fg=THEME['text_white'], 
                 width=16, height=2, command=self.window.destroy,
                 cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def save(self):
        username = self.username_entry.get().strip()
        
        if not username:
            messagebox.showerror("Erreur", "Nom d'utilisateur obligatoire !")
            return
        
        try:
            conn = sqlite3.connect('cmev.db')
            c = conn.cursor()
            
            password = self.password_entry.get().strip()
            
            if password:
                c.execute('''UPDATE Utilisateur 
                            SET Nom_utilisateur=?, Mot_de_passe=?, Role=?, Nom_complet=?
                            WHERE ID_Utilisateur=?''',
                         (username, password, self.role_var.get(),
                          self.fullname_entry.get() or None, self.user_id))
            else:
                c.execute('''UPDATE Utilisateur 
                            SET Nom_utilisateur=?, Role=?, Nom_complet=?
                            WHERE ID_Utilisateur=?''',
                         (username, self.role_var.get(),
                          self.fullname_entry.get() or None, self.user_id))
            
            conn.commit()
            conn.close()
            
            log_activity("Modification", "Administration", f"Utilisateur {username}")
            messagebox.showinfo("Succès", "Utilisateur modifié !")
            self.admin_module.load_users()
            self.window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Ce nom d'utilisateur existe déjà !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*80)
    print("   🏥 CMEV - VERSION COMPLÈTE ASSEMBLÉE")
    print("="*80)
    print("\n📋 Initialisation...")
    
    init_database()
    init_types_examens()
    init_categories_medicaments()
    
    print("✅ Base de données prête")
    print("✅ 20 types d'examens initialisés")
    print("✅ 20 catégories médicaments initialisées")
    print("\n🔑 Compte de test : TEST / 1234")
    print("\n✅ Gestion permissions par rôle activée")
    print("✅ Module Patients intégré")
    print("\n" + "="*80 + "\n")
    
    app = LoginWindow()
    app.run()
