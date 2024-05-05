'''
Name: Samuel Rao
CS230: Section 2
Data: Nuclear Explosions 1945-1998
Description:
This program is for the development of an interactive, web-based Python application 
that analyzes the available data on all nuclear explosions prior to the year 
2000 through the use of parameters including time, country, and location.
'''
# cd C:\Users\srao4\OneDrive\Year 2\CS230 - Intro to Python\Eclipse-Workspace\Final
# C:\Users\srao4\anaconda3\Scripts\streamlit.exe run FinalFile.py

import pandas as pd
import pydeck as pdk
import altair as alt
import streamlit as st
from datetime import datetime

# Function to prepare database for use, renames columns to appropriate names and adds desired columns for later user
def modifyDataframe(df):
    # Create dictionary for renaming column headers
    columnName = {'WEAPON SOURCE COUNTRY': 'Source Country',
                  'WEAPON DEPLOYMENT LOCATION': 'Deployment Location',
                  'Data.Source': 'Data Source',
                  'Location.Cordinates.Latitude': 'latitude',
                  'Location.Cordinates.Longitude': 'longitude',
                  'Location.Cordinates.Depth': 'Depth',
                  'Data.Magnitude.Body': 'Body Magnitude',
                  'Data.Magnitude.Surface': 'Surface Magnitude',
                  'Data.Yeild.Lower': 'Lower Yield',
                  'Data.Yeild.Upper': 'Upper Yield',
                  'Data.Purpose': 'Purpose',
                  'Data.Name': 'Name',
                  'Data.Type': 'Deployment Method',
                  'Date.Day': 'Day',
                  'Date.Month': 'Month',
                  'Date.Year': 'Year'}
    # Rename dataframe column headers
    df = df.rename(columns=columnName)
    
    # Create dictionary for replacing deployment method names to remove abbreviations and redundancies. Source: https://multimedia.scmp.com/news/world/article/to-understand-North-Korea/data/sipri-report-original.pdf
    deploymentMethodName = {'Atmosph': 'Atmosphere',
                   'Shaft/Gr': 'Shaft/Ground',
                   'Shaft/Lg': 'Shaft/Lagoon',
                   'Ug': 'Underground',
                   'Uw': 'Underwater',
                   'Water Su': 'Water Surface',
                   'Watersur': 'Water Surface'}
    # Replace deployment method values with proper names
    df['Deployment Method'] = df['Deployment Method'].replace(deploymentMethodName)
    
    # Create dictionary for replacing purpose names to remove abbreviations and redundancies. Source: https://multimedia.scmp.com/news/world/article/to-understand-North-Korea/data/sipri-report-original.pdf
    purposeName = {'Fms': 'FMS(Soviet tests)',
                   'Me': 'Military exercise',
                   'Pne': 'Peaceful nuclear explosion',
                   'Pne:Plo': 'Plowshare Programme',
                   'Pne:V': 'Vela Uniform Tests',
                   'Sam': 'SAM(Soviet tests)',
                   'Se': 'Safety test',
                   'Transp': 'Transportation-storage',
                   'We': 'Weapons evaluation(WE)',
                   'Wr': 'Weapons-related(WR)',
                   'Fms/Wr': 'FMS/Weapons-related',
                   'Se/Wr': 'Safety/Weapons-related',
                   'Pne/Wr': 'Peaceful/Weapons-related',
                   'We/Sam': 'Weapons evaluation/SAM',
                   'We/Wr': 'Weapons-related/evaluation',
                   'Wr/Se': 'Safety/Weapons-related',
                   'Wr/Pne': 'Peaceful/Weapons-related',
                   'Wr/We': 'Weapons-related/evaluation'}
    # Replace purpose values with proper names
    df['Purpose'] = df['Purpose'].replace(purposeName)
    
    # Create date column in datetime format that combines the year, month, day values
    df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
    # Create yield column by calculating the average between the upper and lower yield
    df['Average Yield'] = (df['Lower Yield'] + df['Upper Yield']) / 2
    
    return df

# Function for generating a bar chart displaying average yield by purpose for selected deployment method
def yieldChart(df, method):
        # Isolate data that falls within specified deployment method
        filtered_df = df[df['Deployment Method'] == method]
        # Group data by purpose and calculate average yield
        deployment_df = filtered_df.groupby(by = "Purpose")['Average Yield'].mean().reset_index()
        # Create bar chart. Source: https://discuss.streamlit.io/t/add-x-axis-y-axis-name-and-title-to-the-chart/20221/3 
        yield_chart_data = alt.Chart(deployment_df, title='Average Yield by Explosion Purpose').mark_bar(color='maroon').encode(x='Purpose:N', y='Average Yield:Q')
        st.altair_chart(yield_chart_data, theme= None, use_container_width=True)

# Function for time slider, bar chart of explosions by country for specified time, and dataframe table for time interval
def sliderChartAndTable(df):
    st.header(":red[Nuclear Explosions by Country Over Time]", divider="red")
    # Create slider for date
    start_time, end_time = st.slider(
        "Specify time interval:",
        datetime(1945, 1, 1), datetime(2000, 1, 1),
        value=(datetime(1945, 1, 1), datetime(2000, 1, 1)),
        format="MM/DD/YYYY")
    
    # Isolate data from dataframe that falls within specified dates. Referenced Joakim Tronstad's code from his building violations project: https://github.com/joakimtronstad/buildingviolations/blob/main/app.py
    date_df = df[(pd.to_datetime(df["Date"]) >= pd.to_datetime(start_time)) & (pd.to_datetime(df["Date"]) <= pd.to_datetime(end_time))]
    # Sort dataframe by date
    date_df = date_df.sort_values("Date", ascending=False)
    # Remove 00:00:00 at end of date
    date_df["Date"] = pd.to_datetime(date_df["Date"]).dt.date
    # Isolate source country and conducts counts for bar chart
    country_counts = date_df['Source Country'].value_counts().reset_index()
    country_counts.columns = ['Source Country', 'Count']
    # Sort the data in descending order by count
    sorted_countries = country_counts.sort_values(by='Count', ascending=False)
    # Create bar chart for explosion count by country for specified time period
    bar_chart = alt.Chart(sorted_countries).mark_bar(color='maroon').encode(x=alt.X('Source Country:N', title='Country'), y=alt.Y('Count:Q', title='Explosion Count'))
    st.altair_chart(bar_chart, theme = None, use_container_width=True)
    
    # Display the time filtered DataFrame
    st.header(":red[Table of Nuclear Explosions Over Specified Interval]", divider = "red")
    date_df.astype(str) 
    date_df = date_df.loc[:, ["Date","Source Country","Deployment Location","Data Source","latitude","longitude","Depth","Lower Yield","Upper Yield","Average Yield","Purpose","Name","Deployment Method"]]
    st.dataframe(date_df)
    
    return sorted_countries
    
# Function for scatterplot overlay on map using data for specified country and purpose
def mapping(df, country, purpose = 'All'):
    st.header(":red["f"Map of Nuclear Explosions Carried Out by {country}]", divider = "red")
    # Create dataframe containing records for only the selected country and purpose
    if purpose != 'All':
        df = df[df['Purpose'] == purpose]
    if country != 'All':
        df = df[df['Source Country'] == country]
    map_df = df

    # Designate default view of map
    view_explosions = pdk.ViewState(
        latitude = map_df["latitude"].mean(),
        longitude = map_df["longitude"].mean(),
        zoom = 0, pitch = 0)
    
    # Create layer that plots datapoints in scatterplot to be overlayed on map
    layer1 = pdk.Layer(
        "ScatterplotLayer",
        data = map_df,
        get_position = "[longitude, latitude]",
        get_radius = 20000,
        opacity = 0.5,
        auto_highlight = True,
        get_color = [85, 142, 211],
        pickable = True)

    # Designate and design tool tip to display data when hovering over datapoints
    tool_tip = {"html": 
                "Source Country: <b>{Source Country}</b></br>"
                "Deployment Location: <b>{Deployment Location}</b></br>"
                "Data Source: <b>{Data Source}</b></br>"
                "Purpose: <b>{Purpose}</b><br/>"
                "Date: <b>{Year}<b></br>",
                "style": {"backgroundColor": (50, 107, 205),
                          "color": (152, 180, 230)}}

    # Create map using previously outlined aspects
    explosionsMap = pdk.Deck(
        map_style = "dark",
        initial_view_state = view_explosions,
        layers=layer1,
        tooltip=tool_tip)
    
    # Plot map
    st.pydeck_chart(explosionsMap)
    
    return map_df

# Function for bar chart creation and dataframe display to compare explosion counts between selected countries
def compareCountries(df, selected_countries):
    # Dropdown to select viewing method of data: bar or pie chart
    chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Pie Chart"])
    # Procedure for unselected or insufficient country selection. Default: US and USSR comparison
    if len(selected_countries) < 2:
        selected_countries = ['USA','USSR']
        st.header(":red[Explosion Count for USA vs. USSR]", divider = "red")
    else:
        st.header(":red[Explosion Count for Selected Countries]", divider = "red")
    
    # Isolate data for selected countries from dataframe
    compare_df = df[df['Source Country'].isin(selected_countries)]
    compare_counts = compare_df['Source Country'].value_counts().reset_index()
    compare_counts.columns = ['Source Country', 'Count']
    # Create bar chart displaying explosion counts for selected countries
    if chart_type == "Bar Chart":
        compare_chart = alt.Chart(compare_counts).mark_bar(color='maroon').encode(
            x=alt.X('Source Country:N', title='Country'),
            y=alt.Y('Count:Q', title='Explosion Count'))
        st.altair_chart(compare_chart, theme=None, use_container_width=True)
    
    # Create pie chart displaying explosion counts for selected countries
    if chart_type == "Pie Chart":
        pie_chart = alt.Chart(compare_counts).mark_arc(color ='maroon').encode(theta='Count:Q',color='Source Country:N',
        tooltip=['Source Country', 'Count']).properties(title="Explosion Count by Country",width=500,height=500)
        st.altair_chart(pie_chart, theme = None, use_container_width=True)
    
    # Sort data by count and display dataframe table
    compare_counts.sort_values(by = "Count", ascending = False)
    st.dataframe(compare_counts, use_container_width=True)
    return compare_df, compare_counts

# Main function for application layout and design, includes tabular segmentation of data within tabs 1-4
def main():
    # Adding page configuration
    st.set_page_config(page_title='CS230 Project - Samuel Rao', page_icon = ":boom:", layout = "centered", initial_sidebar_state="auto")
    # Load in nuclear explosion dataset
    df = pd.read_csv("nuclear_explosions.csv")
    # Prepare dataset for use regarding column names and standardization
    df = modifyDataframe(df)
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["|Homepage|", "|Explosion Data|", "|Geographical Data|", "|Analysis by Country|"]) 
    #Customize tab font size. Source: https://discuss.streamlit.io/t/change-font-size-of-tabs/40945
    css = ''' 
    <style> .stTabs [data-baseweb="tab-list"] 
    button [data-testid="stMarkdownContainer"] 
    p {font-size:1.43rem;} </style> 
    '''
    st.markdown(css, unsafe_allow_html=True)
    
    # Tab for homepage, includes title, image, and program description
    with tab1:
        # Title header
        st.markdown("<h1 style='text-align: center; color: red;'> Nuclear Explosions Data Up Until the Year 2000 </h1>", unsafe_allow_html=True)
        # Homepage image
        st.image("Homepage.jpg")
        # Subheader for application description
        st.markdown("<h2 style='text-align: center; color: black; font-size: 30px;'> This is a web-based Python application that analyzes the available data on all nuclear explosions prior to the year 2000 through the use of parameters including time, country, and location. </h2>", unsafe_allow_html=True)
    
    # Tab for explosion data, includes deployment method query for yield bar chart and slider for explosion counts by country
    with tab2:
        st.header(":red[Average Yield by Deployment Method]", divider = "red")
        st.markdown(":grey[Yield refers to the amount of energy produced by the explosion of a nuclear weapon measured in kilotons. The graph below illustrates the relationship between the average yield of nuclear explosions and the purpose of detonation, further categorized by the variable deployment method of the nuclear weapon.]")
        # Dropdown to select deployment method
        method = st.selectbox("Select Deployment Method", sorted(df['Deployment Method'].dropna().unique()))
        # Create chart for yield by purpose for selected deployment method
        yieldChart(df, method)
        # Create slider, chart, and table for explosions over specified time
        sorted_countries = sliderChartAndTable(df)

    # Tab for geographic visualization through scatterplot overlay on map queried by country, includes data summaries
    with tab3:
        # Dropdown to select source country
        country = st.selectbox("Select a Country", ['All'] + list(sorted(df['Source Country'].unique())))
        # Create a dropdown to select purpose
        purpose = st.selectbox("Select Detonation Purpose", ['All'] + list(sorted(df['Purpose'].unique())))
        # Create map and return map dataframe
        map_df = mapping(df, country, purpose)
        #Caption map with explosion count
        explosion_count = len(map_df)
        st.info(f"Total explosion count: {explosion_count}")
        # Identify and display maximum possible yield for selected data
        max_yield = map_df['Upper Yield'].max()
        st.info(f"Maximum possible explosion yield: {max_yield} KT")
        # Iterate through map dataframe to identify and increase combat count accordingly
        combat_count = 0
        for object in map_df['Purpose']:
            if 'Combat' == object:
                combat_count += 1
        # Display number of combat detonations from selected data
        st.info(f"Number of detonations for combat purposes: {combat_count}")
    
    # Tab for comparing countries identified through multiselect, includes bar chart, dataframe table for counts, and summary data
    with tab4:
        # Multiselect box for source country
        selected_countries = st.multiselect("Select at Least Two Countries", sorted(df['Source Country'].unique()))
        # Execute function to create comparison chart and table, returns comparison dataframe and counts dataframe
        compare_df, compare_counts = compareCountries(df, selected_countries)
        # Find the country with the maximum count of explosions
        max_country = compare_counts.loc[compare_counts['Count'].idxmax(), 'Source Country']
        max_count = compare_counts['Count'].max()
        # Remove max country from dataframe to find runner up
        compare_counts.drop(compare_counts['Count'].idxmax(), inplace=True)
        # Find the runner-up country
        runner_up = compare_counts.loc[compare_counts['Count'].idxmax(), 'Source Country']
        runner_count = compare_counts['Count'].max()
        # Calculate difference 
        difference = max_count - runner_count
        # Display highest explosion count country
        st.info(f"Of the selected countries, the country with the greatest nuclear weapons use is {max_country}. "
                    f"{max_country} conducted {difference} more nuclear explosions than {runner_up}, "
                    f"the country with the second highest nuclear weapons usage.")
        # Identify earliest detonation date and origin country for selected countries
        earliest_date = compare_df['Date'].min()
        earliest_date_index = df['Date'].idxmin()
        earliest_country = df.loc[earliest_date_index, 'Source Country']
        # Remove 00:00:00 from end of date
        earliest_date = earliest_date.strftime('%Y-%m-%d')
        # Print message on earliest detonation
        st.info(f"The earliest use of atomic weapons by the selected countries "
                f"occurred on {earliest_date} by {earliest_country}.")

if __name__ == "__main__":
    main()
