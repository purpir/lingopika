# ClickGUI alignment and dropdown fixes

## Goal
Fix two regressions in `client/gui/screen/ClickGui.java` after the dark-glass redesign:
1. Uneven text/frame alignment in module cards and setting rows.
2. Dropdown (mode/multi popup) not functioning correctly in the new GUI.

## Affected file
- `src/main/java/com/example/nightfall/client/gui/screen/ClickGui.java`

## Root causes
- Setting rows render with `sH = 32.0F` but advance by `38.0F * visibility`, creating inconsistent gaps and off-center text baselines.
- Popup scroll hit area uses `174.0F` width while popup is `200.0F` wide, so wheel-scroll over part of the popup is ignored.
- `handleModePopupClick` changes the value but never closes the popup for `ModeSetting`, so selection appears not to apply.
- Row/card constants (`MODULE_BASE_HEIGHT`, `SETTING_ROW_HEIGHT`) are declared but unused; actual dimensions are hardcoded, so prior constant changes had no effect.

## Implementation tasks
1. In `renderModules`, make row geometry consistent:
   - Set `sH = 34.0F` (or another even value) and advance by the same `sH + 4.0F` (or `38.0F`) consistently.
   - Adjust setting text baselines to `y + sH / 2.0F + 4.0F` where appropriate, or keep `y + 17.6F` only if `sH = 32.0F`.
   - Keep divider line at `cardY + 64.0F` aligned with header height.
2. Fix dropdown hit/scroll:
   - Change popup wheel-scroll hit width from `174.0F` to `200.0F`.
   - In `handleModePopupClick`, after `ModeSetting.setValue(option)`, set `this.modePopupOpen = false`.
   - Keep multi-select popup open after toggle.
3. Fix frame alignment:
   - Reconcile `MODULE_BASE_HEIGHT`/`SETTING_ROW_HEIGHT` usage or remove misleading constants.
   - Ensure module card header (64px) and scissor clip boundaries match `totalCardHeight`.
4. Compile with `gradlew compileJava --offline`.

## Validation
- Open ClickGUI, expand a module with settings: rows evenly spaced, text centered in frames.
- Open a ModeSetting dropdown, click an option: value changes and popup closes.
- Scroll inside dropdown: works across full 200px width.
- No compile errors.
