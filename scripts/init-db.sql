BEGIN;

CREATE TABLE IF NOT EXISTS rate_limits (
    key_hash VARCHAR(64) PRIMARY KEY,
    attempts INTEGER NOT NULL,
    window_started_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_rate_limits_expires_at ON rate_limits (expires_at);

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
    email_verified_at TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ,
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

ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMPTZ;

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
    status VARCHAR(40) NOT NULL DEFAULT 'pending_email_verification',
    joined_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_church_memberships_church_user UNIQUE (church_id, user_id)
);

ALTER TABLE church_memberships
    ADD COLUMN IF NOT EXISTS status VARCHAR(40) NOT NULL DEFAULT 'pending_email_verification';

CREATE INDEX IF NOT EXISTS ix_church_memberships_church_id
    ON church_memberships (church_id);
CREATE INDEX IF NOT EXISTS ix_church_memberships_user_id
    ON church_memberships (user_id);

CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_email_verification_tokens_user_id
    ON email_verification_tokens (user_id);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_user_id
    ON password_reset_tokens (user_id);

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_sessions_user_id ON sessions (user_id);

CREATE TABLE IF NOT EXISTS consumed_refresh_tokens (
    token_hash VARCHAR(64) PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions (id) ON DELETE CASCADE,
    consumed_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_consumed_refresh_tokens_session_id
    ON consumed_refresh_tokens (session_id);

CREATE TABLE IF NOT EXISTS security_audit_events (
    id UUID PRIMARY KEY,
    event_type VARCHAR(80) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    actor_user_id UUID REFERENCES users (id),
    target_user_id UUID REFERENCES users (id),
    church_id UUID REFERENCES churches (id),
    session_id UUID REFERENCES sessions (id)
);

CREATE INDEX IF NOT EXISTS ix_security_audit_events_type
    ON security_audit_events (event_type);
CREATE INDEX IF NOT EXISTS ix_security_audit_events_occurred_at
    ON security_audit_events (occurred_at);
CREATE INDEX IF NOT EXISTS ix_security_audit_events_actor
    ON security_audit_events (actor_user_id, occurred_at);
CREATE INDEX IF NOT EXISTS ix_security_audit_events_church
    ON security_audit_events (church_id, occurred_at);

COMMIT;
