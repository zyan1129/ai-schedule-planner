"""Login + per-user persistence for SmartSchedule.

Auth:    Google (OIDC) via Streamlit's built-in ``st.login()``. Configured in
         the ``[auth]`` section of secrets (see .streamlit/secrets.toml.example).
Storage: Supabase Postgres. One row per user in ``schedules`` holds the parsed
         schedule, the edited ("working") schedule and the current conflicts as
         JSON. See supabase/migrations/001_init.sql.

The Supabase client uses the service_role key and only ever runs on the
Streamlit server, never in the browser. Row Level Security is switched on with
no policies, so the public anon key can't read or write anything.

Both pieces are optional so the app still runs locally with no secrets:
- no ``[auth]`` -> guest mode (no login, session-only data)
- no ``[supabase]`` -> logged in, but data lives only in the browser session
"""

from datetime import datetime, timezone

import streamlit as st


def _secret_section(name):
    """Return st.secrets[name] as a dict, or None if missing / no secrets file."""
    try:
        section = st.secrets.get(name)
    except Exception:  # no secrets.toml at all
        return None
    return dict(section) if section else None


def auth_configured():
    auth = _secret_section("auth")
    return bool(auth and auth.get("client_id") and auth.get("cookie_secret"))


def db_configured():
    db = _secret_section("supabase")
    return bool(db and db.get("url") and db.get("service_role_key"))


@st.cache_resource(show_spinner=False)
def _client():
    from supabase import create_client

    db = _secret_section("supabase")
    return create_client(db["url"], db["service_role_key"])


def upsert_profile(user):
    """Create or refresh the profile row for a logged-in user."""
    _client().table("profiles").upsert({
        "user_id": user["sub"],
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
        "last_login_at": datetime.now(timezone.utc).isoformat(),
    }).execute()


def load_schedule(user_id):
    """Return {'schedule', 'working_schedule', 'conflicts'} or None."""
    res = (
        _client().table("schedules")
        .select("parsed, working, conflicts")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not res.data:
        return None
    row = res.data[0]
    return {
        "schedule": row.get("parsed"),
        "working_schedule": row.get("working"),
        "conflicts": row.get("conflicts"),
    }


def save_schedule(user_id, schedule, working_schedule, conflicts):
    _client().table("schedules").upsert({
        "user_id": user_id,
        "parsed": schedule,
        "working": working_schedule,
        "conflicts": conflicts,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()
