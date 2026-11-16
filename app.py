"""TerraMatch Chile — guided Streamlit explorer, v2 preview (independent visual/interaction layer).

Run with `streamlit run app.py`. All reported scores come from Rojas v0.7.
This application does not calculate new scientific results and never turns missing
observations, out-of-filter cells, or proxy polygons into confirmed analogues.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from v2_components import (
    inject_v2_style, render_mission_explorer, render_metric_comparison, render_evidence_charts,
)

from ui_data import (
    ROOT, VISUALS, SITE_EXPLANATIONS, read_data, scored_cells, astercells,
    make_terrain_map, site_image, status_summary,
)

st.set_page_config(page_title='TerraMatch Chile',
                   page_icon='🌎', layout='wide', initial_sidebar_state='expanded')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');
html,body,[class*="css"],div[data-testid="stApp"] {font-family:'DM Sans',sans-serif;}
.stApp {background:#F7FAFC;}
.block-container {max-width:1230px;padding-top:1.3rem;padding-bottom:3.5rem;}
h1,h2,h3 {font-family:'Outfit','DM Sans',sans-serif!important;letter-spacing:-.025em;}
h1 {color:#132F49!important;font-weight:800!important;}
h2 {color:#173D54!important;}
section[data-testid="stSidebar"] {background:#102A43;}
/* Only the dark sidebar's headings and navigation are light; never recolor all widget descendants. */
section[data-testid="stSidebar"] {color:#F2F8FA;}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] [data-testid="stRadio"] label p {color:#F2F8FA!important;}
section[data-testid="stSidebar"] a {color:#ACF0F1!important;}
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {background:#173C56;border:1px solid #34566D;border-radius:12px;padding:8px 10px;}
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radio"] {accent-color:#66D7D3;}
/* Protect future sidebar selectboxes too, including the popup opened outside the sidebar. */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {background:#FFFFFF!important;color:#173C52!important;}
section[data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"],
section[data-testid="stSidebar"] [data-baseweb="select"] input {color:#173C52!important;}
section[data-testid="stSidebar"] [data-baseweb="radio"] label:hover {background:#1A3F58;}
section[data-testid="stSidebar"] hr {border-color:#34566D;}
section[data-testid="stSidebar"] [data-testid="stRadio"] {font-weight:500;}
.tm-kicker {font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;color:#126878;font-weight:800;margin:0 0 10px;}
.tm-hero {background:radial-gradient(ellipse at 100% 0%,#236A74 0%,transparent 47%),linear-gradient(125deg,#102A43,#1A5165);border-radius:22px;padding:38px 36px;color:white;margin:6px 0 20px;box-shadow:0 10px 24px rgba(13,54,78,.13);}
.tm-hero h1 {color:#FFF!important;font-size:clamp(2.0rem,4vw,3.5rem);line-height:1.05;margin:6px 0 12px;}
.tm-hero p {color:#E1F2F5;font-size:1.12rem;line-height:1.55;max-width:750px;margin:0;}
.tm-hero .tag {display:inline-block;border:1px solid #77B6C4;border-radius:30px;padding:5px 12px;font-size:.77rem;letter-spacing:.045em;font-weight:700;color:#D9F9FB;margin-bottom:8px;}
.tm-note {background:#E9F3F5;border-left:4px solid #268B9A;padding:13px 18px;border-radius:8px;color:#254958;font-size:.91rem;margin:14px 0;}
.tm-warning {background:#FFF5EB;border-left:4px solid #D89A54;padding:12px 18px;border-radius:8px;color:#65462E;font-size:.91rem;margin:14px 0;}
.tm-card {background:#FFF;border:1px solid #E1EAEE;padding:18px 19px;border-radius:15px;height:100%;box-shadow:0 3px 9px rgba(30,54,71,.035);}
.tm-card h3 {font-family:'Outfit',sans-serif;font-size:1.25rem;margin:0 0 8px;color:#173C52;}
.tm-card p {font-size:.91rem;color:#344D5B;margin:0;line-height:1.48;}
.tm-step {display:inline-flex;width:34px;height:34px;align-items:center;justify-content:center;background:#E8F4F3;border-radius:11px;color:#177C83;font-weight:800;margin-right:10px;}
.tm-label {font-size:.81rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#365867;}
.tm-score {font-size:2.7rem;font-weight:800;color:#195B6F;font-family:'Outfit',sans-serif;line-height:1.1;}
.tm-caption {font-size:.8rem;color:#3F5664;line-height:1.45;}
.tm-foot {margin-top:42px;padding:16px 0;border-top:1px solid #DCE9ED;color:#415967;font-size:.8rem;}
div[data-testid="stMetric"] {background:white;border:1px solid #E2EBEF;padding:14px 17px;border-radius:14px;}
div[data-testid="stMetricLabel"] {font-size:.83rem;}
div[data-testid="stMetricValue"] {color:#16485C;}
div.stButton>button[kind="primary"] {background:#146C7A;border-color:#146C7A;color:white;border-radius:12px;}
div.stButton>button[kind="secondary"] {border-radius:12px;border-color:#B7CDD4;color:#215366;}
[data-testid="stExpander"] {border-radius:12px;}
[data-testid="stImage"] img {border-radius:12px;}
/* Contrast audit (WCAG AA for small text, >= 4.5:1) - main light surfaces only. */
[data-testid="stMain"] {color:#173847;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] > p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] > ul,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] > ol {color:#263E4B;}
[data-testid="stMain"] [data-testid="stCaptionContainer"] p,
[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
[data-testid="stMain"] [data-testid="stMetricLabel"] p {color:#334D5B!important;opacity:1!important;}
[data-testid="stMain"] [data-testid="stMetricValue"] {color:#123C50!important;}
[data-testid="stMain"] [data-testid="stDataFrame"] {color:#173847;}
.tm-kicker {color:#126878;}
.tm-card p {color:#344D5B;}
.tm-label {color:#365867;}
.tm-caption {color:#3F5664;}
.tm-foot {color:#415967;}
.tm-note {color:#1F4453;}
.tm-warning {color:#573D26;}
/* Sidebar labels remain light on dark; white inputs keep dark foreground. */
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] > p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:#E3F1F5!important;}
section[data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"],
section[data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"] * {color:#173C52!important;}
</style>''', unsafe_allow_html=True)

# Independent v2 UI layer; scientific data sources remain unchanged.
inject_v2_style()

PAGES=['home','about','method','explore','sites','validation','data']
TR={
'es':{
'nav':'NAVEGACIÓN','home':'Inicio','about':'Sobre el proyecto','method':'Cómo funciona','explore':'Explorar Chile','sites':'Fichas de sitios','validation':'Resultados y validación','data':'Datos y limitaciones',
'lang':'Idioma','context':'Prototipo de investigación · NASA Space Apps Challenge 2026',
'hero_kicker':'CIENCIA PLANETARIA · DATOS ABIERTOS · CHILE',
'hero_title':'Exploramos la Tierra para comprender otros mundos.',
'hero_text':'TerraMatch Chile compara ambientes de nuestro país con superficies seleccionadas de Marte y la Luna. Mediante datos científicos, buscamos similitudes topográficas, reconocemos diferencias y proponemos lugares para investigar.',
'cta_explore':'Explorar el mapa','cta_how':'Conocer la metodología',
'what':'¿Qué es TerraMatch Chile?','what_text':'Una plataforma geoespacial exploratoria que reúne datos terrestres y planetarios para identificar candidatos a análogos parciales. No pretende afirmar que un lugar chileno sea idéntico a Marte o la Luna.',
'why':'¿Por qué Chile?','why_text':'Nuestro territorio reúne desiertos áridos, salares, sistemas volcánicos y zonas de alta montaña. Esa diversidad permite estudiar preguntas distintas usando sitios de referencia y de contraste.',
'journey':'¿Cómo quieres comenzar?','journey1':'Conocer el proyecto','journey1d':'Comprende el problema, los objetivos y las preguntas de investigación.','journey2':'Explorar el mapa','journey2d':'Localiza las zonas con resultados y descubre qué significa cada punto.','journey3':'Visitar los sitios','journey3d':'Compara Yungay, Pajonales, Llullaillaco y las áreas del Llaima.',
'glance':'Nuestra primera exploración, en cifras','s_ast':'Celdas con relieve ASTER','s_planets':'Perfiles planetarios','s_sites':'Sitios de evaluación','s_window':'km por ventana','home_note':'Los resultados se limitan a cuatro teselas ASTER; no son un ranking de todo Chile.',
'about_kicker':'EL PROPÓSITO','about_title':'¿Y si estudiar otros mundos comenzara en Chile?',
'about_problem':'El desafío','about_problem_txt':'Los datos geológicos y topográficos de la Tierra, Marte y la Luna provienen de fuentes diferentes. Compararlos exige armonizar escalas, explicar qué indicadores son comparables y distinguir evidencia de hipótesis.',
'about_question':'Nuestra pregunta de investigación','about_question_txt':'¿Qué ambientes de Chile presentan características medibles comparables a determinados entornos lunares y marcianos, en qué se parecen, en qué difieren y para qué investigaciones podrían ser útiles?',
'about_solution':'Nuestra respuesta','about_solution_txt':'Creamos un flujo de exploración geoespacial que selecciona un perfil planetario, filtra condiciones terrestres relevantes, calcula similitud topográfica y comunica la calidad y límites de cada resultado.',
'about_roles':'Sitios seleccionados con propósitos distintos','mars_profile':'Marte · Elysium Planitia','moon_profile':'Luna · Mare Tranquillitatis',
'about_analogy':'Un análogo es siempre parcial','about_analogy_txt':'Una similitud de relieve no implica igualdad de materiales, atmósfera, gravedad, temperatura ni procesos biológicos. La interpretación depende de la pregunta científica.',
'method_kicker':'UN MÉTODO EXPLICABLE','method_title':'De datos abiertos a comparaciones que se pueden revisar',
'method_sub':'Separamos cuatro etapas para que cada puntuación tenga contexto, datos y limitaciones visibles.',
'step1':'1. Reunir datos','step1d':'ASTER GDEM v3 (Chile), MOLA (Marte), SLDEM2015 (Luna), GPM IMERG (aridez) y cartografía geológica para la Luna.',
'step2':'2. Comparar a la misma escala','step2d':'Remuestreo a ~463 m y extracción de indicadores en ventanas de 5 km. No comparamos pendientes calculadas a resoluciones incompatibles.',
'step3':'3. Aplicar filtros y puntuar','step3d':'Para Marte: aridez ≤250 mm/año. Para la Luna: unidades volcánicas. Solo después se calcula el puntaje topográfico de 0 a 100.',
'step4':'4. Revisar estabilidad','step4d':'500 repeticiones Monte Carlo, cobertura de variables y pruebas de coherencia. Reportamos también las pruebas que no cumplen.',
'metrics':'Las tres variables que sí entran al puntaje','slope':'Pendiente P90','slope_desc':'Qué tan inclinados son los sectores relativamente más empinados en la ventana.','relief':'Relieve local P95–P5','relief_desc':'Diferencia entre cotas altas y bajas: cuánto varía la altura del terreno.','rough':'Rugosidad','rough_desc':'Variabilidad de la inclinación: cuánto cambia la pendiente dentro del sector.',
'method_tip':'El puntaje 100 significa que las tres variables caen cerca de los rangos de referencia definidos. NO significa un 100 % de equivalencia planetaria.',
'explore_kicker':'MAPA INTERACTIVO','explore_title':'Explora las áreas de estudio de Chile',
'explore_sub':'Elige un planeta, enfoca una región y acerca el mapa. Los colores indican similitud topográfica solo donde existe un puntaje válido.',
'planet':'¿Con qué planeta quieres comparar?','mars':'Marte','moon':'Luna','map_mode':'¿Qué quieres visualizar?','score_view':'Similitud topográfica','coverage_view':'Cobertura y filtros',
'region':'Zona del mapa','all':'Chile (referencial)','north':'Norte: Yungay / Pajonales','south':'Sur: Llaima',
'min_score':'Puntaje mínimo','show_sites':'Mostrar sitios destacados',
'map_hint':'Acerca con el mouse y coloca el cursor sobre los puntos. Los diamantes identifican sitios piloto; los puntos pequeños, celdas de análisis. La silueta de Chile es orientativa y no utiliza mapas externos.',
'filter_note':'Fuera de filtro no significa baja similitud. Si faltan datos, no calculamos ningún puntaje.',
'valid_map':'Celdas con puntaje','aster_map':'Celdas ASTER procesadas','total_map':'Celdas de la grilla general',
'legend':'Cómo interpretar el mapa','legend_scored':'Con puntaje: cumple condiciones y tiene suficientes datos.','legend_outside':'Fuera del filtro: no cumple aridez o unidad volcánica.','legend_missing':'Sin datos: no tiene información suficiente de relieve o del filtro.','legend_score':'Cuanto mayor el número, mayor proximidad al perfil topográfico elegido; solo dentro del área piloto.',
'pilot_rank':'Celdas mejor puntuadas en la cobertura piloto','download':'Descargar resultados válidos como CSV','pilot_only':'Los primeros lugares son solo entre celdas elegibles del piloto, no de todo Chile.',
'sites_kicker':'EXPLORA CADA LUGAR','sites_title':'Cinco sectores, cinco preguntas de investigación',
'sites_sub':'Una ficha reúne el propósito del sitio, su relieve, la comparación con el perfil planetario y sus limitaciones.',
'select_site':'Selecciona un sitio para explorar','site_score':'Similitud topográfica','site_pct':'Percentil del piloto','site_cov':'Cobertura de variables','site_conf':'Confianza declarada','terrain_photo':'Visualización del relieve ASTER del sector (no fotografía)',
'what_score':'¿Qué nos dice este resultado?','comp_title':'Sitio chileno frente a la referencia planetaria','value_site':'Sitio (mediana del área)','value_target':'Perfil planetario (mediana)','metric_scope':'Los indicadores del sitio provienen de las celdas seleccionadas en su polígono/área de estudio.',
'interpret':'Interpretación preliminar','proxy_warning':'Pajonales y el sector de coladas del Llaima usan polígonos geológicos aproximados: no son delimitaciones definitivas.',
'llaima_caution':'La mayor similitud del sector de coladas es relativa al cono, NO demuestra terreno lunar equivalente. Su pendiente P90 (~11,8°) supera el intervalo de referencia lunar (~0,9–2,5°).',
'validation_kicker':'EVIDENCIA Y RESULTADOS','validation_title':'Lo que encontramos — y lo que todavía no sabemos',
'validation_intro':'Las pruebas de coherencia no fueron todas exitosas. Mostrarlas también es parte del rigor: los resultados no se ajustaron para forzar conclusiones.',
'mars_results':'Pruebas del perfil marciano','moon_results':'Prueba del perfil lunar','pass':'Cumple','fail':'No cumple','not_eval':'Pendiente',
'yungay_check':'Yungay por encima del percentil 75','paj_check':'Pajonales por encima del percentil 75','llulla_check':'Llullaillaco como control bajo el percentil 25','steep_check':'Terreno empinado como control bajo el percentil 25','llaima_check':'Sector de coladas con mayor similitud que el cono',
'insight':'Hallazgo principal','insight_text':'Yungay y Pajonales son pertinentes como referencias ambientales, pero aquí no destacaron por similitud de relieve con Elysium Planitia. Un candidato puede ser útil para una pregunta científica y no para otra.',
'validation_precision':'Los percentiles están calculados solo entre celdas elegibles del piloto. La confianza de los cinco sitios se reporta como baja; no equivale a probabilidad de que sean análogos.',
'data_kicker':'TRANSPARENCIA','data_title':'Datos abiertos, alcance claro y limitaciones visibles',
'data_sources':'Fuentes principales','limits':'Limitaciones que debes conocer','limits1':'Cobertura restringida: cuatro teselas ASTER y 1.262 celdas con topografía, no un muestreo nacional exhaustivo.',
'limits2':'La procedencia de píxeles ASTER (archivos NUM) aún no se integra explícitamente al cálculo en v0.7.',
'aster_quality_title':'Control adicional de calidad ASTER',
'aster_quality_body':'Según el control de calidad comunicado por el equipo, en las cuatro áreas piloto revisadas el 100 % de los píxeles analizados proviene de mediciones estéreo ASTER (11–29 escenas) y no presenta relleno. Esta verificación adicional fue comunicada por el equipo y aún no figura en AFIRMACIONES_Y_EVIDENCIA.md; debe archivarse su informe NUM para considerarla plenamente respaldada. Las máscaras NUM todavía no se aplican explícitamente dentro del motor v0.7. No equivale a certificar todas las teselas ni todo Chile.',
'limits3':'El filtro geológico lunar utiliza una fuente derivada y una leyenda a escala regional que necesitan confirmación.',
'limits4':'Dos delimitaciones de sitios son proxies geológicos: Pajonales y las coladas del Llaima.',
'limits5':'La validación del motor y la reproducibilidad de las fuentes planetarias requieren completar la auditoría independiente.',
'limits6':'No se infiere habitabilidad, equivalencia geológica completa, rutas de vehículos ni seguridad de aterrizaje.',
'limits7':'El perfil de Elysium Planitia usa solo 5 de 25 ventanas MOLA con al menos 50 % de observaciones directas; aproximadamente 69 % del recorte no tiene medición directa y la interpretación debe reconocer el uso de valores interpolados.',
'limits8':'El informe científico advierte que IMERG puede sobrestimar la precipitación en el desierto. Como sensibilidad, CR2MET produjo percentiles similares para Yungay y Pajonales; esto no elimina la incertidumbre del filtro de aridez.',
'data_status':'¿Qué significa cada estado?','scored_label':'Con puntaje','outside_label':'Fuera del filtro','insuff_label':'Información insuficiente','nofilter_label':'Sin información del filtro',
'data_quality':'Consulta los archivos, resultados y método reproducible desde GitHub.',
'footer':'Desarrollado por Team Joseadores · Universidad de La Frontera, Temuco, Chile · NASA Space Apps Challenge 2026 · Prototipo de investigación (no afiliación ni aval de NASA).',
'pilot_badge':'Vista previa v2 · Datos v0.7',
'source_code':'Código fuente',
'method_link':'Metodología',
'full_method':'Consultar metodología técnica completa',
'review_link':'Revisión de calidad',
'expected_files':'Archivos requeridos:',
'image_missing':'Imagen pendiente de incorporar',
'terrain_caption':'Visualizaciones de relieve derivadas de modelos de elevación; no son fotografías.',
'site_llaima_flows':'Llaima, sector de coladas',
'site_llaima_cone':'Llaima, cono',
'site_pajonales':'Salar de Pajonales',
'site_yungay':'Yungay',
'site_llullaillaco':'Llullaillaco',
'planet_label_mars':'Marte',
'planet_label_moon':'Luna',
'technical_details':'Detalles técnicos',
'detail_site':'Identificador del sitio',
'detail_profile':'Perfil planetario',
'detail_cells':'Celdas de análisis del área',
'detail_scored':'Celdas con puntuación',
'detail_stability':'Frecuencia entre el 1 % superior (p_top)',
'detail_status':'Estado','detail_value':'Valor',
'detail_geometry':'Geometría',
'geometry_polygon':'Polígono',
'geometry_point':'Punto',
'site_comparison':'Coladas del Llaima frente al cono',
'preliminary_geometry':'Comparación piloto; delimitaciones geológicas preliminares.',
'cell_id_label':'ID de celda',
'latitude':'Latitud',
'longitude':'Longitud',
'score_col':'Puntaje',
'coverage_col':'Cobertura (%)',
'confidence_col':'Confianza',
'source_chile_topo':'Chile · topografía',
'source_mars':'Marte · Elysium Planitia',
'source_moon':'Luna · Mare Tranquillitatis',
'source_precip':'Chile · precipitación',
'source_geo':'Chile · geología',
'source_boundaries':'Chile · límites referenciales',
'source_link':'Abrir fuente',
'map_chile_aster':'Chile · ASTER GDEM v3 · Yungay',
'map_mars_mola':'Marte · MOLA · Elysium Planitia',
'map_moon_sldem':'Luna · SLDEM2015 · Mare Tranquillitatis',
'status_scored':'Con puntaje',
'status_outside_filter':'Fuera del filtro',
'status_insufficient_data':'Información insuficiente',
'status_no_filter_data':'Sin datos del filtro',
'nav_git':'GitHub',
'app_error':'Faltan los datos v0.7 o hay un error de formato: ',
},
'en':{
'nav':'NAVIGATION','home':'Home','about':'About the Project','method':'How It Works','explore':'Explore Chile','sites':'Site Profiles','validation':'Results & Validation','data':'Data & Limitations',
'lang':'Language','context':'Research prototype · NASA Space Apps Challenge 2026',
'hero_kicker':'PLANETARY SCIENCE · OPEN DATA · CHILE','hero_title':'Explore Earth. Understand Other Worlds.',
'hero_text':'TerraMatch Chile compares Chilean environments with selected terrains on Mars and the Moon. Using scientific data, we examine topographic similarities, explain differences and identify areas worth investigating.',
'cta_explore':'Explore the map','cta_how':'How it works',
'what':'What is TerraMatch Chile?','what_text':'An exploratory geospatial platform combining Earth and planetary datasets to investigate partial analogue candidates. It does not claim that Chilean locations are identical to Mars or the Moon.',
'why':'Why Chile?','why_text':'Chile includes arid deserts, salt flats, volcanic systems and high mountains. This diversity allows separate scientific questions to be explored using reference and contrast sites.',
'journey':'Where would you like to start?','journey1':'About the project','journey1d':'Understand the problem, objective and research questions.','journey2':'Explore the map','journey2d':'Find the areas with results and learn what each point means.','journey3':'Visit the sites','journey3d':'Compare Yungay, Pajonales, Llullaillaco and the Llaima areas.',
'glance':'Our pilot exploration at a glance','s_ast':'Cells with ASTER terrain','s_planets':'Planetary target profiles','s_sites':'Evaluation sites','s_window':'km analysis window','home_note':'Results cover four ASTER tiles only; they are not an all-Chile ranking.',
'about_kicker':'THE PURPOSE','about_title':'What if studying other worlds began in Chile?',
'about_problem':'The challenge','about_problem_txt':'Geological and topographic datasets for Earth, Mars and the Moon come from different sources. Comparing them requires harmonized scales, appropriate indicators and transparent separation of evidence from hypothesis.',
'about_question':'Our research question','about_question_txt':'Which environments in Chile share measurable characteristics with selected lunar and Martian terrains, where do they differ, and for what research could they be useful?',
'about_solution':'Our response','about_solution_txt':'We built a geospatial exploration workflow that selects a planetary profile, applies relevant environmental filters, computes topographic similarity and communicates quality and limitations.',
'about_roles':'Sites chosen for different scientific roles','mars_profile':'Mars · Elysium Planitia','moon_profile':'Moon · Mare Tranquillitatis',
'about_analogy':'Every analogue is partial','about_analogy_txt':'Similar terrain does not imply identical materials, atmosphere, gravity, temperature or biology. Interpretation depends on the scientific question.',
'method_kicker':'AN EXPLAINABLE METHOD','method_title':'From open datasets to comparisons you can inspect',
'method_sub':'Four steps connect each result to its supporting data and limitations.',
'step1':'1. Collect data','step1d':'ASTER GDEM v3 (Chile), MOLA (Mars), SLDEM2015 (Moon), GPM IMERG (aridity), and geological maps for the lunar filter.',
'step2':'2. Harmonize scale','step2d':'Resample to ~463 m and compute indicators in 5 km windows. Slopes from inconsistent resolutions are not directly compared.',
'step3':'3. Filter and score','step3d':'Mars: aridity ≤250 mm/year. Moon: volcanic units. Only then calculate the 0–100 terrain similarity score.',
'step4':'4. Check robustness','step4d':'500 Monte Carlo repetitions, variable coverage and coherence checks. Failed checks are reported, too.',
'metrics':'The three metrics used in the score','slope':'90th-percentile slope','slope_desc':'How steep the relatively steep portions of the analysis window are.','relief':'Local relief (P95–P5)','relief_desc':'Difference between higher and lower elevation percentiles.','rough':'Terrain roughness','rough_desc':'How much slope varies across the analysis window.',
'method_tip':'A score of 100 means the metrics lie near the selected topographic reference ranges. It does NOT mean 100% planetary equivalence.',
'explore_kicker':'INTERACTIVE MAP','explore_title':'Explore the Chilean study areas','explore_sub':'Choose a planet, focus on an area and zoom. Colors indicate terrain similarity only where a valid score is available.',
'planet':'Select a planetary reference','mars':'Mars','moon':'Moon','map_mode':'What would you like to see?','score_view':'Terrain similarity','coverage_view':'Coverage & filters',
'region':'Map area','all':'Chile (reference)','north':'North: Yungay / Pajonales','south':'South: Llaima',
'min_score':'Minimum score','show_sites':'Show key sites',
'map_hint':'Zoom with the mouse and hover over points. Diamonds identify pilot sites; smaller dots are analytical grid cells. The offline Chile outline is only a cartographic reference.',
'filter_note':'Outside filter does not mean low similarity. Where data are missing, no score is calculated.',
'valid_map':'Scored cells','aster_map':'Cells with ASTER terrain','total_map':'Reference grid cells',
'legend':'How to read the map','legend_scored':'Scored: the cell passes the filter and has enough data.','legend_outside':'Outside filter: fails aridity or volcanic-unit screening.','legend_missing':'Missing: insufficient terrain or filter information.','legend_score':'A larger score means closer terrain metrics, within the pilot coverage only.',
'pilot_rank':'Highest-scoring cells within pilot coverage','download':'Download valid results (CSV)','pilot_only':'These rankings cover only eligible pilot cells, not the entire country.',
'sites_kicker':'EXPLORE EACH PLACE','sites_title':'Five study areas, five different research questions',
'sites_sub':'Each profile explains the site role, measured terrain, planetary comparison, and limitations.',
'select_site':'Choose a site','site_score':'Terrain similarity','site_pct':'Pilot percentile','site_cov':'Variable coverage','site_conf':'Reported confidence','terrain_photo':'ASTER shaded terrain rendering (not a photograph)',
'what_score':'What does this result tell us?','comp_title':'Chilean site vs planetary reference','value_site':'Site (area median)','value_target':'Planetary target (median)','metric_scope':'Site indicators summarize selected analytical cells within the study area.',
'interpret':'Preliminary interpretation','proxy_warning':'Pajonales and the Llaima lava-flow sector use approximate geological polygons and are not final field boundaries.',
'llaima_caution':'The lava-flow sector only scores higher relative to the cone; it is NOT equivalent to lunar terrain. Its P90 slope (~11.8°) exceeds the lunar reference interval (~0.9–2.5°).',
'validation_kicker':'EVIDENCE & RESULTS','validation_title':'What we found — and what remains uncertain',
'validation_intro':'Not all coherence checks passed. Reporting them honestly is part of the method; scores were not altered to force a conclusion.',
'mars_results':'Martian reference checks','moon_results':'Lunar reference check','pass':'Passed','fail':'Not met','not_eval':'Pending',
'yungay_check':'Yungay above 75th percentile','paj_check':'Pajonales above 75th percentile','llulla_check':'Llullaillaco control below 25th percentile','steep_check':'Steep terrain control below 25th percentile','llaima_check':'Mapped lava-flow area scores above the cone',
'insight':'Key finding','insight_text':'Yungay and Pajonales are useful environmental reference sites, but they did not stand out as topographic matches for Elysium Planitia. A site may be relevant to one research question but not another.',
'validation_precision':'Percentiles are based on eligible pilot cells only. All five site-level confidence flags are low; this is not the probability of being a valid planetary analogue.',
'data_kicker':'TRANSPARENCY','data_title':'Open data, clearly stated scope and limitations',
'data_sources':'Main sources','limits':'Important limitations','limits1':'Limited coverage: four ASTER tiles and 1,262 cells with terrain data, not an exhaustive national sample.',
'limits2':'ASTER NUM pixel-provenance masks are not yet explicitly incorporated into scoring in v0.7.',
'aster_quality_title':'Additional ASTER data-quality check',
'aster_quality_body':'According to the quality check reported by the team, all pixels assessed in the four reviewed pilot areas originate from ASTER stereo measurements (11–29 scenes), with no filling. This additional finding was reported by the team and is not yet documented in AFIRMACIONES_Y_EVIDENCIA.md; the NUM quality report should be archived before treating it as fully verified. NUM masks are not yet explicitly applied within the v0.7 scoring engine. This is not a quality certification for all four tiles or for Chile as a whole.',
'limits3':'The lunar volcanic-unit filter relies on a derived regional geological layer requiring source and legend verification.',
'limits4':'Two site outlines are geological proxies: Pajonales and the mapped Llaima lava-flow sector.',
'limits5':'Independent end-to-end validation of the engine and planetary source reconstruction remains incomplete.',
'limits6':'No claims of habitability, full geological equivalence, vehicle routes or landing-site safety are made.',
'limits7':'The Elysium Planitia reference uses only 5 of 25 MOLA windows with at least 50% direct observations; approximately 69% of the crop lacks direct measurements, so interpolation must be acknowledged.',
'limits8':'The scientific report warns that IMERG may overestimate desert rainfall. A CR2MET sensitivity analysis yielded similar percentiles for Yungay and Pajonales, but this does not eliminate uncertainty in aridity screening.',
'data_status':'What do the status flags mean?','scored_label':'Scored','outside_label':'Outside filter','insuff_label':'Insufficient information','nofilter_label':'Missing filter information',
'data_quality':'Inspect the scientific files, results and reproducible method on GitHub.',
'footer':'Built by Team Joseadores · Universidad de La Frontera, Temuco, Chile · NASA Space Apps Challenge 2026 · Research prototype (not NASA-endorsed).',
'pilot_badge':'v2 preview · v0.7 data',
'source_code':'Source code',
'method_link':'Methodology',
'full_method':'Read the full technical methodology',
'review_link':'Quality review',
'expected_files':'Required files:',
'image_missing':'Image not yet available',
'terrain_caption':'Shaded terrain visualizations derived from elevation models; these are not photographs.',
'site_llaima_flows':'Llaima lava-flow sector',
'site_llaima_cone':'Llaima volcanic cone',
'site_pajonales':'Salar de Pajonales',
'site_yungay':'Yungay',
'site_llullaillaco':'Llullaillaco',
'planet_label_mars':'Mars',
'planet_label_moon':'Moon',
'technical_details':'Technical details',
'detail_site':'Site identifier',
'detail_profile':'Planetary profile',
'detail_cells':'Analysis cells in study area',
'detail_scored':'Scored cells',
'detail_stability':'Frequency among top 1% (p_top)',
'detail_status':'Status','detail_value':'Value',
'detail_geometry':'Geometry',
'geometry_polygon':'Polygon',
'geometry_point':'Point',
'site_comparison':'Llaima lava-flow sector vs cone',
'preliminary_geometry':'Pilot comparison; preliminary geological boundaries.',
'cell_id_label':'Cell ID',
'latitude':'Latitude',
'longitude':'Longitude',
'score_col':'Score',
'coverage_col':'Coverage (%)',
'confidence_col':'Confidence',
'source_chile_topo':'Chile · topography',
'source_mars':'Mars · Elysium Planitia',
'source_moon':'Moon · Mare Tranquillitatis',
'source_precip':'Chile · precipitation',
'source_geo':'Chile · geology',
'source_boundaries':'Chile · reference boundaries',
'source_link':'Open source',
'map_chile_aster':'Chile · ASTER GDEM v3 · Yungay',
'map_mars_mola':'Mars · MOLA · Elysium Planitia',
'map_moon_sldem':'Moon · SLDEM2015 · Mare Tranquillitatis',
'status_scored':'Scored',
'status_outside_filter':'Outside filter',
'status_insufficient_data':'Insufficient information',
'status_no_filter_data':'Missing filter information',
'nav_git':'GitHub',
'app_error':'Missing v0.7 data or invalid format: ',
}}

for key in set(TR['es']) | set(TR['en']):
    if key not in TR['es'] or key not in TR['en']:
        raise RuntimeError(f'Missing translation for: {key}')

if 'lang' not in st.session_state: st.session_state.lang='es'
if 'page' not in st.session_state: st.session_state.page='home'
if 'planet' not in st.session_state: st.session_state.planet='mars'

# A high-contrast language radio avoids the white-text-on-white-selectbox bug.
# Language names are displayed in their own language, as is standard for a language switcher.
ui_lang=st.sidebar.radio(TR[st.session_state.lang]['lang'], ['es','en'],
                         format_func=lambda code: 'Español' if code=='es' else 'English',
                         index=0 if st.session_state.lang=='es' else 1,
                         key='ui_lang', horizontal=True)
if ui_lang != st.session_state.lang:
    st.session_state.lang=ui_lang
    st.rerun()  # Refresh the label and all content in the newly selected language.
locale=st.session_state.lang
t=TR[locale]

st.sidebar.markdown('## 🌎 TerraMatch Chile')
st.sidebar.caption(t['context'])
st.sidebar.divider()
st.sidebar.caption(t['nav'])
selection=st.sidebar.radio(t['nav'],options=PAGES,format_func=lambda p:t[p],
                           key='page',label_visibility='collapsed')
st.sidebar.divider()
st.sidebar.caption(t['pilot_badge'])
st.sidebar.markdown(f'[{t["source_code"]}](https://github.com/martizng/terramatch-chile/tree/integracion-motor-rojas-v07) · [{t["method_link"]}](https://github.com/martizng/terramatch-chile/blob/main/docs/methodology.md)')

@st.cache_data(show_spinner=False)
def load_results():
    return read_data()

try:
    SCORES,SITES,TARGETS,VALIDATION=load_results()
except (OSError,ValueError,KeyError) as ex:
    st.error(t['app_error'] + str(ex))
    st.info(t['expected_files'] + ' results/mars_scores_web.csv, results/moon_scores_web.csv, results/sites_summary.csv, results/validation.json, data/targets.json')
    st.stop()

def nav(target):
    st.session_state.page=target

def header(kicker,title,desc=None):
    st.markdown(f'<div class="tm-kicker">{escape(kicker)}</div>',unsafe_allow_html=True)
    st.title(title)
    if desc: st.markdown(desc)

def simple_card(title,detail):
    st.markdown(f'<div class="tm-card"><h3>{escape(title)}</h3><p>{escape(detail)}</p></div>',unsafe_allow_html=True)

def note(msg,warn=False):
    classname='tm-warning' if warn else 'tm-note'
    st.markdown(f'<div class="{classname}">{escape(msg)}</div>',unsafe_allow_html=True)

def num(x,digits=1):
    try:
        if pd.isna(x):return '—'
        return f'{float(x):,.{digits}f}'
    except (TypeError,ValueError):return '—'

def img(path,caption=None):
    p=Path(path)
    if p.exists():
        st.image(str(p),use_container_width=True)
        if caption:st.caption(caption)
    else:
        st.info(t['image_missing'])

def site_role(row):
    labels={'benchmark':('Sitio de referencia','Reference site'), 'control':('Sitio de control','Control site'), 'candidate':('Candidato exploratorio','Exploratory candidate'), 'contrast':('Contraste interno','Internal contrast')}
    return labels.get(str(row['role']),('Sitio piloto','Pilot site'))[0 if locale=='es' else 1]


def localized_site_name(ident):
    key='site_'+str(ident)
    if key in t:
        return t[key]
    row=SITES.loc[SITES['site'].eq(ident),'name']
    return str(row.iloc[0]) if not row.empty else str(ident)

def translated_confidence(value):
    raw=str(value)
    if locale=='es':
        return raw
    return {'Baja':'Low','Media':'Medium','Alta':'High'}.get(raw,raw)

def translated_status(value):
    key='status_'+str(value)
    return t.get(key,str(value))

def score_label(val):
    if pd.isna(val):return '—'
    return f'{float(val):.1f}/100'

def planet_selector(key):
    opts=['mars','moon']
    st.radio(t['planet'],opts,format_func=lambda val:t[val],horizontal=True,key=key)
    return st.session_state[key]

def stat_row():
    cols=st.columns(4)
    vals=[(t['s_ast'],len(astercells(SCORES['mars']))), (t['s_planets'],len(TARGETS)),
          (t['s_sites'],len(SITES)),(t['s_window'],'5')]
    for col,(lab,val) in zip(cols,vals):col.metric(lab,f'{val:,}' if isinstance(val,int) else val)

# ------------------- HOME -------------------
if selection=='home':
    st.markdown(f'<div class="tm-hero"><span class="tag">{escape(t["hero_kicker"])}</span>'
                f'<h1>{escape(t["hero_title"])}</h1><p>{escape(t["hero_text"])}</p></div>',unsafe_allow_html=True)
    bc1,bc2,bc3=st.columns([1,1,1])
    with bc1:
        img(VISUALS/'yungay_aster.jpg')
        st.caption(t['map_chile_aster'])
    with bc2:
        img(VISUALS/'mars_elysium_mola.jpg')
        st.caption(t['map_mars_mola'])
    with bc3:
        img(VISUALS/'moon_tranquillitatis_sldem.jpg')
        st.caption(t['map_moon_sldem'])
    st.caption(t['terrain_caption'])
    render_mission_explorer(locale, SCORES, SITES, site_image)
    ca,cb=st.columns(2,gap='large')
    with ca:simple_card(t['what'],t['what_text'])
    with cb:simple_card(t['why'],t['why_text'])
    st.write('')
    st.subheader(t['journey'])
    g1,g2,g3=st.columns(3,gap='medium')
    for col,heading,detail,target in [(g1,t['journey1'],t['journey1d'],'about'),
                                      (g2,t['journey2'],t['journey2d'],'explore'),
                                      (g3,t['journey3'],t['journey3d'],'sites')]:
        with col:
            simple_card(heading,detail)
            st.button('→ '+heading,key='home_'+target,use_container_width=True,on_click=nav,args=(target,))
    st.write('')
    st.subheader(t['glance'])
    stat_row()
    note(t['home_note'],warn=True)

# ------------------- ABOUT -------------------
elif selection=='about':
    header(t['about_kicker'],t['about_title'])
    c1,c2=st.columns([1.22,1],gap='large')
    with c1:
        st.subheader(t['about_problem']);st.write(t['about_problem_txt'])
        st.subheader(t['about_question']);note(t['about_question_txt'])
        st.subheader(t['about_solution']);st.write(t['about_solution_txt'])
    with c2:
        img(VISUALS/'mars_elysium_mola.jpg','MOLA MEGDR · Elysium Planitia')
        img(VISUALS/'moon_tranquillitatis_sldem.jpg','SLDEM2015 · Mare Tranquillitatis')
    st.subheader(t['about_roles'])
    col1,col2=st.columns(2)
    with col1:
        st.markdown('#### 🔴 '+t['mars_profile'])
        st.markdown('**Yungay:** '+('referencia de aridez' if locale=='es' else 'aridity reference'))
        st.markdown('**Salar de Pajonales:** '+('referencia salina' if locale=='es' else 'salt-flat reference'))
        st.markdown('**Llullaillaco:** '+('control de alta montaña' if locale=='es' else 'high-mountain control'))
    with col2:
        st.markdown('#### ⚪ '+t['moon_profile'])
        st.markdown(f'**{localized_site_name("llaima_flows")}:** '+('candidato exploratorio' if locale=='es' else 'exploratory candidate'))
        st.markdown(f'**{localized_site_name("llaima_cone")}:** '+('control interno' if locale=='es' else 'internal contrast'))
    note(f'{t["about_analogy"]}: {t["about_analogy_txt"]}',warn=True)

# ------------------- HOW IT WORKS -------------------
elif selection=='method':
    header(t['method_kicker'],t['method_title'],t['method_sub'])
    for left,right in [(('step1','step1d'),('step2','step2d')),(('step3','step3d'),('step4','step4d'))]:
        c1,c2=st.columns(2,gap='medium')
        with c1:simple_card(t[left[0]],t[left[1]])
        with c2:simple_card(t[right[0]],t[right[1]])
        st.write('')
    st.subheader(t['metrics'])
    c1,c2,c3=st.columns(3)
    for col,a,b in [(c1,'slope','slope_desc'),(c2,'relief','relief_desc'),(c3,'rough','rough_desc')]:
        with col:simple_card(t[a],t[b])
    st.write('')
    note(t['method_tip'],warn=True)
    st.markdown(f'[📖 {t["full_method"]}](https://github.com/martizng/terramatch-chile/blob/main/docs/methodology.md)')

# ------------------- MAP EXPLORER -------------------
elif selection=='explore':
    header(t['explore_kicker'],t['explore_title'],t['explore_sub'])
    st.session_state.setdefault('map_planet',st.session_state.planet)
    profile=planet_selector('map_planet')
    st.session_state.planet=profile
    scored=scored_cells(SCORES[profile]);aster=astercells(SCORES[profile]);df=SCORES[profile]
    a,b,c=st.columns(3)
    a.metric(t['valid_map'],f'{len(scored):,}')
    b.metric(t['aster_map'],f'{len(aster):,}')
    c.metric(t['total_map'],f'{len(df):,}')
    c1,c2,c3=st.columns([1.35,1.15,1.1])
    with c1:
        view=st.selectbox(t['map_mode'],['score','coverage'],format_func=lambda v:t['score_view'] if v=='score' else t['coverage_view'])
    with c2:
        region=st.selectbox(t['region'],['all','north'] if profile=='mars' else ['all','south'],format_func=lambda v:t[v],index=1)
    with c3:
        threshold=st.slider(t['min_score'],0,100,0,5,disabled=view!='score')
    show=st.checkbox(t['show_sites'],value=True)
    # Show only sites belonging to the selected planetary profile.
    map_sites=SITES[SITES['profile'].eq('mars_elysium' if profile=='mars' else 'moon_tranquillitatis')]
    fig=make_terrain_map(df,map_sites,mode=view,region=region,min_score=threshold,show_sites=show,locale=locale)
    st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False,'modeBarButtonsToRemove':['lasso2d','select2d']})
    st.caption(t['map_hint'])
    if region == 'south':
        st.caption('Los contornos azul y naranja son delimitaciones preliminares de coladas y cono; no representan una equivalencia lunar.' if locale == 'es' else 'Blue and orange outlines are preliminary lava-flow and cone study footprints; they do not imply lunar equivalence.')
        vis1, vis2 = st.columns(2, gap='medium')
        with vis1:
            img(VISUALS/'llaima_flows_aster.jpg', 'Sector de coladas · relieve ASTER (no fotografía)' if locale == 'es' else 'Lava-flow sector · ASTER terrain (not a photograph)')
        with vis2:
            img(VISUALS/'llaima_cone_aster.jpg', 'Cono del Llaima · relieve ASTER (no fotografía)' if locale == 'es' else 'Llaima cone · ASTER terrain (not a photograph)')
    note(t['filter_note'],warn=True)
    with st.expander(t['legend']):
        st.markdown(f'**{t["score_view"]}:** {t["legend_score"]}')
        st.markdown(f'**{t["scored_label"]}:** {t["legend_scored"]}')
        st.markdown(f'**{t["outside_label"]}:** {t["legend_outside"]}')
        st.markdown(f'**{t["insuff_label"]}:** {t["legend_missing"]}')
    st.subheader(t['pilot_rank'])
    highest=scored.nlargest(8,'S')[['cell_id','lat_c','lon_c','S','coverage','confidence']].copy()
    highest['coverage']=highest['coverage']*100
    highest['confidence']=highest['confidence'].map(translated_confidence)
    highest=highest.rename(columns={
        'cell_id':t['cell_id_label'], 'lat_c':t['latitude'], 'lon_c':t['longitude'],
        'S':t['score_col'], 'coverage':t['coverage_col'], 'confidence':t['confidence_col']})
    highest[t['latitude']]=highest[t['latitude']].round(3)
    highest[t['longitude']]=highest[t['longitude']].round(3)
    highest[t['score_col']]=highest[t['score_col']].round(1)
    highest[t['coverage_col']]=highest[t['coverage_col']].round(0)
    st.dataframe(highest,hide_index=True,use_container_width=True)
    st.caption(t['pilot_only'])
    st.download_button(t['download'],data=scored.to_csv(index=False).encode('utf-8-sig'),
                       file_name=f'terramatch_{profile}_pilot_scored.csv',mime='text/csv')

# ------------------- SITE STORIES -------------------
elif selection=='sites':
    header(t['sites_kicker'],t['sites_title'],t['sites_sub'])
    selected=st.selectbox(t['select_site'],SITES['site'].tolist(),
                          format_func=localized_site_name)
    site=SITES[SITES['site'].eq(selected)].iloc[0]
    profile='mars' if site['profile']=='mars_elysium' else 'moon'
    target=next((x for x in TARGETS if x['id']==site['profile']),None)
    col1,col2=st.columns([1.05,1.3],gap='large')
    with col1:
        img(site_image(selected),t['terrain_photo'])
        st.caption(f'≈ {float(site["ref_lat"]):.3f}°, {float(site["ref_lon"]):.3f}° · {site_role(site)}')
    with col2:
        st.markdown('### '+localized_site_name(selected))
        st.markdown(f'**{site_role(site)}** · {t["mars_profile"] if profile=="mars" else t["moon_profile"]}')
        a,b=st.columns(2)
        a.metric(t['site_score'],score_label(site['S']))
        b.metric(t['site_pct'],num(site['percentile'])+' / 100')
        a,b=st.columns(2)
        a.metric(t['site_cov'],num(float(site['coverage'])*100,0)+'%')
        b.metric(t['site_conf'],translated_confidence(site['confidence']))
        note(SITE_EXPLANATIONS.get(selected,{}).get(locale,''))
    if selected in ['pajonales','llaima_flows']:note(t['proxy_warning'],warn=True)
    if selected=='llaima_flows':note(t['llaima_caution'],warn=True)
    st.subheader(t['comp_title'])
    render_metric_comparison(locale, site, target)
    st.caption(t['metric_scope'])
    with st.expander(t['technical_details']):
        details=[
            (t['detail_site'], str(site['site'])),
            (t['detail_profile'], t['mars_profile'] if profile=='mars' else t['moon_profile']),
            (t['detail_cells'], int(site['n_cells'])),
            (t['detail_scored'], int(site['n_scored'])),
            (t['detail_stability'], num(site['p_top'],3)),
            (t['detail_status'], translated_status(site['status'])),
            (t['detail_geometry'], t.get('geometry_'+str(site['geometry']),str(site['geometry'])))
        ]
        st.dataframe(pd.DataFrame(details,columns=[t['technical_details'],t['detail_value']]),hide_index=True,use_container_width=True)

# ------------------- SCIENTIFIC RESULTS -------------------
elif selection=='validation':
    header(t['validation_kicker'],t['validation_title'],t['validation_intro'])
    cols=st.columns(2,gap='large')
    mapping={'yungay_percentile>=75':'yungay_check','pajonales_percentile>=75':'paj_check',
             'llullaillaco_percentile<=25':'llulla_check','steep_top5_median_percentile<=25':'steep_check',
             'llaima_flows_S>llaima_cone_S':'llaima_check'}
    for col,profile,label in [(cols[0],'mars','mars_results'),(cols[1],'moon','moon_results')]:
        with col:
            st.markdown('### '+t[label])
            checks=VALIDATION.get(profile,{}).get('checks',{})
            for key,info in checks.items():
                title=t.get(mapping.get(key,''),key)
                passed=info.get('passed')
                sign='✅' if passed is True else '⚠️' if passed is False else '⏳'
                status=t['pass'] if passed is True else t['fail'] if passed is False else t['not_eval']
                with st.container(border=True):
                    st.markdown(f'{sign} **{title}**')
                    st.caption(f'{status} · {num(info.get("value"),2)}')
    st.subheader(t['insight'])
    a,b=st.columns([1.6,1])
    with a:note(t['insight_text'])
    with b:
        flows=SITES[SITES['site'].eq('llaima_flows')].iloc[0]
        cone=SITES[SITES['site'].eq('llaima_cone')].iloc[0]
        st.metric(t['site_comparison'],f'{float(flows["S"]):.1f} vs {float(cone["S"]):.1f} /100')
        st.caption(t['preliminary_geometry'])
        note(t['llaima_caution'],warn=True)
    render_evidence_charts(locale, SITES)
    note(t['validation_precision'],warn=True)

# ------------------- OPEN DATA & LIMITATIONS -------------------
elif selection=='data':
    header(t['data_kicker'],t['data_title'])
    st.subheader(t['data_sources'])
    sources=[('ASTER GDEM v3',t['source_chile_topo'],'https://lpdaac.usgs.gov/products/astgtmv003/'),
             ('MOLA MEGDR',t['source_mars'],'https://pds-geosciences.wustl.edu/missions/mgs/megdr.html'),
             ('SLDEM2015',t['source_moon'],'https://pgda.gsfc.nasa.gov/products/54'),
             ('GPM IMERG Final V07',t['source_precip'],'https://doi.org/10.5067/GPM/IMERG/3B-MONTH/07'),
             ('SERNAGEOMIN',t['source_geo'],'https://www.sernageomin.cl/'),
             ('BCN',t['source_boundaries'],'https://www.bcn.cl/siit/mapas_vectoriales')]
    for title,sub,link in sources:
        with st.container(border=True):
            c1,c2=st.columns([2,1])
            c1.markdown(f'**{title}** · {sub}')
            c2.markdown(f'[{t["source_link"]} ↗]({link})')
    st.subheader(t['limits'])
    for i in range(1,9):st.markdown(f'**{i}.** {t["limits"+str(i)]}')
    st.subheader(t['aster_quality_title'])
    note(t['aster_quality_body'])
    st.subheader(t['data_status'])
    statuses=[('scored_label','✅',('Con información suficiente y filtro aprobado.','Sufficient data and passes screening.')),
              ('outside_label','🚫',('No cumple el filtro; no se calcula similitud.','Fails the screening rule; no score is computed.')),
              ('insuff_label','▫️',('Falta relieve suficiente, frecuentemente por ausencia de ASTER.','Insufficient terrain data, often because ASTER coverage is absent.')),
              ('nofilter_label','❔',('Falta la clasificación necesaria para el filtro.','Required screening classification is missing.'))]
    for key,emoji,expl in statuses:
        st.markdown(f'{emoji} **{t[key]}:** {expl[0 if locale=="es" else 1]}')
    note(t['data_quality'])
    st.markdown(f'[📂 {t["source_code"]}](https://github.com/martizng/terramatch-chile/tree/integracion-motor-rojas-v07) · [📄 {t["review_link"]}](https://github.com/martizng/terramatch-chile/blob/integracion-motor-rojas-v07/docs/reviews/motor_v07_integracion.md)')

st.markdown(f'<div class="tm-foot">{escape(t["footer"])}</div>',unsafe_allow_html=True)
