import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load and preprocess the data
def load_data():

    df = pd.read_csv("GlobalLandTemperaturesByCountry.csv")

    # Convert 'dt' to datetime and extract the year
    df['dt'] = pd.to_datetime(df['dt'])
    df['year'] = df['dt'].dt.year

    # Drop rows where 'AverageTemperature' is NaN
    df = df.dropna(subset=['AverageTemperature'])

    # Group by country and year to calculate the average temperature
    df_grouped = df.groupby(['Country', 'year'])['AverageTemperature'].mean().reset_index()

    return df_grouped


# Create the line plot for a selected country
def create_line_plot(df, country):
    df_country = df[df['Country'] == country]
    fig = px.line(df_country, x='year', y='AverageTemperature', title=f'Temperature Trend for {country}')
    return fig

# Create the Streamlit app
def main():
    st.title("Geographic Heatmap of Temperature Changes Over Time")

    df = load_data()

    # Slider for selecting the year
    min_year = df['year'].min()
    max_year = df['year'].max()
    selected_year = st.slider("Select Year", min_year, max_year, min_year)

    # Filter data based on selected year
    filtered_df = df[df['year'] == selected_year]

    # Generate the heatmap
    fig = px.choropleth(filtered_df, locations="Country",  # Corrected from "country" to "Country"
                    color="AverageTemperature",  # This matches the DataFrame column name
                    hover_name="Country",  # This now correctly references the 'Country' column
                    color_continuous_scale=px.colors.sequential.Plasma,
                    locationmode='country names')  # Ensure correct mapping of country names



    st.plotly_chart(fig, use_container_width=True)  # Set to use the full width of the Streamlit container

    # Country selection for line plot
    countries = df['Country'].unique()
    selected_country = st.selectbox("Select a Country", countries)

    # Display line plot for the selected country
    if selected_country:
        line_fig = create_line_plot(df, selected_country)
        st.plotly_chart(line_fig)

if __name__ == "__main__":
    main()
