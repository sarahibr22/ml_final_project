-- ============================================================
-- 1. Enable extension + Schema (your original DDL)
-- ============================================================
CREATE EXTENSION IF NOT EXISTS vector;

-- Patients Table
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    date_of_birth DATE,
    gender TEXT,
    phone TEXT,
    email TEXT,
    patient_case_summary TEXT,
    patient_case_embedding vector,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prescriptions Table
CREATE TABLE IF NOT EXISTS prescriptions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_name TEXT,
    prescription_date DATE,
    image_path TEXT NOT NULL,
    ocr_engine TEXT NOT NULL,
    ocr_raw_text TEXT NOT NULL,
    parsed_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Medications Table
CREATE TABLE IF NOT EXISTS medications (
    id SERIAL PRIMARY KEY,
    generic_name TEXT NOT NULL,
    brand_name TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prescription_Medications Table
CREATE TABLE IF NOT EXISTS prescription_medications (
    id SERIAL PRIMARY KEY,
    prescription_id INTEGER REFERENCES prescriptions(id) ON DELETE CASCADE,
    medication_id INTEGER REFERENCES medications(id),
    medication_name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    frequency TEXT NOT NULL,
    duration TEXT NOT NULL,
    instructions TEXT
);

-- ============================================================
-- 2. Clean existing data (optional but recommended for seeding)
-- ============================================================
TRUNCATE TABLE
    prescription_medications,
    prescriptions,
    medications,
    patients
RESTART IDENTITY CASCADE;

-- ============================================================
-- 3. Seed Patients (25 rows)
-- ============================================================
INSERT INTO patients (id, full_name, date_of_birth, gender, phone, email, patient_case_summary)
VALUES
(1,  'Ali Mansour',        '1985-03-12', 'Male',   '+96170111111', 'ali.mansour@example.com',        'Type 2 diabetes, mild hypertension.'),
(2,  'Sara Khoury',        '1990-07-25', 'Female', '+96171111112', 'sara.khoury@example.com',        'Allergic rhinitis and mild asthma.'),
(3,  'Rami Haddad',        '1978-11-03', 'Male',   '+96103123456', 'rami.haddad@example.com',        'Hyperlipidemia on statin therapy.'),
(4,  'Layla Fares',        '1995-01-18', 'Female', '+96176123457', 'layla.fares@example.com',        'Recurrent migraine headaches.'),
(5,  'Nour Chami',         '2002-05-09', 'Female', '+96171123458', 'nour.chami@example.com',         'Seasonal allergies, no chronic disease.'),
(6,  'Omar Hoteit',        '1982-09-30', 'Male',   '+96179123459', 'omar.hoteit@example.com',        'Stable ischemic heart disease.'),
(7,  'Hiba Salameh',       '1988-12-22', 'Female', '+96170123460', 'hiba.salameh@example.com',       'Hypothyroidism on replacement therapy.'),
(8,  'Jad Abou Zeid',      '1975-06-14', 'Male',   '+96103123461', 'jad.abouzeid@example.com',       'Chronic low back pain.'),
(9,  'Maya Ghandour',      '1993-04-05', 'Female', '+96171123462', 'maya.ghandour@example.com',      'Anxiety disorder, on SSRI.'),
(10, 'Hassan Issa',        '1980-02-27', 'Male',   '+96176123463', 'hassan.issa@example.com',        'Hypertension controlled with ACE inhibitor.'),
(11, 'Dana Fawaz',         '1998-08-19', 'Female', '+96170123464', 'dana.fawaz@example.com',         'PCOS, metformin therapy.'),
(12, 'Marwan Kanaan',      '1972-10-01', 'Male',   '+96103123465', 'marwan.kanaan@example.com',      'Chronic obstructive pulmonary disease.'),
(13, 'Rita Nassar',        '1987-01-09', 'Female', '+96171123466', 'rita.nassar@example.com',        'Gastritis, on PPI as needed.'),
(14, 'Karim Barakat',      '1991-11-29', 'Male',   '+96176123467', 'karim.barakat@example.com',      'Obesity and pre-diabetes.'),
(15, 'Lina Saab',          '1994-03-07', 'Female', '+96170123468', 'lina.saab@example.com',          'Mild depression, on sertraline.'),
(16, 'Ahmad Youssef',      '1983-09-11', 'Male',   '+96103123469', 'ahmad.youssef@example.com',      'Post-MI on dual antiplatelet therapy.'),
(17, 'Yara Abboud',        '1996-12-01', 'Female', '+96171123470', 'yara.abboud@example.com',        'Bronchial asthma, controlled with inhalers.'),
(18, 'George Sarkis',      '1979-05-16', 'Male',   '+96176123471', 'george.sarkis@example.com',      'Chronic kidney disease stage 2.'),
(19, 'Mira Rached',        '2000-09-23', 'Female', '+96170123472', 'mira.rached@example.com',        'Frequent tonsillitis.'),
(20, 'Samir Taleb',        '1968-02-03', 'Male',   '+96103123473', 'samir.taleb@example.com',        'Heart failure with reduced ejection fraction.'),
(21, 'Joumana Azar',       '1984-06-21', 'Female', '+96171123474', 'joumana.azar@example.com',       'Rheumatoid arthritis on chronic therapy.'),
(22, 'Fadi Hamdan',        '1977-01-30', 'Male',   '+96176123475', 'fadi.hamdan@example.com',        'Chronic smoker with productive cough.'),
(23, 'Nisrine Melki',      '1992-10-10', 'Female', '+96170123476', 'nisrine.melki@example.com',      'Migraine and tension-type headaches.'),
(24, 'Tarek Khayat',       '1986-07-02', 'Male',   '+96103123477', 'tarek.khayat@example.com',       'Type 1 diabetes on insulin.'),
(25, 'Rana El Hajj',       '1999-11-13', 'Female', '+96171123478', 'rana.elhajj@example.com',        'Iron deficiency anemia.');

-- ============================================================
-- 4. Seed Medications (25 rows)
-- ============================================================
INSERT INTO medications (id, generic_name, brand_name, category)
VALUES
(1,  'Paracetamol',          'Panadol',          'Analgesic / Antipyretic'),
(2,  'Ibuprofen',            'Brufen',           'NSAID'),
(3,  'Amoxicillin',          'Amoxil',           'Antibiotic'),
(4,  'Azithromycin',         'Zithromax',        'Antibiotic'),
(5,  'Metformin',            'Glucophage',       'Antidiabetic'),
(6,  'Amlodipine',           'Norvasc',          'Antihypertensive'),
(7,  'Atorvastatin',         'Lipitor',          'Lipid-lowering'),
(8,  'Omeprazole',           'Losec',            'Proton pump inhibitor'),
(9,  'Pantoprazole',         'Controloc',        'Proton pump inhibitor'),
(10, 'Levothyroxine',        'Eltroxin',         'Thyroid hormone'),
(11, 'Losartan',             'Cozaar',           'Antihypertensive'),
(12, 'Salbutamol',           'Ventolin',         'Bronchodilator'),
(13, 'Cetirizine',           'Zyrtec',           'Antihistamine'),
(14, 'Loratadine',           'Claritin',         'Antihistamine'),
(15, 'Prednisone',           NULL,               'Corticosteroid'),
(16, 'Insulin glargine',     'Lantus',           'Insulin'),
(17, 'Clopidogrel',          'Plavix',           'Antiplatelet'),
(18, 'Warfarin',             'Coumadin',         'Anticoagulant'),
(19, 'Furosemide',           'Lasix',            'Diuretic'),
(20, 'Spironolactone',       'Aldactone',        'Diuretic'),
(21, 'Sertraline',           'Zoloft',           'Antidepressant'),
(22, 'Fluoxetine',           'Prozac',           'Antidepressant'),
(23, 'Diazepam',             'Valium',           'Anxiolytic'),
(24, 'Alprazolam',           'Xanax',            'Anxiolytic'),
(25, 'Cholecalciferol',      'Vitamin D3',       'Vitamin');

-- ============================================================
-- 5. Seed Prescriptions (30 rows)
-- ============================================================
INSERT INTO prescriptions (
    id, patient_id, doctor_name, prescription_date,
    image_path, ocr_engine, ocr_raw_text, parsed_json
)
VALUES
(1,  1,  'Dr. Ahmad Saeed',     '2025-01-05',
 '/data/prescriptions/prescription_001.png',
 'tesseract',
 'Amoxicillin 500 mg three times daily for 7 days.',
 '{"medications":[{"name":"Amoxicillin","dosage":"500 mg","frequency":"TID","duration":"7 days"}]}'),
(2,  2,  'Dr. Lina Khoury',     '2025-01-06',
 '/data/prescriptions/prescription_002.png',
 'tesseract',
 'Cetirizine 10 mg once daily at night.',
 '{"medications":[{"name":"Cetirizine","dosage":"10 mg","frequency":"once daily","duration":"as needed"}]}'),
(3,  3,  'Dr. Omar Daher',      '2025-01-07',
 '/data/prescriptions/prescription_003.png',
 'azure_vision',
 'Atorvastatin 20 mg at bedtime.',
 '{"medications":[{"name":"Atorvastatin","dosage":"20 mg","frequency":"once daily","duration":"chronic"}]}'),
(4,  4,  'Dr. Rana Sleiman',    '2025-01-10',
 '/data/prescriptions/prescription_004.png',
 'tesseract',
 'Paracetamol 1 g every 8 hours for 3 days.',
 '{"medications":[{"name":"Paracetamol","dosage":"1 g","frequency":"q8h","duration":"3 days"}]}'),
(5,  5,  'Dr. Hadi Itani',      '2025-01-11',
 '/data/prescriptions/prescription_005.png',
 'azure_vision',
 'Loratadine 10 mg daily, Salbutamol inhaler as needed.',
 '{"medications":[
    {"name":"Loratadine","dosage":"10 mg","frequency":"once daily","duration":"14 days"},
    {"name":"Salbutamol","dosage":"2 puffs","frequency":"PRN","duration":"as needed"}
]}'),
(6,  6,  'Dr. Ahmad Saeed',     '2025-01-12',
 '/data/prescriptions/prescription_006.png',
 'tesseract',
 'Amlodipine 5 mg once daily.',
 '{"medications":[{"name":"Amlodipine","dosage":"5 mg","frequency":"once daily","duration":"chronic"}]}'),
(7,  7,  'Dr. Sara Fadel',      '2025-01-14',
 '/data/prescriptions/prescription_007.png',
 'tesseract',
 'Levothyroxine 75 mcg once daily before breakfast.',
 '{"medications":[{"name":"Levothyroxine","dosage":"75 mcg","frequency":"once daily","duration":"chronic"}]}'),
(8,  8,  'Dr. Karim Antoun',    '2025-01-15',
 '/data/prescriptions/prescription_008.png',
 'azure_vision',
 'Ibuprofen 400 mg every 8 hours as needed for pain.',
 '{"medications":[{"name":"Ibuprofen","dosage":"400 mg","frequency":"q8h","duration":"5 days"}]}'),
(9,  9,  'Dr. Mira Wehbe',      '2025-01-16',
 '/data/prescriptions/prescription_009.png',
 'tesseract',
 'Sertraline 50 mg once daily in the morning.',
 '{"medications":[{"name":"Sertraline","dosage":"50 mg","frequency":"once daily","duration":"chronic"}]}'),
(10, 10, 'Dr. Rami Chidiac',    '2025-01-18',
 '/data/prescriptions/prescription_010.png',
 'tesseract',
 'Losartan 50 mg daily and Furosemide 40 mg daily.',
 '{"medications":[
    {"name":"Losartan","dosage":"50 mg","frequency":"once daily","duration":"chronic"},
    {"name":"Furosemide","dosage":"40 mg","frequency":"once daily","duration":"chronic"}
]}'),
(11, 11, 'Dr. Dana Halabi',     '2025-01-19',
 '/data/prescriptions/prescription_011.png',
 'azure_vision',
 'Metformin 850 mg twice daily.',
 '{"medications":[{"name":"Metformin","dosage":"850 mg","frequency":"BID","duration":"chronic"}]}'),
(12, 12, 'Dr. Nabil Zogheib',   '2025-01-20',
 '/data/prescriptions/prescription_012.png',
 'tesseract',
 'Salbutamol inhaler as needed, Prednisone 20 mg for 5 days.',
 '{"medications":[
    {"name":"Salbutamol","dosage":"2 puffs","frequency":"PRN","duration":"as needed"},
    {"name":"Prednisone","dosage":"20 mg","frequency":"once daily","duration":"5 days"}
]}'),
(13, 13, 'Dr. Noura Aoun',      '2025-01-21',
 '/data/prescriptions/prescription_013.png',
 'tesseract',
 'Omeprazole 20 mg once daily before meals.',
 '{"medications":[{"name":"Omeprazole","dosage":"20 mg","frequency":"once daily","duration":"4 weeks"}]}'),
(14, 14, 'Dr. Karim Antoun',    '2025-01-22',
 '/data/prescriptions/prescription_014.png',
 'azure_vision',
 'Metformin 1000 mg twice daily, Atorvastatin 20 mg nightly.',
 '{"medications":[
    {"name":"Metformin","dosage":"1000 mg","frequency":"BID","duration":"chronic"},
    {"name":"Atorvastatin","dosage":"20 mg","frequency":"once daily","duration":"chronic"}
]}'),
(15, 15, 'Dr. Mira Wehbe',      '2025-01-23',
 '/data/prescriptions/prescription_015.png',
 'tesseract',
 'Sertraline 100 mg daily and Alprazolam 0.25 mg at night as needed.',
 '{"medications":[
    {"name":"Sertraline","dosage":"100 mg","frequency":"once daily","duration":"chronic"},
    {"name":"Alprazolam","dosage":"0.25 mg","frequency":"HS PRN","duration":"short term"}
]}'),
(16, 16, 'Dr. Ahmad Saeed',     '2025-01-24',
 '/data/prescriptions/prescription_016.png',
 'tesseract',
 'Clopidogrel 75 mg daily and Atorvastatin 40 mg nightly.',
 '{"medications":[
    {"name":"Clopidogrel","dosage":"75 mg","frequency":"once daily","duration":"1 year"},
    {"name":"Atorvastatin","dosage":"40 mg","frequency":"once daily","duration":"chronic"}
]}'),
(17, 17, 'Dr. Lina Khoury',     '2025-01-25',
 '/data/prescriptions/prescription_017.png',
 'azure_vision',
 'Salbutamol inhaler and Cetirizine 10 mg during allergy season.',
 '{"medications":[
    {"name":"Salbutamol","dosage":"2 puffs","frequency":"PRN","duration":"as needed"},
    {"name":"Cetirizine","dosage":"10 mg","frequency":"once daily","duration":"seasonal"}
]}'),
(18, 18, 'Dr. Nabil Zogheib',   '2025-01-26',
 '/data/prescriptions/prescription_018.png',
 'tesseract',
 'Furosemide 40 mg daily, Spironolactone 25 mg daily.',
 '{"medications":[
    {"name":"Furosemide","dosage":"40 mg","frequency":"once daily","duration":"chronic"},
    {"name":"Spironolactone","dosage":"25 mg","frequency":"once daily","duration":"chronic"}
]}'),
(19, 19, 'Dr. Hadi Itani',      '2025-01-27',
 '/data/prescriptions/prescription_019.png',
 'tesseract',
 'Amoxicillin 500 mg TID for 7 days, Paracetamol 1 g TID for 3 days.',
 '{"medications":[
    {"name":"Amoxicillin","dosage":"500 mg","frequency":"TID","duration":"7 days"},
    {"name":"Paracetamol","dosage":"1 g","frequency":"TID","duration":"3 days"}
]}'),
(20, 20, 'Dr. Rami Chidiac',    '2025-01-28',
 '/data/prescriptions/prescription_020.png',
 'azure_vision',
 'Warfarin dose per INR protocol.',
 '{"medications":[{"name":"Warfarin","dosage":"per INR","frequency":"once daily","duration":"chronic"}]}'),
(21, 21, 'Dr. Joumana Tabet',   '2025-01-29',
 '/data/prescriptions/prescription_021.png',
 'tesseract',
 'Prednisone tapering dose for RA flare.',
 '{"medications":[{"name":"Prednisone","dosage":"variable taper","frequency":"once daily","duration":"10 days"}]}'),
(22, 22, 'Dr. Dana Halabi',     '2025-01-30',
 '/data/prescriptions/prescription_022.png',
 'tesseract',
 'Diazepam 5 mg at night for 5 days.',
 '{"medications":[{"name":"Diazepam","dosage":"5 mg","frequency":"HS","duration":"5 days"}]}'),
(23, 23, 'Dr. Mira Wehbe',      '2025-02-01',
 '/data/prescriptions/prescription_023.png',
 'azure_vision',
 'Paracetamol 1 g PRN and Ibuprofen 400 mg PRN.',
 '{"medications":[
    {"name":"Paracetamol","dosage":"1 g","frequency":"PRN","duration":"as needed"},
    {"name":"Ibuprofen","dosage":"400 mg","frequency":"PRN","duration":"as needed"}
]}'),
(24, 24, 'Dr. Ahmad Saeed',     '2025-02-02',
 '/data/prescriptions/prescription_024.png',
 'tesseract',
 'Insulin glargine 20 units at bedtime.',
 '{"medications":[{"name":"Insulin glargine","dosage":"20 units","frequency":"HS","duration":"chronic"}]}'),
(25, 25, 'Dr. Dana Halabi',     '2025-02-03',
 '/data/prescriptions/prescription_025.png',
 'tesseract',
 'Cholecalciferol 50,000 IU weekly for 8 weeks.',
 '{"medications":[{"name":"Cholecalciferol","dosage":"50,000 IU","frequency":"weekly","duration":"8 weeks"}]}'),
(26, 5,  'Dr. Hadi Itani',      '2025-02-04',
 '/data/prescriptions/prescription_026.png',
 'tesseract',
 'Loratadine 10 mg daily for 10 days.',
 '{"medications":[{"name":"Loratadine","dosage":"10 mg","frequency":"once daily","duration":"10 days"}]}'),
(27, 9,  'Dr. Mira Wehbe',      '2025-02-05',
 '/data/prescriptions/prescription_027.png',
 'azure_vision',
 'Fluoxetine 20 mg every morning.',
 '{"medications":[{"name":"Fluoxetine","dosage":"20 mg","frequency":"once daily","duration":"chronic"}]}'),
(28, 14, 'Dr. Karim Antoun',    '2025-02-06',
 '/data/prescriptions/prescription_028.png',
 'tesseract',
 'Metformin 1000 mg BID and Omeprazole 20 mg daily.',
 '{"medications":[
    {"name":"Metformin","dosage":"1000 mg","frequency":"BID","duration":"chronic"},
    {"name":"Omeprazole","dosage":"20 mg","frequency":"once daily","duration":"4 weeks"}
]}'),
(29, 16, 'Dr. Ahmad Saeed',     '2025-02-07',
 '/data/prescriptions/prescription_029.png',
 'tesseract',
 'Clopidogrel 75 mg and Warfarin per cardiology plan.',
 '{"medications":[
    {"name":"Clopidogrel","dosage":"75 mg","frequency":"once daily","duration":"1 year"},
    {"name":"Warfarin","dosage":"per INR","frequency":"once daily","duration":"chronic"}
]}'),
(30, 18, 'Dr. Nabil Zogheib',   '2025-02-08',
 '/data/prescriptions/prescription_030.png',
 'azure_vision',
 'Furosemide 40 mg and Spironolactone 25 mg for volume control.',
 '{"medications":[
    {"name":"Furosemide","dosage":"40 mg","frequency":"once daily","duration":"chronic"},
    {"name":"Spironolactone","dosage":"25 mg","frequency":"once daily","duration":"chronic"}
]}');

-- ============================================================
-- 6. Seed Prescription_Medications (2 meds per Rx = 60 rows)
--    (Some prescriptions only had 1 med logically, but here we
--     still attach up to 2 rows for richer data.)
-- ============================================================
INSERT INTO prescription_medications (
    id, prescription_id, medication_id, medication_name,
    dosage, frequency, duration, instructions
)
VALUES
-- Rx 1
(1,  1,  3, 'Amoxicillin',   '500 mg',   'TID',          '7 days',  'Take after meals.'),
(2,  1,  1, 'Paracetamol',   '1 g',      'q8h',         '3 days',  'Do not exceed 4 g/day.'),

-- Rx 2
(3,  2,  13, 'Cetirizine',   '10 mg',    'once daily',  'as needed','Take at night for allergies.'),
(4,  2,  14, 'Loratadine',   '10 mg',    'once daily',  '10 days', 'Alternative antihistamine.'),

-- Rx 3
(5,  3,  7, 'Atorvastatin',  '20 mg',    'once daily',  'chronic', 'Take at bedtime.'),
(6,  3,  5, 'Metformin',     '500 mg',   'BID',         'chronic', 'Monitor blood glucose.'),

-- Rx 4
(7,  4,  1, 'Paracetamol',   '1 g',      'q8h',         '3 days',  'For headache and fever.'),
(8,  4,  2, 'Ibuprofen',     '400 mg',   'q8h',         '3 days',  'Take with food.'),

-- Rx 5
(9,  5,  14, 'Loratadine',   '10 mg',    'once daily',  '14 days', 'Avoid driving if drowsy.'),
(10, 5,  12, 'Salbutamol',   '2 puffs',  'PRN',         'as needed','Use spacer if available.'),

-- Rx 6
(11, 6,  6, 'Amlodipine',    '5 mg',     'once daily',  'chronic', 'Take at same time each day.'),
(12, 6, 11, 'Losartan',      '50 mg',    'once daily',  'chronic', 'Monitor blood pressure.'),

-- Rx 7
(13, 7, 10, 'Levothyroxine', '75 mcg',   'once daily',  'chronic', 'Take on empty stomach.'),
(14, 7,  1, 'Paracetamol',   '500 mg',   'PRN',         'as needed','For mild pain only.'),

-- Rx 8
(15, 8,  2, 'Ibuprofen',     '400 mg',   'q8h',         '5 days',  'Avoid if gastric pain occurs.'),
(16, 8,  8, 'Omeprazole',    '20 mg',    'once daily',  '1 week',  'Before breakfast.'),

-- Rx 9
(17, 9, 21, 'Sertraline',    '50 mg',    'once daily',  'chronic', 'Take in the morning.'),
(18, 9, 24, 'Alprazolam',    '0.25 mg',  'HS PRN',      'short term','Use only if severe anxiety.'),

-- Rx 10
(19, 10, 11, 'Losartan',     '50 mg',    'once daily',  'chronic', 'Check BP weekly.'),
(20, 10, 19, 'Furosemide',   '40 mg',    'once daily',  'chronic', 'Take in the morning.'),

-- Rx 11
(21, 11, 5,  'Metformin',    '850 mg',   'BID',         'chronic', 'Take with meals.'),
(22, 11, 16, 'Insulin glargine','10 units','HS',        'chronic', 'Adjust per glucose log.'),

-- Rx 12
(23, 12, 12, 'Salbutamol',   '2 puffs',  'PRN',         'as needed','Rinse mouth after use.'),
(24, 12, 15, 'Prednisone',   '20 mg',    'once daily',  '5 days',  'Take in the morning.'),

-- Rx 13
(25, 13, 8,  'Omeprazole',   '20 mg',    'once daily',  '4 weeks', 'Before breakfast.'),
(26, 13, 9,  'Pantoprazole', '40 mg',    'once daily',  '4 weeks', 'Alternative PPI.'),

-- Rx 14
(27, 14, 5,  'Metformin',    '1000 mg',  'BID',         'chronic', 'Monitor HbA1c.'),
(28, 14, 7,  'Atorvastatin', '20 mg',    'once daily',  'chronic', 'Avoid grapefruit juice.'),

-- Rx 15
(29, 15, 21, 'Sertraline',   '100 mg',   'once daily',  'chronic', 'Do not stop abruptly.'),
(30, 15, 24, 'Alprazolam',   '0.25 mg',  'HS PRN',      'short term','Risk of dependence.'),

-- Rx 16
(31, 16, 17, 'Clopidogrel',  '75 mg',    'once daily',  '1 year',  'Do not miss doses.'),
(32, 16, 7,  'Atorvastatin', '40 mg',    'once daily',  'chronic', 'Night dosing preferred.'),

-- Rx 17
(33, 17, 12, 'Salbutamol',   '2 puffs',  'PRN',         'as needed','Use for acute symptoms.'),
(34, 17, 13, 'Cetirizine',   '10 mg',    'once daily',  'seasonal','For allergy control.'),

-- Rx 18
(35, 18, 19, 'Furosemide',   '40 mg',    'once daily',  'chronic', 'Monitor weight and edema.'),
(36, 18, 20, 'Spironolactone','25 mg',   'once daily',  'chronic', 'Check potassium regularly.'),

-- Rx 19
(37, 19, 3,  'Amoxicillin',  '500 mg',   'TID',         '7 days',  'Complete full course.'),
(38, 19, 1,  'Paracetamol',  '1 g',      'TID',         '3 days',  'Max 4 g per day.'),

-- Rx 20
(39, 20, 18, 'Warfarin',     'per INR',  'once daily',  'chronic', 'Regular INR monitoring.'),
(40, 20, 17, 'Clopidogrel',  '75 mg',    'once daily',  'chronic', 'Avoid NSAIDs.'),

-- Rx 21
(41, 21, 15, 'Prednisone',   'variable', 'once daily',  '10 days', 'Follow taper schedule.'),
(42, 21, 1,  'Paracetamol',  '500 mg',   'PRN',         'as needed','For pain relief.'),

-- Rx 22
(43, 22, 23, 'Diazepam',     '5 mg',     'HS',          '5 days',  'Do not drive after dose.'),
(44, 22, 22, 'Fluoxetine',   '20 mg',    'once daily',  'chronic', 'Take in the morning.'),

-- Rx 23
(45, 23, 1,  'Paracetamol',  '1 g',      'PRN',         'as needed','For headache.'),
(46, 23, 2,  'Ibuprofen',    '400 mg',   'PRN',         'as needed','With food to avoid gastritis.'),

-- Rx 24
(47, 24, 16, 'Insulin glargine','20 units','HS',        'chronic', 'Adjust as per fasting glucose.'),
(48, 24, 5,  'Metformin',    '850 mg',   'BID',         'chronic', 'Take with meals.'),

-- Rx 25
(49, 25, 25, 'Cholecalciferol','50,000 IU','weekly',    '8 weeks', 'Take once weekly.'),
(50, 25, 1,  'Paracetamol',  '500 mg',   'PRN',         'as needed','For bone pain.'),

-- Rx 26
(51, 26, 14, 'Loratadine',   '10 mg',    'once daily',  '10 days', 'For allergic rhinitis.'),
(52, 26, 13, 'Cetirizine',   '10 mg',    'once daily',  '10 days', 'Alternative antihistamine.'),

-- Rx 27
(53, 27, 22, 'Fluoxetine',   '20 mg',    'once daily',  'chronic', 'Takes 2–4 weeks for effect.'),
(54, 27, 21, 'Sertraline',   '50 mg',    'once daily',  'chronic', 'Do not combine without MD advice.'),

-- Rx 28
(55, 28, 5,  'Metformin',    '1000 mg',  'BID',         'chronic', 'With breakfast and dinner.'),
(56, 28, 8,  'Omeprazole',   '20 mg',    'once daily',  '4 weeks', 'Before eating.'),

-- Rx 29
(57, 29, 17, 'Clopidogrel',  '75 mg',    'once daily',  '1 year',  'Post-stent therapy.'),
(58, 29, 18, 'Warfarin',     'per INR',  'once daily',  'chronic', 'Check INR regularly.'),

-- Rx 30
(59, 30, 19, 'Furosemide',   '40 mg',    'once daily',  'chronic', 'Take in the morning.'),
(60, 30, 20, 'Spironolactone','25 mg',   'once daily',  'chronic', 'Monitor potassium.');

-- ============================================================
-- 7. Optional: Fix sequences so future inserts work smoothly
-- ============================================================
SELECT setval('patients_id_seq',                (SELECT MAX(id) FROM patients));
SELECT setval('medications_id_seq',            (SELECT MAX(id) FROM medications));
SELECT setval('prescriptions_id_seq',         (SELECT MAX(id) FROM prescriptions));
SELECT setval('prescription_medications_id_seq',(SELECT MAX(id) FROM prescription_medications));
