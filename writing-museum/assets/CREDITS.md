# Asset credits (Writing Museum)

The texture sets and the sky were copied from the Chronicle Museum
(`Earth_Worldbuild/_Museum/assets/`, same author) and are all **CC0 1.0 (public
domain)**; no attribution is required, but the sources are credited anyway. The
viewer loads the raw maps from `textures/<set>/` (`albedo.jpg`, `normal.jpg`
(OpenGL +Y), `roughness.jpg` / `metalness.jpg`, or Poly Haven's packed `arm.jpg` =
AO / roughness / metalness) and tiles them in world space (`web/js/matlib.js`).

| Set | Source | Asset | Maps kept | Licence |
|---|---|---|---|---|
| parquet | Poly Haven | [herringbone_parquet](https://polyhaven.com/a/herringbone_parquet) (2K) | diffuse, normal (GL), ARM | CC0 ([polyhaven.com/license](https://polyhaven.com/license)) |
| marble | ambientCG | [Marble012](https://ambientcg.com/view?id=Marble012) (2K) | color, normal (GL), roughness | CC0 ([docs.ambientcg.com/license](https://docs.ambientcg.com/license/)) |
| plaster | ambientCG | [PaintedPlaster017](https://ambientcg.com/view?id=PaintedPlaster017) (1K) | color, normal (GL), roughness | CC0 |
| metal | ambientCG | [Metal048A](https://ambientcg.com/view?id=Metal048A) (1K) | color, normal (GL), roughness, metalness | CC0 |

## Sky

`sky.jpg` is the scene background (equirectangular, sRGB; `web/js/render.js`), seen
through the rotunda oculus: [Kloofendal 48d Partly Cloudy (Pure Sky)](https://polyhaven.com/a/kloofendal_48d_partly_cloudy_puresky)
by Greg Zaal (sky edits Jarod Guest), Poly Haven, CC0
([polyhaven.com/license](https://polyhaven.com/license)); the tonemapped JPG
downscaled to 2048 × 1024.

## Models

None. `models.json` is an empty catalog; the museum places no sculptures.

## The passages on the walls

Every panel is a verbatim passage from one of the author's own works in
`creative-writing/vault/`, cited on its placard by vault path and line range. The
works are the author's; nothing here is generated text.
