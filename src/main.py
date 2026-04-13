"""
Command line runner for the Music Recommender Simulation.

Runs every defined user profile and prints the top-5 recommendations
for each, including adversarial / edge-case profiles designed to probe
the scoring logic.
"""

from pathlib import Path
try:
    from recommender import load_songs, recommend_songs
except ImportError:
    from src.recommender import load_songs, recommend_songs

SONGS_CSV = Path(__file__).parent.parent / "data" / "songs.csv"

# ---------------------------------------------------------------------------
# User taste profiles
#   genre / mood     : categorical, matched exactly
#   target_energy    : 0.0 (very calm) – 1.0 (very intense)
#   target_valence   : 0.0 (dark/sad)  – 1.0 (bright/happy)
#   likes_acoustic   : True favors acoustic-textured songs
# ---------------------------------------------------------------------------

# --- Standard profiles ------------------------------------------------------

HIGH_ENERGY_POP = {
    "name": "High-Energy Pop",
    "genre": "pop",
    "mood": "happy",
    "target_energy": 0.90,
    "target_valence": 0.88,
    "likes_acoustic": False,
}

CHILL_LOFI = {
    "name": "Chill Lofi",
    "genre": "lofi",
    "mood": "chill",
    "target_energy": 0.38,
    "target_valence": 0.58,
    "likes_acoustic": True,
}

DEEP_INTENSE_ROCK = {
    "name": "Deep Intense Rock",
    "genre": "rock",
    "mood": "intense",
    "target_energy": 0.92,
    "target_valence": 0.35,
    "likes_acoustic": False,
}

EDM_EUPHORIA = {
    "name": "EDM Euphoria",
    "genre": "edm",
    "mood": "euphoric",
    "target_energy": 0.94,
    "target_valence": 0.85,
    "likes_acoustic": False,
}

# --- Adversarial / edge-case profiles ---------------------------------------
# These are designed to expose unexpected or surprising behaviour in the
# scoring logic. Each one targets a specific potential weakness.

# Conflict: extremely high energy but a deeply sad mood.
# Energy suggests intensity/hype; mood suggests brooding/melancholic.
# These two signals pull the scorer in opposite directions.
CONTRADICTED_VIBE = {
    "name": "Contradicted Vibe (high-energy + sad)",
    "genre": "rock",
    "mood": "melancholic",      # no rock song in catalog has this mood
    "target_energy": 0.90,
    "target_valence": 0.10,     # very dark
    "likes_acoustic": False,
}

# Ghost genre: the requested genre does not exist in the catalog at all.
# The scorer can never award the genre +3.0 bonus, so results are driven
# entirely by mood, energy, and valence — exposes whether the system
# degrades gracefully.
GHOST_GENRE = {
    "name": "Ghost Genre (k-pop – not in catalog)",
    "genre": "k-pop",
    "mood": "happy",
    "target_energy": 0.80,
    "target_valence": 0.80,
    "likes_acoustic": False,
}

# Acoustic rock paradox: wants acoustic texture (likes_acoustic=True) but
# requests rock, which in this catalog has very low acousticness. The
# acoustic bonus will almost never fire for rock songs, so the user gets
# rock recommendations that don't feel acoustic.
ACOUSTIC_ROCK_PARADOX = {
    "name": "Acoustic Rock Paradox",
    "genre": "rock",
    "mood": "intense",
    "target_energy": 0.88,
    "target_valence": 0.45,
    "likes_acoustic": True,     # rock songs are rarely acoustic (< 0.6)
}

# Blank slate: no genre, neutral mood that doesn't exist in catalog,
# all continuous features at exactly 0.5. Tests the system's behaviour
# when nothing differentiates the songs on the categorical axes.
BLANK_SLATE = {
    "name": "Blank Slate (no preferences)",
    "genre": "",
    "mood": "",
    "target_energy": 0.50,
    "target_valence": 0.50,
    "likes_acoustic": False,
}

# ---------------------------------------------------------------------------

ALL_PROFILES = [
    HIGH_ENERGY_POP,
    CHILL_LOFI,
    DEEP_INTENSE_ROCK,
    EDM_EUPHORIA,
    CONTRADICTED_VIBE,
    GHOST_GENRE,
    ACOUSTIC_ROCK_PARADOX,
    BLANK_SLATE,
]


def run_profile(user_prefs: dict, songs: list, k: int = 5) -> None:
    name = user_prefs.get("name", "Unnamed Profile")
    # build a clean copy without the display-only "name" key
    prefs = {k: v for k, v in user_prefs.items() if k != "name"}

    separator = "=" * 60
    print(f"\n{separator}")
    print(f"  Profile: {name}")
    print(separator)
    print(
        f"  genre={prefs.get('genre') or '(none)'}  "
        f"mood={prefs.get('mood') or '(none)'}  "
        f"energy={prefs.get('target_energy'):.2f}  "
        f"valence={prefs.get('target_valence'):.2f}  "
        f"acoustic={prefs.get('likes_acoustic')}"
    )
    print()

    recommendations = recommend_songs(prefs, songs, k=k)

    for rank, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        print(f"  {rank}. {song['title']} — {song['artist']}")
        print(f"     Score: {score:.2f}  |  {explanation}")
        print()


def main() -> None:
    songs = load_songs(SONGS_CSV)
    print(f"Loaded {len(songs)} songs from catalog.\n")

    for profile in ALL_PROFILES:
        run_profile(profile, songs, k=5)

    print("=" * 60)
    print("  Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
