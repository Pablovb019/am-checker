--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

-- Started on 2025-06-02 14:45:23

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

--
-- TOC entry 5 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- TOC entry 4914 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 256 (class 1255 OID 109867)
-- Name: update_site_statistics(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_site_statistics() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    target_id INTEGER;
    current_date_only DATE := CURRENT_DATE;  -- Usamos solo la fecha
BEGIN
    -- Obtener el ID usando la fecha sin zona horaria
    target_id := EXTRACT(ISODOW FROM current_date_only);

    INSERT INTO public.site_stats (
        id,
        snapshot_date,
        last_updated,
        total_products,
        total_reviews,
        percent_authentic_products,
        percent_robotized_products,
        best_category_authentic_products,
        worst_category_robotized_products,
        best_category_authentic_reviews,
        worst_category_robotized_reviews,
        day_most_analysis,
        hour_interval_most_analysis,
        total_users
    )
    VALUES (
        target_id,
        current_date_only,  -- Fecha sin hora
        CURRENT_TIMESTAMP,  -- Hora exacta con zona horaria
        (SELECT COUNT(*) FROM public.products),
        (SELECT COUNT(*) FROM public.reviews),
        (SELECT COALESCE(AVG((1 - ml_predict_avg) * 100), 0) FROM public.products),
        (SELECT COALESCE(100 - AVG((1 - ml_predict_avg) * 100), 100) FROM public.products),
        (SELECT category FROM (
              SELECT category, AVG(1 - ml_predict_avg) AS avg_authenticity 
              FROM public.products 
              GROUP BY category
              ORDER BY avg_authenticity DESC
              LIMIT 1
             ) AS subquery),
        (SELECT category FROM (
              SELECT category, AVG(1 - ml_predict_avg) AS avg_authenticity 
              FROM public.products 
              GROUP BY category
              ORDER BY avg_authenticity ASC
              LIMIT 1
             ) AS subquery),
        (SELECT category FROM (
              SELECT p.category, AVG(1 - r.ml_predict) AS avg_authenticity 
              FROM public.reviews r
              JOIN public.products p ON p.id = r.product_id
              GROUP BY p.category
              ORDER BY avg_authenticity DESC
              LIMIT 1
             ) AS subquery),
        (SELECT category FROM (
              SELECT p.category, AVG(1 - r.ml_predict) AS avg_authenticity 
              FROM public.reviews r
              JOIN public.products p ON p.id = r.product_id
              GROUP BY p.category
              ORDER BY avg_authenticity ASC
              LIMIT 1
             ) AS subquery),
        (SELECT date(last_scan) FROM public.products GROUP BY date(last_scan) ORDER BY COUNT(*) DESC LIMIT 1),
        (SELECT to_char(date_trunc('hour', last_scan), 'HH24:MI') || '-' ||
                to_char(date_trunc('hour', last_scan) + interval '1 hour', 'HH24:MI') 
         FROM public.products 
         GROUP BY date_trunc('hour', last_scan)
         ORDER BY COUNT(*) DESC
         LIMIT 1),
        (SELECT COUNT(DISTINCT user_id) FROM public.user_sessions)
    )
    ON CONFLICT (id) DO UPDATE SET
        snapshot_date = EXCLUDED.snapshot_date,
        last_updated = EXCLUDED.last_updated,
        total_products = EXCLUDED.total_products,
        total_reviews = EXCLUDED.total_reviews,
        percent_authentic_products = EXCLUDED.percent_authentic_products,
        percent_robotized_reviews = EXCLUDED.percent_robotized_reviews,
        best_category_authentic_products = EXCLUDED.best_category_authentic_products,
        worst_category_robotized_products = EXCLUDED.worst_category_robotized_products,
        best_category_reviews_authentic = EXCLUDED.best_category_reviews_authentic,
        worst_category_reviews_robotized = EXCLUDED.worst_category_reviews_robotized,
        day_most_analysis = EXCLUDED.day_most_analysis,
        hour_interval_most_analysis = EXCLUDED.hour_interval_most_analysis,
        total_users = EXCLUDED.total_users;
END;
$$;


ALTER FUNCTION public.update_site_statistics() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 219 (class 1259 OID 106732)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    id character varying(50) NOT NULL,
    name text NOT NULL,
    description text NOT NULL,
    category text NOT NULL,
    price numeric(10,2) NOT NULL,
    rating numeric(3,2) NOT NULL,
    country character varying(100) NOT NULL,
    country_suffix character varying(10) NOT NULL,
    image_url character varying(500) NOT NULL,
    last_scan timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ml_predict_avg numeric(5,4),
    ml_predict_date timestamp without time zone
);


ALTER TABLE public.products OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 106740)
-- Name: reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reviews (
    id character varying(50) NOT NULL,
    product_id character varying(50) NOT NULL,
    author text NOT NULL,
    rating numeric(3,2),
    date date NOT NULL,
    title text NOT NULL,
    text text NOT NULL,
    ml_predict numeric(5,4),
    CONSTRAINT reviews_rating_check CHECK (((rating >= 1.00) AND (rating <= 5.00)))
);


ALTER TABLE public.reviews OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 109794)
-- Name: site_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.site_stats (
    id integer NOT NULL,
    snapshot_date date DEFAULT CURRENT_TIMESTAMP NOT NULL,
    total_products integer NOT NULL,
    total_reviews integer NOT NULL,
    percent_authentic_products numeric(5,2) NOT NULL,
    percent_robotized_products numeric(5,2) NOT NULL,
    best_category_authentic_products text,
    worst_category_robotized_products text,
    best_category_authentic_reviews text,
    worst_category_robotized_reviews text,
    day_most_analysis date,
    hour_interval_most_analysis text,
    total_users integer NOT NULL,
    last_updated timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.site_stats OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 109763)
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_sessions (
    id integer NOT NULL,
    user_id text NOT NULL,
    accessed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.user_sessions OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 109762)
-- Name: user_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_sessions_id_seq OWNER TO postgres;

--
-- TOC entry 4915 (class 0 OID 0)
-- Dependencies: 236
-- Name: user_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_sessions_id_seq OWNED BY public.user_sessions.id;


--
-- TOC entry 4748 (class 2604 OID 109766)
-- Name: user_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions ALTER COLUMN id SET DEFAULT nextval('public.user_sessions_id_seq'::regclass);


--
-- TOC entry 4754 (class 2606 OID 106739)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- TOC entry 4756 (class 2606 OID 106747)
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- TOC entry 4762 (class 2606 OID 109801)
-- Name: site_stats site_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.site_stats
    ADD CONSTRAINT site_stats_pkey PRIMARY KEY (id);


--
-- TOC entry 4758 (class 2606 OID 118080)
-- Name: user_sessions unique_user_sessions_user_id; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT unique_user_sessions_user_id UNIQUE (user_id);


--
-- TOC entry 4760 (class 2606 OID 109771)
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 4763 (class 2606 OID 106748)
-- Name: reviews fk_reviews_products; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT fk_reviews_products FOREIGN KEY (product_id) REFERENCES public.products(id);


-- Completed on 2025-06-02 14:45:23

--
-- PostgreSQL database dump complete
--

