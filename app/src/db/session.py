"""
SQLAlchemy session management.

Provides the engine, session factory, and a FastAPI dependency
``get_db`` that yields a session per request with automatic commit / rollback.

Engine creation is lazy so that the module can be imported without a live
ODBC driver (e.g. during CI lint / test on macOS without unixODBC).
"""

from typing import Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from src.config import settings

# Lazy singleton
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine() -> Engine:
    """Return (and cache) the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=settings.DEBUG,
            connect_args={"fast_executemany": True},
        )
    return _engine


def get_session_factory() -> sessionmaker:
    """Return (and cache) the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(), autocommit=False, autoflush=False
        )
    return _SessionLocal


def get_db():
    """FastAPI dependency — yields a SQLAlchemy session.

    Usage::

        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            ...
    """
    factory = get_session_factory()
    db = factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

