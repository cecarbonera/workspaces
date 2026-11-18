-- =============================================================================
-- SCRIPT DE DDL (DATA DEFINITION LANGUAGE)
-- Sistema: Pet Store & Clinic (Bytesquad)
-- Banco de Dados Recomendado: PostgreSQL / MySQL / SQL Server
-- =============================================================================

-- Drop de tabelas existentes (para reinicialização limpa se necessário)
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS appointment CASCADE;
DROP TABLE IF EXISTS pet CASCADE;
DROP TABLE IF EXISTS receptionist CASCADE;
DROP TABLE IF EXISTS doctor CASCADE;
DROP TABLE IF EXISTS manager CASCADE;
DROP TABLE IF EXISTS shop CASCADE;
DROP TABLE IF EXISTS client CASCADE;
DROP TABLE IF EXISTS product CASCADE;
DROP TABLE IF EXISTS bill CASCADE;
DROP TABLE IF EXISTS role CASCADE;

-- 1. Tabela ROLE (Funções/Perfis de Acesso)
CREATE TABLE role (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- 2. Tabela BILL (Faturas/Cobranças)
CREATE TABLE bill (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabela PRODUCT (Produtos)
CREATE TABLE product (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    price_per_unit NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    stock NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    type VARCHAR(50)
);

-- 4. Tabela CLIENT (Clientes/Tutores)
CREATE TABLE client (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    occupation VARCHAR(100),
    address VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    phone VARCHAR(30),
    about TEXT
);

-- 5. Tabela SHOP (Lojas/Clínicas - Entidade Inferida)
CREATE TABLE shop (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    address VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    phone VARCHAR(30)
);

-- 6. Tabela MANAGER (Gerentes da Loja/Clínica)
CREATE TABLE manager (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    shop_id BIGINT,
    address VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    phone VARCHAR(30),
    about TEXT,
    CONSTRAINT fk_manager_shop FOREIGN KEY (shop_id) REFERENCES shop (id) ON DELETE SET NULL
);

-- 7. Tabela DOCTOR (Veterinários/Médicos)
CREATE TABLE doctor (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    shop_id BIGINT,
    address VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    phone VARCHAR(30),
    about TEXT,
    CONSTRAINT fk_doctor_shop FOREIGN KEY (shop_id) REFERENCES shop (id) ON DELETE SET NULL
);

-- 8. Tabela RECEPTIONIST (Recepcionistas)
CREATE TABLE receptionist (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    role_id BIGINT,
    shop_id BIGINT,
    address VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    phone VARCHAR(30),
    about TEXT,
    CONSTRAINT fk_receptionist_role FOREIGN KEY (role_id) REFERENCES role (id) ON DELETE SET NULL,
    CONSTRAINT fk_receptionist_shop FOREIGN KEY (shop_id) REFERENCES shop (id) ON DELETE SET NULL
);

-- 9. Tabela PET (Animais de Estimação)
CREATE TABLE pet (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    client_id BIGINT NOT NULL,
    species VARCHAR(50),
    breed VARCHAR(50),
    gender VARCHAR(20),
    date_of_birth DATE,
    colour VARCHAR(50),
    CONSTRAINT fk_pet_client FOREIGN KEY (client_id) REFERENCES client (id) ON DELETE CASCADE
);

-- 10. Tabela APPOINTMENT (Consultas/Agendamentos)
CREATE TABLE appointment (
    id BIGSERIAL PRIMARY KEY,
    client_id BIGINT NOT NULL,
    pet_id BIGINT NOT NULL,
    doctor_id BIGINT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    finish_time TIMESTAMP NOT NULL,
    CONSTRAINT fk_appointment_client FOREIGN KEY (client_id) REFERENCES client (id) ON DELETE CASCADE,
    CONSTRAINT fk_appointment_pet FOREIGN KEY (pet_id) REFERENCES pet (id) ON DELETE CASCADE,
    CONSTRAINT fk_appointment_doctor FOREIGN KEY (doctor_id) REFERENCES doctor (id) ON DELETE CASCADE
);

-- 11. Tabela FEEDBACK (Avaliações/Comentários)
CREATE TABLE feedback (
    id BIGSERIAL PRIMARY KEY,
    client_id BIGINT NOT NULL,
    shop_id BIGINT,
    doctor_id BIGINT,
    title VARCHAR(150),
    message TEXT NOT NULL,
    CONSTRAINT fk_feedback_client FOREIGN KEY (client_id) REFERENCES client (id) ON DELETE CASCADE,
    CONSTRAINT fk_feedback_shop FOREIGN KEY (shop_id) REFERENCES shop (id) ON DELETE CASCADE,
    CONSTRAINT fk_feedback_doctor FOREIGN KEY (doctor_id) REFERENCES doctor (id) ON DELETE CASCADE
);

-- Índices para otimização de consultas e Chaves Estrangeiras
CREATE INDEX idx_pet_client ON pet(client_id);
CREATE INDEX idx_appointment_client ON appointment(client_id);
CREATE INDEX idx_appointment_pet ON appointment(pet_id);
CREATE INDEX idx_appointment_doctor ON appointment(doctor_id);
CREATE INDEX idx_doctor_shop ON doctor(shop_id);
CREATE INDEX idx_manager_shop ON manager(shop_id);
CREATE INDEX idx_receptionist_shop ON receptionist(shop_id);
CREATE INDEX idx_receptionist_role ON receptionist(role_id);
CREATE INDEX idx_feedback_client ON feedback(client_id);
CREATE INDEX idx_feedback_doctor ON feedback(doctor_id);
CREATE INDEX idx_feedback_shop ON feedback(shop_id);
