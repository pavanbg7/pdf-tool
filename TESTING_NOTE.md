## Tester Feedback

Had a friend clone the repo and try running it using only the README, without any help from me.

Where they got stuck:
- Wasn't sure at first whether they needed the virtual environment steps if they were going to use Docker instead the README didn't make clear these are two alternative paths, not sequential steps.
- When running the Docker command, initially used their real Windows file path instead of `/data/...` inside the container, since it wasn't obvious those needed to be different.
- Everything else (cloning, running merge/split, --help) worked without issues once past those two points.

Fix applied: added a short note clarifying that the local setup and Docker setup are separate options, and made the `/data/` path explanation more prominent in the Docker section.