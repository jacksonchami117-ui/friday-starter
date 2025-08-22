# Friday Martial Arts OS
Setup instructions here.

### Timeline Editor (New)
- Drag assets into a video track, drag to reorder, resize to trim
- Text overlay track with inline editing (supports {{tokens}} for lead fields)
- Zoom & snapping feel; keyboard: arrows to nudge (Shift=1s), Delete to remove
- Save/Load manifest via `/campaigns/<cid>/manifest`
- Asset uploads at `/campaigns/<cid>/assets/upload` (video/image), thumbnails via ffmpeg

### Providers (optional)
Set these to enable notifications:
- `SENDGRID_API_KEY`, `EMAIL_FROM`
- `TWILIO_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM`

### Cleanup
- `CLEAN_DAYS` (default 14): outputs older than this are deleted daily.
