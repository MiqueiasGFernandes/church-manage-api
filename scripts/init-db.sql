BEGIN;

CREATE TABLE IF NOT EXISTS churches (
    id UUID PRIMARY KEY,
    official_name VARCHAR(150) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    document VARCHAR(14),
    institutional_email VARCHAR(254) NOT NULL,
    institutional_phone VARCHAR(16) NOT NULL,
    website VARCHAR(2048),
    slug VARCHAR(60) NOT NULL,
    timezone VARCHAR(64) NOT NULL,
    status VARCHAR(40) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_churches_document UNIQUE (document),
    CONSTRAINT uq_churches_slug UNIQUE (slug)
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    phone VARCHAR(16) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(40) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS addresses (
    id UUID PRIMARY KEY,
    church_id UUID NOT NULL REFERENCES churches (id) ON DELETE CASCADE,
    postal_code VARCHAR(16) NOT NULL,
    street VARCHAR(200) NOT NULL,
    number VARCHAR(30) NOT NULL,
    complement VARCHAR(100),
    district VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    country VARCHAR(2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_addresses_church_id ON addresses (church_id);

CREATE TABLE IF NOT EXISTS church_settings (
    church_id UUID PRIMARY KEY REFERENCES churches (id) ON DELETE CASCADE,
    locale VARCHAR(10) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    timezone VARCHAR(64) NOT NULL,
    date_format VARCHAR(20) NOT NULL,
    country VARCHAR(2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS congregations (
    id UUID PRIMARY KEY,
    church_id UUID NOT NULL REFERENCES churches (id) ON DELETE CASCADE,
    address_id UUID NOT NULL UNIQUE REFERENCES addresses (id) ON DELETE RESTRICT,
    name VARCHAR(150) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_congregations_name UNIQUE (church_id, name)
);

CREATE INDEX IF NOT EXISTS ix_congregations_church_id ON congregations (church_id);

CREATE TABLE IF NOT EXISTS church_memberships (
    id UUID PRIMARY KEY,
    church_id UUID NOT NULL REFERENCES churches (id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    joined_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_church_memberships_church_user UNIQUE (church_id, user_id)
);

CREATE INDEX IF NOT EXISTS ix_church_memberships_church_id
    ON church_memberships (church_id);
CREATE INDEX IF NOT EXISTS ix_church_memberships_user_id
    ON church_memberships (user_id);

COMMIT;
