CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    age INTEGER NOT NULL,
    revenu_mensuel INTEGER NOT NULL,
    nombre_experiences_precedentes INTEGER NOT NULL,
    annee_experience_totale INTEGER NOT NULL,
    annees_dans_l_entreprise INTEGER NOT NULL,
    annees_dans_le_poste_actuel INTEGER NOT NULL,
    satisfaction_employee_environnement INTEGER NOT NULL,
    satisfaction_employee_nature_travail INTEGER NOT NULL,
    satisfaction_employee_equipe INTEGER NOT NULL,
    satisfaction_employee_equilibre_pro_perso INTEGER NOT NULL,
    note_evaluation_precedente INTEGER NOT NULL,
    note_evaluation_actuelle INTEGER NOT NULL,
    niveau_hierarchique_poste INTEGER NOT NULL,
    heure_supplementaires INTEGER NOT NULL,
    augementation_salaire_precedente DOUBLE PRECISION NOT NULL,
    nombre_participation_pee INTEGER NOT NULL,
    nb_formations_suivies INTEGER NOT NULL,
    distance_domicile_travail INTEGER NOT NULL,
    niveau_education INTEGER NOT NULL,
    annees_depuis_la_derniere_promotion INTEGER NOT NULL,
    annes_sous_responsable_actuel INTEGER NOT NULL,
    genre VARCHAR(10) NOT NULL,
    statut_marital VARCHAR(50) NOT NULL,
    departement VARCHAR(100) NOT NULL,
    poste VARCHAR(100) NOT NULL,
    domaine_etude VARCHAR(100) NOT NULL,
    frequence_deplacement VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prediction_inputs (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    age INTEGER NOT NULL,
    revenu_mensuel INTEGER NOT NULL,
    nombre_experiences_precedentes INTEGER NOT NULL,
    annee_experience_totale INTEGER NOT NULL,
    annees_dans_l_entreprise INTEGER NOT NULL,
    annees_dans_le_poste_actuel INTEGER NOT NULL,
    satisfaction_employee_environnement INTEGER NOT NULL,
    satisfaction_employee_nature_travail INTEGER NOT NULL,
    satisfaction_employee_equipe INTEGER NOT NULL,
    satisfaction_employee_equilibre_pro_perso INTEGER NOT NULL,
    note_evaluation_precedente INTEGER NOT NULL,
    note_evaluation_actuelle INTEGER NOT NULL,
    niveau_hierarchique_poste INTEGER NOT NULL,
    heure_supplementaires INTEGER NOT NULL,
    augementation_salaire_precedente DOUBLE PRECISION NOT NULL,
    nombre_participation_pee INTEGER NOT NULL,
    nb_formations_suivies INTEGER NOT NULL,
    distance_domicile_travail INTEGER NOT NULL,
    niveau_education INTEGER NOT NULL,
    annees_depuis_la_derniere_promotion INTEGER NOT NULL,
    annes_sous_responsable_actuel INTEGER NOT NULL,
    genre VARCHAR(10) NOT NULL,
    statut_marital VARCHAR(50) NOT NULL,
    departement VARCHAR(100) NOT NULL,
    poste VARCHAR(100) NOT NULL,
    domaine_etude VARCHAR(100) NOT NULL,
    frequence_deplacement VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prediction_outputs (
    id SERIAL PRIMARY KEY,
    prediction_input_id INTEGER NOT NULL UNIQUE REFERENCES prediction_inputs(id),
    prediction INTEGER NOT NULL,
    probability DOUBLE PRECISION NOT NULL,
    threshold DOUBLE PRECISION NOT NULL,
    label VARCHAR(50) NOT NULL,
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_prediction_inputs_employee_id
    ON prediction_inputs(employee_id);

CREATE INDEX IF NOT EXISTS idx_prediction_outputs_prediction_input_id
    ON prediction_outputs(prediction_input_id);

CREATE INDEX IF NOT EXISTS idx_prediction_inputs_created_at
    ON prediction_inputs(created_at);

CREATE INDEX IF NOT EXISTS idx_prediction_outputs_created_at
    ON prediction_outputs(created_at);
