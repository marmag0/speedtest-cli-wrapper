-- migrate:up

CREATE TABLE IF NOT EXISTS speedtest_servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    server_id INT UNIQUE NOT NULL,
    server_url TEXT NOT NULL,
    server_name TEXT NOT NULL,
    server_country CHAR(2) NOT NULL,
    server_longitude NUMERIC(9, 6) NOT NULL,
    server_latitude NUMERIC(9, 6) NOT NULL
);

CREATE TABLE IF NOT EXISTS isps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    isp_name TEXT UNIQUE NOT NULL,
    isp_country CHAR(2) NOT NULL
);

CREATE TABLE IF NOT EXISTS speedtests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    start_time TIMESTAMPTZ NOT NULL,
    finish_time TIMESTAMPTZ,
    is_successful BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,
    download_speed NUMERIC(7, 2),
    upload_speed NUMERIC(7, 2),
    ping NUMERIC(8, 3),
    server_id UUID REFERENCES speedtest_servers(id) ON DELETE RESTRICT,
    isp_id UUID REFERENCES isps(id) ON DELETE RESTRICT,
    client_ip INET
);

-- migrate:down

DROP TABLE IF EXISTS speedtests CASCADE;
DROP TABLE IF EXISTS speedtest_servers CASCADE;
DROP TABLE IF EXISTS isps CASCADE;