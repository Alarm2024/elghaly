# Site art: prompts and status

Every picture in `assets/art/` is a **PLACEHOLDER** for now.

- They were drawn by `tools/art/placeholder_art.py` from shapes. No model made them, so there is no model licence on them.
- They follow the same look as the prompts below (palette 5b): near-black cards on a soft indigo-purple, with small gold lights. No green or teal.

## Replacing a placeholder with AI art

1. Generate the picture with the prompt for its slot, using **FLUX.1-schnell** or **Qwen-Image**.
   - Both are Apache-2.0, so commercial use is allowed.
   - Do **not** use FLUX.1-dev: its licence does not allow commercial use.
   - Do **not** use pictures made on a trial or evaluation service whose terms forbid production use (for example an NVIDIA API trial), even with an allowed model.
2. Save the result as a PNG.
3. Run `python3 tools/art/build_art.py <slot> <file.png>`. It writes every size and format the pages use, under the same file names.
4. No HTML change is needed. Commit the new files.

**Settings:**
- FLUX.1-schnell: 4 steps, guidance 0 (its default), seed 3535. Use the size in the table, or larger at the same shape.
- Qwen-Image: the aspect ratio in the table, 30–50 steps.
- Negative prompt (Qwen-Image): `text, letters, watermark, logo, signature, people, faces, hands, blurry, low resolution`

## The shared style (part of every prompt below)

> premium minimal 3D render, solid near-black objects (#0d0b1f) with softly rounded edges and a thin lavender rim light (#b9b3e6), a soft indigo-purple glow behind them (#5a4fc0 to #6a5fd0), a few small warm gold lights (#f5c542), gentle studio lighting, subtle film grain, calm and quiet, lots of empty space, no green, no teal, no text, no logos, no people

## Slots

| Slot | Used on | Shape / source size | Files written | Status |
|---|---|---|---|---|
| `hero-wide` | Home hero background, screens wider than 700px | 16:9, 1920×1080 | `hero-wide-1280/1920.avif/.webp` | placeholder |
| `hero-tall` | Home hero background, phones | 3:4, 900×1200 | `hero-tall-600/900.avif/.webp` | placeholder |
| `svc-servers` | Home, "Linux servers" card | 16:10, 1200×750 | `svc-servers-400/800.*` | placeholder |
| `svc-bots` | Home, "Telegram bots" card | 16:10, 1200×750 | `svc-bots-400/800.*` | placeholder |
| `svc-tools` | Home, "Solana tools" card | 16:10, 1200×750 | `svc-tools-400/800.*` | placeholder |
| `plumb` | Home Plumb card, /plumb hero | 16:10, 1200×750 | `plumb-400/800/1200.*` | placeholder |
| `quay` | Home QUAY card, /quay hero | 16:10, 1200×750 | `quay-400/800/1200.*` | placeholder |
| `og-home` | Link preview for elghaly.dev | 1200×630 | `og-home-1200x630.jpg` | placeholder |
| `og-plumb` | Link preview for /plumb | 1200×630 | `og-plumb-1200x630.jpg` | placeholder |
| `og-quay` | Link preview for /quay | 1200×630 | `og-quay-1200x630.jpg` | placeholder |

For the `og-*` slots, `build_art.py` handles the layout itself:
- it slides the picture to the right;
- it darkens the left side;
- it writes "elghaly" and the page title on it, in the site font.

So the prompt must ask for **no text**, with the subject in the centre.

## Prompts (copy one whole line, then add the shared style)

**hero-wide** (1920×1080)
> Wide abstract composition on a soft indigo-purple background (#5a4fc0): three near-black rounded cards like wallet cards floating at slight angles on the right side, each with one or two tiny gold lights, a few small gold specks of light in the air, the left half calm and empty for a headline, a lighter purple glow from the upper right,

**hero-tall** (900×1200)
> Tall abstract composition on a soft indigo-purple background (#5a4fc0): two near-black rounded cards floating at slight angles in the upper right, one in the lower left, tiny gold lights on them, the middle calm and empty for a headline, a lighter purple glow from the top,

**svc-servers** (1200×750)
> Three slim near-black server units stacked with even gaps, centred, each with a row of tiny glowing gold status lights on the left and dark vent slots on the right, front view, on a near-black background with a purple glow behind,

**svc-bots** (1200×750)
> One near-black chat bubble, centred, with a solid gold paper plane shape inside it, one small gold light floating to the upper right, on a near-black background with a purple glow behind,

**svc-tools** (1200×750)
> A near-black hexagon, centred, holding a round lens with a thin lavender ring and a gold light at its centre, a soft beam of gold light passing toward the lower right, on a near-black background with a purple glow behind,

**plumb** (1200×750)
> A near-black plumb bob hanging perfectly straight on a thin lavender thread from the top edge, a glowing gold core inside it, a thin dark level line near the bottom, centred, on a near-black background with a purple glow behind,

**quay** (1200×750)
> A minimal near-black pier stretching from the viewer toward a calm dark purple sea at night, one small gold light at the far end of the pier and its soft gold reflection on the water, thin purple horizontal light lines on the water, centred, low eye level,

**og-home** (1200×630)
> Abstract: three near-black rounded cards with tiny gold lights floating at slight angles on a soft indigo-purple background, centred,

**og-plumb** (1200×630)
> A near-black plumb bob with a glowing gold core hanging straight on a thin lavender thread, purple glow behind, centred,

**og-quay** (1200×630)
> A minimal near-black pier leading to one small gold light over a calm dark purple sea, centred, low eye level,

## From #26 (not AI-generated by us, kept as they were)

These files are in `assets/`, byte-identical to PR #26:
- `elghaly-hero-640/1168.webp`
- `35-card-192.webp`
- `plumb-card-192.webp`
- `quay-card-192.webp`
- `elghaly-lock-192.webp`
