# TerraMatch Chile – Afirmaciones del modelo y su evidencia (validación científica, Gantt #11)

**Para:** Carlos, Benja y Pancho · **De:** Rojas · **Domingo 15-nov-2026**
Usen solo estas afirmaciones en la página y la demo. Cada una tiene su archivo de respaldo. Si un texto dice algo que no está aquí, avísenme antes de publicarlo.

## Lo que SÍ podemos afirmar

| # | Afirmación | Evidencia | Archivo |
|---|---|---|---|
| 1 | Usamos 4 productos NASA: MOLA MEGDR, SLDEM2015, ASTER GDEM v3 y GPM IMERG V07 | Identificadores de producto y fuentes | `data/targets.json`, `data/raw/METADATOS_BJOR.txt`, `data/chile/processed/imerg_precip_2001_2024.metadata.txt` |
| 2 | Los recortes MOLA son idénticos a los archivos originales del PDS | Comparación píxel a píxel | `data/targets.json` (`input_files`) |
| 3 | Elysium Planitia es muy lisa a 463 m: pendiente P90 0,45°, relieve 15 m y rugosidad 0,15° en 5 km | Mediana de 5 ventanas MOLA | `data/targets.json` |
| 4 | Mare Tranquillitatis: pendiente P90 1,17°, relieve 59 m y rugosidad 0,42° | Mediana de 25 ventanas SLDEM2015 | `data/targets.json` |
| 5 | Comparamos 1.262 celdas de Chile con datos ASTER (4 teselas piloto) | Conteo de celdas con las 3 variables | `data/processed/master.metadata.json` |
| 6 | El modelo separa bien el terreno empinado: Llullaillaco queda en el percentil 8 y el 5% más empinado en el 2,5 | Pruebas de control | `results/validation.json` |
| 7 | Yungay (percentil 47) y Pajonales (percentil 63) no se parecen topográficamente a Elysium a esta escala | Pruebas de referencia no cumplidas | `results/validation.json`, `results/sites_summary.csv` |
| 8 | En la Luna, las coladas del Llaima se parecen más a Mare Tranquillitatis que el cono (S 39,0 contra 17,2) | Prueba de contraste | `results/validation.json` |
| 9 | Los resultados no dependen de la fuente de lluvia: con CR2MET los percentiles son prácticamente iguales (47,3 y 63,0) | Análisis complementario | `results/validation.json` → `sensitivity` |
| 10 | Las celdas más parecidas a Elysium están cerca de 24,5° S y 68,9° O (S = 100, confianza Alta) | Ranking entre las celdas puntuadas | `results/mars_scores_web.csv` |
| 11 | Todo es reproducible: pruebas, cálculo de variables, pipeline, notebook y figuras | Scripts ejecutados desde una carpeta limpia | `tests/`, `src/`, `notebooks/exploratory_analysis.ipynb`, `figures/make_figures.py` |

## Lo que NO podemos afirmar

| No decir | Por qué | Decir en cambio |
|---|---|---|
| "Encontramos el mejor análogo de Marte en Chile" | Solo cubrimos 4 teselas; no hay ranking nacional | "En las zonas piloto, las celdas más parecidas son…" |
| "Yungay y Pajonales validan el modelo" | No pasaron la prueba de relieve | "Son análogos por aridez, no por relieve a 5 km; el modelo lo detecta" |
| "Las coladas del Llaima son terreno lunar" | Siguen siendo más empinadas que el mar lunar (11,8° contra 0,9–2,5°) | "Se parecen más que el cono: es un resultado relativo" |
| "Alta confianza" para los sitios | Los 5 sitios tienen confianza Baja (p_top = 0) | Mostrar la confianza tal cual |
| Cualquier geoforma en 24,5° S, 68,9° O (salar, planicie, etc.) | Aún no se revisa en imagen satelital | "Planicies por identificar" hasta que Pancho lo confirme |
| Que la IA generó o ajustó resultados | Ningún valor fue generado por IA | "La IA asistió en el código; los datos y resultados vienen de productos NASA procesados" |

## Limitaciones que deben acompañar los resultados

Cobertura piloto · perfil de Marte con 5 de 25 ventanas (69% interpolado por MOLA) · comparación a 463 m y en ventanas de 5 km · IMERG sobrestima la lluvia en el desierto · mapa geológico 1:1M de una copia de terceros.
