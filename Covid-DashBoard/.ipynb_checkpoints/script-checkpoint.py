import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

mapbox_access_token = "pk.eyJ1IjoiaGFyc2hpdGsiLCJhIjoiY2toeHUyc3hpMDN3ZzJ1b2E0MTV1MjcybyJ9.kdenbRD0dVz19JovVwwqDg"
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

#########################
#   Plots for the APP   #
#########################
def getAllCountryPlot(data, top_ten_country):
    ten_count = top_ten_country
    fig = px.line(data.query("location in @ten_count"), x="date", y="total_cases", color = "location")
    # fig.update_traces(mode='markers+lines')
    fig.update_xaxes(showline=False, gridwidth=2, gridcolor='#ededed')
    fig.update_yaxes(showline=False, gridwidth=2, gridcolor='#ededed')
    fig.update_layout(
            paper_bgcolor = '#f7f7f7',
            plot_bgcolor = '#f7f7f7',
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
    fig.update_layout(
            paper_bgcolor = '#f5f5f5',
            plot_bgcolor = '#f5f5f5',
            font=dict(
                family="Courier New, monospace",
                size=14
            ))
    return fig
        
def run_the_app():
    st.title("Consolidated DashBoard since the OutBreak")
    st.markdown("This application is a Streamlit dashboard that can be used "
                "to analyze the spread of COVID-19 💥🚗")

    @st.cache(suppress_st_warning=True, persist=True, allow_output_mutation=True)
    def load_data():
        data = pd.read_csv(DATA_URL, parse_dates=['date'], usecols =[1,2,3,4,5,7,8,10,11,13,14,34,35,47])
        data_country = pd.read_csv('dataFinal_Country.csv')
        data.drop(data[data['continent'].isnull()].index, inplace = True)
        data.drop(data[(data['new_cases'].isnull()) & (data['total_cases'].isnull())].index, inplace = True)
        
        groups = data.groupby('location')

        x = groups.agg({'total_cases':'max', 'total_deaths':'max'})
        x.reset_index(inplace = True)
        x.columns = ['Country', "Max Total Cases", "Total Deaths"]
        x.sort_values("Max Total Cases",ascending = False, inplace = True)
        x.reset_index(drop = True, inplace = True)

        top_ten = x[:10]
        
        return data, top_ten, groups, data_country
    
    #######################
    #   Data Preperation  #
    #######################
    data, top_ten, groups, country_data = load_data()
    
    grouped = groups.agg({'total_cases':'max', 'total_deaths':'max'})
    grouped.reset_index(inplace=True)
    df = grouped.merge(country_data, how = 'left', left_on = 'location', right_on = 'name')
    
    countries = data.location.unique()
    month_dict = {'January':1, 'February':2, 'March':3, 
                  'April':4,'May':5,'June':6,'July':7,
                  'August':8,'September':9,'October':10}
                  # 'November':11,'December':12}
       
    imp_columns = {'Total Cases':'total_cases',
                   'Total Deaths':'total_deaths',
                   'New Cases':'new_cases'}
    
    ##########################
    #   Laying out the APP   #
    ##########################
    country = st.sidebar.selectbox("Choose the Country", countries)
    st.sidebar.subheader('Choose Date Time range')
    day1, day2 = st.sidebar.slider("Day(s)", 1, 31, (5,10))
    options = st.sidebar.multiselect(
                                'Choose Month(s)',
                                list(month_dict.keys()), list(month_dict.keys()))
    st.sidebar.write("November and December are disabled due to unavailability of data")
    
    country_data = groups.get_group(country)
    
    st.subheader("COVID OutBreak Country-Wise")
    fig = go.Figure(go.Scattermapbox(
                mode = "markers",
                lon = df["longitude"], lat = df["latitude"],
                marker = {'size': np.log(df['total_cases'])*4, "opacity": 0.35},
                hovertext = ["Country/Region: {} <br>Total Cases: {} <br>Total Deaths: {} ".format(loc, conf, dea)
                          for loc, conf, dea in zip(df['location'], df['total_cases'], df['total_deaths'])]
                ))
    
    fig.update_layout(mapbox_style       = "dark", 
                      margin             = {"r":0,"t":0,"l":0,"b":0}, 
                      font               = dict(color=colors['figure_text']),
                      titlefont          = dict(color=colors['text']),
                      hovermode          = "closest",
                      legend             = dict(font=dict(size=10), orientation='h'),
                      mapbox             = dict(accesstoken=mapbox_access_token,
                                                style='mapbox://styles/mapbox/dark-v10',
                                                center=dict(
                                                    lon=78.96288,
                                                    lat=20.593684),
                                                zoom=1),
                      autosize           = True)

    st.write(fig)
    st.write(getAllCountryPlot(data, top_ten.Country))
    cols = {'location':"Country",
            'date':"Date",
            'total_cases':"Total Cases",
            'total_deaths':"Total Deaths"}
    df_display = country_data[list(cols.keys())].copy().reset_index(drop = True)
    
    def highlight_col(x):
        r = 'color: red'
        b = 'color: blue'
        df1 = pd.DataFrame('', index=x.index, columns=x.columns)
        df1.iloc[:,3] = r
        df1.iloc[:,2] = b
        return df1    
    df_display = df_display.style.apply(highlight_col, axis=None).hide_index()
    def magnify():
        return [dict(selector="th",
                     props=[("font-size", "4pt")]),
                dict(selector="td",
                     props=[('padding', "0em 0em")]),
                dict(selector="th:hover",
                     props=[("font-size", "12pt")]),
                dict(selector="tr:hover td:hover",
                     props=[('max-width', '200px'),
                            ('font-size', '12pt')])]
    
    df_display = df_display.set_caption("Hover to magnify")\
                           .set_precision(2)\
                           .set_table_styles(magnify())
            
    if st.checkbox("Show Table View"):
        st.write(df_display)
    
    column = st.radio("Choose the Column to display data", list(imp_columns.keys()))
    st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    
    if len(options) == 0:
        options = list(month_dict.keys())
    temp = pd.DataFrame()
    for i in options:
        temp_day2 = day2
        if i == 'February' and day2>29:
            temp_day2 = 29
        elif i in ['April', 'June', 'September'] and day2>30:
            temp_day2 = 30
        # st.write("Month: ",i," max day: ", temp_day2)
        datetime = '2020-'+str(month_dict[i])+'-'+str(day1)
        datetime2 = '2020-'+str(month_dict[i])+'-'+str(temp_day2)
        t = country_data[(country_data['date']>=datetime)&(country_data['date']<=datetime2)]
        temp = pd.concat([temp, t], ignore_index=True)
        
    st.write(getPlot(temp, imp_columns[column]))
    
def main():
    st.sidebar.title("COVID OUTBREAK !!!")
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
        
if __name__ == "__main__":
    main()