from matplotlib.pyplot import text
import pandas as pd
import plotly.express as px  
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash import Dash, dcc, html, Input, Output, dash_table, no_update 
from dash.exceptions import PreventUpdate
from dash import dcc
import dash_bootstrap_components as dbc
import os.path

sharing_architectures_dict = {
    'Dark Fiber Leasing' : 'Fixed',
    'FTTH Wholesale' : 'Fixed',
    'IP/Ethernet Services' : 'Fixed',
    'Wavelength Service' : 'Fixed',
    'Active Sharing' : 'Mobile',
    'MNO/MVNO Wholesale': 'Mobile'
    }

network_type_dict ={
    'Single Wholesale Network' : 'Mobile',
    'Fixed OAN' : 'Fixed',
    'Independent Fixed NaaSCo' : 'Fixed',
    'Mobile OAN' : 'Mobile',
    'Independent Mobile NaaSCo' : 'Mobile',
    'Joint Venture' : 'Mobile'
}

color_deployments_dict = {
                "Mobile OAN": "#3ba9b6",
                "Fixed OAN": "#a5cf4c",
                "Independent Fixed NaaSCo": "#c1dc7f",
                "Independent Mobile NaaSCo": "#74c7ce"
                }

color_scenario_dict = {
    'Rural' : '#c1dc7f',
    'Urban': '#74c7ce',
    'Rural & Urban': '#3ba9b6'
}

color_arch_dict = {
    'Active Sharing' : '#74c7ce',
    'MNO/MVNO Wholesale': '#74c7ce',
    'Dark Fiber Leasing' : '#c1dc7f',
    'FTTH Wholesale' : '#c1dc7f',
    'IP/Ethernet Services' : '#c1dc7f',
    'Wavelength Service' : '#c1dc7f',
}

sharing_archi_wrapText_dict = {
    'Dark Fiber Leasing' : 'Dark Fiber<br>Leasing',
    'FTTH Wholesale' : 'FTTH<br>Wholesale',
    'IP/Ethernet Services' : 'IP/Ethernet<br>Services',
    'Wavelength Service' : 'Wavelength<br>Service',
    'Active Sharing' : 'Active Sharing',
    'MNO/MVNO Wholesale': 'MNO/MVNO<br>Wholesale'
    }

scenario_img_dict = {
    
    'Rural' : 'rural.png',
    'key_string': 'ultra_rural.png',
    'Low-ARPU Urban':'low_urban.png',
    'High-ARPU Urban': 'high_urban.png'
}

hoverlabel_dict = {
        'font_size' : 12,
        'font_family':'Montserrat'
}

annotation_dict = {
    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "No matching<br>data found",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 16,
                    "family":'Montserrat'
                }
            }
        ]
    }
}

font_dic ={
            'family' :"Montserrat",
            'size' : 10
        }

coloraxis_colorbar_dict = {
                'title' : '',
                'thickness' : 10,
                #'tickformat': ',d'
        }

def trim_text_df(dataframe, list_columns):

    for i in list_columns:
        dataframe[i] = dataframe[i].str.rstrip()
        dataframe[i] = dataframe[i].str.lstrip()

    return dataframe

def Create_Tracker_df(dataframe):
    dataframe = pd.read_csv("NaaSTracker.csv", encoding='utf-8', keep_default_na = False)
    list_2_trim_Tracker = ['Name',	'Region',	'ISO_3166',	'Business Model', 'Deployment Scenario']
    dataframe = trim_text_df(dataframe, list_2_trim_Tracker)
    dataframe['id'] = dataframe.index
    dataframe["Network_Type"] = dataframe['Business Model'].map(network_type_dict)
    dataframe['Business Model'] = dataframe['Business Model'].str.replace('Single Wholesale Network','Mobile OAN')
    dataframe['Business Model'] = dataframe['Business Model'].str.replace('Joint Venture','Independent Mobile NaaSCo')
    dataframe.loc[dataframe['Network Sharing Architecture'].str.contains('MORAN'), 'Network Sharing Architecture'] = 'Active Sharing'
    dataframe.loc[dataframe['Network Sharing Architecture'].str.contains('MOCN'), 'Network Sharing Architecture'] = 'Active Sharing'
    dataframe.sort_values(by=['Name'])
    dataframe['key'] = (dataframe['Name'].str.upper()).astype(str) + '_' + (dataframe['Network_Type'].str.upper()).astype(str)
    dataframe.sort_values(by=['Name'])
 
    return dataframe

def Create_Profiles_df(dataframe):
    dataframe = pd.read_csv("Profiles_Data.csv", encoding='utf-8', keep_default_na = False)
    list_2_trim_Profiles = [ 'Company',	'Flag',	'Deployment','Country', 'Business Model']
    dataframe =trim_text_df(dataframe, list_2_trim_Profiles)
    dataframe["Network_Type"] = dataframe['Business Model'].map(network_type_dict)
    dataframe['id'] = dataframe.index
    dataframe['key'] = (dataframe['Deployment'].str.upper()).astype(str) + '_' + (dataframe['Network_Type'].str.upper()).astype(str)
    dataframe = dataframe.sort_values(by=['Deployment'])

    return dataframe

def filter_profiles(df_NaaS_Tracker, df_Profiles, column_key):
    df_filtered =pd.DataFrame()
    list_2_filter = df_NaaS_Tracker[column_key].tolist()
    df_filtered = df_Profiles[df_Profiles[column_key].isin(list_2_filter)]
    df_filtered = df_filtered[['Deployment', 'id']]
    df_filtered.columns = ['NaaSCo Profiles','id']

    return df_filtered

def unique_values_list(dataframe, column):
   unique_list = dataframe[column].unique()
   unique_list.sort()
   return(unique_list)

def summary(dataframe):

   deployments = dataframe['Name'].count()
   countries = len(unique_values_list(dataframe, 'Country'))
   companies = len(unique_values_list(dataframe, 'Name'))

   return [countries, companies, deployments]

def scenario_filter(dataframe):
    key1 = "Rural"
    key2 = "Urban"
    key3 = "Rural & Urban"
    column = "Deployment Scenario"
    df_rural_urban = dataframe.loc[(dataframe[column].str.contains(key1, case=False)) & ( dataframe[column].str.contains(key2, case=False))]
    df_urban = dataframe[~dataframe[column].str.contains(key1, case=False)] 
    df_rural = dataframe[~dataframe[column].str.contains(key2, case=False)] 

    df_Scenarios = pd.DataFrame()
    df_Scenarios['Number of Deployments'] = [len(df_rural), len(df_urban), len(df_rural_urban)]
    df_Scenarios['Scenario'] = [key1, key2, key3]
    
    return df_Scenarios

def sharing_architecture_filter(dataframe, sharing_dict, column):
    df_temp = pd.DataFrame()
    new_df = pd.DataFrame()
    values = []
    for i in sharing_dict:
       df_temp = dataframe[dataframe[column].str.contains(i, case=False)]
       values.append(len(df_temp))
    new_df ['Number of Deployments'] = values
    new_df [column] = sharing_dict.keys()
    new_df ['Arch_Wrap_Text'] = sharing_archi_wrapText_dict.values()

    return new_df

def deployment_list_filter(dataframe, chart_list):
    column_BM = 'Business Model'
    column_R = 'Region'
    deployments_list = []
   
    df_temp = dataframe[[column_BM, column_R]]
    df_chart = df_temp.value_counts().reset_index()
    df_chart.columns = [column_BM, column_R, 'Number of Deployments']
    deployments_list =  df_chart[column_R].tolist()
    missing_regions = list(set(chart_list) - set(deployments_list))
   
    if len(missing_regions) > 0 :
        missing_values =  [0] * len(missing_regions)
        #print('missing zeros',missing_values)
        dummy_BM = BM_List[:len(missing_regions)]
        #print('missing ', dummy_BM)
        missing_zipped = list( zip(dummy_BM, missing_regions, missing_values))
        missing_df = pd.DataFrame(missing_zipped)
        missing_df.columns = [column_BM, column_R, 'Number of Deployments']

        df_chart = df_chart.append(missing_df)
    
    df_chart = df_chart.sort_values(column_R)

    return df_chart 

def create_img(block_img):
    if block_img[0] == '':
        x = ''
        rurt = x
    else:
        x = block_img[0].split("/")
        x = x[2].upper()
        x = x.replace("_", " ")
        x = x.replace(".PNG", "")
        if x == 'RURAL':
            x = 'Rural'
        if x == 'LOW URBAN':
            x = 'Low-ARPU Urban'
        if x == 'HIGH URBAN':
            x = 'High-ARPU Urban'
        if x == 'ULTRA RURAL':
            x = 'Ultra Rural'
        rurt = x
    return rurt

def create_img_1(block_img):
    if block_img[1] == '':
        x = ''
        rurt = x
    else:
        x = block_img[1].split("/")
        x = x[2].upper()
        x = x.replace("_", " ")
        x = x.replace(".PNG", "")
        if x == 'RURAL':
            x = 'Rural'
        if x == 'LOW URBAN':
            x = 'Low-ARPU Urban'
        if x == 'HIGH URBAN':
            x = 'High-ARPU Urban'
        if x == 'ULTRA RURAL':
            x = 'Ultra Rural'
        rurt = x
    return rurt
def create_img_2(block_img):
    if block_img[2] == '':
        x = ''
        rurt = x
    else:
        x = block_img[2].split("/")
        x = x[2].upper()
        x = x.replace("_", " ")
        x = x.replace(".PNG", "")
        if x == 'RURAL':
            x = 'Rural'
        if x == 'LOW URBAN':
            x = 'Low-ARPU Urban'
        if x == 'HIGH URBAN':
            x = 'High-ARPU Urban'
        if x == 'ULTRA RURAL':
            x = 'Ultra Rural'
        rurt = x
    return rurt

def create_img_3(block_img):
    if block_img[3] == '':
        x = ''
        rurt = x
    else:
        x = block_img[3].split("/")
        x = x[2].upper()
        x = x.replace("_", " ")
        x = x.replace(".PNG", "")
        if x == 'RURAL':
            x = 'Rural'
        if x == 'LOW URBAN':
            x = 'Low-ARPU Urban'
        if x == 'HIGH URBAN':
            x = 'High-ARPU Urban'
        if x == 'ULTRA RURAL':
            x = 'Ultra Rural'
        print(x)
        rurt = x
    return rurt

def create_bullets(s_text):
    bullets = []

    if len(s_text) > 0:
        for i in s_text.splitlines( ):
            bullets.append(html.Li(i))
    
    return bullets

def create_bullets_2(s_text):
    bullets = []
    
    if len(s_text) > 0:
        for i in s_text.splitlines( ):
            #bullets.append(html.Li(i))
            if "&&" in i:
                x = i.replace("&&", "")
                bullets.append(html.Ul(html.Li(x)))
            else:
                bullets.append(html.Li(i))
                #break
    
    return bullets

def create_deployment_list_axis(r_list, bm_list):

    axis_list = []
    temp = []

    for i in r_list:
        for x in bm_list:
            temp.append(i + '_' + x)
    axis_list = temp + axis_list

    return axis_list

def deployment_scenario(str_scenario, str_path):
    list_img = []

    str_scenario = str_scenario.replace('Ultra-Rural', 'key_string')

    for i in scenario_img_dict:
        if i in str_scenario:
            list_img.append(str_path + scenario_img_dict[i])

    if len(list_img)< 4:
        for i in range(4-len(list_img)):
            list_img.append('')

    #print(list_img)        

    return list_img

def fill_countries(dataframe):

    all_countries = []
    filtered = []

    df_GAPMINDER['iso_alpha'] = df_GAPMINDER['iso_alpha'].str.rstrip()
    df_GAPMINDER['iso_alpha'] = df_GAPMINDER['iso_alpha'].str.lstrip()

    all_countries = df_GAPMINDER['iso_alpha'].tolist()
    #print('Gapminder',len(all_countries ))
    #print(all_countries)
    
    filtered = dataframe['Id'].tolist()
    #print('Plot', len(filtered))
    #print(filtered)

    missing_countries = list(set(all_countries) - set(filtered))

    print('len missinf :',len(missing_countries))

    if len(missing_countries) > 0 :
        missing_values =  [0] * len(missing_countries)
        missing_zipped = list( zip(missing_countries, missing_values))
        missing_df = pd.DataFrame(missing_zipped)
        missing_df.columns = ['Id', 'Number of Deployments']
        dataframe = dataframe.append(missing_df)

    #print(missing_df)
        
    return dataframe



BM_Mobile_List = [ 'Mobile OAN' , 'Independent Mobile NaaSCo']
BM_Fixed_List = ['Fixed OAN', 'Independent Fixed NaaSCo']
Tech_List = ['2G', '3G', '4G', '5G']
Arch_Mobile_List = ['Active Sharing', 'MNO/MVNO Wholesale']
Arch_Fixed_List = ['Dark Fiber Leasing', 'FTTH wholesale','IP/Ethernet Services', 'Wavelength Service']

General = pd.DataFrame()

Tracker_df = pd.DataFrame()
Tracker_df = Create_Tracker_df(Tracker_df)
Profiles_df = pd.DataFrame()
Profiles_df = Create_Profiles_df(Profiles_df)


#df_GAPMINDER = px.data.gapminder().query("year==2007")
df_GAPMINDER = px.data.gapminder()

column ="Region"
Region_List = unique_values_list(Tracker_df,column)
BM_List = BM_Mobile_List + BM_Fixed_List

axis_list = create_deployment_list_axis(Region_List, BM_List)



modal = html.Div(
    [
        dbc.Modal([  
                dbc.ModalBody(
                    dbc.Form(
                        [                                            
                            html.Div(className="modal-content", children=[
                                html.Div(className="modal-body", children=[
                                    html.H4( className="title-results", id = 'modal_name' , children = []),
                                    html.Div(className="logo-info-section", children=[
                                        html.Div(className="img-peq-container", children=[
                                            html.Img( id ='modal_logo',
                                                className="img-cover"
                                            )
                                        ]),
                                        html.Div(className="info-container", children=[
                                        html.Div(className="info-container-point", children=[
                                            html.Div(className="flex info-container-point-title", children=[
                                                html.Img(
                                                    src=r'assets/dashboard_icons/geography.png',
                                                    className="info-container-point-title-img"
                                                    #alt="map"
                                                ),
                                                html.P(children = 'Geography')
                                            ]),
                                            html.Div(className="info-container-point-blue-container", children=[
                                                html.Div(className="flex", children=[
                                                    html.P(className ='top-bar-text', id = 'modal_country', children =[]),
                                                    html.Div(className="flag-img-container", children=[
                                                        html.Img( id = 'modal_flag',
                                                            className="flag"
                                                        )
                                                    ])
                                                ])
                                            ])
                                        ]),
                                        html.Div(className="info-container-point", children=[
                                            html.Div(className="flex info-container-point-title", children=[
                                                html.Img(
                                                    src=r'assets/dashboard_icons/mnos.png',
                                                    className="info-container-point-title-img"
                                                ),
                                                html.P(children = 'MNOs Other Operators')
                                            ]),
                                            html.Div(className="info-container-point-blue-container", children=[
                                                html.P(className ='top-bar-text', id = 'modal_mnos', children = [])
                                            ])
                                        ]),
                                        html.Div(className="info-container-point", children=[
                                            html.Div(className="flex info-container-point-title", children=[
                                                html.Img(
                                                    src=r'assets/dashboard_icons/Sharing_Model.png',
                                                    className="info-container-point-title-img"
                                                ),
                                                html.P(children = 'Sharing Architecture')
                                            ]),
                                            html.Div(className="info-container-point-blue-container", children=[
                                                html.P( className ='top-bar-text', id = 'modal_SM', children = [])
                                            ])
                                        ]),
                                        html.Div(className="info-container-point", children=[
                                            html.Div(className="flex info-container-point-title", children=[
                                                html.Img(
                                                    src=r'assets/dashboard_icons/Business_Model.png',
                                                    className="info-container-point-title-img"
                                                    #alt="map"
                                                ),
                                                html.P(children = 'Business Model')
                                            ]),
                                            html.Div(className="info-container-point-blue-container", children=[
                                                html.P(className ='top-bar-text', id = 'modal_BM', children = [])
                                            ])
                                        ]),
                                    ]),
                                    ]),
                                    html.Div(className="scope-highlights-container", children=[
                                        html.Div(className="scope-container", children=[
                                            html.H2( className="scope-title", children = 'Scope'),
                                            html.Div(className="scope", children=[
                                                html.Div(className="scope-inner", children=[
                                                    html.Ul(className="ul-iconos", id = 'modal_scope', children=[  
                                                        #html.Li(id = 'modal_scope',children = [])
                                                    ]),
                                                    html.Div(className="scope-img-container", children=[
                                                        html.Div(className="scope-img-inner-container", children=[
                                                            html.Div(className="scope-img-wrapper", children=[
                                                                html.Img( id = 'modal_rural',
                                                                    className="scope-img"
                                                                )
                                                            ]),
                                                            html.P( id ='legend_rural', children = [])
                                                        ]),
                                                        html.Div(className="scope-img-inner-container", children=[
                                                            html.Div(className="scope-img-wrapper", children=[
                                                                html.Img(id = 'modal_ultra_rural',
                                                                    className="scope-img"
                                                                )
                                                            ]),
                                                            html.P( id ='legend_rural_2', children = [])
                                                        ]),
                                                        html.Div(className="scope-img-inner-container", children=[
                                                            html.Div(className="scope-img-wrapper", children=[
                                                                html.Img(id = 'modal_low_urban',
                                                                    className="scope-img"
                                                                )
                                                            ]),
                                                            html.P( id ='legend_rural_3', children = [])
                                                        ]),
                                                        html.Div(className="scope-img-inner-container", children=[
                                                            html.Div(className="scope-img-wrapper", children=[
                                                                html.Img(id ='modal_high_urban',
                                                                    className="scope-img"
                                                                )
                                                            ]),
                                                            html.P( id ='legend_rural_4', children = [])
                                                        ])
                                                    ])
                                                ])
                                            ]),
                                            html.Div(className="active-date-container", children=[
                                                html.Div(className="flex", children=[
                                                    html.Div(className="active-date-container-blue", children=[
                                                        html.P(children = 'Status')
                                                    ]),
                                                    html.Div(className="active-date-container-grey", children=[
                                                        html.P(id ='modal_status', children = [])
                                                    ])
                                                ]),
                                                html.Div(className="flex", children=[
                                                    html.Div(className="active-date-container-blue", children=[
                                                        html.P(children = 'Year')
                                                       # html.Img(
                                                       #     src=r'assets/dashboard_icons/year.png',
                                                       #     className="date-icon"
                                                       #     #alt="map"
                                                       #)                                                                
                                                    ]),
                                                    html.Div(className="active-date-container-grey", children=[
                                                        html.P(id ='modal_year' ,children = [])
                                                    ])
                                                ])
                                            ])
                                        ]),
                                        html.Div(className="highlights-container", children=[
                                        html.H2( className="highlights-title", children = 'Highlights'),
                                        html.Div(className="highlights", children=[
                                                html.Ul(className="ul-iconos", children=[
                                                    html.Li( id = 'modal_highlights', children = []),
                                                ]),
                                        ])
                                    ])
                                ]),
                                ])
                            ]),
                        ],
                    )
                )               

        ],
            id="modal",
            is_open=False,    # True, False
            size="xl",        # "sm", "lg", "xl"
            backdrop=True,    # True, False or Static for modal to not be closed by clicking on backdrop
            scrollable=True,  # False or True if modal has a lot of text
            centered=True,    # True, False
            fade=True         # True, False
        ),
    ]
)

getting_started = html.Div(
        [
           dbc.Modal([  
                dbc.ModalBody(
                    dbc.Form(
                        [                                            
                            html.Div(className="modal-content", children=[
                                html.Div(className="modal-body-2", children=[
                                    html.H4( className="title-results-2", children = 'Getting Started'),
                                    html.Div(className="modal-body-2-inner-container", children=[
                                        html.Div(className="logo-info-section-2", children=[
                                        html.P(className='P_GS', children = 'Welcome to the Global NaaS Tracker! This tool provides an interface to explore a comprehensive data set of NaaS deployments worldwide, enabling ecosystem stakeholders to derive insights and assess the potential for the NaaS business model.')
                                    ]),
                                    html.Br(),
                                        html.Div(className="logo-info-section-2", children=[
                                        html.P(className='P_GS', children = 'The dataset includes mobile and fixed NaaS deployments according to the definitions set forth below:')
                                    ]),
                                    html.Br(),
                                    
                                    html.Div(className="logo-info-section-2", children=[
                                        html.Ul(children = [
                                            html.Li(children = [
                                                html.P(children = [html.B("Mobile NaaSCo")," Neutral Host that builds and manages RAN and transport infrastructure and provides access services under a wholesale arrangement to MNOs or MVNOs:"]),
                                                
                                                html.Ul(children = [
                                                    html.Li(children = [
                                                        html.P(children = [html.B("Independent Mobile NaaSCo.")," Third-party company, independent from the government that implements the Mobile NaaS model."]),
                                                    ]),
                                                    html.Li(children = [
                                                        html.P(children = [html.B("Mobile Open Access Network (OAN).")," Neutral host entity created, funded, or supported by the government, that operates with regulatory and/or governmental conditions/stipulations, including openness and non-discriminatory pricing. "]),
                                                    ])
                                                ]),
                                            ]),
                                            html.Br(),
                                            html.Li(children = [
                                                html.P(className='P_GS', children = [html.B("Fixed NaaSCo")," Neutral Host that builds and manages access and transport infrastructure with the primary objective to provide access and transport services under a wholesale arrangement to fixed or mobile Service Providers"]),
                                                
                                                html.Ul(children = [
                                                    html.Li(children = [
                                                        html.P(children = [html.B("Independent Fixed NaaSCo.")," Third-party company, independent from the government that implements the Fixed NaaS model."]),
                                                    ]),
                                                    html.Li(children = [
                                                        html.P(className='P_GS', children = [html.B("Fixed Open Access Network (OAN).")," Neutral host entity that operates under a government agreement or concession that defines its business structure, including buildout schedule and pricing structure. "]),
                                                    ])
                                                ]),
                                            ])
                                        ])
                                    ]),
                                    html.Br(),
                                                                        html.Div(className="logo-info-section-2", children=[
                                        html.B(children = 'How to use the tracker?')
                                    ]),
                                                                        html.Div(className="logo-info-section-2", children=[
                                        html.P(className='P_GS', children = 'The dashboard consists of a statistics panel, a heatmap, a chart section, and a list of NaaSCo Profiles. These elements are updated based on the filters applied in the heatmap and chart sections.')
                                    ]),
                                    html.Br(),
                                                                        html.Div(className="logo-info-section-2", children=[
                                        html.P(className='P_GS',children = 'By clicking on a country in the map the results are further filtered for that country.')
                                    ]),
                                    html.Br(),
                                    ]),
                                    html.Br(),
                                ])
                            ]),
                        ],
                    )
                )               

        ],
            id="getting_started",
            is_open=False,    # True, False
            size="xl",        # "sm", "lg", "xl"
            backdrop=True,    # True, False or Static for modal to not be closed by clicking on backdrop
            scrollable=True,  # False or True if modal has a lot of text
            centered=True,    # True, False
            fade=True         # True, False
        ),
    ]
)


#######################
external_scripts = [ {'src':"http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"},
                     {'src':"jquery.fittext.js"}
                    ]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],external_scripts=external_scripts)
#app = Dash(__name__)
#BS = "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
#app = Dash(__name__, external_stylesheets=[BS])

######################
app.config.suppress_callback_exceptions=True

app.layout =  html.Main(className="dashboard", children=[
      html.Div( className="dashboard-container", children=[
        html.Section( className="section-1", children=[
          html.Div( className="logo-container", children=[
            html.Img( src=r'assets/dashboard_icons/TIP_logo.png', className="logo")
          ]), #logo-container
          html.Div(className = "instructions-container", children = [
                html.Button('Getting Started', id='button_start', n_clicks=0)
                  ]),#instructions-container
          html.Div( className="insert deployment-list-container", children=[
          html.Div(className="list-container", id="Deployment_List", children=[ 
          ], style = {'height': '100%', 'overflowY': 'auto'})#insert-inner
          ]) #insert deployment-list-container
        ]), #section-1
        html.Section( className="section-2", children=[
          html.Div( className="center-top-section", children=[
            html.Div( className = "section-2-title", children = 'Statistics'),
                html.Div( className = "section-2-items-container", children = [
                    html.Div( className="center-top-section-item", children=[
              html.Div( className="center-top-section-item-title", children=[
                html.Img(
                  src=r'assets/dashboard_icons/Countries.png',
                  className="center-top-section-item-title-image"
              ),
                html.H3( className="center-top-section-item-title-text", children = 'Countries')
              ]), #center-top-section-item-title
              html.Div( className="center-top-section-item-content", id = 'n_countries', children = [])
            ]),#center-top-section-item
            html.Div( className="center-top-section-item", children=[
              html.Div( className="center-top-section-item-title", children=[
                html.Img(
                  src=r'assets/dashboard_icons/Companies.png',
                  className="center-top-section-item-title-image"
                ),
                html.H3( className="center-top-section-item-title-text", children = 'Companies')
              ]), #center-top-section-item-title
              html.Div( className="center-top-section-item-content", id = 'n_companies', children = [])
            ]), #center-top-section-item
            html.Div( className="center-top-section-item", children=[
              html.Div( className="center-top-section-item-title", children=[
                html.Img(
                  src=r'assets/dashboard_icons/Deployments.png',
                  className="center-top-section-item-title-image"
                ),
                html.H3( className="center-top-section-item-title-text", children = 'Deployments')
              ]), #center-top-section-item-title
              html.Div( className="center-top-section-item-content", id ='n_deployments', children = [])
            ]) #center-top-section-item-title                
            ])#className = "section-2-items-container
          ]), #center-top-section
          html.Div( className="center-bottom-section", children=[
           html.Div( className="map-select-container", children = [
                dcc.Store(id='store-data', data=[], storage_type='memory'),
                    html.Div(className='map-dropdown-style', id = 'BM_Container', children=[
                        dcc.Dropdown(BM_Mobile_List + BM_Fixed_List, id='Business_Model_Dropdown',
                        value = '',
                        multi=False,
                        clearable=False,
                        placeholder="Business Model..."
                        )]),
                html.Div(className='map-dropdown-style', id = 'Arch_Container', children = [  
                        dcc.Dropdown(id='Architecture_Dropdown',
                        value = '',
                        multi=False,
                        clearable=False,
                        placeholder="Architecture..."
                        )], style= {'visibility': 'hidden'}), 
                html.Div(className='map-dropdown-style', id ='Tech_Container', children = [ 
                        dcc.Dropdown(id='Technology_Dropdown',
                        value = '',
                        multi=False,
                        clearable=False,
                        placeholder="Technology"
                        )], style = {'visibility': 'hidden'})
            ]),#map-select-container"
            html.Div( className="map_Section", children = [
            html.Div(dcc.Tabs(id='Map_Tabs', value='All', children=[
                           dcc.Tab(label='All', value='All'),
                           dcc.Tab(label='Mobile', value='Mobile'),
                           dcc.Tab(label='Fixed', value='Fixed')
                         ])),
            html.Div(className = "container-Map",children =[dcc.Graph(id='HeatMap',style={'width': '100%', 'height':'100%'} )]),
          ])#map  
          ]) #center-bottom-section
        ]), #section-2
        html.Section( className="section-3", children=[
          html.Div( className="right-top-section", children=[
            html.Div( className="global-region-radius-button-container", children=[
              html.Div( className="chart-select-container", children=[
                html.Div([
                            dcc.RadioItems(className = "label-radio-button", options = ['Global', 'Region'], id = 'Region_Charts_Radio',
                            value='Global')]),  
                        html.Div(className = "label-dropdown-region",children =[dcc.Dropdown(Region_List, id='Region_Charts_Dropdown',
                                    value = '',
                                    multi=False,
                                    clearable=False,
                                    placeholder="Select a Region..."
                                    )],style = {'width': '50%','visibility': 'hidden'})
              ])
            ]), #global-region-radius-button-container
            html.Div( className="insert deployments", children=[
              html.Div( className="deployments-title-container", children = 'Deployments'),
              html.Div( className="deployment-content", children=[
                html.Div( className="insert-inner", children =[
                  dcc.Graph(id="Deployment_List_Bar_Chart", figure={}, style={'width': '100%', 'height': '100%'})
                ])
              ]) #deployment-content
            ]) #insert deployments
          ]), #right-top-section
          html.Div( className="right-bottom-section", children=[
            html.Div( className="right-bottom-section-half-container-1", children=[
              html.Div( className="right-bottom-section-half-container-title", children=[
                html.P(className="right-bottom-section-half-container-title-text",
                  children ='Deployment Scenario'
                )
              ]),#right-bottom-section-half-container-title
              html.Div( className="right-bottom-section-half-container-content", children=[
                      dcc.Graph(id="Deployment_Scenario_Pie_Chart", figure={},style={'width': '100%','height':'100%'})
              ])
            ]),#right-bottom-section-half-container
            html.Div( className="right-bottom-section-half-container-2", children=[
              html.Div( className="right-bottom-section-half-container-title", children=[
                html.P( className="right-bottom-section-half-container-title-text",
                  children = 'Network Sharing Architecture'
                )
              ]),
              html.Div(className="right-bottom-section-half-container-content", children=[
                      dcc.Graph(id="Sharing_Model_Architecture_Bar_Chart", figure={},style={'width': '100%', 'height':'100%'})
              ])
            ])#right-bottom-section-half-container
          ])#right-bottom-section
        ]) #section-3
      ]), ##dashboard-container
     modal,
     getting_started
    ]) ## Main

@app.callback(Output('Business_Model_Dropdown', 'options'),
              Output('Architecture_Dropdown', 'options'),
              Output('Technology_Dropdown', 'options'),
              Output('Arch_Container', 'style'),
              Output('Tech_Container', 'style'),
              Input('Map_Tabs', 'value'),
              Input('Business_Model_Dropdown', 'value')
              )

def Define_Dropdown(tab, BM_value):

    Tech_visibility = 'hidden'
    Arch_visibility = 'hidden'
    Arch_options = Arch_Mobile_List + Arch_Fixed_List 
    BM_options = BM_Mobile_List + BM_Fixed_List
    Tech_options = Tech_List

    if tab == 'All' and BM_value =='':
       Tech_visibility = 'hidden'
       Arch_visibility = 'hidden'

    if  tab =='All' and BM_value in BM_Mobile_List:
        Arch_options = Arch_Mobile_List
        Tech_visibility = 'visible'
        Arch_visibility = 'visible'

    if  tab =='All' and BM_value in BM_Fixed_List:
        Arch_options = Arch_Fixed_List
        Arch_visibility = 'visible'
        Tech_visibility = 'hidden'

    if tab == 'Mobile':
       BM_options =  BM_Mobile_List
       Arch_options =  Arch_Mobile_List
       Tech_options =  Tech_List
       Tech_visibility = 'visible'
       Arch_visibility = 'Visible'
    
    if tab == 'Fixed':
       BM_options = BM_Fixed_List 
       Arch_options = Arch_Fixed_List
       Tech_visibility = 'hidden'
       Arch_visibility = 'visible'

    return BM_options, Arch_options, Tech_options, {'visibility': Arch_visibility}, {'visibility': Tech_visibility}

@app.callback(
              Output('store-data', 'data'),
              Output('Region_Charts_Dropdown','style'),
              Input('Map_Tabs', 'value'), 
              Input('Business_Model_Dropdown', 'value'),
              Input('Architecture_Dropdown', 'value'),
              Input('Technology_Dropdown', 'value'),
              Input('Region_Charts_Radio', 'value'),
              Input('Region_Charts_Dropdown', 'value')
              )

def store_data(tab, BM_v, Arch_v, Tech_v, RadioButton_v, Region_v):
     
    HeatMap_df = Tracker_df.copy()
    Dropdown_visibility = 'hidden'

    if tab != 'All':
        HeatMap_df = HeatMap_df[Tracker_df['Network_Type'] == tab]
        
    if BM_v != '':
        HeatMap_df = HeatMap_df[Tracker_df['Business Model'] == BM_v]

    if Arch_v != '':
        HeatMap_df = HeatMap_df[HeatMap_df['Network Sharing Architecture'].str.contains(Arch_v, case=False)]

    if Tech_v != '':
        HeatMap_df = HeatMap_df[HeatMap_df['Network Technology'].str.contains(Tech_v, case=False)]

    if RadioButton_v != 'Global':
        Dropdown_visibility = 'visible'

    if Region_v != '':
       HeatMap_df = HeatMap_df[HeatMap_df["Region"] == Region_v]
    
    
    return HeatMap_df.to_dict('records'), {'visibility': Dropdown_visibility}


@app.callback(Output('HeatMap', 'figure'),
              Input('store-data', 'data'))


def HeatMap_content(dataframe):

    Filtered_df = pd.DataFrame(dataframe)

    Plot_df = pd.DataFrame()
    Plot_df['Id'] = 0
    Plot_df['Number of Deployments'] = 0
    max_value = 20

    if len(dataframe) != 0:
        Plot_df = pd.DataFrame({'Id':Filtered_df['ISO_3166'].value_counts().index,'Number of Deployments':Filtered_df['ISO_3166'].value_counts().values,'Country':Filtered_df['Country'].value_counts().index,'Deploys':Filtered_df['ISO_3166'].value_counts().index})
        max_value = Plot_df ['Number of Deployments'].max()

    #Plot_df = fill_countries(Plot_df)

    #print(df_GAPMINDER)
    #df_GAPMINDER.to_csv('df_GAPMINDER.csv')
    #print(Filtered_df)
    Plot_df['points_duplicate'] = Plot_df.loc[:, 'Number of Deployments']
    Plot_df['points_duplicate'] = Plot_df['points_duplicate'].apply(str)
        
    fig = px.choropleth(df_GAPMINDER, locations = Plot_df['Id'], color = Plot_df['Number of Deployments'],
                           color_continuous_scale = ["#c1dc7f", "#29818c", "#19666e"],
                           #hover_data=Plot_df['country'],
                           range_color=(1, max_value) 
                        )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0,'pad':0},
                      #coloraxis_showscale=False,
                      font= font_dic,
                      autosize=True,
                      #hovermode='closest',
                      legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=1.5,
                        xanchor="center",
                        x=0.5,
                        ),
                        #hoverlabel = hoverlabel_dict,
                      coloraxis_colorbar = coloraxis_colorbar_dict
                     )

    #fig.update_traces(hovertemplate = Plot_df['points_duplicate'])
    # I created my own hover template for on hover event
    hovertemp = '<i style="color:#3ba9b6;"><b>Country: </b></i><b style="color:#98c035;">' + Plot_df['Country'] + '</b><br>'
    hovertemp += '<i style="color:#3ba9b6;"><b>Number of Deployments: </b></i><b style="color:#98c035;">' + Plot_df['points_duplicate'] + '</b><br>'
    fig.update_traces(hovertemplate=hovertemp)
    #fig.update_traces(hovertemplate= 'Country: ' + Plot_df['Country'] + '\n'+' -- No of Deployments: ' + Plot_df['points_duplicate'])  
    
    fig.update_geos(showcountries = True, 
                    countrycolor = '#c2c2c2',
                    fitbounds="locations", visible=False        
                    )

    return fig

@app.callback(Output('Business_Model_Dropdown', 'value'),
              Output('Architecture_Dropdown', 'value'),
              Output('Technology_Dropdown', 'value'),
              Input('Map_Tabs', 'value')
              )

def erase_content(tab):
    BM_value = ''
    Arch_value = ''
    Tech_value =''

    return BM_value, Arch_value, Tech_value

@app.callback(
              Output('Region_Charts_Dropdown', 'value'),
              Input('Region_Charts_Radio', 'value'))

def erase_content2(radio_button):
    
    region_dropdown = ''

    return region_dropdown


@app.callback(Output('modal', 'is_open'),
              Output('modal_name', 'children'),
              Output('modal_country', 'children'),
              Output('modal_mnos', 'children'),
              Output('modal_SM', 'children'),
              Output('modal_BM', 'children'),
              Output('modal_highlights', 'children'),
              Output('modal_status', 'children'),
              Output('modal_year', 'children'),
              Output('modal_logo', 'src'),
              Output('modal_flag', 'src'),
              Output('modal_rural', 'src'),
              Output('modal_ultra_rural', 'src'),
              Output('modal_low_urban', 'src'),
              Output('modal_high_urban', 'src'),
              Output('modal_scope', 'children'),
              Output('legend_rural', 'children'),
              Output('legend_rural_2', 'children'),
              Output('legend_rural_3', 'children'),
              Output('legend_rural_4', 'children'),
              Input('Table', 'active_cell'))
             
def show_profile(active_cell):

    path_logo = 'assets/company_logo/'
    path_flag = 'assets/flags/'
    logo_enviroments = 'assets/dashboard_icons/'

    if active_cell is None:
      raise PreventUpdate
    else:
      row = active_cell['row_id']
     
      profile_name = Profiles_df.at[row,'Deployment'] 
      profile_country = Profiles_df.at[row,'Country'] 
      profile_mnos = Profiles_df.at[row,'Mnos'] 
      profile_SM = Profiles_df.at[row,'Sharing Model'] 
      profile_BM = Profiles_df.at[row,'Business Model'] 
      scope = Profiles_df.at[row,'Scope']
      highlights = Profiles_df.at[row,'Highlights']
      profile_year = Profiles_df.at[row,'Year']
      profile_status = Profiles_df.at[row,'Status']
      profile_scenario = Profiles_df.at[row,'Deployment Scenario']

      img_logo = path_logo + Profiles_df.at[row,'Company'] + '.png'
      img_flag = path_flag + Profiles_df.at[row,'Flag'] + '.png'

      block_img = deployment_scenario(profile_scenario, logo_enviroments)
      #print(block_img)

      profile_scope = create_bullets(scope)
      profile_highlights = create_bullets_2(highlights) 
      img_a = create_img(block_img)
      img_b = create_img_1(block_img)
      img_c = create_img_2(block_img)
      img_d = create_img_3(block_img)

      if not os.path.isfile(img_flag):
        img_flag = ''

      if not os.path.isfile(img_logo):
        img_logo = ''


      img_rural =  block_img[0]
      img_ultra_rural =  block_img[1]
      img_low_urban =  block_img[2]
      img_high_urban =  block_img[3]
     
      return True, profile_name, profile_country, profile_mnos, profile_SM, profile_BM, profile_highlights, profile_status, profile_year, img_logo, img_flag, img_rural, img_ultra_rural, img_low_urban, img_high_urban, profile_scope, img_a, img_b, img_c, img_d

@app.callback(Output('getting_started', 'is_open'),
              Input('button_start', 'n_clicks'))

def modal_getting_started(n):
    if n:
        return True


@app.callback(
    Output('Deployment_List_Bar_Chart','figure'),
    Output('Deployment_Scenario_Pie_Chart','figure'),
    Output('Sharing_Model_Architecture_Bar_Chart','figure'),
    Output('Deployment_List', 'children'),
    Output('n_countries', 'children'),
    Output('n_companies', 'children'),
    Output('n_deployments', 'children'),
    Input('store-data', 'data'),
)

def update_informative_chart(data): 
    column = 'Network Sharing Architecture'
    Deployment_df = pd.DataFrame(data)
    Deployment_Scenario_df = pd.DataFrame()
    Sharing_Architecture_df = pd.DataFrame()

    num_countries = 0
    num_companies = 0
    num_deployments = 0

    if len(Deployment_df) != 0:

        Deployment_List_df = deployment_list_filter(Deployment_df, Region_List)
        Deployment_Scenario_df = scenario_filter(Deployment_df)
        Sharing_Architecture_df = sharing_architecture_filter(Deployment_df, sharing_architectures_dict, column)

        
        Deployment_List_fig = px.bar(Deployment_List_df, y ='Region', x ='Number of Deployments',
                                     color='Business Model',
                                     #text = 'Number of Deployments',
                                     hover_data ={'Region': False, 'Business Model':False},
                                     color_discrete_map = color_deployments_dict,
                                     )
        Deployment_Scenario_fig = px.pie(Deployment_Scenario_df, values='Number of Deployments', hole=0.5, names='Scenario', color ='Scenario', color_discrete_map = color_scenario_dict)
        Sharing_Architecture_fig = px.bar(Sharing_Architecture_df, y = 'Arch_Wrap_Text', x ='Number of Deployments', 
                                      color = column, 
                                      color_discrete_map = color_arch_dict,
                                      text = 'Number of Deployments',
                                      hover_data ={'Arch_Wrap_Text': False})
  
        summary_list = summary(Deployment_df)
        num_countries =  summary_list[0]
        num_companies = summary_list[1]
        num_deployments = summary_list[2]


        data_table = filter_profiles(Deployment_df, Profiles_df, 'key')


        Deployment_Table = dash_table.DataTable(
                id = 'Table',
                data = data_table.to_dict('records'),
                columns=[{"name": c, "id": c} for c in data_table.columns if c != 'id'],
                page_action='none',
                #style_table={'height': '250px', 'width': '100%', 'overflowY': 'auto'},
                style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                },
                editable = False,
                style_cell={'textAlign': 'left',
                             'fontSize':12, 
                             'font-family':'Montserrat',
                },
                style_header = {'background-color': '#19666e',
                                'fontSize':15, 
                                'color':'white',
                                'font-family':'Montserrat',
                                'text-align': 'center'
                             }
                     )

        Deployment_List_fig.update_layout( font_family='Montserrat' ,
                                       font_size = 9,
                                       legend_font_size = 8,
                                       legend_title="",
                                       legend=dict(
                                       orientation="h",
                                       yanchor="top",
                                       y=1.5,
                                       xanchor="center",
                                       x=0.5,
                                        ),
                                        margin=dict(t=5,r=5,b=5,l=5),
                                        hoverlabel = hoverlabel_dict,
                                       )
        #Deployment_List_fig.update_traces(hovertemplate='Number of Deployments: %{x}') 
        Deployment_List_fig.update_yaxes(title=None)
        Deployment_List_fig.update_xaxes(title=None)

        Deployment_Scenario_fig.update_layout(font_family='Montserrat' ,
                                       font_size = 9,
                                       legend_font_size = 8,
                                       legend_title="",
                                       legend=dict(
                                        orientation="h",
                                        #yanchor="top",
                                        y=1.5,
                                        #xanchor="left",
                                        x= 0
                                        ),
                                        hovermode = False,
                                        margin=dict(t=5,r=5,b=5,l=5),
                                        legend_itemsizing = 'constant',
                                        legend_tracegroupgap = 3)

        Deployment_Scenario_fig.update_traces(insidetextfont_color='white', textinfo='value', selector=dict(type='pie'))
        Deployment_Scenario_fig.update_yaxes(title=None)
        Deployment_Scenario_fig.update_xaxes(title=None)
    
        Sharing_Architecture_fig.update_layout(font_family='Montserrat' ,
                                       font_size = 8,
                                       legend_title="",
                                       showlegend=False, 
                                       margin=dict(t=5,r=5,b=5,l=5),
                                       hoverlabel = hoverlabel_dict,
                                       hovermode = False
                                       )
        Sharing_Architecture_fig.update_traces(insidetextfont_color='white', hovertemplate='Number of Deployments: %{x}')                               
        Sharing_Architecture_fig.update_yaxes(title=None)
        Sharing_Architecture_fig.update_xaxes(title=None)

    else:
        Deployment_Table = {}
        Deployment_List_fig = annotation_dict
        Deployment_Scenario_fig = annotation_dict
        Sharing_Architecture_fig = annotation_dict

    return Deployment_List_fig, Deployment_Scenario_fig, Sharing_Architecture_fig, Deployment_Table, num_countries, num_companies, num_deployments



if __name__ == '__main__':
    #app.run_server(debug=True, port=5480)
    app.run_server(debug = True)


   