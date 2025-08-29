import streamlit as st
import pandas as pd

st.set_page_config(page_title="Immobilien KPI Vergleich", layout="wide")
st.title("🏠 Immobilien KPI Dashboard – Objektvergleich A vs. B")

# --- KPI Berechnung ---
def calc_kpis(name, kaufpreis, miete, flaeche, nk_rate, makler_rate, ek_quote, annuitaet, opex, capex):
    nk = kaufpreis * nk_rate
    courtage = kaufpreis * makler_rate
    gesamtkosten = kaufpreis + nk + courtage

    EK = gesamtkosten * ek_quote
    FK = gesamtkosten - EK

    opex_total = opex * flaeche
    capex_total = capex * flaeche
    NOI = miete - opex_total - capex_total

    schuldendienst = FK * annuitaet

    cap_rate = NOI / gesamtkosten if gesamtkosten > 0 else 0
    dscr = NOI / schuldendienst if schuldendienst > 0 else 0
    coc = (NOI - schuldendienst) / EK if EK > 0 else 0
    nettomietrendite = NOI / kaufpreis if kaufpreis > 0 else 0

    return {
        "Objekt": name,
        "Gesamtkosten (€)": gesamtkosten,
        "Eigenkapital (€)": EK,
        "Fremdkapital (€)": FK,
        "NOI (€)": NOI,
        "Cap Rate (%)": cap_rate * 100,
        "DSCR": dscr,
        "CoC Rendite (%)": coc * 100,
        "Nettomietrendite (%)": nettomietrendite * 100
    }

# --- Eingaben ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 Objekt A")
    kp_a = st.number_input("Kaufpreis A (€)", value=700000, step=10000)
    miete_a = st.number_input("Jahresmiete A (€)", value=55000, step=1000)
    flaeche_a = st.number_input("Wohnfläche A (m²)", value=300, step=10)
    nk_rate_a = st.slider("Nebenkosten A (%)", 0.05, 0.15, 0.12, step=0.01)
    makler_a = st.slider("Maklercourtage A (%)", 0.0, 0.05, 0.0357, step=0.005)
    ek_a = st.slider("Eigenkapitalquote A", 0.0, 1.0, 0.10, step=0.01)
    ann_a = st.slider("Annuität A (Zins+Tilgung)", 0.01, 0.10, 0.055, step=0.005)
    opex_a = st.number_input("Opex A (€/m²)", value=15, step=1)
    capex_a = st.number_input("CapEx A (€/m²)", value=10, step=1)

with col2:
    st.subheader("📌 Objekt B")
    kp_b = st.number_input("Kaufpreis B (€)", value=850000, step=10000)
    miete_b = st.number_input("Jahresmiete B (€)", value=60000, step=1000)
    flaeche_b = st.number_input("Wohnfläche B (m²)", value=400, step=10)
    nk_rate_b = st.slider("Nebenkosten B (%)", 0.05, 0.15, 0.12, step=0.01)
    makler_b = st.slider("Maklercourtage B (%)", 0.0, 0.05, 0.0357, step=0.005)
    ek_b = st.slider("Eigenkapitalquote B", 0.0, 1.0, 0.10, step=0.01)
    ann_b = st.slider("Annuität B (Zins+Tilgung)", 0.01, 0.10, 0.055, step=0.005)
    opex_b = st.number_input("Opex B (€/m²)", value=15, step=1)
    capex_b = st.number_input("CapEx B (€/m²)", value=10, step=1)

# --- Berechnung ---
kpis_a = calc_kpis("Objekt A", kp_a, miete_a, flaeche_a, nk_rate_a, makler_a, ek_a, ann_a, opex_a, capex_a)
kpis_b = calc_kpis("Objekt B", kp_b, miete_b, flaeche_b, nk_rate_b, makler_b, ek_b, ann_b, opex_b, capex_b)

df = pd.DataFrame([kpis_a, kpis_b]).set_index("Objekt")
df["Delta (A-B)"] = df.loc["Objekt A"] - df.loc["Objekt B"]

# --- Ampellogik für Karten ---
def delta_style(val, metric_type="higher"):
    if metric_type == "higher":
        return "🟢 besser" if val > 0 else ("🔴 schlechter" if val < 0 else "⚪ gleich")
    else:  # lower is better
        return "🟢 besser" if val < 0 else ("🔴 schlechter" if val > 0 else "⚪ gleich")

# --- KPI-Karten ---
st.subheader("🔑 Wichtigste Kennzahlen")
kcol1, kcol2, kcol3 = st.columns(3)

delta_cap = df.loc["Objekt A", "Cap Rate (%)"] - df.loc["Objekt B", "Cap Rate (%)"]
delta_dscr = df.loc["Objekt A", "DSCR"] - df.loc["Objekt B", "DSCR"]
delta_coc = df.loc["Objekt A", "CoC Rendite (%)"] - df.loc["Objekt B", "CoC Rendite (%)"]

kcol1.metric("Cap Rate A", f"{df.loc['Objekt A', 'Cap Rate (%)']:.2f} %", delta_style(delta_cap, "higher"))
kcol2.metric("DSCR A", f"{df.loc['Objekt A', 'DSCR']:.2f}", delta_style(delta_dscr, "higher"))
kcol3.metric("CoC Rendite A", f"{df.loc['Objekt A', 'CoC Rendite (%)']:.2f} %", delta_style(delta_coc, "higher"))

# --- Vergleichstabelle ---
styled_df = df.style.format({
    "Gesamtkosten (€)": "{:,.0f} €",
    "Eigenkapital (€)": "{:,.0f} €",
    "Fremdkapital (€)": "{:,.0f} €",
    "NOI (€)": "{:,.0f} €",
    "Cap Rate (%)": "{:.2f} %",
    "DSCR": "{:.2f}",
    "CoC Rendite (%)": "{:.2f} %",
    "Nettomietrendite (%)": "{:.2f} %",
    "Delta (A-B)": "{:.2f}"
})

st.subheader("📊 KPI Vergleich – Objekt A vs. Objekt B")
st.table(styled_df)

# --- Definitionen ---
with st.expander("ℹ️ Definitionen der Kennzahlen"):
    st.markdown("""
    - **Gesamtkosten (€):** Kaufpreis + Nebenkosten + Maklercourtage  
    - **Eigenkapital (€):** Anteil der Gesamtkosten, der mit Eigenkapital finanziert wird  
    - **Fremdkapital (€):** Anteil der Gesamtkosten, der mit Bankdarlehen finanziert wird  
    - **NOI (€):** Net Operating Income = Jahresmiete – Opex – CapEx  
    - **Cap Rate (%):** NOI ÷ Gesamtkosten (inkl. NK) → misst Rendite auf Objektbasis  
    - **DSCR:** Debt Service Coverage Ratio = NOI ÷ Schuldendienst  
        - > 1,2 = tragfähig, < 1 = Defizit  
    - **CoC Rendite (%):** (NOI – Schuldendienst) ÷ Eigenkapital → EK-Rendite im 1. Jahr  
    - **Nettomietrendite (%):** NOI ÷ Kaufpreis  
    - **Delta (A-B):** Differenz zwischen Objekt A und B  
    """)
