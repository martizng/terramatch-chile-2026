# Resultados piloto v0.7 (inmutables en la vista previa v2)

Estos CSV/JSON son los mismos del repositorio oficial TerraMatch Chile (commit `8e871558f1d512ef1256f395c338f0f63e8dfd5c`). El objetivo de esta carpeta es **mostrar** resultados científicos existentes, no recalcularlos.

| Archivo | Función |
|---|---|
| `mars_scores_web.csv` | 31.660 celdas, 895 con puntaje válido para Marte |
| `moon_scores_web.csv` | 31.660 celdas, 256 con puntaje válido para la Luna |
| `sites_summary.csv` | Cinco sitios piloto, puntajes, percentiles y niveles de confianza |
| `validation.json` | Pruebas de coherencia y sensibilidad |
| `mars_profile.csv`, `moon_profile.csv` | Comparación por indicador |
| `mars_montecarlo.csv`, `moon_montecarlo.csv` | Sensibilidad y estabilidad del ordenamiento |

**No constituyen un ranking nacional.** `scored` no debe confundirse con `outside_filter`, `insufficient_data` ni `no_filter_data`. En las celdas sin puntaje válido, `S` permanece nulo.

Consultar [evidencia del equipo](../docs/validation/AFIRMACIONES_Y_EVIDENCIA.md) y [metodología oficial](https://github.com/martizng/terramatch-chile/blob/main/docs/methodology.md).
