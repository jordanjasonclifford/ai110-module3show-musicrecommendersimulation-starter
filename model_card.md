# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**Sound Zilla AI (SZA)**

---

## 2. Intended Use  

This recommender is meant to suggest songs based on how they actually feel, not just what they’re called or who made them. The goal is to take a user’s preferences and return a ranked list of songs that match that vibe as closely as possible, using things like genre, mood, energy, and overall emotional tone (valence).

It assumes the user can describe what they want upfront. Things like what genre they like, what mood they’re in, how energetic they want the music to be, and whether they lean more acoustic. It does not learn from history or adapt over time, it just works off that one snapshot of preferences.

This is mainly a classroom project to show how a basic content-based recommender works. It is not trying to be a real production system or handle personalization at scale.

---

## 3. How the Model Works  

Each song is basically treated like a set of traits that describe its vibe. The main ones I focus on are genre, mood, energy, and valence. Together, these give a pretty solid picture of how a song feels, whether that is high energy and upbeat or slow and more melancholic.

When a user gives their preferences, the system goes through every song and compares those traits directly. If the genre matches, it gets a solid boost. If the mood matches, it gets another boost. For things like energy and valence, it is not exact matching, instead the system gives more credit the closer the song is to the user’s target.

Every song ends up with a total score based on those comparisons. Then everything is ranked from highest to lowest, and the top songs are returned. The ones that match across most of the features naturally rise to the top, and weaker matches fall lower.

The main difference from the starter version is that everything is based on actual musical features. Things like title, ID, or artist are ignored since they do not really tell you if someone will like a song.

Avoid code here. 

---

## 4. Data

The dataset is a hand-built CSV of 20 songs, each representing a distinct genre and mood combination. Genres covered include pop, lofi, rock, edm, hip-hop, metal, jazz, blues, r&b, folk, country, reggae, indie pop, synthwave, ambient, classical, and punk. No songs were added or removed from the starter set. One thing worth noting is that the catalog skews almost entirely toward Western, English-language music; there are no K-pop, Latin, Afrobeats, or other global styles represented, which is why the Ghost Genre adversarial profile requesting k-pop could never receive a genre bonus. There is also exactly one song per genre, so the system cannot learn anything about patterns within a genre; it only knows whether a tag matches or not.

---

## 5. Strengths

The system works best when the user profile is well-defined and the catalog has a song that fits it closely. Profiles like EDM Euphoria and Chill Lofi produced near-perfect top scores because the catalog happened to contain a song matching on genre, mood, energy, and valence simultaneously; those results matched intuition right away. The Ghost Genre profile, where no matching genre existed at all, was still handled reasonably; the system returned musically sensible results ranked purely by energy and valence similarity, which showed the continuous signals degrade gracefully when categorical ones are unavailable. The scoring is also fully transparent; every recommendation includes a breakdown of exactly which signals fired and how many points each contributed, making it straightforward to check whether a result makes sense.

---

## 6. Limitations and Bias

The most significant bias discovered through testing is what I would call a **single-entry filter bubble**: the catalog contains exactly one song per genre, so any user whose preferred genre exists in the catalog will always receive that same song as their top recommendation regardless of how well it actually fits their mood, energy, or valence targets. This was most visible in the Deep Intense Rock profile, where Storm Runner ranked first even when the user's mood was switched to "melancholic" — a mood Storm Runner does not have — simply because the genre tag still fired and no other rock song existed to compete with it.

A second weakness is **exact-match brittleness on both genre and mood**. The scoring treats "indie pop" and "pop" as completely unrelated, and "focused" and "chill" as completely unrelated. During the mood-removal experiment, removing the mood signal caused Focus Flow (mood: focused) to rank as the top lofi recommendation for a user who wanted chill music — the system had no way to recognize that focused and chill are adjacent vibes, not opposites.

A third issue is the **silent acoustic preference failure**. When a user sets `likes_acoustic = True` alongside a rock genre, the acoustic bonus never fires because every rock song in the catalog has an acousticness score below the 0.6 threshold. The system returns results as if the acoustic preference simply was not there, with no indication to the user that their preference could not be satisfied. In a real product this would feel broken — the user asked for something and got nothing back about it.

---

## 7. Evaluation

I tested eight user profiles total: four standard ones covering High-Energy Pop, Chill Lofi, Deep Intense Rock, and EDM Euphoria, and four adversarial ones designed to find edge cases. The adversarial profiles covered a conflicting energy and mood combination, a genre not in the catalog, a user who wanted acoustic rock despite the catalog having no acoustic rock songs, and a fully neutral profile with no stated preferences. I also ran two controlled experiments. The first was a weight shift, lowering genre from 3.0 to 1.5 and raising energy and valence, which produced more intuitive rankings for profiles where mood mattered more than the label. The second was a feature removal test where I commented out the mood check entirely; that made nearly every profile worse, confirming mood is a load-bearing signal and not redundant with energy or valence.

---

## 8. Future Work

The most useful improvement would be fuzzy genre and mood matching; right now "indie pop" and "pop" share zero credit, and "focused" and "chill" are treated as completely unrelated. A similarity layer between categories would fix most of the exact-match brittleness observed in testing. Expanding the catalog well beyond 20 songs would also help considerably; a single-entry-per-genre structure means the genre signal behaves like a binary flag rather than a real pattern. A diversity constraint, such as capping results at one song per artist in the top five, would reduce the risk of the same artist appearing repeatedly in a small catalog. Longer term, tracking user skips and replays to adjust weights over time would make the profile dynamic rather than a one-time snapshot.

---

## 9. Personal Reflection

The biggest learning moment came when I changed the genre weight from 3.0 to 1.5 and watched the rankings shift noticeably across every profile, even though the raw score differences were only a point or two. In a 20-song catalog, the weight design is essentially the whole product; there is no volume of data to absorb a bad decision the way a real system would. That was the first time this felt less like a homework exercise and more like an actual engineering tradeoff.

AI tools helped the most during the adversarial profile design phase. I would not have systematically thought through cases like a ghost genre, a silent acoustic preference failure, or a contradicted energy and mood combination on my own; having those surfaced as prompts saved real time. That said, I had to verify every suggestion against the actual CSV and scoring logic, because the tool had no idea which moods or genres existed in the catalog. The Ghost Genre profile was a clear example; the suggestion was good, but I had to manually confirm that k-pop was genuinely absent before the test meant anything. The tool generated the idea and I did the verification, which felt like the right split.

What surprised me was how much the simple version still felt like a real recommendation when the profile was well-matched. EDM Euphoria scored 8.50 out of 9.0 and the top result, Overdrive Sunrise, was genuinely the right answer; five arithmetic operations produced something that would have been hard to argue with. The explanation output helped a lot with that feeling; seeing exactly which signals fired made the result feel earned rather than arbitrary, which is something most real recommenders cannot give you.

If I extended this, the first thing I would add is fuzzy matching between genre and mood labels, since the exact-match brittleness was the most consistent failure mode throughout testing. After that, a larger catalog, at minimum one where each genre has several entries with different moods and energy levels, so the system is actually choosing between real options rather than defaulting to the only song that qualifies.
