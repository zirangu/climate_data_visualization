import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime

# Load and preprocess the data
@st.cache_data
def load_data():

    df = pd.read_csv("GlobalLandTemperaturesByCountry.csv")

    # Convert 'dt' to datetime and extract the year
    df['dt'] = pd.to_datetime(df['dt'])
    df['year'] = df['dt'].dt.year

    # Drop rows where 'AverageTemperature' is NaN
    df = df[df['year'] >= 1900]
    df = df.dropna(subset=['AverageTemperature','AverageTemperatureUncertainty'])
 

    # Group by country and year to calculate the average temperature
    df_grouped = df.groupby(['Country', 'year'])['AverageTemperature'].mean().reset_index()

    return df


# Create the line plot for a selected country
@st.cache_data
def create_line_plot(df, country,show_ci, show_ma):
    df_country = df[df['Country'] == country].groupby('year').agg({
        'AverageTemperature': 'mean',
        'AverageTemperatureUncertainty': 'mean'
    }).reset_index()
    # fig = px.line(df_country, x='year', y='AverageTemperature', title=f'Temperature Trend for {country}')
    
    # fig = go.Figure([
    #     go.Scatter(
    #         name='Average Temperature',
    #         x=df_country['year'],
    #         y=df_country['AverageTemperature'],
    #         mode='lines',
    #         line=dict(color='rgb(31, 119, 180)'),
    #         fill='tonexty',
    #         fillcolor='rgba(68, 68, 68, 0.3)'
    #     )
    # ])

     # Calculate the 20-year moving average
    if show_ma:
        df_country['MovingAverage'] = df_country['AverageTemperature'].rolling(window=20).mean()
        # print(df_country.head(100)) # for debug purpose

    fig = px.line(df_country, x='year', y='AverageTemperature', title=f'Temperature Trend for {country}')
    

   

    if show_ma:
        fig.add_trace(go.Scatter(
            name='20-Year Moving Average',
            x=df_country['year'],
            y=df_country['MovingAverage'],
            mode='lines',
            line=dict(color='rgb(255, 127, 14)'),
            # visible='legendonly'  # Set to only show when selected in legend
            showlegend = False
        ))

    # Add confidence interval if checkbox is checked
    if show_ci:
        fig.add_trace(go.Scatter(
            name='Upper Bound',
            x=df_country['year'],
            y=df_country['AverageTemperature'] + df_country['AverageTemperatureUncertainty'],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            name='Lower Bound',
            x=df_country['year'],
            y=df_country['AverageTemperature'] - df_country['AverageTemperatureUncertainty'],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        ))
    
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


    show_ci = st.checkbox("Show 95% Confidence Interval")

    # Checkbox to show/hide the moving average
    show_ma = st.checkbox("Show 20-Year Moving Average")

    # Display line plot for the selected country
    if selected_country:
        line_fig = create_line_plot(df, selected_country,show_ci,show_ma)
        st.plotly_chart(line_fig)

if __name__ == "__main__":
    main()
