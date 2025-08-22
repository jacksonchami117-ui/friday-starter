# FRIDAY Starter — Copilot Review Checklist

## Editor DnD — Reviewer Checklist
- [ ] Dragging assets onto the video track creates segments at the drop time
- [ ] Resize handles constrain to ≥ 0.1s and prevent negative durations
- [ ] Keyboard shortcuts: Arrows nudge, Shift=1s, Delete removes
- [ ] Text overlays are editable inline; saved into manifest with x/y/size/color
- [ ] Uploading assets creates server files in STATE_DIR and generates thumbnails (if ffmpeg present)
- [ ] /render/api/start receives the current manifest; legacy /render/start fallback still works
- [ ] All routes return friendly messages; no stack traces leak to UI

# FRIDAY — Polish & Reliability Review

## Reliability
- [ ] /settings correctly shows provider status and sends test messages (when keys present)
- [ ] Analytics "Retry" button triggers re-run without errors (engine may re-render all; acceptable)
- [ ] Housekeeping deletes outputs older than CLEAN_DAYS (default 14)
- [ ] Export CSV contains columns: business, first, last, email, website, phone, date, status, reason, video, thumb

## UX & A11y
- [ ] Campaign card shows progress bar (rendered/total)
- [ ] Buttons and forms have labels/roles; dropzones keyboard-operable
- [ ] Plain-English messages everywhere; no leaked traces

## Tests & CI
- [ ] pytest passes in CI
- [ ] Smoke still green after route additions

## Security
- [ ] No secrets stored in repo or state; env vars only
- [ ] File uploads restricted to allowed types; stored under STATE_DIR
