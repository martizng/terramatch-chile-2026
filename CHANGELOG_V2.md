# TerraMatch Chile — v2 final

## New user-facing experience
- Subtle animated orbital-style hero and starfield, with `prefers-reduced-motion` accessibility support.
- Floating cards, smooth hover transitions and an improved main page hierarchy.
- Guided **Mission Explorer**: switch Mars/Moon, choose one of the five study areas, preview evidence and open its planetary map.
- Interactive **Terrain Differences** chart on site profiles: change between slope P90, local relief P95–P5 and roughness; unit-specific axes.
- Tabbed **Results & Evidence** charts for Martian benchmark percentiles and lunar relative scores, each explicitly on a 0–100 axis.
- Every new explanatory label is provided in **Spanish and English**.

## Not changed
- No scientific scores, percentile values, Monte Carlo outputs, quality statuses, references or filters are recalculated.
- Original Llaima zoom and preliminary GeoJSON overlays are preserved in `ui_data.py`.
- Five scientific JSON/CSV files match their original repository blob IDs exactly.
- Existing official Streamlit deployment and original GitHub repository were not modified.

## Pre-publication verification
- Python source syntax checked.
- 5 published scientific file Git blob IDs checked.
- 895 valid Mars cells, 256 Moon cells, 31,660 records per file, 5 study sites validated.
- New Plotly comparison charts generated for each site in both languages using a simulated Streamlit environment.
- Offline north/south Plotly map construction checked.
- **Browser/Streamlit Cloud end-to-end rendering still needs to be tested once deployed.**

## v2 final — Disclosure and scientific communication
- Added bilingual, four-item AI use disclosure in a readable bordered card.
- Removed the additional ASTER stereo-quality check block in Spanish and English.
- Kept the independently documented NUM-related **general limitation** unchanged.
- All source data files remain unchanged.
