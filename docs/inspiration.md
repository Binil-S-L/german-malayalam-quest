# Inspiration & Reference

| Repository | URL | Licence | Notes |
|---|---|---|---|
| fastapi/full-stack-fastapi-template | https://github.com/fastapi/full-stack-fastapi-template | MIT | Production-ready scaffold: SQLModel patterns, PostgreSQL wiring, Pydantic v2 validation, JWT auth. Baseline for project layout and API conventions. |
| zhanymkanov/fastapi-best-practices | https://github.com/zhanymkanov/fastapi-best-practices | MIT | 18 k stars. Patterns for dependency injection, route organisation, DB session scoping — used directly in this codebase. |
| open-spaced-repetition/py-fsrs | https://github.com/open-spaced-repetition/py-fsrs | MIT | Core SRS scheduling model (FSRS, not SM-2), built into Anki 23.10+. Informs `UserProgress` card-state fields and interval logic. Pure Python; can be imported or adapted. |
| user1823/fsrs4anki | https://github.com/user1823/fsrs4anki | MIT | Reference for review-state transitions and difficulty weighting. Conceptual use only. |
| Subekshyan/Habit-Tracker0 | https://github.com/Subekshyan/Habit-Tracker0 | Unknown | FastAPI + PostgreSQL + SQLAlchemy gamified backend with XP, streaks, freeze tokens, leaderboards. Direct template for the Three-Ring completion model. |

**Licensing note:** Anki itself is AGPL — no code copied, scheduler logic referenced conceptually only.
