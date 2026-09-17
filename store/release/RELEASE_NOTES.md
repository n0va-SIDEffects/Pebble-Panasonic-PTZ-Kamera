# PTZ Remote 0.9 (Beta)

First public release.

**Camera control** — tested against an AW-UE100 on real hardware.

- Buttons: up/down work the selected axis, select switches between
  TILT, PAN, ZOOM and FOCUS, hold select for the menu.
- Motion: hold select as a dead-man switch and tilt your wrist. Zero is
  the posture you start from. Release to stop.
- Presets with a confirmation before overwriting, up to 8 cameras,
  adjustable speed, sensitivity and dead zone.
- Safety: dead-man switch, 250 ms arming delay, watchdog on the phone that
  stops the camera if the watch goes quiet mid-move, stop on exit.

**Camera preview** — experimental, off by default.

Fetches a still frame after a move, a preset or a camera change. Not yet
verified against real camera hardware; needs JPEG transmission enabled in
the camera's web menu (Video over IP → JPEG(1)).

**Known limits**

- Basic authentication only. Cameras that require digest auth (some newer
  AW-UE models with user auth switched on) will refuse the connection.
- Round displays (chalk) are not supported in this release — the layout
  does not fit yet.
- Interface is English only.
