import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

#Page Configuration

st.set_page_config(
    page_title="Nigeria Housing Marketplace Dashboard",
    page_icon="🏘️",
    layout="wide"
)

@st.cache_data #Decorator to speed up the app
def load_data():
    try:
        df = pd.read_csv("data/jiji_housing_cleaned.csv")
        return df
    except FileExistsError as e:
        st.warning(f'Error!: {e}')

def sidebar_filter(df):
    st.sidebar.header('Housing Filters')

    region = st.sidebar.multiselect(
        'Select Region',
        options=df['Region'].unique(),
        default=df['Region'].unique()
    )

    furnished = st.sidebar.multiselect(
        'Furnishing Condition',
        options=df['Furnishing'].unique(),
        default=df['Furnishing'].unique()
    )

    boosting = st.sidebar.multiselect(
        'Boost',
        options=df['Is_Boost'].unique(),
        default=df['Is_Boost'].unique()
    )
    return region, furnished, boosting

    #To connect the filters
def filter_data(df, region, furnished, boosting):
    filtered_df = df[df['Region'].isin(region) & df['Furnishing'].isin(furnished) & df['Is_Boost'].isin(boosting)]
    return filtered_df


    #KPI
def display_kpi(filtered_df):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric('🏘️ Total Houses', len(filtered_df))

    with col2:
        average_price = filtered_df['Price'].mean() if len(filtered_df) > 0 else 0
        if average_price >= 1_000_000:
            formatted_average = f"₦{int(average_price / 1_000_000)} M"
        elif average_price >= 1_000:
            formatted_average = f"₦{int(average_price / 1_000)} K"
        else:
            formatted_average = f"₦{int(average_price)}"

        st.metric("🏠 Average House Price", formatted_average)

    with col3:
        top_region = filtered_df['Region_Parent_Name'].mode()[0] if len(filtered_df) > 0 else 0
        st.metric('🏡 Top Region', top_region)

    with col4:
        furnished_pct = (filtered_df['Furnishing'] == 'Furnished').sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric('🛖🪑Furnished Houses', f'{furnished_pct:.2f}%')


def charts(filtered_df):
    if len(filtered_df) == 0:
        st.warning("Please Select Filters")
        return
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Total Hosing By Regions')
        region1 = filtered_df.groupby('Region_Parent_Name')['Title'].count().sort_values(ascending=False)
        fig1 = px.bar(
            x=region1.values,
            y=region1.index,
        )
        fig1.update_layout(
            xaxis_title="Counts",
            yaxis_title="Regions"
        )
        st.plotly_chart(fig1)

    with col2:
        st.subheader('Average Price By Regions')
        region2 = filtered_df.groupby('Region_Parent_Name')['Price'].mean().sort_values(ascending=False)
        fig2 = px.bar(
            x=region2.values,
            y=region2.index,
        )
        fig2.update_layout(
            xaxis_title="Average Price",
            yaxis_title="Regions"
        )
        st.plotly_chart(fig2, width='stretch')

    col3, col4 = st.columns(2)

    with col3:
        st.subheader('Distribution of Property Price')
        fig3 = px.histogram(
            filtered_df, x='Price', nbins=10
        )
        fig3.update_traces(
            marker_line_color='white',
            marker_line_width=1
        )
        fig3.update_layout(
            xaxis_title='Price',
            yaxis_title='Frequency'
        )
        st.plotly_chart(fig3, width='stretch')

    with col4:
        fig4 = px.scatter(
            filtered_df,
            x="Property_Size",
            y="Price",
            title="Property Size vs. Price",
            labels={'Property_Size': 'Property_Size', 'Price': 'Price'}
        )
        fig4.update_traces(
            marker=dict(size=12, opacity=0.8)
        )
        fig4.update_layout(
            xaxis_title="Property Size", 
            yaxis_title="Price"
        )
        st.plotly_chart(fig4, width='stretch')

    col5, = st.columns(1)

    with col5:
        st.subheader('Price By Bedroom Number')
        fig5 = px.box(
            filtered_df,
            x='Bedrooms',
            y='Price'
        )
        st.plotly_chart(fig5, width='stretch')
    
    col6, col7 = st.columns(2)
    with col6:
        st.subheader('Furnishing Distribution')
        furnishing_counts = filtered_df['Furnishing'].value_counts()
        fig6 = px.pie(
            values=furnishing_counts.values,
            names=furnishing_counts.index,
        hole=0.4
        )
        st.plotly_chart(fig6, width='stretch')
        
    with col7:
        st.subheader('Correlation of Numeric Variables')
        num = filtered_df.select_dtypes(include=['number'])
        corr = num.corr()
        fig7, ax = plt.subplots(figsize=(8,6))
        sns.heatmap(
        corr,
        annot=True,
        cmap="vlag",
        fmt=".2f",
        linewidths=0.5,
        ax=ax
        )
        st.pyplot(fig7)

def table_data(filtered_df):
    if len (filtered_df) > 0:
        st.dataframe(filtered_df, width='stretch', height=300)
    else:
        st.warning("No Housing Data To Display")



#Control Function
def main():
    #load data
    df = load_data()

    #sidebar call
    region, furnished, boosting = sidebar_filter(df)

    #filter connection
    filtered_df = filter_data(df, region, furnished, boosting)

    st.title('Nigeria Housing Marketplace Dashboard')
    st.markdown('---')

    #call filter
    display_kpi(filtered_df)

    # #Display Chart
    st.markdown("---")
    charts(filtered_df)

    #Display dataframe
    st.markdown("---")
    table_data(filtered_df)

main()