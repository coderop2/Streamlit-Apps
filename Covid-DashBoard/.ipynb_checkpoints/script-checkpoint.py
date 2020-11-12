import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATE_TIME = "date"
DATA_URL = (
    "data.csv"
)
colors = {
    'background': '#2D2D2D',
    'text': '#E1E2E5',
    'figure_text': '#ffffff',
    'confirmed_text':'#3CA4FF',
    'deaths_text':'#f44336',
    'recovered_text':'#5A9E6F',
    'highest_case_bg':'#393939',
    'gridcolor':'#363636'
}


@st.cache(show_spinner=True)
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
        st.code(get_file_content_as_string("script.py"))
    elif app_mode == "Run the app":
        #dataSize = st.sidebar.slider("Choose the Size of the dataset to be run", 5000, 15000)
        run_the_app()
        
def getAllCountryPlot(data, top_ten_country):
    ten_count = top_ten_country
    fig = px.line(data.query("location in @ten_count"), x="date", y="total_cases", color = "location")
    fig.update_traces(mode='markers+lines')
    fig.update_xaxes(showline=False, gridwidth=2, gridcolor='#363636')
    fig.update_yaxes(showline=False, gridwidth=2, gridcolor='#363636')
    fig.update_layout(
            font=dict(
                family="Courier New, monospace",
                size=14
            ),
            margin=dict(l=0, 
                    r=0, 
                    t=0, 
                    b=0))
    return fig

def getPlot(data, col):
    fig = px.line(data, x='date',y=col)
    fig.update_traces(mode='markers+lines')
    return fig
        
def run_the_app():
    st.title("Consolidated DashBoard since the OutBreak")
    st.markdown("This application is a Streamlit dashboard that can be used "
                "to analyze the spread of COVID-19 💥🚗")

    @st.cache(suppress_st_warning=True, persist=True)
    def load_data():
        data = pd.read_csv(DATA_URL, parse_dates=['date'], usecols =[1,2,3,4,5,7,8,10,11,13,14,34,35,47])
        data.drop(data[data['continent'].isnull()].index, inplace = True)
        data.drop(data[(data['new_cases'].isnull()) & (data['total_cases'].isnull())].index, inplace = True)
        
        groups = data.groupby('location')

        x = groups.agg({'total_cases':'max', 'total_deaths':'max'})
        x.reset_index(inplace = True)
        x.columns = ['Country', "Max Total Cases", "Total Deaths"]
        x.sort_values("Max Total Cases",ascending = False, inplace = True)
        x.reset_index(drop = True, inplace = True)

        top_ten = x[:10]
        return data, top_ten, groups
    
    data, top_ten, groups = load_data()
    
    countries = data.location.unique()
    
    st.write(getAllCountryPlot(data, top_ten.Country))
    
    country = st.sidebar.selectbox("Choose the Country", countries)
    
    #col1, col2 = st.beta_columns(2)
    country_data = groups.get_group(country)
    column = st.radio("Choose", ['total_cases','total_deaths','new_cases'])
    st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    st.write(getPlot(country_data, column))
    #with col1:
        #st.write(getPlot(country_data, "total_cases"))
    #with col2:
        #st.write(getPlot(country_data, "total_deaths"))
    #with col3:
       # st.write(getPlot(country_data, "new_cases"))


if __name__ == "__main__":
    main()