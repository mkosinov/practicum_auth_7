BEGIN;
CREATE SCHEMA IF NOT EXISTS content;

SET search_path=content;

CREATE TYPE movie_type AS ENUM ('mv', 'tv');

CREATE TABLE IF NOT EXISTS film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT CHECK(rating >= 0.0 AND rating <= 10),
    type movie_type NOT NULL,
    file_path varchar(100),
    created timestamp with time zone,
    modified timestamp with time zone
); 

CREATE TABLE IF NOT EXISTS genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
); 

CREATE TABLE IF NOT EXISTS person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
); 

CREATE TABLE IF NOT EXISTS person_film_work (
    id uuid PRIMARY KEY,
    person_id uuid REFERENCES person ON DELETE CASCADE,
    film_work_id uuid REFERENCES film_work ON DELETE CASCADE,
    role TEXT NOT NULL,
    created timestamp with time zone
); 

CREATE TABLE IF NOT EXISTS genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid REFERENCES genre ON DELETE CASCADE,
    film_work_id uuid REFERENCES film_work ON DELETE CASCADE,
    created timestamp with time zone
); 

CREATE INDEX IF NOT EXISTS film_work_creat_dat_ratin_idx ON film_work(creation_date, rating);

CREATE UNIQUE INDEX IF NOT EXISTS genre_film_work_idx ON genre_film_work(genre_id, film_work_id);

CREATE UNIQUE INDEX IF NOT EXISTS person_film_work_role_idx ON person_film_work(person_id, film_work_id, role);

COMMIT;