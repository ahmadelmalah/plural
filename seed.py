"""
Seed script for Plural - Identity Management API

Creates sample users with multidimensional personas to demonstrate
the project's vision of managing fragmented digital identities.
"""

import json

from app.database import SessionLocal
from app.models import Persona, User

SAMPLE_USERS = [
    {
        "email": "tom.h.2847@gmail.com",
        "username": "tomh",
        "personas": [
            {
                "name": "Work",
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
                "is_public": True,
                "data": {
                    "instagram": "@nina.captures",
                    "gear": "Sony a7iii + 35mm",
                    "style": "street photography, mostly",
                },
            },
            {
                "name": "Work",
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
    """Remove all existing users and personas."""
    db = SessionLocal()
    try:
        persona_count = db.query(Persona).delete()
        user_count = db.query(User).delete()
        db.commit()
        print(f"Cleared {user_count} users and {persona_count} personas.")
    finally:
        db.close()


def seed_database():
    """Seed users and their personas."""
    db = SessionLocal()
    try:
        for user_data in SAMPLE_USERS:
            # Create user
            user = User(
                email=user_data["email"],
                username=user_data["username"],
            )
            db.add(user)
            db.flush()  # Get the user ID

            # Create personas for this user
            for persona_data in user_data["personas"]:
                persona = Persona(
                    user_id=user.id,
                    name=persona_data["name"],
                    is_public=persona_data["is_public"],
                    data=json.dumps(persona_data["data"]),
                )
                db.add(persona)

        db.commit()

        total_personas = sum(len(u["personas"]) for u in SAMPLE_USERS)
        print(f"Seeded {len(SAMPLE_USERS)} users with {total_personas} personas.")
        print("\nSample users created:")
        for user_data in SAMPLE_USERS:
            public_count = sum(1 for p in user_data["personas"] if p["is_public"])
            private_count = len(user_data["personas"]) - public_count
            print(f"  - {user_data['username']}: {public_count} public, {private_count} private personas")
    finally:
        db.close()


if __name__ == "__main__":
    print("Clearing existing data...")
    clear_database()
    print("\nSeeding fresh data...")
    seed_database()
