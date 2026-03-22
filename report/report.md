---
title: "Plural"
subtitle: |
  **Identity and Profile Management Service**

  *One Identity, Many Dimensions*
toc: true
---

## 1. Introduction

### 1.1 Code Repository

The full source code for this project is publicly available at: [https://github.com/ahmadelmalah/plural](https://github.com/ahmadelmalah/plural)

### 1.2 Selected Template
7.1 Project Idea 1: Identity and profile management API

### 1.3 Challenge Overview: Digital Identity Fragmentation

Modern digital platforms are designed to capture or focus on a certain dimensions of human identities. When users engage with these platforms, they are expected to show the identity, the dimension and the role suited to that environment. For example, LinkedIn is designed to highlight the professional persona; it is a space where sharing an Azure certification is appropriate, but sharing a gaming high score would be out of context. Conversely, a platform like Steam captures the recreational "gamer" dimension, while Goodreads captures the intellectual "reader" dimension.

However, while these dimensions are distinct in function, focus and interest they belong to a single human entity. The current digital infrastructure fails to reflect this unity. These platforms operate as isolated silos, unaware of the user's existence outside their specific boundary. This fragmentation is not just a technical inconvenience. Research shows that people naturally present different sides of themselves in different social contexts [1], and that current platforms force all these audiences into one view, a phenomenon known as "context collapse" [2].

**Centralized Identity Management:** The user lacks a centralized mechanism to manage these fragmented selves. Instead, they must manually duplicate data across different systems, leading to administrative friction and a loss of holistic control over their digital footprint.

**Public multidimensional Identity:** This presents another challenge, particularly for individuals with diverse interests. These users want to reflect a multidimensional public picture of themselves; for example: 'I am a software engineer, but also a reader interested in philosophy and a gamer who loves Chess and League of Legends'. A definition that spans different dimensions.

**Private Identity:** Equally important is the need for privacy and boundary enforcement. While users want to show multiple sides of themselves, they also need to keep other sides strictly confidential. For instance, a user must share their legal identity for government services but may need to hide it from online gaming communities for safety. Currently, users lack the granular control to ensure that sensitive private attributes do not leak into inappropriate contexts.

**Conclusion:** To bridge these gaps, we need a centralized system where users can manage their identity dimensions, choosing what to share publicly and what to keep private, while integrating seamlessly with existing external platforms via a RESTful API.

### 1.4 Solution Overview

The project aims for implementing a centralized place for orchestrating the digital multidimensional identity, by allowing the users to manage the identity as an aggregation of distinct personas. Each persona belongs to a **Context**, an identity dimension (e.g. Professional, Gaming, Legal) that categorises what aspect of the user's life this persona represents. A persona has its own set of attributes relevant to that context, and is set to be either public or private (protected access). Both the API and the web interface support filtering personas by context, so a recruiter can query only the "Professional" context while a gaming friend can view the "Gaming" context.

Each user will have a general profile that presents all of the user's public personas and what they want to share about themselves (e.g., professional persona, reader persona, gamer persona), while strictly hiding confidential personas (e.g., legal persona).

The system responds dynamically based on the context. If a recruiter queries the profile, they will see only LinkedIn and GitHub accounts; however, if a gamer friend explores the platform, they may see the gamer identity. This means that a single user endpoint can yield completely different JSON responses depending on the negotiation context.

**The Final Outcome:** The system provides both a REST API for programmatic access and a web interface (GUI) that allows users to manage their personas through a browser.

### 1.5 Solution Scope

It's important to define a clear scope to avoid any scope creep

**What this project IS:** The application is a Representation Layer: it manages how a user presents themselves in different contexts. Users create multiple personas, each belonging to a context (e.g. Professional, Gaming, Legal) with its own attributes and a public/private visibility toggle. The system exposes these personas through a REST API and a web interface, enforcing privacy boundaries so that the same profile returns different data depending on who is asking. The core contribution is contextual identity projection, not authentication or access control.

**What this project is NOT:** To clarify the specific contribution of this work, it is important to distinguish it from existing terms:

- **This is not an IAM Service:** While the terminology (i.e. identity management) is similar to cloud services like AWS IAM or Azure AD, they serve different purposes. Cloud IAM manages permissions for infrastructure resources, whereas this project manages user profile contexts, they focus on authentication while this project focuses on representation.

- **This is not a Single Sign-On (SSO) Solution:** The goal is not to provide a mechanism where users sign in once to access multiple platforms without sharing credentials.

In practice, the system supports two authentication methods: a built-in session-based flow (email/password) and a delegated flow via AWS Cognito using OIDC. The persona logic is completely independent of how the user authenticated. The design philosophy is integration, not competition: the application delegates authentication to dedicated identity providers and focuses on persona management.

### 1.6 Motivation

**Personal Motivation:** I am deeply interested in backend web development, security and identity management systems. My passion lies in building secure, scalable APIs that act as bridges between disconnected platforms. For me, this project is not just a requirement; it is an opportunity to build the kind of structural, data-driven tool that I personally enjoy using.

**Domain Opportunity:** The current software market is already saturated with strong solutions for Authentication ("Who are you?") and Authorization ("What are you allowed to do?") [3][4][5]. However, there is a significant gap when it comes to Representation ("How do you appear in this context?").

---

## 2. Literature Review

### 2.1 Introduction

Digital identity representation exists at the intersection of human sociological behavior and software engineering architecture. To propose a robust solution, it is necessary to examine research from both domains: the human studies that define why we fragment our identities, and the technical studies that define how current systems manage them. This chapter evaluates the current digital status quo, analyzing relevant projects, protocols, and services to identify the specific architectural gap this project intends to fill.

### 2.2 Defining Digital Identity

Before designing a system to manage identity, we must establish a working definition of the term.

From a technical perspective, industry leaders offer converging definitions. Oracle defines digital identity as "a collection of data points that comprise the characteristics, attributes, and activities that identify an entity" [6]. Cloudflare views it as "the recorded set of measurable characteristics by which a computer can identify an external entity" [7]. IBM defines it as "a profile or set of information tied to a specific user, machine or other entity in an IT ecosystem" [8].

These definitions treat identity as a single fixed profile. But that does not match how people actually behave. Goffman (1959) argued that people naturally perform different roles in different social situations, we act differently in a job interview than we do with friends, not because we are being dishonest, but because different settings call for different presentations of ourselves [1]. This idea that identity is not one thing but many context-dependent facets is central to this project.

Clauß and Kohntopp (2001) brought this idea into computer science with the concept of "partial identities", the different subsets of a person's attributes used in different contexts [9]. They argued that identity management systems should let users control which partial identity is shown to which party. This is essentially what this project calls a "Persona."

The problem is that most current platforms do the opposite. Marwick and boyd (2011) describe "context collapse", when social media flattens all your audiences into one, so a post meant for friends is also visible to your employer [2]. The user loses the ability to show different sides of themselves to different people.

Nissenbaum (2004) explains why this matters from a privacy perspective. Her theory of "contextual integrity" says that privacy is not about hiding information, but about information flowing to the right context [10]. Sharing your legal name with a bank is normal; having it exposed in a gaming forum is a violation of context. This framework supports the design decision behind Plural's per-persona privacy controls, each persona belongs to a context, and the system enforces boundaries between them.

**Synthesis:** From these definitions, we can conclude that Digital Identity is fundamentally a set of information and attributes representing a profile. But the academic literature shows that this set is not one thing, it is made up of context-dependent subsets (what Clauß and Kohntopp call "partial identities" [9] and what this project calls "Personas"). Current platforms collapse these contexts [2], and the goal of this project is to restore those boundaries by giving users control over which part of their identity is visible in which context.

### 2.3 Comparative Analysis of Existing Systems

The current technological landscape is full by numerous systems, technologies and services that address distinct but adjacent challenges. However they solve slightly different set of problems and they solve them from different angles or using fundamentally different approaches, so it's a good idea to take a look at some of them.

#### 2.3.1 Cloud-based Identity and Access Management Services (IAM)

The dominant standard in the current web ecosystem is Identity and Access Management (IAM). IAM systems manage digital identities and control user access to resources, ensuring that the right people can access the right systems at the right time [3][4][5]. In practice, this means IAM is built around two core questions: Authentication ("Is this user who they claim to be?") and Authorization ("Is this user allowed to access this resource?").

Neither of these addresses a third question that this project focuses on: Representation ("Which dimension of this user should appear in this context?"). An IAM system can verify that a user is "John Doe" and that he is allowed to access a resource, but it cannot present him as a "gamer" to one visitor and as a "lawyer" to another. The data model of IAM systems does not support multiple contextual projections of the same identity.

It is worth noting that Cameron (2005) proposed seven "Laws of Identity" for building identity systems, including principles like user control, minimal disclosure, and support for multiple operators [11]. These principles recognise that users should only reveal the minimum information necessary for each interaction, an idea that aligns with this project's approach of exposing only relevant personas per context. However, mainstream IAM implementations have focused on the authentication and authorisation aspects rather than on contextual self-presentation.

**Integration not Replacement:** The proposed project is not a replacement for IAM but a complement to it. Architecturally, the system functions as a representation layer that sits on top of existing IAM infrastructure. IAM handles the security question (who are you?), while Plural handles the presentation question (which version of you should this visitor see?). The two layers are designed to work together, not compete.

#### 2.3.2 Blockchain-Based Identity Management System (IDMS)

Several researches focuses on Decentralized Identity Management Systems (IDMS), often leveraging blockchain technology to address privacy and ownership concerns.

Alanzi and Alkhatib (2025) discuss the privacy and security threats related to traditional systems: "Traditional IDMS relies on a third party to store user information and authenticate the user. However, this approach poses threats to user privacy and increases the risk of single point of failure (SPOF), user tracking, and data unavailability" [12].

They suggest that modern blockchain-based systems could overcome these challenges: "In contrast, decentralized IDMSs that use blockchain technology offer potential solutions to these issues as they offer powerful features including immutability, transparency, anonymity, and decentralization" [12].

However, the authors are realistic about the limitations of this technology: "Despite its advantages, blockchain technology also suffers from limitations related to performance, third-party control, weak authentication, and data leakages. Furthermore, some blockchain-based IDMSs still exhibit centralization issues, which can compromise user privacy and create SPOF risks" [12].

**Blockchain Limitation:** Despite these advantages, blockchain solutions suffer from low adoption rates, performance bottlenecks, weak authentication mechanisms (private key management), and complexity. Furthermore, they often require a complete paradigm shift, both the user and the visiting platform must adopt Web3 standards (Wallets, Smart Contracts).

**Differentiation:** Both blockchain-based IDMS and this project share the goal of giving users more control over their data. However, they differ fundamentally in approach. Blockchain systems require both the user and every consuming platform to adopt Web3 infrastructure (wallets, smart contracts, decentralised protocols). This creates a high adoption barrier. The proposed project takes a pragmatic approach: it uses standard RESTful APIs that any existing web application can consume without adopting new protocols. A game client or a recruitment platform can query a user's persona via a simple HTTP request, no blockchain integration required. The trade-off is that the system is centralised (the user trusts the Plural server), but in return it gains simplicity, performance, and compatibility with the existing web.

#### 2.3.3 Federated Identity and Social Login (OAuth 2.0 & OIDC)

Federated Identity handles cross-platform identity through protocols like OAuth 2.0 and OpenID Connect (OIDC), popularly known as "Log in with Google" or "Log in with Facebook." The core idea is that a user authenticates once with a trusted Identity Provider (IdP) and can then access multiple third-party applications without creating separate accounts for each one [13][14][15].

In practice, when a user logs in via an IdP, the application receives a "User Info" bundle, typically a name, email, and profile picture. The user gets convenience (one login for many services), and the application gets verified identity data without handling passwords itself.

**Differentiation:** Federated access and this project address related but distinct problems. Federated access solves the problem of using *the same identity* across different platforms, one login for many services. This project solves the opposite problem: presenting *different facets of the same identity* depending on the context. OAuth can tell a service "this is John Doe," but it cannot tell one service "show John's gaming profile" and another service "show John's professional profile." The User Info bundle shared by an IdP is a fixed set of attributes (name, email, picture); it has no concept of contextual personas or privacy toggles. Plural fills this gap by adding a representation layer on top of the authentication layer.

#### 2.3.4 Identity Aggregators (Link-in-Bio Tools)

While the previous sections covered infrastructure-level solutions, there is also a user-facing category of tools that addresses identity fragmentation directly. Platforms such as Linktree, Carrd, and About.me, commonly known as "link-in-bio" tools, allow users to create a single landing page containing links to all their profiles across different platforms (e.g., Instagram, LinkedIn, GitHub, Spotify). They serve as a "digital business card" that routes visitors to the user's presence elsewhere on the web.

**Limitation:** Despite their popularity, these tools have significant limitations regarding the goals of this project:

- **Static Landing Pages:** These pages are static; they present the exact same list of links to every visitor. The user cannot choose to show their LinkedIn to a recruiter while hiding their Spotify playlist.

- **Lack of Granular Control:** The user lacks the ability to define distinct "Personas." There is no mechanism to group attributes into logical dimensions (e.g., a "Work Mode" vs. a "Social Mode")

- **Technical Isolation:** These tools are designed for human navigation, not system integration. They lack a RESTful API to support programmatic integration with existing systems, making them unsuitable for the architectural role of an identity middleware.

**Differentiation:** Identity Aggregators and this project both attempt to centralise a user's fragmented digital presence, but they differ in three key ways. First, aggregators are static, every visitor sees the same page, whereas Plural returns different data depending on the access context. Second, aggregators lack privacy controls, there is no mechanism to hide certain links from certain visitors, whereas Plural enforces public/private boundaries per persona. Third, aggregators are designed for human browsing (HTML pages), not machine consumption; they lack APIs that would allow a third-party application to programmatically retrieve a user's gamer profile or professional credentials. Plural addresses all three of these limitations.

---

## 3. Design

### 3.1 Project Overview

This project is a web application called **Plural** that allows users to manage multiple digital personas from a single account. The core concept is simple: a user signs up once, and then creates as many personas as they need. Each persona belongs to a **Context** (e.g., "Professional," "Gaming," "Legal"), which represents a specific dimension of the user's identity. A persona has its own set of attributes (stored as flexible JSON data) and a visibility setting: **public** (visible to anyone) or **private** (accessible only with a secret access token). Visitors can filter a user's public personas by context, viewing only the dimension relevant to them.

The system has two interfaces:

1. **A REST API**, the primary product. Third-party applications, recruiters, or other systems can query a user's profile programmatically. When they do, the API returns only the user's public personas. Private personas are completely hidden unless the caller provides the correct access token in the request header. This means the same API endpoint can return different data depending on who is asking.

2. **A web interface**, a browser-based dashboard where users can log in, create/edit/delete personas, toggle visibility, and share their public profile via a URL (`/u/{username}`).

The architecture follows a standard three-tier pattern: the FastAPI application serves both the API and the web interface, backed by a PostgreSQL database. The privacy enforcement logic sits in the application layer, filtering persona data before it reaches the response.

### 3.2 Domain and Target Audience

The project operates within the domain of Privacy Engineering and Identity Management (IdM). It addresses the friction between modern privacy needs and the rigid "Single Sign-On" structures of the current web. The academic literature supports the need for this kind of system: Clauß and Kohntopp (2001) argued that identity management systems should support "partial identities" that users can selectively disclose [9], and Nissenbaum (2004) showed that privacy violations occur when information flows outside its intended context [10]. This project is a practical attempt to implement those principles.

**Target Audience:**

- **Individuals with conflicting digital reputations:** People who maintain different roles that should not mix, for example a corporate lawyer who is also a competitive streamer, or a teacher who is also active in political advocacy. These users need strict boundaries between their public-facing identities.

- **Freelancers and multi-discipline professionals:** People who work across different industries or clients and need to present relevant credentials to each audience without exposing unrelated work. A designer who also does security consulting does not want their gaming profile visible to a corporate client.

- **Privacy-conscious users:** Individuals who want to compartmentalise their online presence for safety reasons, for example keeping a legal identity separate from online communities where anonymity is expected.

- **Third-party developers:** Engineers building applications that need user profile data (like a nickname or avatar) without handling the liability of storing Personally Identifiable Information (PII). The REST API allows them to query only the relevant persona without accessing the user's full identity.

### 3.3 System Architecture

The system follows a three-tier architecture. At the top layer, two types of clients interact with the application: human users through a browser (the web interface) and external systems through HTTP requests (the REST API). Both hit the same FastAPI application server, which handles routing, authentication, input validation (via Pydantic), and the privacy enforcement logic. The application server communicates with a PostgreSQL database through SQLAlchemy ORM.

**[Figure 1: System Architecture Diagram]**

### 3.4 Design and Architectural Choices

The following sections describe the key technical decisions I made and the reasoning behind each one.

#### 3.4.1 Authentication Strategy (Dual Auth)

**Decision:** Dual authentication: built-in session-based (email/password) plus delegated AWS Cognito via OIDC

**Justification:** Building a fully-featured authentication system from scratch (handling MFA, social login, and password reset flows) is error-prone and distracts from the core innovation of "Persona Management." I initially implemented a simpler session-based authentication using password hashing and cookies, which gave me a working auth layer without the integration overhead. Later, I added AWS Cognito as a second authentication method using the OpenID Connect (OIDC) Authorization Code flow. This gives users the choice: they can register with email/password directly, or sign up through Cognito's hosted UI. Both methods end in the same session-based login, and the persona logic depends only on `user_id`, not on how the user authenticated. This separation was a deliberate design choice that made the Cognito integration straightforward to add without touching the core persona code.

#### 3.4.2 API-First Design (REST)

**Decision:** The core product is a RESTful API

**Justification:** Identity service is an infrastructure component. For this system to be scalable, it must be consumable by other machines (e.g., a game client requesting a user's "Gamer Profile"). A visual dashboard is provided for configuration, but the primary value is delivered via JSON responses to API consumers.

#### 3.4.3 Backend Framework

**Decision:** FastAPI (migrated from an initial Flask prototype)

**Justification:** I initially chose Flask for its micro-framework philosophy, which allowed rapid prototyping of the routing logic and offered granular control over the HTTP response lifecycle. However, after building the prototype, I migrated to FastAPI for several benefits that proved valuable in practice:

- **Native Asynchronous Support (ASGI):** FastAPI is built on Starlette, allowing for non-blocking I/O. This matters for an identity service that may eventually need to query external APIs.

- **Strict Data Validation (Pydantic):** FastAPI uses Pydantic for request and response validation. This was a significant improvement over Flask, where I was doing manual dictionary manipulation. I defined separate response models for public responses (which exclude the `access_token`) and owner responses (which include it). Pydantic handles the filtering automatically at the framework level, which is more reliable.

- **Automatic Documentation:** FastAPI generates an interactive Swagger UI at `/docs`, which made testing the API much easier during development and would make it straightforward for third-party developers to consume.

#### 3.4.4 Database Engine

**Decision:** PostgreSQL (migrated from an initial SQLite prototype)

**Justification:** I initially chose SQLite for prototyping because it required no setup and let me focus on the application logic. The application uses SQLAlchemy ORM, which made the eventual migration straightforward. I migrated to PostgreSQL running inside Docker, which gives proper concurrent access, better JSON handling, and a setup that more closely resembles a production environment. The tests still use an in-memory SQLite database for speed and isolation.

### 3.5 Database Design

I decided to start with three main tables representing the core entities:

- **Users Table:** The biological entity/account holder
- **Contexts Table:** The identity dimension that a persona belongs to (e.g. Professional, Gaming, Legal). Contexts define the categories of identity; personas are the user's specific projection within that category
- **Personas Table:** The dimension or the projection for a certain context (e.g. A single user could have a gamer persona, a reader persona, a legal persona, and a professional persona). Each persona must belong to exactly one context

#### Users Table

**Table 1:** Users Table Schema

| Column | Description |
|--------|-------------|
| id | Table Primary Key |
| email | The user's email address (unique) |
| username | A public username for the user (unique) |
| password_hash | Hashed password for session-based authentication (nullable; Cognito users have no local password) |
| cognito_sub | The unique subject identifier from AWS Cognito (nullable, unique). Present only for users who authenticated via Cognito OIDC |
| created_at | The registration date of the user |
| updated_at | Last time the user has updated their information |

#### Contexts Table

**Table 2:** Contexts Table Schema

| Column | Description |
|--------|-------------|
| id | Table Primary Key |
| name | The name of the identity dimension (e.g. Professional, Gaming, Legal). Must be unique |
| description | An optional description of what this context represents |
| created_at | When was the context created |
| updated_at | When was the context last updated |

#### Personas Table

**Table 3:** Personas Table Schema

| Column | Description |
|--------|-------------|
| id | Table Primary Key |
| user_id | A foreign key to link the persona with a user (One to many relationship) |
| context_id | A foreign key to link the persona with a context (Many to one relationship). Every persona must belong to a context |
| name | Name of the persona (e.g. Freelancer, Dota 2 Player, Designer) |
| is_public | Determines of the persona is publicly accessible for all visitors |
| access_token | Required if the persona is private, which is a security key used to access the persona |
| Data | The actual unique attributes and values of this persona, this field is JSON to keep it flexible; for example a gamer persona could have Steam ID while a professional persona could have linkedin profile or Github account |
| created_at | When was the persona created |
| updated_at | When was the last time the persona was updated |

**[Figure 2: Entity Relationship Diagram]**

---

## 4. Implementation

### 4.1 Technical Stack

After the prototyping phase with Flask and SQLite, I migrated the project to a stack that better suits the requirements:

- **Web Framework:** FastAPI (running on Uvicorn, an ASGI server)
- **Database:** PostgreSQL 16 (running in Docker)
- **ORM:** SQLAlchemy with Alembic for migrations
- **Validation:** Pydantic for request/response schemas
- **Authentication:** Dual: session-based (cookies) with bcrypt password hashing, plus AWS Cognito OIDC (OpenID Connect Authorization Code flow) as a delegated alternative. Access tokens for private persona API access
- **OIDC Library:** Authlib for JWT decoding and JWKS verification
- **Templates:** Jinja2 for server-rendered HTML pages
- **Admin:** SQLAdmin for database administration
- **Rate Limiting:** slowapi for per-IP request throttling
- **Containerisation:** Docker Compose to orchestrate the application and database services

### 4.2 REST API

The API is the core deliverable of the project. I implemented two groups of endpoints:

**User endpoints** handle the account lifecycle, creating, listing, reading, updating, and deleting users. When you fetch a user's profile via `GET /api/users/{id}`, the response includes only their public personas. Private personas are filtered out at the application level before the response is sent.

**Persona endpoints** handle creating, reading, updating, and deleting personas. Each persona belongs to a user. When a private persona is created, the system generates a unique access token and returns it to the owner; public personas do not receive a token since they are accessible to everyone. Any mutation on a private persona (update, delete, token regeneration) requires presenting the correct token in the `X-Access-Token` header.

I also defined separate Pydantic response models: `PersonaPublicResponse` excludes the `access_token` field entirely, while `PersonaOwnerResponse` includes it. This means even if I make a mistake in the endpoint logic, Pydantic will strip the token from any public-facing response, a second layer of defence that I did not have with Flask.

### 4.3 Privacy Enforcement

This is the core logic of the project, the part that makes it more than a basic CRUD API. The privacy model works as follows:

Each persona has two relevant fields: `is_public` (a boolean) and `access_token` (a randomly generated string, only present for private personas; public personas have no token). When someone requests a persona via the API:

1. If `is_public` is `True`, the persona data is returned to anyone
2. If `is_public` is `False`, the API checks for an `X-Access-Token` header
3. If no token is provided, the API returns `403 Forbidden`
4. If the token is provided but wrong, the API returns `403 Forbidden`
5. Only if the token matches does the API return the persona data

This means a single user profile can look completely different depending on the context. A recruiter browsing `GET /api/users/10` sees the Professional and Gamer personas (both public), but has no idea that a Legal persona with sensitive data even exists. Someone who was given the Legal persona's access token can retrieve it directly via `GET /api/personas/5` with the token header.

### 4.4 Web Interface

While the API is the primary product, I also built a web interface so that users can manage their personas without needing tools like Postman or curl. The interface is server-rendered using Jinja2 templates and includes:

- **Landing Page:** The root URL (`/`) serves a public landing page that introduces the project's concept with a tagline, three feature cards (Multiple Personas, Privacy Control, One Link), and calls to action for signing up or viewing a demo profile

- **Login/Signup pages:** Session-based authentication using cookies. When a user signs up, their password is hashed using bcrypt and stored. On login, the password is verified against the bcrypt hash and a session cookie is set. Both pages also include a "Continue with AWS Cognito" button (with a visual divider) that redirects to Cognito's hosted UI. The login page redirects to Cognito's login screen, while the signup page redirects directly to Cognito's registration screen
- **Dashboard:** After logging in, users see all their personas (both public and private) with options to create, edit, or delete them. They can toggle visibility from the edit page, and switching a persona to private automatically generates an access token
- **Public Profile:** Each user has a shareable profile page at `/u/{username}` that shows only their public personas, with filter buttons to narrow by context. Clicking a persona card opens a dedicated detail page at `/u/{username}/{id}` showing its full attributes. This is what visitors see

All templates extend a base template (`base.html`) that provides the consistent layout and navigation.

### 4.5 AWS Cognito OIDC Integration

After the core persona logic was stable, I added AWS Cognito as a second authentication method using the OpenID Connect (OIDC) Authorization Code flow. This was the largest single feature addition to the project, touching 10 files across the backend, frontend, database, tests, and deployment configuration.

**Why Cognito:** The original session-based auth works but lacks features users expect from a production system: social login, multi-factor authentication, and password reset flows. Rather than building all of these from scratch, I delegated them to AWS Cognito, which provides a hosted UI and handles the security-critical parts of user registration and authentication. The application only needs to verify the tokens Cognito returns.

**How It Works:** The integration follows the standard OIDC Authorization Code flow:

1. The user clicks "Continue with AWS Cognito" on the login or signup page
2. The application redirects to Cognito's hosted UI (`/oauth2/authorize` for login, `/signup` for registration), passing a CSRF state parameter stored in the session
3. After the user authenticates on Cognito's hosted UI, Cognito redirects back to `/auth/cognito/callback` with an authorization code
4. The application exchanges the code for tokens at Cognito's `/oauth2/token` endpoint using Basic auth (client ID + secret)
5. The ID token (a JWT) is decoded and verified against Cognito's public JWKS (JSON Web Key Set) endpoint to extract the user's `sub` (unique identifier) and `email`
6. The application then resolves the user: if a user with that `cognito_sub` exists, they are logged in directly; if a user with that email exists (a local account), the `cognito_sub` is linked to their account; if no user exists, they are redirected to a username picker page (`/auth/cognito/complete`) since Plural requires a username for profile URLs

**Account Linking:** A key design decision was to support linking existing local accounts. If a user originally registered with email/password and later signs in via Cognito using the same email, the system links the Cognito identity to their existing account rather than creating a duplicate. This means the user keeps all their existing personas and profile data.

**Logout:** The logout flow was extended to redirect to Cognito's `/logout` endpoint (passing the `client_id` and `logout_uri`), which ensures the user is signed out of both the application session and the Cognito session. If Cognito is not configured, logout falls back to simply clearing the local session.

**Configuration:** All Cognito settings (region, pool ID, client ID, client secret, domain) are loaded from environment variables via a `.env` file. The Docker Compose configuration was updated to pass these variables to the container. If the Cognito environment variables are empty, the Cognito buttons and routes gracefully fall back to the local auth flow, so the application works with or without Cognito configured.

**Database Migration:** A new `cognito_sub` column was added to the Users table via an Alembic migration. The column is nullable (local users do not have one) and unique (each Cognito identity maps to exactly one user). The `password_hash` column was also made nullable to support Cognito-only users who have no local password.

### 4.6 Admin Panel

I integrated SQLAdmin to provide a quick way to browse and manage the database during development. It mounts at `/admin` and exposes views for Users, Personas, and Contexts with search and sort functionality. This was useful for debugging and for verifying data integrity during development.

### 4.7 Flexible Data Model

One design decision I am happy with is the JSON `data` field on personas. Instead of defining fixed columns for every possible attribute (which would be impossible given the variety of persona types), I store the persona's attributes as a JSON string in a Text column. This means:

- A Gamer persona can store `{"discord": "ghosttom#4821", "rank": "plat 2"}`
- A Professional persona can store `{"linkedin": "linkedin.com/in/user", "github": "github.com/user"}`
- A Legal persona can store `{"full_name": "John Doe", "national_id": "..."}`

Each persona type has completely different fields, and the system handles them all the same way. The trade-off is that I cannot query or index individual JSON fields at the database level, but for this use case that is acceptable, the data is always accessed as a whole blob attached to a persona.

### 4.8 Modular Route Architecture

Initially, all API endpoints lived in `main.py` alongside the application setup, which grew to over 450 lines. The web routes (authentication, dashboard, profile) were already split into separate modules using FastAPI's `APIRouter`, so I applied the same pattern to the API routes. I created `app/routes/api_users.py` for user and context endpoints, `app/routes/api_personas.py` for persona endpoints, and `app/utils.py` for shared helper functions (serialization, response conversion). This reduced `main.py` to application setup and router registration only. A side benefit was centralising the database session dependency (`get_db`) into `app/database.py`, which all route modules now import from a single source, ensuring consistent behaviour across all endpoints and simplifying the test configuration.

### 4.9 Rate Limiting

To protect against brute-force attacks, I integrated `slowapi` (a FastAPI-compatible rate limiting library built on top of `limits`). The limiter uses the client's IP address to track request counts. Authentication endpoints (`/login`, `/signup`) and the token regeneration endpoint are limited to 10 requests per minute, while the general API default is 60 requests per minute. When a client exceeds the limit, the API returns a `429 Too Many Requests` response. This prevents attackers from guessing access tokens or brute-forcing login credentials at scale.

### 4.10 Automated Test Suite Architecture

To ensure the API and authentication flows function correctly, I implemented 76 automated tests using pytest. A key implementation detail is the use of `pytest` fixtures to manage test state efficiently. For example, a `sample_user` fixture creates a user object in the database before a test runs, and a `sample_user_with_personas` fixture sets up both public and private personas. This pattern kept the individual test functions completely focused on asserting logic, rather than repeating database setup boilerplate. Of the 76 tests, 60 cover the REST API and persona logic, and 16 cover the Cognito OIDC authentication flow (login redirect, callback handling, account linking, username completion, and logout).

### 4.11 Seed Script

To make the application immediately usable after deployment, I created a seed script (`seed.py`) that populates the database with foundational data. The script first creates the core set of contexts (Professional, Gaming, Creative, Social, Legal, Academic, Fitness), which are the categories users select when creating a persona. It then seeds five sample users, each with two to three personas spanning different contexts and visibility settings, giving a total of 15 personas. The sample data is deliberately realistic: one user is a backend developer who also games, another is a writer and photographer who keeps her day job private. This makes the seed data useful both for development and for demonstrating the project's core concept to evaluators. The landing page links to one of these seeded profiles so that visitors can immediately explore a working example.

---

## 5. Evaluation

### 5.1 Evaluation Strategy & Success Criteria

#### Why Automated Testing

The core product is a REST API designed primarily for machine consumption. Unlike a user-facing GUI where subjective usability matters, an API either behaves correctly or it does not, making automated assertions the natural fit. I considered other evaluation methods: user testing would be appropriate if the web interface were the primary product, but since the API is the main deliverable, functional correctness matters more than subjective experience. Expert review could be valuable for security auditing, but the priority for this project is verifying that the privacy model works as designed.

The test suite uses pytest and FastAPI's TestClient to simulate real HTTP requests and verify the expected responses. Tests run against an in-memory SQLite database, ensuring isolation (each test starts clean without risking orphaned data in a live database) and speed (minimizing network and disk I/O).

#### Success Criteria

Each criterion is derived from the project aims defined in section 1.3:

- **Privacy Enforcement (addresses the "Private Identity" goal):** The central promise of this project is that private personas are hidden from unauthorised access. To verify this, private personas must return `403 Forbidden` when accessed without a valid token. Tests cover three cases: no token provided, wrong token provided, and correct token provided, ensuring the privacy boundary holds in all scenarios.

- **Contextual Identity (addresses the "context collapse" problem):** The project exists because current platforms show the same data to everyone. To verify that Plural solves this, the API must return distinct data for the same user depending on the access context. Tests verify that `GET /api/users/{id}` returns only public personas, while `GET /api/personas/{id}` with the correct `X-Access-Token` header returns private persona data. Additionally, the `?context=` query parameter on the persona list endpoint allows callers to filter by context name (e.g., `?context=Professional`), so the same endpoint returns different subsets depending on the requested context. This directly tests whether the system prevents context collapse.

- **Data Integrity:** Deleting a User must cascade and remove all associated Personas to prevent orphaned data. Tests create a user with multiple personas, delete the user, and verify all personas return `404 Not Found`.

- **Input Validation:** The API must reject malformed input (invalid emails, missing required fields, duplicate usernames) with appropriate error codes (`400` or `422`).

#### Scenario-Based Evaluation

In addition to unit-level criteria, the test suite includes two scenario tests that simulate real-world use cases:

- **Recruiter Scenario:** A recruiter queries a user's profile via `GET /api/users/{id}`. The test verifies that they see only public personas (Professional, Gamer) and have no indication that a private Legal persona exists. This directly validates the "Public multidimensional Identity" goal from section 1.3.

- **Contextual Identity Scenario:** The same user is queried by two different callers, one without a token and one with a valid access token. The test verifies that they receive different responses from the same system, proving that the API supports contextual identity projection.

### 5.2 API Verification (Automated Testing)

#### 5.2.1 What the Tests Cover

The 76 tests are organised into the following groups, as shown in Table 4.

**Table 4:** Automated Test Suite Coverage

| Test Group | Tests | What It Covers |
|------------|-------|----------------|
| Root | 1 | Landing page loads correctly |
| User Create | 7 | Success, duplicate email/username, invalid email, missing fields, username too short |
| User List | 2 | Empty list, list with data |
| User Get | 3 | Success, not found, only public personas shown |
| User Update | 5 | Email update, username update, not found, duplicate conflicts |
| User Delete | 2 | Success, not found |
| Context List | 3 | Empty list, list with data, response fields |
| Persona Create | 7 | Public/private creation, user not found, without data, name too short, missing context_id, invalid context_id |
| Persona List | 6 | Empty, only public shown, user not found, filter by context, case-insensitive filter, nonexistent context |
| Persona Get | 5 | Public without token, private without token (403), valid token, invalid token, not found |
| Persona Update | 6 | Name, visibility, data updates, missing/invalid token, not found |
| Persona Delete | 4 | Success, missing/invalid token, not found |
| Token Regeneration | 3 | Success (old token invalidated, new works), invalid token, not found |
| Cascade Delete | 1 | Deleting user removes all their personas |
| Privacy Boundaries | 2 | Recruiter scenario (only sees public), contextual identity (same user, different responses) |
| Data Integrity | 3 | Maps directly to the success criteria from section 5.1 |
| Cognito Login | 2 | Redirect to Cognito authorize URL, graceful fallback when Cognito is not configured |
| Cognito Callback | 5 | Missing code/state, invalid state, new user redirect to complete, existing Cognito user login, email-based account linking, token exchange failure |
| Cognito Complete | 5 | Redirect without session, form display with session, user creation, duplicate username rejection, POST without session |
| Cognito Logout | 2 | Redirect to Cognito logout endpoint, fallback to local logout without Cognito |

### 5.2.2 Results Against Success Criteria

In section 5.1, I defined four success criteria. Here is how the tests validate each one:

**Privacy Enforcement ("Private Personas must return 403 Forbidden when accessed without a token"):** Multiple tests confirm this. `test_get_private_persona_without_token_forbidden` sends a GET request to a private persona without any token header and asserts a 403 response. `test_get_private_persona_with_invalid_token` does the same with a wrong token and also gets 403.

**Contextual Identity ("The API must return distinct attributes for the same user ID when requested with different headers"):** The `test_same_user_different_responses` test creates a user with both public and private personas, then shows that `GET /api/users/{id}` returns only the public persona, while `GET /api/personas/{id}` with the correct access token returns the private one. Same user, different views.

**Data Integrity ("Deleting a User must cascade and remove all associated Personas"):** The `test_delete_user_deletes_all_personas` test creates a user with personas, deletes the user, and verifies that both personas return 404.

**Input Validation ("The API must reject malformed input with appropriate error codes"):** The User Create tests cover invalid emails, missing required fields, usernames shorter than the minimum length, and duplicate email/username conflicts. In each case the API returns `400` or `422` as expected, confirming that Pydantic validation rejects bad input before it reaches the database.

### 5.3 Web Interface Verification (Manual Walkthrough)

The web interface is evaluated through manual walkthrough testing. Since the API's functional correctness is proven by the automated test suite, the goal of this manual evaluation is to prove that the graphical interface successfully translates those privacy controls to the end user. 

The evaluation covers the core user journey:

**Step 1: User Registration and Dashboard**
Testing confirmed that the registration and login flow (using session-based cookies) functions correctly. Upon login, the dashboard successfully aggregates and displays all of the user's personas, regardless of visibility status.
*(Insert Screenshot 1: The user dashboard showing a mix of public and private personas)*

**Step 2: Persona Creation and Privacy Toggling**
The evaluation verified that users can create new personas and edit existing ones. The visibility is controlled via a dropdown menu where the user selects "Public" or "Private." When set to private, the edit page displays the Access Token section with copy and regenerate options; when switched to public, this section is hidden since public personas do not need tokens.
*(Insert Screenshot 2: The 'Create/Edit Persona' form highlighting the visibility dropdown)*

**Step 3: Verifying the Public Context Boundary (Critical Evaluation)**
To definitively prove that the system solves the "Context Collapse" problem identified in the project aims, the public profile page (`/u/{username}`) was evaluated from the perspective of an unauthenticated visitor. The test was highly successful: the public profile rendered *only* the personas marked as public, while completely omitting any trace of the private personas visible on the user's internal dashboard. Context filter buttons on the profile page allow visitors to narrow the view by context, so a recruiter selecting "Professional" sees only professionally relevant personas while gaming personas are hidden from that view. Clicking a persona card navigates to a dedicated detail page (`/u/{username}/{persona_id}`) showing its full attributes.
*(Insert Screenshot 3: The public /u/username profile, visually proving the private personas are hidden)*

**Step 4: Token Management**
Finally, testing confirmed that users can manually regenerate access tokens from the dashboard, which successfully invalidates the old token for API access.

**Step 5: AWS Cognito Authentication Flow**
The Cognito login and signup flows were tested with a configured AWS Cognito User Pool. Clicking "Continue with AWS Cognito" on the login page redirects to Cognito's hosted login screen, while clicking it on the signup page redirects directly to Cognito's registration screen. After authenticating on Cognito's hosted UI, the callback correctly resolves the user: returning users are logged in immediately, while new users are redirected to the username completion page (`/auth/cognito/complete`). Account linking was also verified by signing in via Cognito with an email that already had a local account; the system linked the Cognito identity to the existing account and preserved all existing personas. Logout was confirmed to clear both the local session and the Cognito session.

**Step 6: Rate Limiting**
Rate limiting was verified by sending repeated requests to the login endpoint. After exceeding the configured threshold (10 requests per minute), the server returned `429 Too Many Requests` as expected. This confirms that the slowapi integration is active and correctly throttling per-IP request rates on authentication endpoints.

**Step 7: Docker Deployment**
The full application was deployed using `docker-compose up` to verify that the containerised environment works end-to-end. The PostgreSQL database initialised correctly, Alembic migrations ran on startup, and the FastAPI application served both the API and web interface. Environment variables for Cognito were passed through the Docker Compose configuration and picked up by the application without issues.

### 5.4 Strengths

**Separation of Authentication and Persona Logic:** The architecture keeps authentication and persona management fully decoupled. The persona layer depends only on `user_id`, not on how the user authenticated. This was validated when I added AWS Cognito OIDC as a second authentication method (see section 4.5): the integration touched 10 files but required no changes to any existing persona code. The fact that a major feature could be added purely through additive changes confirms that the original separation was sound.

**Privacy Enforcement at the API Level:** The access token mechanism for private personas means that privacy is enforced in the API layer itself, not just in the UI. Even if a client bypasses the web interface entirely, private personas remain hidden unless the correct token is provided. This is a stronger guarantee than UI-only visibility controls.

**Comprehensive Test Coverage:** The test suite covers 76 cases across authentication, persona CRUD, privacy enforcement, API access tokens, and the Cognito OIDC flow. Tests run against an in-memory SQLite database, keeping them fast and isolated. The Cognito tests use mocked HTTP responses, so they verify the application logic without depending on external services.

### 5.5 Limitations and Future Improvements

The project meets the success criteria I defined, but working through the implementation exposed several weaknesses. For each one, I describe the problem, why it matters, and how I would concretely fix it.

**No External Platform Connectors (Functionality - Medium Priority)**

All persona data is currently entered manually by the user. The system does not connect to external platforms to pull data automatically. This means a Gamer persona cannot sync stats from Steam, and a Professional persona cannot import repositories from GitHub. The user must type in every attribute by hand, which creates friction and means the data can go stale. The flexible JSON data model (section 4.7) was designed to accommodate any attribute structure, so adding connectors would not require schema changes. The implementation would involve a connector layer that authenticates with external APIs (via OAuth where needed), fetches the relevant data, and writes it into the persona's JSON `data` field on a schedule or on demand. This is the highest-priority improvement discussed in section 6.2.

**Limited Social Authentication Options (Architecture - Low Priority)**

As established in section 1.5, this project is not an authentication system; it is a representation layer that integrates with existing identity providers. The current Cognito integration demonstrates this principle, but it only supports email/password registration through Cognito's hosted UI. It does not yet offer social login options such as "Sign in with Google" or "Sign in with Microsoft." Cognito itself supports federation with Google, Facebook, Apple, and SAML providers like Azure AD, so enabling these would primarily be a configuration change on the Cognito side, plus adding the appropriate identity provider scopes to the OIDC request. The application code would require minimal changes since the callback flow already handles any identity Cognito returns. Expanding the range of supported providers would reinforce the project's design philosophy: Plural delegates authentication to dedicated identity platforms and focuses entirely on persona management.

**Limited Frontend Validation (Usability - Low Priority)**

The web forms use HTML5 validation attributes (`required`, `type="email"`, `minlength`, `maxlength`) to catch common errors before submission, but more advanced checks (such as duplicate email or username detection) still rely on server-side validation and require a full page reload. Adding asynchronous validation (e.g., checking username availability as the user types) would improve the experience, but this is low priority because the REST API is the primary product and its Pydantic validation is solid.

---

## 6. Conclusion

### 6.1 Summary of Achievements

The goal of this project was to take the idea of "context collapse" from the academic literature and show that it can be addressed at the software level. Plural does this by giving users a way to split their digital identity into separate personas, each tied to a context, and control which ones are visible to which audience.

The system sits on top of standard authentication and adds a representation layer. Users group their information into context-bound Personas and set each one as public or private. The API enforces these boundaries with access tokens, so a requesting platform only sees the persona it is supposed to see. Adding dual authentication (session-based and AWS Cognito OIDC) showed that keeping authentication separate from persona logic was the right call, since the entire Cognito integration required no changes to any existing persona code. The automated tests and scenario evaluations confirmed that the system enforces Nissenbaum's contextual integrity [10] in practice: the right information reaches the right context, and private data stays hidden.

### 6.2 Future Work and Extensions

The current implementation proves the core concept, but moving it toward a production-ready service would need a few key extensions:

**External Platform Connectors:** Right now, all persona data is typed in manually by the user. The biggest improvement would be a connector layer that pulls data from external APIs (e.g., Steam, GitHub, LinkedIn) via OAuth and writes it into the persona's JSON data field automatically. This would turn Plural from a static data store into something closer to a live identity hub.

**Infrastructure-Level Security:** The application uses slowapi for rate limiting, which works but runs inside the application itself. In a production setup, this should sit at the edge instead. An API Gateway (like AWS API Gateway) and a Web Application Firewall (WAF) would block DDoS attacks and token brute-forcing before traffic reaches the FastAPI server.

**OAuth 2.0 Authorization Server:** Currently, private personas are unlocked with custom access tokens. A natural next step would be making Plural an OAuth 2.0 Authorization Server, so third-party apps can request specific scopes (e.g., `read:persona_gaming`). This would give users a standard, consent-based way to share parts of their identity with external platforms.

### 6.3 Technical Reflection

Looking back, the most useful lesson was learning when to defer a feature and when to come back to it.

I originally planned to add Cognito from the start, but that was pulling my attention away from the core problem. Falling back to simple session-based auth let me focus on getting the persona logic right: the privacy enforcement, the access tokens, the contextual responses. Once that was solid and fully tested, adding Cognito was straightforward because the architecture kept the two concerns separate. The OIDC routes and the `cognito_sub` column were purely additive changes that did not touch a single line of persona code.

The API-first approach also paid off. Because privacy is enforced in the API layer, private personas stay hidden no matter how the data is accessed. The web interface does not need its own privacy logic; it just renders whatever the API returns. If I had built the UI first, I probably would have implemented privacy as a frontend concern and then had to redo it for the API.

Migrating from Flask to FastAPI was also worth the effort. Pydantic's response models (`PersonaPublicResponse` vs. `PersonaOwnerResponse`) gave me a framework-level guarantee that access tokens would never appear in public responses, even if I made a mistake in the endpoint logic. That kind of safety net did not exist in the Flask prototype.

### 6.4 Broader Themes

At a wider level, this project points to a gap in how most platforms handle user profiles. The standard approach treats identity as a single thing: one row in a database, one profile page, one set of attributes shown to everyone. That made sense when people used one or two platforms, but it does not match how people actually live online today.

As digital footprints grow, this one-size-fits-all model leads to context collapse and privacy fatigue. Plural shows that identity does not have to be a binary choice between full exposure and anonymity. By building systems that support "partial identities" and enforce contextual boundaries by default, developers can create tools that match how people naturally behave: showing different sides of themselves to different audiences. The future of digital identity is not about building higher walls around a single profile, but about giving users the tools to manage their own complexity.

---

## References

[1] Goffman, E. (1959) *The Presentation of Self in Everyday Life*. New York: Doubleday Anchor Books.

[2] Marwick, A.E. and boyd, d. (2011) 'I Tweet Honestly, I Tweet Passionately: Twitter Users, Context Collapse, and the Imagined Audience,' *New Media & Society*, 13(1), pp. 114-133.

[3] IBM (n.d.) *What is Identity and Access Management (IAM)?* Available at: https://www.ibm.com/think/topics/identity-access-management (Accessed: 9 February 2026).

[4] SailPoint (n.d.) *Identity and Access Management.* Available at: https://www.sailpoint.com/identity-library/identity-and-access-management (Accessed: 9 February 2026).

[5] Cisco (n.d.) *What is Identity Access Management?* Available at: https://www.cisco.com/site/us/en/learn/topics/security/what-is-identity-access-management.html (Accessed: 9 February 2026).

[6] Oracle (n.d.) *What is Digital Identity?* Available at: https://www.oracle.com/middleeast/security/identity-management/digital-identity/ (Accessed: 9 February 2026).

[7] Cloudflare (n.d.) *What is Identity?* Available at: https://www.cloudflare.com/learning/access-management/what-is-identity/ (Accessed: 9 February 2026).

[8] IBM (n.d.) *What is Digital Identity?* Available at: https://www.ibm.com/think/topics/digital-identity (Accessed: 9 February 2026).

[9] Clauß, S. and Kohntopp, M. (2001) 'Identity Management and Its Support of Multilateral Security,' *Computer Networks*, 37, pp. 205-219.

[10] Nissenbaum, H. (2004) 'Privacy as Contextual Integrity,' *Washington Law Review*, 79(1), pp. 119-157.

[11] Cameron, K. (2005) *The Laws of Identity*. Microsoft Corporation. Available at: https://www.identityblog.com/stories/2005/05/13/TheLawsOfIdentity.pdf (Accessed: 9 February 2026).

[12] Alanzi, H.M. and Alkhatib, M. (2025) 'Blockchain-Based Identity Management System Prototype for Enhanced Privacy and Security,' *Electronics*, 14(13), 2605. doi: 10.3390/electronics14132605.

[13] Amazon Web Services (n.d.) *Federated Access.* Available at: https://docs.aws.amazon.com/whitepapers/latest/establishing-your-cloud-foundation-on-aws/federated-access.html (Accessed: 9 February 2026).

[14] Okta (n.d.) *What is Federated Identity?* Available at: https://www.okta.com/identity-101/what-is-federated-identity/ (Accessed: 9 February 2026).

[15] Entitle.io (n.d.) *What is Federated Access?* Available at: https://www.entitle.io/resources/glossary/federated-access (Accessed: 9 February 2026).
