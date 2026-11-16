# 🌎 TerraMatch Chile · Visual Experience v2 (Preview)

**Independent UI prototype by/for Team Joseadores · NASA Space Apps Challenge 2026**

> **Not the official submitted website.** This v2 is an experimental visual/interface version intended for review. It is **not** deployed to or merged into the original TerraMatch repository. The original web app remains at https://terramatch-chile-v07.streamlit.app/.

## ✨ What's new

- **Animated landing experience:** a subtle CSS starfield, a stylized planetary sphere and responsive transitions.
- **Guided mission explorer:** choose Mars or the Moon, preview one of the five pilot study areas, and jump directly into the map.
- **Interactive terrain comparison:** switch between slope P90, relief P95–P5 and roughness to compare each Chilean study area with its selected planetary reference. Values are the original v0.7 medians.
- **Interactive evidence views:** separate, readable Mars percentile and Moon similarity charts, with 0–100 axes and predefined Mars benchmark lines.
- **Better responsive accessibility:** high contrast, gentle hover effects and a `prefers-reduced-motion` alternative.
- **Bilingual interface (Spanish / English)** and the existing seven sections and regional zoom of the Llaima.

## 🔬 Scientific integrity — unchanged

**The numerical results and reference profiles are identical, byte-for-byte, to `martizng/terramatch-chile` at commit `8e871558f1d512ef1256f395c338f0f63e8dfd5c`.** Only presentation code, additional UI components, and this preview documentation differ.

- **4 ASTER GDEM v3 tiles** studied; **1,262** Chilean cells with terrain measurements.
- **895** Mars pilot cells and **256** Moon pilot cells with valid scores. **No national ranking.**
- Yungay (47.4th percentile) and Pajonales (63.1st) do not meet their Martian benchmark; Llullaillaco (8.3rd) behaves as a negative control.
- Mapped Llaima lava-flow sector (S≈39.0) scores above the cone (S≈17.2), **a relative result, not proof of lunar equivalence**.
- All five study sites have *low site-level confidence*. Mars MOLA direct-data coverage and volcanic cartography limitations remain.
- Blank/unscored/out-of-filter cells are **never** converted to zero similarity.

Scientific original: [source repo](https://github.com/martizng/terramatch-chile) · [methods](https://github.com/martizng/terramatch-chile/blob/main/docs/methodology.md) · [evidence](https://github.com/martizng/terramatch-chile/blob/main/docs/validation/AFIRMACIONES_Y_EVIDENCIA.md).

## 🚀 How to run as an independent Streamlit app

Upload the **contents of this folder** to a *different repository*. Keep the folder structure intact: `app.py`, `ui_data.py`, `v2_components.py`, `requirements.txt`, `data/`, `results/` and `assets/` must sit together at the repository root.

In [Streamlit Community Cloud](https://share.streamlit.io/), create a **new** app and select **your new repository**, its default branch, and `app.py` as the entrypoint. Give it a new name such as `terramatch-v2-preview`. Do **not** edit the deployment of the current official Streamlit site.

Alternatively, with Python installed:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

This preview requires no API keys or secrets. The minimum software dependencies are listed in `requirements.txt`; the exact Python version is not pinned. The app reads local CSV, JSON, GeoJSON and JPEG assets. It does not require the original large raster archives to **display** its results.

## Structure

```text
app.py                 Existing v0.10.3 frontend, extended only in layout/interaction
ui_data.py             Existing v0.10.3 data loader and offline map — unchanged
v2_components.py       NEW: CSS animations, guided experience, interactive charts
data/targets.json      UNCHANGED planetary reference profiles
data/chile/sites/      UNCHANGED study-area GeoJSON polygons
results/               UNCHANGED v0.7 scientific score/validation CSV and JSON
assets/visuals/        Existing elevation-derived images and Chile outline
requirements.txt       Streamlit, Pandas, NumPy, Plotly
```

## Important

The Mars and Moon percentiles/scores are **different measures**. The interface does not mix them on one chart. A 0–100 score is *topographic similarity under this pilot method*, not a percentage of overall planetary equivalence. All mapped Llaima lava-flow and Pajonales boundaries remain preliminary geological proxies.

All animations are visual-only and may be turned off via OS/browser reduced-motion preferences. Images are DEM-derived terrain renderings, not photographs; credits are in [`assets/visuals/ATTRIBUTION.md`](assets/visuals/ATTRIBUTION.md).

---

**Versión de prueba:** Esta v2 es una propuesta de interfaz independiente. No modifica ni los resultados científicos ni la página oficial de TerraMatch Chile. El objetivo es que el equipo pueda evaluar mejoras visuales y de navegación antes de decidir si incorpora alguna de ellas.
