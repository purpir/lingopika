# Fix Karaoke timing for Yandex Music

## Goal
Make `MediaSessionReader.mediaTimeToMillis` handle native media session durations/positions in different units so Yandex Music tracks get correct timing and lyrics can sync.

## Context
- `MediaSessionReader` reads media from Windows SMTC.
- `mediaTimeToMillis(long value)` currently always does `value * 1000L`, assuming seconds.
- Yandex Music reports values that are already milliseconds/larger ticks, causing duration/position to be wrong (often 0 or huge).
- Debug showed `dur=0` from PowerShell and `dur=180000` forced fallback in Java.

## Proposed Change
Update `mediaTimeToMillis` to classify the input:
- `value <= 0` -> 0
- `value > 1_000_000` -> treat as 100-nanosecond ticks, divide by 10_000
- `value > 1_000` -> treat as milliseconds, return as-is
- otherwise -> treat as seconds, multiply by 1_000

## Files
- `src/main/java/com/example/nightfall/util/media/MediaSessionReader.java`

## Validation
- Compile with Java 21 / Gradle.
- Run client and check `[KaraokeDebug]` logs: native duration/position should be non-zero and plausible.
- Verify lyrics timing advances with playback.

## Notes
- Keep debug logging for now; can remove later.
- Do not change `SyncedLyricsService` unless timing is still wrong after this fix.
