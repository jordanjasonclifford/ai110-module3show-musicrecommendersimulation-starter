"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path
try:
    from recommender import load_songs, recommend_songs
except ImportError:
    from src.recommender import load_songs, recommend_songs

SONGS_CSV = Path(__file__).parent.parent / "data" / "songs.csv"


def main() -> None:
    songs = load_songs(SONGS_CSV)

    print(f"Loaded songs: {len(songs)}\n")

    # --- User taste profiles ---
    # genre / mood: categorical, matched exactly
    # target_energy / target_valence: numeric 0.0–1.0
    #   energy  — 0.0 = very calm,  1.0 = very intense
    #   valence — 0.0 = dark/sad,   1.0 = bright/happy
    # likes_acoustic: True favors acoustic-textured songs

    bright_pop = {
        "genre": "pop",
        "mood": "happy",
        "target_energy": 0.80,
        "target_valence": 0.82,
        "likes_acoustic": False,
    }

    chill_lofi = {
        "genre": "lofi",
        "mood": "chill",
        "target_energy": 0.38,
        "target_valence": 0.58,
        "likes_acoustic": True,
    }

    intense_rock = {
        "genre": "rock",
        "mood": "intense",
        "target_energy": 0.90,
        "target_valence": 0.40,
        "likes_acoustic": False,
    }

    edm_euphoria = {
        "genre": "edm",
        "mood": "euphoric",
        "target_energy": 0.94,
        "target_valence": 0.85,
        "likes_acoustic": False,
    }

    # Active profile — swap this out to test different users
    user_prefs = bright_pop

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
