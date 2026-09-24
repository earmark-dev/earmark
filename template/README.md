# My earmark library

A private podcast feed of things I meant to read, dictated by
[earmark](https://earmark-dev.github.io/earmark) and served by GitHub Pages.

## Setup (once)

1. **Settings → Pages**: set *Source* to **Deploy from a branch**, branch
   **main**, folder **/ (root)**, then click Save.
2. **Actions** tab: open the **earmark** workflow. Making this repo started a
   first run, which creates `earmark.toml`. If there is no run, click **Run
   workflow**.
3. When the run finishes, its summary shows your feed URL. Paste it into your
   podcast app as a feed you add by URL.

## Adding something

Edit [`sources.yml`](sources.yml) and add a line such as
`- https://example.com/an-article`, then commit. For a PDF or a Word file,
upload it into [`files/`](files) first, then list it as `- files/name.pdf`.

To remove an episode, delete its line from `sources.yml`.

## Changing the voice or the speed

The first run adds [`earmark.toml`](earmark.toml) to this repo. It holds the
settings for every new episode. Edit it and commit, the same way as
`sources.yml`:

```toml
voice = "bf_emma"   # hear every voice: https://earmark-dev.github.io/earmark/settings/
speed = 1.1         # 0.5 to 2.0
lang = "en-gb"      # en-gb for a British voice, en-us for an American one
```

A change applies to episodes made after it, not to the ones you already have.
To give one entry its own voice, write it as a mapping in `sources.yml`:

```yaml
- source: https://example.com/an-article
  voice: am_michael
```

Every setting is on the [Settings
page](https://earmark-dev.github.io/earmark/settings/).

## Worth knowing

- **Everything in a public repo is public**, including files you upload to
  `files/`. Only upload what you have the right to redistribute.
- GitHub Pages stops at about 1 GB. At the default bitrate one hour of audio is
  about 29 MB, so that is roughly 30 hours of audio.
