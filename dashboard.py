import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Immobilien KPI Vergleich", layout="wide")
st.title("🏠 Immobilien KPI Dashboard – Objektvergleich")

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
with st.expander("📌 Parameter Objekt A", expanded=True):
    name_a = st.text_input("Name Objekt A", value="Objekt A")
    kp_a = st.number_input("Kaufpreis (€)", value=700000, step=10000, key="kp_a")
    miete_a = st.number_input("Jahresmiete (€)", value=55000, step=1000, key="miete_a")
    flaeche_a = st.number_input("Wohnfläche (m²)", value=300, step=10, key="flaeche_a")
    nk_rate_a = st.number_input("Nebenkosten (%)", value=12.0, step=0.1, key="nk_a") / 100
    makler_a = st.number_input("Maklercourtage (%)", value=3.57, step=0.1, key="makler_a") / 100
    ek_a = st.number_input("Eigenkapitalquote (%)", value=10.0, step=1.0, key="ek_a") / 100
    ann_a = st.number_input("Annuität (%)", value=5.5, step=0.1, key="ann_a") / 100
    opex_a = st.number_input("Opex (€/m²)", value=15, step=1, key="opex_a")
    capex_a = st.number_input("CapEx (€/m²)", value=10, step=1, key="capex_a")

with st.expander("📌 Parameter Objekt B", expanded=True):
    name_b = st.text_input("Name Objekt B", value="Objekt B")
    kp_b = st.number_input("Kaufpreis (€)", value=850000, step=10000, key="kp_b")
    miete_b = st.number_input("Jahresmiete (€)", value=60000, step=1000, key="miete_b")
    flaeche_b = st.number_input("Wohnfläche (m²)", value=400, step=10, key="flaeche_b")
    nk_rate_b = st.number_input("Nebenkosten (%)", value=12.0, step=0.1, key="nk_b") / 100
    makler_b = st.number_input("Maklercourtage (%)", value=3.57, step=0.1, key="makler_b") / 100
    ek_b = st.number_input("Eigenkapitalquote (%)", value=10.0, step=1.0, key="ek_b") / 100
    ann_b = st.number_input("Annuität (%)", value=5.5, step=0.1, key="ann_b") / 100
    opex_b = st.number_input("Opex (€/m²)", value=15, step=1, key="opex_b")
    capex_b = st.number_input("CapEx (€/m²)", value=10, step=1, key="capex_b")

# --- Berechnung ---
kpis_a = calc_kpis(name_a, kp_a, miete_a, flaeche_a, nk_rate_a, makler_a, ek_a, ann_a, opex_a, capex_a)
kpis_b = calc_kpis(name_b, kp_b, miete_b, flaeche_b, nk_rate_b, makler_b, ek_b, ann_b, opex_b, capex_b)

df = pd.DataFrame([kpis_a, kpis_b]).set_index("Objekt")
df["Delta (A-B)"] = df.iloc[0] - df.iloc[1]

# --- KPI Cards für Mobile ---
st.subheader("📊 KPI Vergleich (Kartenansicht)")

for metric in ["Gesamtkosten (€)", "Eigenkapital (€)", "Fremdkapital (€)", "NOI (€)", 
               "Cap Rate (%)", "DSCR", "CoC Rendite (%)", "Nettomietrendite (%)"]:
    col1, col2, col3 = st.columns([1,1,1])
    val_a = df.loc[name_a, metric]
    val_b = df.loc[name_b, metric]
    delta = val_a - val_b

    # Formatierung
    if "€" in metric:
        val_a_fmt = f"{val_a:,.0f} €"
        val_b_fmt = f"{val_b:,.0f} €"
        delta_fmt = f"{delta:,.0f} €"
    elif "%" in metric:
        val_a_fmt = f"{val_a:.2f} %"
        val_b_fmt = f"{val_b:.2f} %"
        delta_fmt = f"{delta:.2f} %"
    else:
        val_a_fmt = f"{val_a:.2f}"
        val_b_fmt = f"{val_b:.2f}"
        delta_fmt = f"{delta:.2f}"

    # Ampelfarben
    better_high = ["NOI (€)", "Cap Rate (%)", "DSCR", "CoC Rendite (%)", "Nettomietrendite (%)"]
    if metric in better_high:
        delta_symbol = "🟢" if delta > 0 else ("🔴" if delta < 0 else "⚪")
    else:
        delta_symbol = "🟢" if delta < 0 else ("🔴" if delta > 0 else "⚪")

    col1.metric(f"{metric} – {name_a}", val_a_fmt)
    col2.metric(f"{metric} – {name_b}", val_b_fmt)
    col3.metric("Delta (A-B)", f"{delta_fmt} {delta_symbol}")

# --- Radar Chart ---
st.subheader("📈 Grafischer Vergleich (Radar-Chart)")
metrics = ["Cap Rate (%)", "DSCR", "CoC Rendite (%)", "Nettomietrendite (%)"]

values_a = [df.loc[name_a, m] for m in metrics]
values_b = [df.loc[name_b, m] for m in metrics]

angles = list(range(len(metrics)))
angles += [angles[0]]

values_a += [values_a[0]]
values_b += [values_b[0]]

fig, ax = plt.subplots(figsize=(5,5), subplot_kw=dict(polar=True))
ax.plot(angles, values_a, label=name_a, linewidth=2)
ax.fill(angles, values_a, alpha=0.25)
ax.plot(angles, values_b, label=name_b, linewidth=2)
ax.fill(angles, values_b, alpha=0.25)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(metrics, fontsize=10)
ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.05))

st.pyplot(fig)

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
