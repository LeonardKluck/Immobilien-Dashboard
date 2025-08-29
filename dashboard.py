import streamlit as st
import pandas as pd

st.set_page_config(page_title="Immobilien KPI Dashboard", layout="wide")

st.title("🏠 Immobilien KPI Dashboard – Dynamische Analyse")

# Eingabeparameter
st.sidebar.header("🔧 Parameter")

kaufpreis = st.sidebar.number_input("Kaufpreis (€)", value=700000, step=10000)
jahresmiete = st.sidebar.number_input("Jahresnettokaltmiete (€)", value=55000, step=1000)
wohnflaeche = st.sidebar.number_input("Wohnfläche (m²)", value=300, step=10)
knk_rate = st.sidebar.slider("Kaufnebenkosten (%)", 5.0, 15.0, 12.0, step=0.5) / 100
ek_quote = st.sidebar.slider("Eigenkapitalquote (%)", 0.0, 1.0, 0.10, step=0.01)
annuitaet = st.sidebar.slider("Annuität (Zins + Tilgung) %", 0.01, 0.10, 0.055, step=0.005)
opex = st.sidebar.number_input("Nicht umlagefähige Kosten (€/m² a)", value=15, step=1)
capex = st.sidebar.number_input("CapEx-Reserve (€/m² a)", value=10, step=1)

# Berechnungen
gesamtkosten = kaufpreis * (1 + knk_rate)
EK = gesamtkosten * ek_quote
FK = gesamtkosten - EK

opex_total = opex * wohnflaeche
capex_total = capex * wohnflaeche

NOI = jahresmiete - opex_total - capex_total
schuldendienst = FK * annuitaet

cap_rate = NOI / gesamtkosten if gesamtkosten > 0 else 0
dscr = NOI / schuldendienst if schuldendienst > 0 else 0
coc = (NOI - schuldendienst) / EK if EK > 0 else 0
nettomietrendite = NOI / kaufpreis if kaufpreis > 0 else 0

# Ausgabe KPIs
data = {
    "KPI": ["Gesamtkosten (inkl. NK)", "Eigenkapital", "Fremdkapital", "NOI (bereinigt)",
            "Cap Rate", "DSCR", "Cash-on-Cash Rendite Jahr 1", "Nettomietrendite"],
    "Wert": [
        f"{gesamtkosten:,.0f} €", f"{EK:,.0f} €", f"{FK:,.0f} €", f"{NOI:,.0f} €",
        f"{cap_rate*100:.2f} %", f"{dscr:.2f}", f"{coc*100:.2f} %", f"{nettomietrendite*100:.2f} %"
    ]
}

df = pd.DataFrame(data)

st.subheader("📊 Ergebnis-KPIs")
st.table(df)

# Visualisierung
st.subheader("📈 Visualisierungen")
col1, col2 = st.columns(2)

with col1:
    st.metric("Cap Rate", f"{cap_rate*100:.2f} %")
    st.progress(min(max(cap_rate, 0), 0.1))

with col2:
    st.metric("DSCR", f"{dscr:.2f}")
    if dscr < 1:
        st.error("⚠️ NOI deckt Schuldendienst nicht!")
    elif dscr < 1.2:
        st.warning("🔶 Grenzwertig tragfähig")
    else:
        st.success("✅ Sicher tragfähig")
