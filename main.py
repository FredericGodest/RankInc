from function_module import *
import streamlit as st

df = get_df()
clean_df = str2float(df)

st.set_page_config(
   page_title="RankedInc",
   page_icon="📊",
   layout="wide",
   initial_sidebar_state="expanded",
)
st.markdown("# Bienvenue sur RankedInc")
st.markdown(f"RankedInc est une plateforme gratuite qui analyse {len(clean_df)} entreprises françaises en se basant "
            f"sur des ratios fondamentaux.")

st.markdown("## Analyse d'un secteur en particulier:")
sector_list = tuple(clean_df["secteur"].drop_duplicates())
option = st.selectbox(
     'Choisissez le secteur',
     sector_list)

fig, df_ranked = sector_analysis(clean_df, option)
st.plotly_chart(fig)
st.dataframe(df_ranked)


st.markdown("## Analyse des ratios fondamentaux par rapport au marché:")
figs = multiplot(clean_df)
for fig in figs:
     st.plotly_chart(fig)





