--
-- PostgreSQL database dump
--

\restrict yktK4rvz33Jc5XFZC5EOq8aYiK23dbMhuEoQqfhH1N1ACiemg4IF1kP7AgqWAr1

-- Dumped from database version 16.13 (Debian 16.13-1.pgdg13+1)
-- Dumped by pg_dump version 16.13 (Debian 16.13-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: user_role; Type: TYPE; Schema: public; Owner: admin
--

CREATE TYPE public.user_role AS ENUM (
    'admin',
    'user',
    'auditor'
);


ALTER TYPE public.user_role OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO admin;

--
-- Name: pdf_chunks; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.pdf_chunks (
    id integer NOT NULL,
    document_id integer NOT NULL,
    chunk_index integer NOT NULL,
    content text NOT NULL,
    start_char integer NOT NULL,
    end_char integer NOT NULL
);


ALTER TABLE public.pdf_chunks OWNER TO admin;

--
-- Name: pdf_chunks_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.pdf_chunks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pdf_chunks_id_seq OWNER TO admin;

--
-- Name: pdf_chunks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.pdf_chunks_id_seq OWNED BY public.pdf_chunks.id;


--
-- Name: pdf_documents; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.pdf_documents (
    id integer NOT NULL,
    original_filename character varying(512),
    stored_filename character varying(512) NOT NULL,
    file_size_bytes integer NOT NULL,
    extracted_text text,
    cleaned_text text,
    processing_error text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.pdf_documents OWNER TO admin;

--
-- Name: pdf_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.pdf_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pdf_documents_id_seq OWNER TO admin;

--
-- Name: pdf_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.pdf_documents_id_seq OWNED BY public.pdf_documents.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(255),
    role public.user_role DEFAULT 'user'::public.user_role NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: pdf_chunks id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.pdf_chunks ALTER COLUMN id SET DEFAULT nextval('public.pdf_chunks_id_seq'::regclass);


--
-- Name: pdf_documents id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.pdf_documents ALTER COLUMN id SET DEFAULT nextval('public.pdf_documents_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.alembic_version (version_num) FROM stdin;
20260408_0002
\.


--
-- Data for Name: pdf_chunks; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.pdf_chunks (id, document_id, chunk_index, content, start_char, end_char) FROM stdin;
1	3	0	DEEPAK MANE\nFull Stack Developer\n​91 9082958346 ​manedeep2001@gmail.com ​https://www.linkedin.com/in/deepak-mane-400a241aa\n​https://github.com/DeepakMane15/ ​Mumbai, India\nSUMMARY SKILLS\nFull Stack Engineer with 2.9 years of experience building scalable SaaS and\nAngular React NextJs NodeJs\nEdtech platforms. Experienced in designing RESTful APIs, implementing\ncomplex third-party integrations SSO, LTI, Microsoft, Google), and\noptimizing application performance 60% API improvement). Strong hands- Express NestJ	0	512
2	3	1	on performance 60% API improvement). Strong hands- Express NestJs JavaScript\non expertise in React, Angular, Node.js, Django, and SQL. Passionate about\nclean architecture, system reliability, and solving ambiguous, high-impact Typescript Python Django\nengineering problems.\nFastAPI SQL MongoDB\nPROJECTS\nTeachers of Tomorrow RabbitMQ Docker Jenkins\n08/2025 - Present\n• Contributing to the development of a custom Learning Management Auth0 KeyCloak AWS\nSystem LMS based on the Open-EDX open-source platform to meet	448	960
3	3	2	WS\nSystem LMS based on the Open-EDX open-source platform to meet\norganization-specific requirements. Redis\n• Developed custom plugins in Django, React micro-frontend, ensuring\nOpen-EDX compliance without modifying the core code.\n• Integrated LTI Learning Tools Interoperability) components, enabling EDUCATION\ninteroperability with third-party learning tools.\n• Tech: Django, React, MySQL, MongoDB. Bachelor of Engineering\nShah and Anchor Kutchhi Engineering\nPASCO Portal\nCollege\n08/2023 - 07/2025\n08/2019 - 05/2	896	1408
4	3	3	ngineering\nPASCO Portal\nCollege\n08/2023 - 07/2025\n08/2019 - 05/2023 Chembur, Mumbai, India\nhttps://portal.pasco.com\n• Implemented Clever Class-link, LTI Learning Tools Interoperability)\nEXPERIENCE\nAPIs for single sign-on and student roster management, reducing manual\nonboarding effort by 40%.\nSenior Software Engineer\n• Integrated Microsoft SSO, Resource Sharing, and Google Classroom\nAPIs for seamless authentication, data sync, and resource distribution. Zeus Learning\n• Optimized application architecture and	1344	1856
5	3	4	ribution. Zeus Learning\n• Optimized application architecture and Google Lighthouse scores,\n07/2023 - Present Mumbai, India\nimproving load times by 30%, accessibility, and SEO best practices.\n• Full-stack developer responsible for\n• Designed Microservices Backend Architecture.\narchitecting, developing, and deploying a\n• Optimized Stored Procedures and introduced Redis caching, improving\nLearning Management System LMS portal.\nAPI response times by over 60%.\n• Oversaw end-to-end feature development,\n• Tech: An	1792	2304
6	3	5	y over 60%.\n• Oversaw end-to-end feature development,\n• Tech: Angular, NodeJS, Express, MySQL, MongoDB, Elastic, RabbitMQ.\nperformance optimization, and security\nAMRC (ODR System) enhancements while collaborating with cross-\nfunctional teams in an Agile environment.\nhttps://arbitcase.com\nSoftware Developer (Internship)\n• Created an Online Dispute Resolution system enabling banks and legal\nfirms to manage and track loan default cases. Synccit Solutions Pvt. Ltd\n• Integrated AWS Amplify for managing and uploa	2240	2752
7	3	6	lutions Pvt. Ltd\n• Integrated AWS Amplify for managing and uploading case-related\n09/2021 - 05/2022 Mumbai, India\ndocuments to AWS S3.\n• Worked as a full-stack development intern\n• Built Excel bulk upload pipeline with async processing via RabbitMQ.\nassisting in the development of web\n• Automated PDF generation of case templates using RTE and Puppeteer,\napplications using React, Node.js, and MySQL.\nreducing manual effort.\n• Built reusable UI components and resolved\n• Integrated WATI WhatsApp API, SMS Gatewa	2688	3200
8	3	7	mponents and resolved\n• Integrated WATI WhatsApp API, SMS Gateway Hub, and Zoho Mail to\nfront-end bugs, resulting in a 20% boost in\nautomate the delivery communication workflow.\ninterface responsiveness and smoother UX.\n• Tech: NextJs, NodeJs, Express, MySQL, RabbitMQ.\nVOLUNTEERING\nKEY ACHIEVEMENTS\nIT Volunteer (Frontend Lead)\nOpen-EDX Customization\nSant Nirankari Mission\nMade custom Tutor plugins and React micro-frontends.\n2023 - Present\nRoster Automation\nTechnical Volunteer at Sant Nirankari Mission\nImple	3136	3648
9	3	8	r Automation\nTechnical Volunteer at Sant Nirankari Mission\nImplemented Clever, Class-link, and LTI APIs, reducing manual onboarding supporting project development and maintenance.\neffort by 40% Contributed expertise to transformative digital\ninitiatives. Privileged to be part of a noble cause.\nPerformance Optimization\nEnhanced application performance by 30% through architectural\nimprovements and Google Lighthouse optimization.	3584	4014
\.


--
-- Data for Name: pdf_documents; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.pdf_documents (id, original_filename, stored_filename, file_size_bytes, extracted_text, cleaned_text, processing_error, created_at) FROM stdin;
3	DeepakMane-Resume.pdf	6412425e556b4f2f8c368e18a29e1f98_DeepakMane-Resume.pdf	155597	DEEPAK MANE\nFull Stack Developer\n​91 9082958346 ​manedeep2001@gmail.com ​https://www.linkedin.com/in/deepak-mane-400a241aa\n​https://github.com/DeepakMane15/ ​Mumbai, India\nSUMMARY SKILLS\nFull Stack Engineer with 2.9 years of experience building scalable SaaS and\nAngular React NextJs NodeJs\nEdtech platforms. Experienced in designing RESTful APIs, implementing\ncomplex third-party integrations SSO, LTI, Microsoft, Google), and\noptimizing application performance 60% API improvement). Strong hands- Express NestJs JavaScript\non expertise in React, Angular, Node.js, Django, and SQL. Passionate about\nclean architecture, system reliability, and solving ambiguous, high-impact Typescript Python Django\nengineering problems.\nFastAPI SQL MongoDB\nPROJECTS\nTeachers of Tomorrow RabbitMQ Docker Jenkins\n08/2025 - Present\n• Contributing to the development of a custom Learning Management Auth0 KeyCloak AWS\nSystem LMS based on the Open-EDX open-source platform to meet\norganization-specific requirements. Redis\n• Developed custom plugins in Django, React micro-frontend, ensuring\nOpen-EDX compliance without modifying the core code.\n• Integrated LTI Learning Tools Interoperability) components, enabling EDUCATION\ninteroperability with third-party learning tools.\n• Tech: Django, React, MySQL, MongoDB. Bachelor of Engineering\nShah and Anchor Kutchhi Engineering\nPASCO Portal\nCollege\n08/2023 - 07/2025\n08/2019 - 05/2023 Chembur, Mumbai, India\nhttps://portal.pasco.com\n• Implemented Clever Class-link, LTI Learning Tools Interoperability)\nEXPERIENCE\nAPIs for single sign-on and student roster management, reducing manual\nonboarding effort by 40%.\nSenior Software Engineer\n• Integrated Microsoft SSO, Resource Sharing, and Google Classroom\nAPIs for seamless authentication, data sync, and resource distribution. Zeus Learning\n• Optimized application architecture and Google Lighthouse scores,\n07/2023 - Present Mumbai, India\nimproving load times by 30%, accessibility, and SEO best practices.\n• Full-stack developer responsible for\n• Designed Microservices Backend Architecture.\narchitecting, developing, and deploying a\n• Optimized Stored Procedures and introduced Redis caching, improving\nLearning Management System LMS portal.\nAPI response times by over 60%.\n• Oversaw end-to-end feature development,\n• Tech: Angular, NodeJS, Express, MySQL, MongoDB, Elastic, RabbitMQ.\nperformance optimization, and security\nAMRC (ODR System) enhancements while collaborating with cross-\nfunctional teams in an Agile environment.\nhttps://arbitcase.com\nSoftware Developer (Internship)\n• Created an Online Dispute Resolution system enabling banks and legal\nfirms to manage and track loan default cases. Synccit Solutions Pvt. Ltd\n• Integrated AWS Amplify for managing and uploading case-related\n09/2021 - 05/2022 Mumbai, India\ndocuments to AWS S3.\n• Worked as a full-stack development intern\n• Built Excel bulk upload pipeline with async processing via RabbitMQ.\nassisting in the development of web\n• Automated PDF generation of case templates using RTE and Puppeteer,\napplications using React, Node.js, and MySQL.\nreducing manual effort.\n• Built reusable UI components and resolved\n• Integrated WATI WhatsApp API, SMS Gateway Hub, and Zoho Mail to\nfront-end bugs, resulting in a 20% boost in\nautomate the delivery communication workflow.\ninterface responsiveness and smoother UX.\n• Tech: NextJs, NodeJs, Express, MySQL, RabbitMQ.\nVOLUNTEERING\nKEY ACHIEVEMENTS\nIT Volunteer (Frontend Lead)\nOpen-EDX Customization\nSant Nirankari Mission\nMade custom Tutor plugins and React micro-frontends.\n2023 - Present\nRoster Automation\nTechnical Volunteer at Sant Nirankari Mission\nImplemented Clever, Class-link, and LTI APIs, reducing manual onboarding supporting project development and maintenance.\neffort by 40% Contributed expertise to transformative digital\ninitiatives. Privileged to be part of a noble cause.\nPerformance Optimization\nEnhanced application performance by 30% through architectural\nimprovements and Google Lighthouse optimization.	DEEPAK MANE\nFull Stack Developer\n​91 9082958346 ​manedeep2001@gmail.com ​https://www.linkedin.com/in/deepak-mane-400a241aa\n​https://github.com/DeepakMane15/ ​Mumbai, India\nSUMMARY SKILLS\nFull Stack Engineer with 2.9 years of experience building scalable SaaS and\nAngular React NextJs NodeJs\nEdtech platforms. Experienced in designing RESTful APIs, implementing\ncomplex third-party integrations SSO, LTI, Microsoft, Google), and\noptimizing application performance 60% API improvement). Strong hands- Express NestJs JavaScript\non expertise in React, Angular, Node.js, Django, and SQL. Passionate about\nclean architecture, system reliability, and solving ambiguous, high-impact Typescript Python Django\nengineering problems.\nFastAPI SQL MongoDB\nPROJECTS\nTeachers of Tomorrow RabbitMQ Docker Jenkins\n08/2025 - Present\n• Contributing to the development of a custom Learning Management Auth0 KeyCloak AWS\nSystem LMS based on the Open-EDX open-source platform to meet\norganization-specific requirements. Redis\n• Developed custom plugins in Django, React micro-frontend, ensuring\nOpen-EDX compliance without modifying the core code.\n• Integrated LTI Learning Tools Interoperability) components, enabling EDUCATION\ninteroperability with third-party learning tools.\n• Tech: Django, React, MySQL, MongoDB. Bachelor of Engineering\nShah and Anchor Kutchhi Engineering\nPASCO Portal\nCollege\n08/2023 - 07/2025\n08/2019 - 05/2023 Chembur, Mumbai, India\nhttps://portal.pasco.com\n• Implemented Clever Class-link, LTI Learning Tools Interoperability)\nEXPERIENCE\nAPIs for single sign-on and student roster management, reducing manual\nonboarding effort by 40%.\nSenior Software Engineer\n• Integrated Microsoft SSO, Resource Sharing, and Google Classroom\nAPIs for seamless authentication, data sync, and resource distribution. Zeus Learning\n• Optimized application architecture and Google Lighthouse scores,\n07/2023 - Present Mumbai, India\nimproving load times by 30%, accessibility, and SEO best practices.\n• Full-stack developer responsible for\n• Designed Microservices Backend Architecture.\narchitecting, developing, and deploying a\n• Optimized Stored Procedures and introduced Redis caching, improving\nLearning Management System LMS portal.\nAPI response times by over 60%.\n• Oversaw end-to-end feature development,\n• Tech: Angular, NodeJS, Express, MySQL, MongoDB, Elastic, RabbitMQ.\nperformance optimization, and security\nAMRC (ODR System) enhancements while collaborating with cross-\nfunctional teams in an Agile environment.\nhttps://arbitcase.com\nSoftware Developer (Internship)\n• Created an Online Dispute Resolution system enabling banks and legal\nfirms to manage and track loan default cases. Synccit Solutions Pvt. Ltd\n• Integrated AWS Amplify for managing and uploading case-related\n09/2021 - 05/2022 Mumbai, India\ndocuments to AWS S3.\n• Worked as a full-stack development intern\n• Built Excel bulk upload pipeline with async processing via RabbitMQ.\nassisting in the development of web\n• Automated PDF generation of case templates using RTE and Puppeteer,\napplications using React, Node.js, and MySQL.\nreducing manual effort.\n• Built reusable UI components and resolved\n• Integrated WATI WhatsApp API, SMS Gateway Hub, and Zoho Mail to\nfront-end bugs, resulting in a 20% boost in\nautomate the delivery communication workflow.\ninterface responsiveness and smoother UX.\n• Tech: NextJs, NodeJs, Express, MySQL, RabbitMQ.\nVOLUNTEERING\nKEY ACHIEVEMENTS\nIT Volunteer (Frontend Lead)\nOpen-EDX Customization\nSant Nirankari Mission\nMade custom Tutor plugins and React micro-frontends.\n2023 - Present\nRoster Automation\nTechnical Volunteer at Sant Nirankari Mission\nImplemented Clever, Class-link, and LTI APIs, reducing manual onboarding supporting project development and maintenance.\neffort by 40% Contributed expertise to transformative digital\ninitiatives. Privileged to be part of a noble cause.\nPerformance Optimization\nEnhanced application performance by 30% through architectural\nimprovements and Google Lighthouse optimization.	\N	2026-04-08 17:34:38.721042+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.users (id, email, hashed_password, full_name, role, is_active, created_at) FROM stdin;
1	admin@gmail.com	$2b$12$w3k.dUV/6Za95n6VHlsWo.Gwvs4nrIybWHxjC8L8GoHwbcEU80Uui	\N	admin	t	2026-04-08 17:15:05.487394+00
\.


--
-- Name: pdf_chunks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.pdf_chunks_id_seq', 9, true);


--
-- Name: pdf_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.pdf_documents_id_seq', 3, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: pdf_chunks pdf_chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.pdf_chunks
    ADD CONSTRAINT pdf_chunks_pkey PRIMARY KEY (id);


--
-- Name: pdf_documents pdf_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.pdf_documents
    ADD CONSTRAINT pdf_documents_pkey PRIMARY KEY (id);


--
-- Name: pdf_chunks uq_pdf_chunk_document_index; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.pdf_chunks
    ADD CONSTRAINT uq_pdf_chunk_document_index UNIQUE (document_id, chunk_index);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_pdf_chunks_document_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_pdf_chunks_document_id ON public.pdf_chunks USING btree (document_id);


--
-- Name: ix_pdf_documents_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_pdf_documents_id ON public.pdf_documents USING btree (id);


--
-- Name: ix_pdf_documents_stored_filename; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX ix_pdf_documents_stored_filename ON public.pdf_documents USING btree (stored_filename);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: pdf_chunks pdf_chunks_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.pdf_chunks
    ADD CONSTRAINT pdf_chunks_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.pdf_documents(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict yktK4rvz33Jc5XFZC5EOq8aYiK23dbMhuEoQqfhH1N1ACiemg4IF1kP7AgqWAr1

