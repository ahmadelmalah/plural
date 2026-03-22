"""
Seed script for Plural - Identity Management API

Seeds contexts, sample users, and personas to make the application
immediately usable after deployment. Contexts are the core lookup
data that users select when creating personas.
"""

import json
import secrets

from app.database import SessionLocal
from app.models import Context, Persona, User

# Contexts are the foundational data - users pick one when creating a persona
CONTEXTS = [
    {"name": "Professional", "description": "Work, career, and business networking"},
    {"name": "Gaming", "description": "Gaming profiles, ranks, and communities"},
    {"name": "Creative", "description": "Art, music, writing, and content creation"},
    {"name": "Social", "description": "Casual social media and personal presence"},
    {"name": "Legal", "description": "Legal identity and official documents"},
    {"name": "Academic", "description": "Education, research, and academic work"},
    {"name": "Fitness", "description": "Health, sports, and fitness tracking"},
]

SAMPLE_USERS = [
    {
        "email": "tom.h.2847@gmail.com",
        "username": "tomh",
        "personas": [
            {
                "name": "Work",
                "context": "Professional",
                "is_public": True,
                "data": {
                    "role": "Backend Dev",
                    "company": "Spotify",
                    "linkedin": "linkedin.com/in/tomharrison91",
                    "github": "github.com/tomh2847",
                },
            },
            {
                "name": "Gaming",
                "context": "Gaming",
                "is_public": True,
                "data": {
                    "discord": "ghosttom#4821",
                    "steam": "ghosttom_",
                    "main_games": ["valorant", "cs2", "rocket league"],
                    "rank": "plat 2 (hardstuck lol)",
                },
            },
            {
                "name": "Government",
                "context": "Legal",
                "is_public": False,
                "data": {
                    "legal_name": "Thomas Richard Harrison",
                    "dob": "1991-11-03",
                    "passport": "ends in 4821",
                },
            },
        ],
    },
    {
        "email": "nina.writes@outlook.com",
        "username": "ninawrites",
        "personas": [
            {
                "name": "Writing",
                "context": "Creative",
                "is_public": True,
                "data": {
                    "blog": "medium.com/@ninawrites",
                    "substack": "ninathinks.substack.com",
                    "topics": "tech, productivity, random thoughts",
                    "newsletter_subs": "~2.3k",
                },
            },
            {
                "name": "Photography",
                "context": "Creative",
                "is_public": True,
                "data": {
                    "instagram": "@nina.captures",
                    "gear": "Sony a7iii + 35mm",
                    "style": "street photography, mostly",
                },
            },
            {
                "name": "Work",
                "context": "Professional",
                "is_public": False,
                "data": {
                    "role": "product manager",
                    "company": "not sharing lol",
                    "note": "keeping work separate from creative stuff",
                },
            },
        ],
    },
    {
        "email": "kfitness99@gmail.com",
        "username": "karim_fit",
        "personas": [
            {
                "name": "Fitness",
                "context": "Fitness",
                "is_public": True,
                "data": {
                    "instagram": "@karim.fitness",
                    "youtube": "youtube.com/@karimlifts",
                    "focus": "powerlifting + meal prep content",
                    "current_total": "1420 @ 83kg",
                },
            },
            {
                "name": "Day Job",
                "context": "Professional",
                "is_public": False,
                "data": {
                    "title": "accountant",
                    "firm": "deloitte",
                    "linkedin": "linkedin.com/in/karim-hassan-cpa",
                    "note": "clients dont need to know about the youtube thing",
                },
            },
            {
                "name": "Gaming",
                "context": "Gaming",
                "is_public": True,
                "data": {
                    "twitch": "twitch.tv/karim_plays",
                    "games": ["elden ring", "baldurs gate 3"],
                    "schedule": "weekends mostly",
                },
            },
        ],
    },
    {
        "email": "old.email.from.2012@yahoo.com",
        "username": "maya_dev",
        "personas": [
            {
                "name": "Tech",
                "context": "Professional",
                "is_public": True,
                "data": {
                    "github": "github.com/mayasharma",
                    "twitter": "@mayacodes",
                    "blog": "maya.dev",
                    "focus": "rust, systems programming",
                },
            },
            {
                "name": "Music",
                "context": "Creative",
                "is_public": True,
                "data": {
                    "soundcloud": "soundcloud.com/mayabeats",
                    "bandcamp": "mayabeats.bandcamp.com",
                    "genre": "lofi / chillhop",
                    "setup": "ableton + op-1",
                },
            },
            {
                "name": "Personal",
                "context": "Social",
                "is_public": False,
                "data": {
                    "real_name": "Maya Sharma",
                    "location": "vancouver",
                    "reddit": "u/throwaway_maya_42",
                },
            },
        ],
    },
    {
        "email": "david.chen.work@protonmail.com",
        "username": "dchen",
        "personas": [
            {
                "name": "Professional",
                "context": "Professional",
                "is_public": True,
                "data": {
                    "role": "senior counsel",
                    "firm": "Morrison & Foerster",
                    "specialty": "M&A, tech transactions",
                    "bar": "CA, NY",
                    "linkedin": "linkedin.com/in/davidchen-esq",
                },
            },
            {
                "name": "MTG",
                "context": "Gaming",
                "is_public": False,
                "data": {
                    "arena_name": "ControlFreak#12847",
                    "format": "legacy, modern",
                    "lgs": "channelfireball game center",
                    "note": "partners would roast me if they knew how much i spend on cardboard",
                },
            },
            {
                "name": "Legal Docs",
                "context": "Legal",
                "is_public": False,
                "data": {
                    "full_name": "David Wei Chen",
                    "bar_no": "CA 298471",
                    "dob": "1985-06-12",
                },
            },
        ],
    },
]


def clear_database():
    """Remove all existing data in dependency order."""
    db = SessionLocal()
    try:
        persona_count = db.query(Persona).delete()
        user_count = db.query(User).delete()
        context_count = db.query(Context).delete()
        db.commit()
        print(f"Cleared {user_count} users, {persona_count} personas, {context_count} contexts.")
    finally:
        db.close()


def seed_contexts(db):
    """Seed contexts and return a name-to-id mapping."""
    context_map = {}
    for ctx_data in CONTEXTS:
        ctx = Context(name=ctx_data["name"], description=ctx_data["description"])
        db.add(ctx)
        db.flush()
        context_map[ctx.name] = ctx.id
    print(f"Seeded {len(CONTEXTS)} contexts: {', '.join(c['name'] for c in CONTEXTS)}")
    return context_map


def seed_users(db, context_map):
    """Seed users and their personas."""
    for user_data in SAMPLE_USERS:
        user = User(
            email=user_data["email"],
            username=user_data["username"],
        )
        db.add(user)
        db.flush()

        for persona_data in user_data["personas"]:
            is_public = persona_data["is_public"]
            persona = Persona(
                user_id=user.id,
                name=persona_data["name"],
                context_id=context_map[persona_data["context"]],
                is_public=is_public,
                access_token=None if is_public else secrets.token_urlsafe(32),
                data=json.dumps(persona_data["data"]),
            )
            db.add(persona)

    total_personas = sum(len(u["personas"]) for u in SAMPLE_USERS)
    print(f"Seeded {len(SAMPLE_USERS)} users with {total_personas} personas.")
    print("\nSample users created:")
    for user_data in SAMPLE_USERS:
        public_count = sum(1 for p in user_data["personas"] if p["is_public"])
        private_count = len(user_data["personas"]) - public_count
        print(f"  - /u/{user_data['username']}: {public_count} public, {private_count} private")


def seed_database():
    """Seed all data in a single transaction."""
    db = SessionLocal()
    try:
        context_map = seed_contexts(db)
        seed_users(db, context_map)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Clearing existing data...")
    clear_database()
    print("\nSeeding fresh data...")
    seed_database()
    print("\nDone! Visit /u/tomh or /u/ninawrites to see sample profiles.")
