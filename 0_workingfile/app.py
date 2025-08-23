import pandas as pd
import streamlit as st


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



df=pd.read_csv('company_names_further_removed_dupli.csv')

#List of All the companies with their head
st.header("List of all the companies")

summary_df = pd.DataFrame({
    "Metric": ["Count", "Columns", "Unique values"],
    "Value": [
        df["Name"].count(),
        df.columns.to_list(),
        df.nunique().to_dict()
    ]
})



st.table(summary_df)    
st.header("Count of the number of Companies along with thier Categories")

category_counts = df['Category'].value_counts().sort_values(ascending=False)
unique_categories = category_counts.index.tolist()

if 'selected_cat' not in st.session_state:
    st.session_state.selected_cat = None


if st.session_state.selected_cat:
    st.markdown(f"### Details for Category: `{st.session_state.selected_cat}`")

    # Filter data for selected category
    filtered_data = df[df['Category'] == st.session_state.selected_cat][['Name', 'Symbol']]
    st.dataframe(filtered_data.reset_index(drop=True))
    



c1, c2 = st.columns([4, 3], gap="small", border=True)


with st.container():
    for cat in unique_categories:
        with c1:
            if st.button(cat, key=f"btn_{cat}", use_container_width=True):
                st.session_state.selected_cat = cat
                
        with c2:
            st.html(f"<div class='equal-box'>{category_counts[cat]}</div>")


