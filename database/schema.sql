-- Schema para la base de datos de cartera financiera
-- Ejecutar: psql -U postgres -d cartera_db -f database/schema.sql

CREATE TABLE IF NOT EXISTS cartera_financiera (
    id              SERIAL PRIMARY KEY,
    entidad         VARCHAR(255)   NOT NULL,
    tipo_cartera    VARCHAR(255)   NOT NULL,
    producto        VARCHAR(255)   NOT NULL,
    periodo         VARCHAR(7)     NOT NULL,  -- formato: YYYY-MM
    saldo           NUMERIC(20, 2),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Índices para acelerar los filtros más comunes de la API
CREATE INDEX IF NOT EXISTS idx_entidad      ON cartera_financiera (entidad);
CREATE INDEX IF NOT EXISTS idx_tipo_cartera ON cartera_financiera (tipo_cartera);
CREATE INDEX IF NOT EXISTS idx_periodo      ON cartera_financiera (periodo);

-- Restricción de unicidad para evitar duplicados al re-ejecutar el RPA
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_registro
    ON cartera_financiera (entidad, tipo_cartera, producto, periodo);
