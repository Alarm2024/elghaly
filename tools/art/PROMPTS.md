# Site art: prompts and status

Every picture in `assets/art/` is a **PLACEHOLDER** for now.

- They were drawn by `tools/art/placeholder_art.py` from shapes. No model made them, so there is no model licence on them.
- They follow the same look as the prompts below: frosted glass on midnight navy, lit in pastel mint.

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

> premium minimal 3D render, frosted glass with soft rounded edges, deep midnight navy background (#070d1f), soft pastel mint rim light (#9ff0d0) and a faint periwinkle haze, gentle studio lighting, subtle film grain, calm and quiet, lots of dark empty space, no text, no logos, no people

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
> Wide abstract composition: three large frosted glass panels floating at slight angles on the right side, two small glass spheres catching light, the left half calm and empty for a headline, soft mint glow from the upper right, periwinkle haze lower left,

**hero-tall** (900×1200)
> Tall abstract composition: two frosted glass panels floating at slight angles in the upper right, one small glass sphere, the middle and lower half calm and empty for a headline, soft mint glow from the top, periwinkle haze at the bottom,

**svc-servers** (1200×750)
> Three slim frosted glass server units stacked with even gaps, centred, each with a row of tiny glowing mint status lights on the left and dark vent slots on the right, front view,

**svc-bots** (1200×750)
> One frosted glass chat bubble, centred, with a solid pastel mint paper plane shape inside it, one small glass sphere floating to the upper right,

**svc-tools** (1200×750)
> A frosted glass hexagon, centred, holding a round glass lens, a soft beam of mint light passing through the lens toward the lower right,

**plumb** (1200×750)
> A frosted glass plumb bob hanging perfectly straight on a thin glowing mint thread from the top edge, a soft mint core inside the glass, a thin glass level line near the bottom, centred,

**quay** (1200×750)
> A minimal frosted glass pier stretching from the viewer toward a calm dark navy sea at night, one small mint light at the far end of the pier and its soft reflection on the water, thin horizontal light lines on the water, centred, low eye level,

**og-home** (1200×630)
> Abstract: three frosted glass panels and two small glass spheres floating at slight angles, centred, soft mint glow,

**og-plumb** (1200×630)
> A frosted glass plumb bob hanging straight on a thin glowing mint thread, centred,

**og-quay** (1200×630)
> A minimal frosted glass pier leading to one small mint light over a calm dark navy sea, centred, low eye level,

## From #26 (not AI-generated by us, kept as they were)

These files are in `assets/`, byte-identical to PR #26:
- `elghaly-hero-640/1168.webp`
- `35-card-192.webp`
- `plumb-card-192.webp`
- `quay-card-192.webp`
- `elghaly-lock-192.webp`
