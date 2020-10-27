import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import urllib

DATE_TIME = "date/time"
DATA_URL = (
    "Motor_Vehicle_Collisions_-_Crashes.csv"
)
@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    url = path
    response = open(url)
    return response.read()  

def main():
    st.sidebar.title("Welcome !!!")
    st.sidebar.header("What to do")
    
    app_mode = st.sidebar.selectbox("Choose the app mode",
        ["Show instructions", "Run the app", "Show the source code"])
    if app_mode == "Show instructions":
        st.sidebar.success('To continue select "Run the app".')
    elif app_mode == "Show the source code":
        st.code(get_file_content_as_string("test.py"))
    elif app_mode == "Run the app":     
        run_the_app()
        
def run_the_app():
    st.title("Motor Vehicle Collisions in New York City")
    st.markdown("This application is a Streamlit dashboard that can be used "
                "to analyze motor vehicle collisions in NYC 🗽💥🚗")

    @st.cache(suppress_st_warning=True, persist=True)
    def load_data(nrows):
        data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH DATE', 'CRASH TIME']])
        data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
        data.rename(lambda x: "_".join(str(x).lower().split(" ")), axis="columns", inplace=True)
        data.rename(columns={"crash_date_crash_time": "date/time"}, inplace=True)
        return data

    data = load_data(50000)
    st.header("Where are the most people injured in NYC?")
    injured_people = st.sidebar.slider("Number of persons injured in vehicle collisions", 0, 19)
    st.map(data.query("number_of_persons_injured >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

    st.header("How many collisions occur during a given time of day?")
    hour = st.sidebar.slider("Hour to look at", 0, 23)
    original_data = data
    data = data[data[DATE_TIME].dt.hour == hour]
    st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

    midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))
    st.write(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": midpoint[0],
                "longitude": midpoint[1],
                "zoom": 11,
                "pitch": 50,
            },
            layers=[
                pdk.Layer(
                "HexagonLayer",
                data=data[['date/time', 'latitude', 'longitude']],
                get_position=["longitude", "latitude"],
                auto_highlight=True,
                radius=100,
                extruded=True,
                pickable=True,
                elevation_scale=4,
                elevation_range=[0, 1000],
                ),
            ],
        ))
    if st.checkbox("Show raw data", False):
        st.subheader("Raw data by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
        st.write(data)

    st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
    filtered = data[
        (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
    ]
    hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
    chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})

    fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
    st.write(fig)

    st.header("Top 5 dangerous streets by affected class")
    select = st.sidebar.selectbox('Affected class', ['Pedestrians', 'Cyclists', 'Motorists'])
    
    col1, col2 = st.beta_columns(2)
    
    if select == 'Pedestrians':
        with col1:
            st.write(original_data.query("number_of_pedestrians_injured >= 1")[["on_street_name", "number_of_pedestrians_injured"]].sort_values(by=['number_of_pedestrians_injured'], ascending=False).dropna(how="any")[:5], use_column_width=True)
        with col2:
            st.write(original_data.query("number_of_pedestrians_killed >= 1")[["on_street_name", "number_of_pedestrians_injured"]].sort_values(by=['number_of_pedestrians_injured'], ascending=False).dropna(how="any")[:5], use_column_width=True)    

    elif select == 'Cyclists':
        st.write(original_data.query("number_of_cyclist_injured >= 1")[["on_street_name", "number_of_cyclist_injured"]].sort_values(by=['number_of_cyclist_injured'], ascending=False).dropna(how="any")[:5])

    else:
        st.write(original_data.query("number_of_motorist_injured >= 1")[["on_street_name", "number_of_motorist_injured"]].sort_values(by=['number_of_motorist_injured'], ascending=False).dropna(how="any")[:5])
    
    
if __name__ == "__main__":
    main()