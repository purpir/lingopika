# Improve Karaoke lyrics matching for all languages

## Goal
Increase the chance of finding synced/plain lyrics for tracks from any player and language, including Yandex Music, SoundCloud, Spotify, and non-Latin titles.

## Current state
- `MediaSessionReader` now handles Cyrillic metadata, invalid Yandex durations, and bad `LastUpdatedTime` position deltas.
- `SyncedLyricsService` queries LRCLIB with `fetchExact` and `fetchSearch`, then `lyrics.ws` plain fallback.
- Search is still too narrow: it tries only the original title/artist, one stripped-title variant, first artist, and title-only.

## Proposed changes
1. Add a query-variant generator in `SyncedLyricsService`:
   - Normalize title/artist with `strip` and remove repeated spaces.
   - Generate variants:
     - original title + original artist
     - title without parenthetical/bracket text + original artist
     - original title + first artist before comma
     - stripped title + first artist
     - title only
     - stripped title only
   - Deduplicate variants.
2. In `load(...)`:
   - Try `fetchExact` for variants that have a non-empty artist and `durationMs > 0`.
   - Try `fetchSearch` for all variants.
   - Pick the first result with synced lyrics; otherwise the first with plain lyrics.
   - Keep the existing `lyrics.ws` plain fallback if all LRCLIB attempts fail.
3. Optional: add a second free plain-lyrics fallback using `lyrics.ovh` if `lyrics.ws` fails.
4. Keep UTF-8 URL encoding everywhere (already present) so Finnish, Chinese, Russian, etc. work.
5. Keep debug logging until validation; remove it as a final cleanup.

## Files
- `src/main/java/com/example/nightfall/util/media/SyncedLyricsService.java`
- `src/main/java/com/example/nightfall/util/media/MediaSessionReader.java` (already fixed; no further change unless debug removal)

## Validation
- Compile with Java 21.
- Test with:
  - Russian Yandex Music track
  - English Spotify track
  - SoundCloud browser track
  - A track with remix/feat in title
- Check `[KaraokeDebug] lyrics result ...` shows non-zero lines for at least one variant.
- Verify lyrics progress follows playback after seek/pause.

## Risks
- More HTTP requests per track; keep timeouts at 7s and single-thread executor.
- LRCLIB may still not contain some tracks; plain fallback remains.
- Debug logging should be removed before release.
