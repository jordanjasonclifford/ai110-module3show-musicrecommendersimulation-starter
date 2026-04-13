import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: float = 0.5  # neutral default; tests omit this field


# ---------------------------------------------------------------------------
# Scoring recipe
#
#   Genre match      +1.5  pts  — tiebreaker, not a trump card
#   Mood match       +2.0  pts  — emotional vibe is non-negotiable
#   Energy closeness  0–3.0 pts  — 3.0 × (1 − |song.energy − target|)
#   Valence closeness 0–2.0 pts  — 2.0 × (1 − |song.valence − target|)
#   Acoustic bonus   +0.5  pts  — if likes_acoustic and acousticness > 0.6
#
#   Maximum possible: 9.0 pts
#
#   Rationale: lowering genre from 3.0 → 1.5 prevents a single genre tag
#   from overriding feel. Raising energy (2.0 → 3.0) and valence (1.5 → 2.0)
#   lets audio-feature similarity compete on equal footing, mirroring how
#   real recommenders (e.g. Spotify's audio features) weight continuous
#   signals over categorical labels.
# ---------------------------------------------------------------------------

def _score(
    song: Song,
    genre: str,
    mood: str,
    target_energy: float,
    target_valence: float,
    likes_acoustic: bool,
) -> Tuple[float, str]:
    """Return (score, explanation) for one song against user preferences."""
    score = 0.0
    reasons = []

    if song.genre == genre:
        score += 1.5
        reasons.append("genre match (+1.5)")

    if song.mood == mood:
        score += 2.0
        reasons.append("mood match (+2.0)")

    energy_pts = 3.0 * (1.0 - abs(song.energy - target_energy))
    score += energy_pts
    reasons.append(f"energy fit +{energy_pts:.2f}")

    valence_pts = 2.0 * (1.0 - abs(song.valence - target_valence))
    score += valence_pts
    reasons.append(f"valence fit +{valence_pts:.2f}")

    if likes_acoustic and song.acousticness > 0.6:
        score += 0.5
        reasons.append("acoustic bonus (+0.5)")

    return score, " | ".join(reasons)


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        """Store the catalog of songs this recommender will rank."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score every song against the user profile and return the top k results."""
        scored = [
            (song, _score(
                song,
                user.favorite_genre,
                user.favorite_mood,
                user.target_energy,
                user.target_valence,
                user.likes_acoustic,
            )[0])
            for song in self.songs
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable breakdown of why this song was recommended."""
        _, explanation = _score(
            song,
            user.favorite_genre,
            user.favorite_mood,
            user.target_energy,
            user.target_valence,
            user.likes_acoustic,
        )
        return explanation


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    genre = user_prefs.get("genre", "")
    mood = user_prefs.get("mood", "")
    target_energy = user_prefs.get("target_energy", 0.5)
    target_valence = user_prefs.get("target_valence", 0.5)
    likes_acoustic = user_prefs.get("likes_acoustic", False)

    scored = []
    for song_dict in songs:
        song = Song(
            id=song_dict["id"],
            title=song_dict["title"],
            artist=song_dict["artist"],
            genre=song_dict["genre"],
            mood=song_dict["mood"],
            energy=song_dict["energy"],
            tempo_bpm=song_dict["tempo_bpm"],
            valence=song_dict["valence"],
            danceability=song_dict["danceability"],
            acousticness=song_dict["acousticness"],
        )
        pts, explanation = _score(
            song, genre, mood, target_energy, target_valence, likes_acoustic
        )
        scored.append((song_dict, pts, explanation))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
