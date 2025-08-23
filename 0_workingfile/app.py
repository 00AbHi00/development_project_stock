import pandas as pd
import streamlit as st
import datetime as dt


#Defining styles
st.html("""
    <style>
    .equal-box {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 40px;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 4px 8px;
    }
    .category-col {
        
        width: 100%;
        margin-bottom: 6px;
    }
    </style>
""")


begin_date = st.date_input("Enter Begin Date", value=dt.date(2010, 4, 15))
end_date = st.date_input("Enter End Date", value=dt.date(2025,7,7))


df=pd.read_csv('clean1_enriched.csv')

#add and give a single line code which takes begin date and end date and filters dataframe acc, do i need to worry like react?
# df=df['']

#List of All the companies with their head
st.header("List of all the companies")
df_fil=df[['sn', 'Name', 'Symbol', 'Category', 'company.name_x', 'first_appear_date', 'last_appear_date']]

summary_df = pd.DataFrame({
    "Metric": ["Count", "Columns", "Unique values"],
    "Value": [
        df_fil["Name"].count(),
        df_fil.columns.to_list(),
        df_fil.nunique().to_dict()
    ]
})



st.table(summary_df)    
category_counts = df['Category'].value_counts().sort_values(ascending=False)
unique_categories = category_counts.index.tolist()

if 'selected_cat' not in st.session_state:
    st.session_state.selected_cat = None


if st.session_state.selected_cat:
    st.markdown(f"### Details for Category: `{st.session_state.selected_cat}`")

    # Filter data for selected category
    filtered_data = df[df['Category'] == st.session_state.selected_cat][['Name', 'Symbol','first_appear_date','last_appear_date']]
    st.dataframe(filtered_data.reset_index(drop=True))
    



st.header("Count of the number of Companies along with thier Categories")
c1, c2 = st.columns([4, 3], gap="small", border=True)


with st.container():
    for cat in unique_categories:
        with c1:
            if st.button(cat, key=f"btn_{cat}", use_container_width=True):
                st.session_state.selected_cat = cat
                
        with c2:
            st.html(f"<div class='equal-box'>{category_counts[cat]}</div>")


# Filtering IPOs/ Mergers of last 10 years

