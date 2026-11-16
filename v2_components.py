"""Presentation-only extensions for TerraMatch Chile v2 preview.

Reads existing v0.7 data. Never changes, imputes or recalculates scientific scores.
No network services, API keys or JavaScript are required.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui_data import SITE_EXPLANATIONS, SITE_NAME_TRANSLATIONS, scored_cells

V2_STRINGS = {
    'es': {
        'mission': 'Centro de exploración',
        'mission_desc': 'Elige un mundo y conoce uno de nuestros sectores piloto antes de abrir el mapa.',
        'planet': 'Destino de comparación',
        'site': 'Sector de estudio',
        'score': 'Similitud topográfica',
        'percentile': 'Percentil del piloto',
        'confidence': 'Confianza del sitio',
        'explore': 'Explorar estas celdas en el mapa',
        'scope': 'Resultados de cuatro teselas piloto, no de todo Chile. Los puntajes no representan equivalencia planetaria.',
        'reference': 'Región de referencia',
        'valid': 'Celdas con puntaje en el piloto',
        'mars': '🔴 Marte · Elysium Planitia',
        'moon': '⚪ Luna · Mare Tranquillitatis',
        'no_photo': 'Visualización derivada del DEM; no es una fotografía.',
        'compare_title': 'Explora las diferencias del terreno',
        'compare_desc': 'Cambia la variable para comparar el sector seleccionado con la mediana del perfil planetario. Cada variable usa sus propias unidades.',
        'metric': 'Variable a comparar',
        'chile': 'Sector chileno',
        'target': 'Referencia planetaria',
        'slope': 'Pendiente P90',
        'relief': 'Relieve local P95–P5',
        'rough': 'Rugosidad',
        'metric_note': 'La coincidencia en una variable no demuestra equivalencia geológica, ambiental ni operacional.',
        'evidence_title': 'Resultados, explicados visualmente',
        'evidence_sub': 'Estas son pruebas realizadas con el motor v0.7. Los sitios se comparan solo con celdas elegibles dentro del piloto.',
        'mars_tab': '🔴 Marte · percentiles',
        'moon_tab': '⚪ Luna · puntuación',
        'benchmark_note': 'Yungay y Pajonales esperaban ≥75; Llullaillaco, como control, ≤25. No todos los criterios se cumplieron.',
        'moon_note': 'El sector de coladas supera al cono en puntaje, pero ambos presentan confianza baja; el polígono es preliminar.',
        'y_axis': 'Percentil dentro del piloto',
        's_axis': 'Puntaje de similitud (0–100)',
        'low_confidence': 'Confianza reportada: baja en los cinco sitios evaluados.',
    },
    'en': {
        'mission': 'Mission explorer',
        'mission_desc': 'Choose a world and get to know one pilot site before opening the map.',
        'planet': 'Planetary reference',
        'site': 'Study area',
        'score': 'Terrain similarity',
        'percentile': 'Pilot percentile',
        'confidence': 'Site confidence',
        'explore': 'Explore these cells on the map',
        'scope': 'Results from four pilot ASTER tiles, not the whole country. Scores do not imply planetary equivalence.',
        'reference': 'Reference region',
        'valid': 'Scored cells in pilot',
        'mars': '🔴 Mars · Elysium Planitia',
        'moon': '⚪ Moon · Mare Tranquillitatis',
        'no_photo': 'Elevation-derived terrain rendering, not a photograph.',
        'compare_title': 'Explore terrain differences',
        'compare_desc': 'Switch metrics to compare the selected Chilean site with the planetary target median. Each metric retains its own units.',
        'metric': 'Metric to compare',
        'chile': 'Chilean site',
        'target': 'Planetary reference',
        'slope': 'Slope P90',
        'relief': 'Local relief P95–P5',
        'rough': 'Roughness',
        'metric_note': 'Matching one terrain metric does not establish geological, environmental or operational equivalence.',
        'evidence_title': 'Results explained visually',
        'evidence_sub': 'These are v0.7 engine checks. Sites are compared only with eligible cells within the pilot.',
        'mars_tab': '🔴 Mars · percentiles',
        'moon_tab': '⚪ Moon · scores',
        'benchmark_note': 'Yungay and Pajonales expected ≥75; Llullaillaco was a ≤25 negative control. Not every criterion passed.',
        'moon_note': 'The mapped lava-flow sector scores above the cone, but both have low confidence and the boundary is provisional.',
        'y_axis': 'Percentile within the pilot',
        's_axis': 'Similarity score (0–100)',
        'low_confidence': 'Reported confidence: low for all five evaluated sites.',
    },
}

V2_CSS = """
<style>
/* TerraMatch v2: animation is decorative; no animations manipulate data. */
:root { --tm-ink: #173847; --tm-teal: #147b83; --tm-orange: #ce794b; }
.tm-hero { position:relative; overflow:hidden; isolation:isolate; background:linear-gradient(125deg,#102A43 3%,#153c53 53%,#12656c 145%); min-height:260px; }
.tm-hero::before { content:''; position:absolute; inset:0; z-index:0; opacity:.62;
 background-image:radial-gradient(circle,#ffffffdb 1px,transparent 2px), radial-gradient(circle,#acf4ff99 1px,transparent 2px);
 background-size:73px 79px,119px 109px; background-position:10px 9px,44px 26px;
 animation:tm-stars 32s linear infinite; pointer-events:none; }
.tm-hero::after { content:''; position:absolute; z-index:0; top:-96px; right:-60px;
 width:345px; height:345px; border-radius:50%; opacity:.8; pointer-events:none;
 box-shadow:0 0 80px 16px #fa92523d,inset -58px -30px 42px #2b1a33a8;
 background:radial-gradient(circle at 27% 28%,#eeb18c 0%,#ca774e 23%,#9d4c44 56%,#49334b 100%);
 animation:tm-planet 13s ease-in-out infinite; }
.tm-hero h1,.tm-hero p,.tm-hero .tag {position:relative; z-index:2;}
.tm-hero p {max-width:690px;}
.tm-card,div[data-testid="stMetric"],div[data-testid="stVerticalBlockBorderWrapper"] { transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease; }
.tm-card:hover,div[data-testid="stMetric"]:hover {transform:translateY(-3px);box-shadow:0 14px 30px #163d5020!important;border-color:#b2d5da!important;}
.stButton button {transition:transform .18s ease,box-shadow .18s ease,background .18s ease;}
.stButton button:hover {transform:translateY(-2px);box-shadow:0 7px 18px #176b7826;}
[data-testid="stMain"] .stTabs [data-baseweb="tab"] {font-weight:600;}
[data-testid="stMain"] .stTabs [aria-selected="true"] {color:#106778!important;}
[data-testid="stMain"] .stTabs [data-baseweb="tab-highlight"] {background:#147b83!important;}
.tm-v2-label {color:#145e6d!important;font-size:.76rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;}
.tm-v2-scope {background:#ecf5f6;border-left:4px solid #197b84;color:#254554;border-radius:9px;padding:12px 15px;margin:9px 0 16px;font-size:.89rem;}
.tm-v2-section {margin:24px 0 12px;animation:tm-in .65s ease-out both;}
.tm-v2-kpi {border:1px solid #d9e7ea;background:#f8fcfd;border-radius:14px;padding:12px 15px;}
.tm-v2-kpi .val {font:800 1.55rem 'Outfit',sans-serif;color:#144f61;}
.tm-v2-kpi .lbl {color:#37566a;font-size:.81rem;font-weight:600;}
.tm-v2-img-caption {color:#405a69;font-size:.78rem;padding:3px 0 0;}
@keyframes tm-in { from{opacity:0;transform:translateY(12px);} to{opacity:1;transform:translateY(0)} }
@keyframes tm-stars { from{background-position:10px 9px,44px 26px} to{background-position:83px 88px,163px 135px} }
@keyframes tm-planet { 0%,100%{transform:translateY(0) rotate(-4deg)} 50%{transform:translateY(10px) rotate(4deg)} }
@media (max-width:770px){ .tm-hero {padding:30px 22px;min-height:0;} .tm-hero::after {width:210px;height:210px;top:-78px;right:-120px;opacity:.40;} }
@media (prefers-reduced-motion:reduce){ .tm-hero::before,.tm-hero::after,.tm-v2-section {animation:none!important;} *,*::before,*::after {scroll-behavior:auto!important;transition-duration:.01ms!important;} }
</style>
"""


def inject_v2_style() -> None:
    st.markdown(V2_CSS, unsafe_allow_html=True)


def _go_map(planet: str) -> None:
    st.session_state['page'] = 'explore'
    st.session_state['map_planet'] = planet
    st.session_state['planet'] = planet


def _localized_name(site_id: str, locale: str) -> str:
    return SITE_NAME_TRANSLATIONS.get(site_id, {}).get(locale, site_id)


def _metric_box(value: str, label: str) -> None:
    from html import escape
    st.markdown(f'<div class="tm-v2-kpi"><div class="val">{escape(value)}</div>'
                f'<div class="lbl">{escape(label)}</div></div>', unsafe_allow_html=True)


def render_mission_explorer(locale: str, scores: dict[str, pd.DataFrame], sites: pd.DataFrame,
                            site_image: Callable[[str], Path]) -> None:
    """Site-oriented guided experience; source scores stay unchanged."""
    l = V2_STRINGS[locale]
    st.markdown('<div class="tm-v2-section"><div class="tm-v2-label">' + ('MODO EXPLORACIÓN' if locale=='es' else 'EXPLORATION MODE') + '</div></div>', unsafe_allow_html=True)
    st.subheader('🪐 ' + l['mission'])
    st.write(l['mission_desc'])
    planet = st.radio(l['planet'], ['mars', 'moon'], format_func=lambda p: l[p],
                      horizontal=True, key='v2_mission_planet')
    profile = 'mars_elysium' if planet == 'mars' else 'moon_tranquillitatis'
    possible = sites.loc[sites['profile'].eq(profile)].copy()
    if possible.empty:
        return
    select_id = st.selectbox(l['site'], possible['site'].tolist(),
                             format_func=lambda k: _localized_name(k, locale), key='v2_mission_site')
    site = possible.loc[possible['site'].eq(select_id)].iloc[0]
    c1,c2=st.columns([.85,1.15],gap='large')
    with c1:
        asset=site_image(select_id)
        if asset.exists():
            st.image(str(asset),use_container_width=True)
            st.caption(l['no_photo'])
    with c2:
        st.markdown('#### '+_localized_name(select_id, locale))
        a,b=st.columns(2)
        with a:
            _metric_box(f'{float(site["S"]):.1f}/100' if pd.notna(site['S']) else '—', l['score'])
        with b:
            _metric_box(f'{float(site["percentile"]):.1f}' if pd.notna(site['percentile']) else '—', l['percentile'])
        st.markdown('')
        st.write(SITE_EXPLANATIONS.get(select_id,{}).get(locale,''))
        st.caption(l['low_confidence'])
        st.button('🗺️ '+l['explore'],key='v2_mission_to_map',use_container_width=True,
                  on_click=_go_map,args=(planet,))
    c3,c4=st.columns(2)
    with c3:
        _metric_box(str(len(scored_cells(scores[planet]))),l['valid'])
    with c4:
        _metric_box('Elysium Planitia' if planet=='mars' else 'Mare Tranquillitatis',l['reference'])
    st.markdown('<div class="tm-v2-scope">'+l['scope']+'</div>',unsafe_allow_html=True)


def render_metric_comparison(locale: str, site: pd.Series, target: dict | None) -> None:
    l=V2_STRINGS[locale]
    st.markdown('<div class="tm-v2-section"></div>', unsafe_allow_html=True)
    st.subheader('📐 '+l['compare_title'])
    st.write(l['compare_desc'])
    dims={
        'slope_p90_deg': ('slope_p90_deg_value','°',l['slope']),
        'relief_m': ('relief_m_value','m',l['relief']),
        'rough_sd_deg': ('rough_sd_deg_value','°',l['rough'])
    }
    metric=st.radio(l['metric'], list(dims), format_func=lambda key:dims[key][2],
                    horizontal=True,key='v2_metric_choice')
    key,unit,title=dims[metric]
    base=(target or {}).get('variables',{}).get(metric,{})
    ref=base.get('value')
    measured=site.get(key)
    if pd.isna(measured) or ref is None:
        st.info('Información insuficiente' if locale=='es' else 'Insufficient information')
        return
    s_value,r_value=float(measured),float(ref)
    f=go.Figure()
    f.add_trace(go.Bar(x=[s_value],y=[l['chile']],orientation='h',marker_color='#1b7f8a',
                       text=[f'{s_value:,.2f} {unit}'],textposition='outside',cliponaxis=False,
                       hovertemplate='%{x:.2f} '+unit+'<extra></extra>'))
    f.add_trace(go.Bar(x=[r_value],y=[l['target']],orientation='h',marker_color='#cf825b',
                       text=[f'{r_value:,.2f} {unit}'],textposition='outside',cliponaxis=False,
                       hovertemplate='%{x:.2f} '+unit+'<extra></extra>'))
    f.update_layout(barmode='group',showlegend=False,height=245,
                    margin={'l':4,'r':55,'t':8,'b':25},
                    paper_bgcolor='#F7FAFC',plot_bgcolor='#F7FAFC',
                    font={'family':'Arial,sans-serif','color':'#173847'},
                    xaxis={'range':[0,max(s_value,r_value,1)*1.3], 'title':unit, 'zeroline':False,'gridcolor':'#e0eaee'},
                    yaxis={'autorange':'reversed','tickfont':{'size':13}})
    st.plotly_chart(f,use_container_width=True,config={'displaylogo':False,'staticPlot':False})
    st.caption(l['metric_note'])


def render_evidence_charts(locale: str, sites: pd.DataFrame) -> None:
    l=V2_STRINGS[locale]
    st.markdown('<div class="tm-v2-section"></div>',unsafe_allow_html=True)
    st.subheader('📈 '+l['evidence_title'])
    st.write(l['evidence_sub'])
    mars=sites.loc[sites['profile'].eq('mars_elysium')]
    moon=sites.loc[sites['profile'].eq('moon_tranquillitatis')]
    tabs=st.tabs([l['mars_tab'],l['moon_tab']])
    with tabs[0]:
        v=mars.loc[mars['site'].isin(['yungay','pajonales','llullaillaco'])]
        labels=[_localized_name(x,locale) for x in v['site']]
        fig=go.Figure(go.Bar(x=labels,y=v['percentile'],marker_color=['#d78a64','#c96946','#37838d'][:len(v)],
                             text=v['percentile'].map(lambda x:f'{x:.1f}'),textposition='outside',cliponaxis=False,
                             hovertemplate='%{x}: %{y:.1f}<extra></extra>'))
        fig.add_hline(y=75,line_dash='dash',line_color='#935c38',annotation_text='P75',annotation_position='top right')
        fig.add_hline(y=25,line_dash='dot',line_color='#267b83',annotation_text='P25',annotation_position='bottom right')
        fig.update_layout(yaxis={'range':[0,100],'title':l['y_axis'],'gridcolor':'#e0eaee'},
                          xaxis={'tickfont':{'size':12}},showlegend=False,height=345,
                          margin={'l':10,'r':22,'t':32,'b':35},
                          plot_bgcolor='#fbfdfe',paper_bgcolor='#fbfdfe',font={'color':'#173847'})
        st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False})
        st.caption(l['benchmark_note'])
    with tabs[1]:
        v=moon.loc[moon['site'].isin(['llaima_flows','llaima_cone'])]
        labels=[_localized_name(x,locale) for x in v['site']]
        fig=go.Figure(go.Bar(x=labels,y=v['S'],marker_color=['#1e8491','#d4865d'][:len(v)],
                             text=v['S'].map(lambda x:f'{x:.1f}'),textposition='outside',cliponaxis=False,
                             hovertemplate='%{x}: %{y:.1f}<extra></extra>'))
        fig.update_layout(yaxis={'range':[0,100],'title':l['s_axis'],'gridcolor':'#e0eaee'},
                          showlegend=False,height=345,margin={'l':10,'r':22,'t':22,'b':52},
                          plot_bgcolor='#fbfdfe',paper_bgcolor='#fbfdfe',font={'color':'#173847'})
        st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False})
        st.caption(l['moon_note'])
    st.caption(l['low_confidence'])
