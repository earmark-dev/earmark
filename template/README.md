# My earmark library

A private podcast of things I meant to read, narrated by
[earmark](https://earmark-dev.github.io/earmark) and served by GitHub Pages.

## Setup (once)

1. **Settings → Pages**: set *Source* to **Deploy from a branch**, branch
   **main**, folder **/ (root)**, then click Save.
2. **Actions** tab: open the **earmark** workflow and click **Run workflow**.
   This first run creates `earmark.toml`.
3. When it finishes, the run's summary shows your feed URL. Paste it into your
   podcast app as a feed you add by URL.

## Adding something

Edit [`sources.yml`](sources.yml) and add a line such as
`- https://example.com/an-article`, then commit. For a PDF or a Word file,
upload it into [`files/`](files) first, then list it as `- files/name.pdf`.

To remove an episode, delete its line from `sources.yml`.

## Worth knowing

- **Everything in a public repo is public**, including files you upload to
  `files/`. Only upload what you have the right to redistribute.
- GitHub Pages stops at about 1 GB. At the default bitrate one hour of audio is
  about 29 MB, so that is roughly 30 hours of audio.
- Settings you can change, such as the voice and the speed, are in
  `earmark.toml`, which appears after the first run.
