--
-- PostgreSQL database dump
--

\restrict U2g6tpJHyruFs9BpjieSfYg9T0UubHl8CuG4d8H5Z1Zg1DZ1rG589IDivHcfgPo

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: languages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.languages (
    id integer NOT NULL,
    code text NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.languages OWNER TO postgres;

--
-- Name: languages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.languages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.languages_id_seq OWNER TO postgres;

--
-- Name: languages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.languages_id_seq OWNED BY public.languages.id;


--
-- Name: terms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.terms (
    id_vocabulary integer NOT NULL,
    english_term text,
    target_language_term text,
    transliteration text,
    example_sentence text,
    example_sentence_explained text,
    notes text,
    learned integer,
    correct_counter integer
);


ALTER TABLE public.terms OWNER TO postgres;

--
-- Name: terms_id_vocabulary_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.terms_id_vocabulary_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.terms_id_vocabulary_seq OWNER TO postgres;

--
-- Name: terms_id_vocabulary_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.terms_id_vocabulary_seq OWNED BY public.terms.id_vocabulary;


--
-- Name: vocab_raw; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vocab_raw (
    english text,
    target_script text,
    transliteration text,
    sample_sentence_target text,
    sample_sentence_explained text,
    notes text,
    learned numeric,
    correct_counter numeric
);


ALTER TABLE public.vocab_raw OWNER TO postgres;

--
-- Name: languages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.languages ALTER COLUMN id SET DEFAULT nextval('public.languages_id_seq'::regclass);


--
-- Name: terms id_vocabulary; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.terms ALTER COLUMN id_vocabulary SET DEFAULT nextval('public.terms_id_vocabulary_seq'::regclass);


--
-- Name: languages languages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.languages
    ADD CONSTRAINT languages_pkey PRIMARY KEY (id);


--
-- Name: terms terms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.terms
    ADD CONSTRAINT terms_pkey PRIMARY KEY (id_vocabulary);


--
-- PostgreSQL database dump complete
--

\unrestrict U2g6tpJHyruFs9BpjieSfYg9T0UubHl8CuG4d8H5Z1Zg1DZ1rG589IDivHcfgPo

