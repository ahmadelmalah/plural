# Plural - Identity and Profile Management API

## 1. Introduction

### 1.1 Selected Template
7.1 Project Idea 1: Identity and profile management API

### 1.2 Challenge Overview: Digital Identity Fragmentation

Modern digital platforms are designed to capture or focus on a certain dimensions of human identities. When users engage with these platforms, they are expected to show the identity, the dimension and the role suited to that environment. For example, LinkedIn is designed to highlight the professional persona; it is a space where sharing an Azure certification is appropriate, but sharing a gaming high score would be out of context. Conversely, a platform like Steam captures the recreational "gamer" dimension, while Goodreads captures the intellectual "reader" dimension.

However, while these dimensions are distinct in function, focus and interest they belong to a single human entity. The current digital infrastructure fails to reflect this unity. These platforms operate as isolated silos, unaware of the user's existence outside their specific boundary.

**Centralized Identity Management:** The user lacks a centralized mechanism to observe and manage these fragmented selves, Instead, they are forced to manually duplicate data and manage different profiles across different systems, leading to administrative friction and a loss of holistic control over their own scattered digital footprint.

**Public multidimensional Identity:** This presents another challenge, particularly for individuals with multifaceted talents and diverse interests. These users want to reflect a fair, multidimensional public picture of themselves; for example, they want to say: 'I am a professional software engineer, but I am also a reader interested in history and philosophy, and a gamer who loves Chess and League of Legends'; A definition that spans different dimensions.

**Private Identity:** Equally important is the need for privacy and boundary enforcement. While users often want to show multiple sides of themselves, they also need to keep other sides strictly confidential. For instance, a user must share their legal identity for government services but may need to hide that same identity from online gaming communities for safety. Currently, users lack the granular control to ensure that sensitive private attributes (like a legal name) do not leak into inappropriate contexts.

**Conclusion:** To bridge these gaps, we need a centralized system where users can manage their identity dimensions, choosing what to share publicly and what to keep private, while integrating seamlessly with existing external platforms via a RESTful API.

### 1.3 Solution Overview

The project aims for implementing a centralized place for orchestrating the digital multidimensional identity, by allowing the users to manage the identity as an aggregation of distinct personas, each persona represents a particular dimension (e.g. Legal, Reader, Gamer, Worker), and has its own set of attributes and relevant in a certain context, each persona is set to be public or private (protected access)

Each user will have a general profile that presents all of the user's public personas and what they want to share about themselves (e.g., professional persona, reader persona, gamer persona), while strictly hiding confidential personas (e.g., legal persona).

The system responds dynamically based on the context. If a recruiter queries the profile, they will see only LinkedIn and GitHub accounts; however, if a gamer friend explores the platform, they may see the gamer identity. This means that a single user endpoint can yield completely different JSON responses depending on the negotiation context.

**The Final Outcome:** The preliminary demo will focus on the REST API, but the final project is intended to involve a GUI for user convenience.

### 1.4 Solution Scope

It's important to define a clear scope to avoid any scope creep

**What this project IS:** The application focuses on the Representation Layer (how the user wants to present themselves in different contexts). Therefore, it will delegate other responsibilities, such as Authentication, to external parties like AWS Cognito (an Identity and Access Management service by Amazon) to enhance integration with other systems.

**What this project is NOT:** To clarify the specific contribution of this work, it is important to distinguish it from existing terms:

- **This is not an IAM Service:** While the terminology (i.e. identity management) is similar to cloud services like AWS IAM or Azure AD, they serve different purposes. Cloud IAM manages permissions for infrastructure resources, whereas this project manages user profile contexts, they focus on authentication while this project focuses on representation.

- **This is not a Single Sign-On (SSO) Solution:** The goal is not to provide a mechanism where users sign in once to access multiple platforms without sharing credentials.

While the application could integrate with external systems like IAM and SSO services, it is designed from the ground up to serve a single purpose: managing and projecting the different representations and dimensions (personas) of the user.

### 1.5 Motivation

**Personal Motivation:** I am deeply interested in backend web development, data, security and identity management systems, I enjoy building APIs that could be used and integrated in different systems, I enjoy system integration. My passion lies in the challenge of system integration: building secure, scalable APIs that act as bridges between disconnected platforms. For me, this project is not just a requirement; it is an opportunity to build the kind of structural, data-driven tool that I personally enjoy using.

**Domain Opportunity:** The current software market is already saturated with strong solutions for Authentication ("Who are you?") and Authorization ("What are you allowed to do?"). However, there is a significant gap when it comes to Representation ("How do you appear in this context?").

---

## 2. Literature Review

### 2.1 Introduction

Digital identity representation exists at the intersection of human sociological behavior and software engineering architecture. To propose a robust solution, it is necessary to examine research from both domains: the human studies that define why we fragment our identities, and the technical studies that define how current systems manage them. This chapter evaluates the current digital status quo, analyzing relevant projects, protocols, and services to identify the specific architectural gap this project intends to fill.

### 2.2 Defining Digital Identity

Before designing a system to manage identity, we must establish a working definition of the term. Industry leaders offer varying but converging definitions:

**Oracle** defines digital identity as "a collection of data points that comprise the characteristics, attributes, and activities that identify an entity. Along with authorization technology, digital identity verifies a person, organization, application, or device as both authorized to access certain assets or data and as the legitimate holder of that access."
https://www.oracle.com/middleeast/security/identity-management/digital-identity/

**Cloudflare** views it as "the recorded set of measurable characteristics by which a computer can identify an external entity. That entity may be a person, an organization, a software program, or another computer."
https://www.cloudflare.com/learning/access-management/what-is-identity/

**IBM** defines it as "a profile or set of information tied to a specific user, machine or other entity in an IT ecosystem. Digital IDs help computer systems distinguish between different users for access control, activity tracking, fraud detection and cyberattack prevention."
https://www.ibm.com/think/topics/digital-identity

**Synthesis:** From these definitions, we can conclude that Digital Identity is fundamentally a set of information and attributes representing a profile. In the context of this project, this aligns with the concept of the Persona. If "Identity" is the total sum of all attributes, a "Persona" is a contextual subset of those attributes used for a specific context.

### 2.3 Comparative Analysis of Existing Systems

The current technological landscape is full by numerous systems, technologies and services that address distinct but adjacent challenges. However they solve slightly different set of problems and they solve them from different angles or using fundamentally different approaches, so it's a good idea to take a look at some of them.

#### 2.3.1 Cloud-based Identity and Access Management Services (IAM)

The dominant standard in the current web ecosystem is Identity and Access Management (IAM). Major providers define this discipline as follows:

**IBM** defines it as "the cybersecurity discipline that deals with provisioning and protecting digital identities and user access permissions in an IT system. IAM tools help ensure that the right people can access the right resources for the right reasons at the right time."
https://www.ibm.com/think/topics/identity-access-management

**SailPoint** defines it as "the framework and processes organizations use to manage and secure digital identities and control user access to critical information."
https://www.sailpoint.com/identity-library/identity-and-access-management

And they defined the purpose of it as: "Identity and access management systems protect sensitive data and systems from unauthorized access and breaches while also streamlining and automating the management of users' digital identities, access permissions, and security policies."

**Cisco** defines it as "the practice of making sure that people and entities with digital identities have the right level of access to enterprise resources like networks and databases. User roles and access privileges are defined and managed through an IAM system."
https://www.cisco.com/site/us/en/learn/topics/security/what-is-identity-access-management.html

**Different Scopes:** Analyzing these definitions shows the scope of this project. IAM systems are architected primarily to solve the Authentication problem ("Is this user who they claim to be?") and the Authorization problem ("Is this user allowed to access this resource?"). They're not designed to solve the Representation problem ("Which dimension of this user should appear in this context?").

**Integration not Replacement:** The proposed project is not a replacement for IAM but a complement to it. Architecturally, the system functions as a representation layer or a middleware that sits on top of existing IAM infrastructure (such as AWS Cognito). It delegates security (Authentication) to the IAM provider so that it can focus on the logic of presentation (Persona management).

#### 2.3.2 Blockchain-Based Identity Management System (IDMS)

Several researches focuses on Decentralized Identity Management Systems (IDMS), often leveraging blockchain technology to address privacy and ownership concerns.

A recent study (MDPI, 2024) talked about the privacy and security threats related to the traditional systems: "Traditional IDMS relies on a third party to store user information and authenticate the user. However, this approach poses threats to user privacy and increases the risk of single point of failure (SPOF), user tracking, and data unavailability."

And they suggested that modern blockchain-based system could overcome these challenges: "In contrast, decentralized IDMSs that use blockchain technology offer potential solutions to these issues as they offer powerful features including immutability, transparency, anonymity, and decentralization"

But the researches were realistic about their expectations from the new technology: "Despite its advantages, blockchain technology also suffers from limitations related to performance, third-party control, weak authentication, and data leakages. Furthermore, some blockchain-based IDMSs still exhibit centralization issues, which can compromise user privacy and create SPOF risks"
https://www.mdpi.com/2079-9292/14/13/2605

**Blockchain Limitation:** Despite these advantages, blockchain solutions suffer from low adoption rates, performance bottlenecks, weak authentication mechanisms (private key management), and complexity. Furthermore, they often require a complete paradigm shift, both the user and the visiting platform must adopt Web3 standards (Wallets, Smart Contracts).

**Differentiation:** The proposed project takes a pragmatic "Web 2.0" approach. Instead of forcing users to adopt complex blockchain wallets, it uses standard RESTful APIs to provide similar privacy benefits (granular control over data) without the performance overhead or implementation complexity of a blockchain. It offers a centralized governance model for the user that is easier to integrate with the existing web (LinkedIn, Steam, GitHub) than a purely decentralized smart contract.

#### 2.3.3 Federated Identity and Social Login (OAuth 2.0 & OIDC)

Federated Identity handles cross-platform identity. This includes protocols like OAuth 2.0 and OpenID Connect (OIDC), popularly known as "Log in with Google" or "Log in with Facebook."

**AWS** defines Federation as "a common approach to building access control systems which manage users centrally within a central Identity Providers (IdP) and govern their access to multiple applications and services acting as Service Providers (SP)."
https://docs.aws.amazon.com/whitepapers/latest/establishing-your-cloud-foundation-on-aws/federated-access.html

**OKTA** defines it as "a method of linking a user's identity across multiple separate identity management systems. It allows users to quickly move between systems while maintaining security."
https://www.okta.com/identity-101/what-is-federated-identity/

**Entitle.io** expanded the definition of federated access to be "a term used in Information Technology (IT) to describe a type of identity management solution that separates user authentication from the application or service that the user is trying to access. It allows a user to use the same identity or set of credentials to access multiple systems, applications, or networks across a distributed environment, which might be owned or managed by several different entities. Federated Access works by linking or associating each of the user's identities across these various environments, which is achieved by sharing digital identity and entitlement/rights (attributes) across network and system boundaries."

So, Federated identity allows a user to use a trusted Identity Provider (IdP) to access a third-party application (RP). The IdP shares a "User Info" bundle, typically containing a name, email, and profile picture, with the application.

**Differentiation:** Federated access and this proposed project solve adjacent problems not identical ones, federated access allow you to use the same identity in different domains and contexts, while this proposed project allows you to use different masks, dimensions or personas in different context.

#### 2.3.4 Identity Aggregators (Link-in-Bio Tools)

On the user-facing side, a category of tools known as "Identity Aggregators" has emerged, exemplified by platforms such as Linktree, Carrd, and About.me. These tools allow users to create a single static landing page containing links to all their fragmented profiles (e.g., Instagram, LinkedIn, GitHub, Spotify).

These platforms address the problem of digital fragmentation by allowing users to manually curate a centralized collection of links to their disparate portfolios. They serve as a "digital business card" that routes visitors to the user's presence on other platforms.

**Limitation:** Despite their popularity, these tools have significant limitations regarding the goals of this project:

- **Static Landing Pages:** These pages are static; they present the exact same list of links to every visitor. The user cannot choose to show their LinkedIn to a recruiter while hiding their Spotify playlist.

- **Lack of Granular Control:** The user lacks the ability to define distinct "Personas." There is no mechanism to group attributes into logical dimensions (e.g., a "Work Mode" vs. a "Social Mode")

- **Technical Isolation:** These tools are designed for human navigation, not system integration. They lack a RESTful API to support programmatic integration with existing systems, making them unsuitable for the architectural role of an identity middleware.

**Differentiation:** While Identity Aggregators offer a static table of contents for a user's digital life, the proposed project offers a dynamic API. The project evolves the concept from a simple list of links to an intelligent Orchestrator that changes its appearance based on who is viewing it.

---

## 3. Design & Plan

### 3.1 Project Overview

**Selected Template:** 7.1 Project Idea 1: Identity and profile management API

This project focuses on the development of a backend-centric REST API that serves as a centralized governance engine for digital identity. The system acts as a "Representation Layer," allowing users to manage their identity not as a monolith, but as an aggregation of distinct Personas. Each Persona represents a specific dimension of the user (e.g., "Professional," "Gamer," "Anonymous") and contains a unique set of attributes relevant only to specific contexts.

While the primary deliverable is the API, the project also includes a graphical user interface (GUI) to demonstrate the "Persona Switching" capabilities to end-users and for demonstration purposes.

### 3.2 Domain and Target Audience

The project operates within the domain of Privacy Engineering and Identity Management (IdM). It addresses the friction between modern privacy needs and the rigid "Single Sign-On" structures of the current web.

**Target Audience:**

- **Individuals:** who maintain conflicting digital reputations (e.g., a corporate lawyer who is also a competitive streamer) and need to strictly separate these worlds.

- **REST API for Engineers:** Engineers building third-party apps who want to request user data (like a nickname or avatar) without handling the liability of storing Personally Identifiable Information (PII) like real names or emails.

### 3.3 Design and Architectural Choices

I had to go through a set of technical decisions and trade-offs

#### 3.3.1 Authentication Strategy (Delegated Auth)

**Decision:** Delegate authentication to AWS Cognito (OIDC)

**Justification:** Building a secure authentication system from scratch (handling password hashing, MFA, and session security) is error-prone and distracts from the core innovation of "Persona Management." By treating Authentication as a commodity and offloading it to AWS, the project focuses its engineering effort on the "Representation Logic."

**Future Considerations:** To ensure the system avoids vendor lock-in with AWS Cognito; the design should be abstract to allow AWS Cognito to be swapped with other IdP like Auth0 or Google Identity.

#### 3.3.2 API-First Design (REST)

**Decision:** The core product is a RESTful API

**Justification:** Identity service is an infrastructure component. For this system to be scalable, it must be consumable by other machines (e.g., a game client requesting a user's "Gamer Profile"). A visual dashboard is provided for configuration, but the primary value is delivered via JSON responses to API consumers.

#### 3.3.3 Backend Framework

**Decision:** Python Flask.

**Justification:** Flask was selected over heavier frameworks (like Django) for its micro-framework philosophy. It allows for rapid prototyping of the routing logic and offers granular control over the HTTP response lifecycle, which is critical for implementing the custom "Context Headers" logic. Additionally, its robust extension ecosystem (Flask-SQLAlchemy, Authlib) simplifies the integration with AWS OIDC.

**Future Considerations:** As the core service is a REST API, I intend to migrate to FastAPI in future iterations. It provides three distinct advantages relevant to this project:

- **Native Asynchronous Support (ASGI):** Unlike Flask's synchronous nature, FastAPI is built on Starlette, allowing for non-blocking I/O. This is ideal for an "Orchestrator" that spends significant time waiting for external responses (e.g., querying AWS Cognito or external databases).

- **Strict Data Validation (Pydantic):** FastAPI uses Pydantic for data validation. Given that this project relies on enforcing strict schemas for "Public" vs. "Private" personas, Pydantic would eliminate much of the manual validation code currently written in Flask.

- **Automatic Documentation:** FastAPI automatically generates interactive Swagger UI (OpenAPI) documentation, which would make the API significantly easier for third-party developers to consume.

#### 3.3.4 Database Engine

**Decision:** SQLite for the (Prototype)

**Justification:** For the current prototype phase, SQLite provides a serverless, zero-configuration SQL engine that ensures portability. The application uses SQLAlchemy ORM, ensuring that the underlying database can be switched to a production-ready RDBMS like PostgreSQL or MySQL in a production environment without changing the application code, or at least with the minimal efforts.

### 3.4 Initial Database Design

This is not the final database design, this is just an initial design to build the prototype test the hypothesis.

I decided to start with two main tables representing the two main entities we have:

- **Users Table:** The biological entity/account holder
- **Personas Table:** The dimension or the projection for a certain context (e.g. A single user could have a gamer persona, a reader persona, a legal persona, and a professional persona)

#### Users Table

The minimal columns for the users table are:

| Column | Description |
|--------|-------------|
| id | Table Primary Key |
| cognito_sub | Used to link the user with its relevant AWS cognito subject (user) for authentication |
| Nickname | A public name for the user, not linked to any persona |
| email_verified | Bool: True if the user has confirmed the email address |
| created_at | The registration date of the user |
| updated_at | Last time the user has updated his/her information |

#### Personas Table

The minimal columns for the personas table are:

| Column | Description |
|--------|-------------|
| id | Table Primary Key |
| user_id | A foreign key to link the persona with a user (One to many relationship) |
| name | Name of the persona (e.g. reader, gamer, legal) |
| is_public | Determines of the persona is publicly accessible for all visitors |
| access_token | Required if the persona is private, which is a security key used to access the persona |
| Data | The actual unique attributes and values of this persona, this field is JSON to keep it flexible; for example a gamer persona could have Steam ID while a professional persona could have linkedin profile or Github account |
| created_at | When was the persona created |
| updated_at | When was the last time the persona was updated |

### 3.5 Work Plan

The project execution is structured into three distinct development phases, allowing for iterative refinement and risk mitigation.

#### Phase 1: Discovery & Prototyping (Weeks 1-10) [COMPLETED]

This initial phase focused on feasibility analysis and architectural validation. The primary objective was to test critical strategic assumptions, specifically the viability of delegating authentication to AWS Cognito to ensure a "Representation-First" architecture.

The key achievements of this phase are:
- Having a solid vision about the project and its scope.
- A successful integration with AWS Cognito
- Building a basic prototype with tools Flask and SQLite, which gives me a good idea about what to keep and what to consider changing.

#### Phase 2: Core Implementation (Weeks 11-18) [CURRENT STATUS]

The next step for me is to start implementing the actual project, the priority is transitioning from the prototype to a secure, scalable REST API.

The key objectives of this phase are:
- Developing a powerful and secure REST API
- Implement Security Logic for private Personas
- Create a UI Dashboard for testing
- Integrating the AWS Cognito with the REST API

#### Phase 3: Refinement & Summative Evaluation (Week 19+)

While testing is an ongoing process embedded in every sprint, this final phase is dedicated to the holistic assessment of the system against the original design requirements.

Planned activities of this phase are:
- **Product Evaluation:** Did the project manage to solve the main problem and address the requirements?
- **System Auditing:** Security and performance audits.
- **Documentation:** Finalizing technical documentation, including API references (Swagger/Postman) and architectural decision records.
- **Critical Analysis:** Producing a final evaluation report detailing the system's strengths, limitations, and potential for future scalability.

### 3.6 Success Criteria & Evaluation Methodology

To determine if the project has successfully met its objectives, the final system will be evaluated against the following concrete metrics:

- **Security Compliance:** Private Personas must return 403 Forbidden when accessed without a token. (Verified via automated Pytest scripts).

- **Contextual Accuracy:** The API must return distinct attributes for the same user ID when requested with different headers. (Verified via Postman scenario testing or Pytest).

- **Data Integrity:** Deleting a User must strictly cascade and remove all associated Personas to prevent data leaks. (Verified via database state assertions).

---

## 4. Feature Prototype

### 4.1 Prototype Overview

To validate the technical feasibility of the project, I have demonstrated a couple of functional features:

- **Identity Infrastructure (AWS):** Proving that authentication can be successfully offloaded to a third-party provider (AWS Cognito) without friction.

- **Operational Capability (REST API):** Demonstrating a fully functional RESTful interface that allows for the creation, retrieval, updating, and deletion (CRUD) of users and their multidimensional personas.

### 4.2 Core Feature Implementations

#### 4.2.1 Basic REST API Endpoints (CRUD Operations)

As shown in the demonstration, the core of the prototype is a robust REST API that manages the data lifecycle. The system exposes endpoints that handle the foundational logic of the application:

- **User Lifecycle:** The API successfully creates and retrieves user records, establishing the "biological entity" in the database.

- **Persona Management:** The demo highlights the ability to create distinct personas for a single user (e.g., adding a "Gamer" profile).

- **Data Flexibility:** By utilizing a JSON data field, the prototype demonstrates the ability to store widely different attributes (like a SteamID vs. a LinkedIn URL) via standard POST/PUT requests, validating the "Schema-less within SQL" approach.

#### 4.2.2 AWS Cognito Integration

In parallel with the data management, the prototype demonstrates a live integration with AWS Cognito via the OpenID Connect (OIDC) protocol.

- **Live Auth Flow:** The demo captures the redirection to the AWS-hosted UI, the secure login process, and the subsequent return to the application.

- **Identity Sync:** It serves as a proof-of-concept for the "Delegated Auth" architecture, showing how the local database synchronizes with the AWS token to create the local user record automatically.

### 4.3 Technical Environment

The current implementation utilizes the following stack, as seen in the demonstration:

- **Web Framework:** Flask
- **Database:** SQLite (Relational structure with JSON support).
- **Security (Authentication):** AWS Cognito User Pools & OIDC.
- **Testing:** Postman was used during the demo to simulate third-party application requests to the API.

### 4.4 Critical Evaluation

In alignment with standard Software Engineering practices for Backend Development, the prototype was evaluated using Functional API Testing and Security Verification.

#### 4.4.1 Evaluation Methodology

The evaluation focused on "Black Box" testing, where the API is treated as an opaque system to ensure it behaves correctly regardless of internal implementation.

- Postman was used to execute a suite of requests against the exposed endpoints.
- The PoC was deemed successful because it managed to integrate with AWS Cognito, which opens the door for separation of concerns between IAM auth services and my service.

#### 4.4.2 Analysis of Results

The prototype performs well within the scope of a single-user test environment. The separation of concerns is effective: AWS handles the heavy lifting of Identity Verification (AuthN), allowing the Flask application to respond instantly to Persona requests (AuthZ) without latency. However, the current reliance on SQLite limits concurrent write performance, which is an acceptable trade-off for this prototyping phase.

### 4.5 Future Improvements

Based on the architectural evaluation of the prototype, the single most critical improvement identified for the production phase is the migration of the core backend framework from Flask to FastAPI. This decision is driven by three specific architectural limitations observed during the prototyping phase:

#### 1. Automated API Documentation Generation

**Current Limitation:** The current REST API requires manual documentation updates in the README whenever an endpoint changes. This leads to "documentation drift," where the docs no longer match the code.

**Strategic Improvement:** FastAPI automatically generates an interactive Swagger UI (OpenAPI) specification based on the function signatures. This ensures that the API contract is always 100% accurate, which is a requirement for any Identity System intended to be consumed by third-party developers.

#### 2. Strict Schema Enforcement (Pydantic)

**Current Limitation:** The current Flask prototype relies on manual dictionary manipulation to filter "Private" attributes from the JSON response. This approach is prone to human error.

**Strategic Improvement:** FastAPI is tightly integrated with Pydantic. This allows for the definition of strict Response Models.

*Example:* A PublicPersona model can be defined that strictly excludes the access_token field.

*Benefit:* The validation happens at the framework level. Even if the database query returns sensitive data, Pydantic will automatically strip it from the response before it reaches the client, providing a second layer of defense against privacy breaches.

#### 3. Transition to Non-Blocking Concurrency (ASGI)

**Current Limitation:** Flask operates on a synchronous WSGI model. In an "Identity Orchestrator," the system will eventually need to query external APIs (e.g., validating a SteamID with Valve's servers or fetching claims from AWS Cognito). In Flask, these network calls block the entire worker thread, severely limiting throughput under load.

**Strategic Improvement:** FastAPI is built on Starlette, utilizing the standard Python async/await syntax. This allows the API to handle thousands of concurrent "waiting" connections (I/O bound) without blocking the CPU. For a middleware service that sits between users and third-party platforms, this non-blocking architecture is essential for scalability.

**However,** this last reason is connected with migration from SQLite to a production-grade database engine like MySQL or PostgreSQL, so that the database is not a bottleneck for concurrency, SQLite is not designed for concurrency, it's a good tool for single-user systems.
