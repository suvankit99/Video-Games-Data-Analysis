import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from geopy.geocoders import Nominatim
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components
from wordcloud import WordCloud
import plotly.graph_objects as go

# Load the dataset for the world map plot
sales_data = pd.read_csv('sales_data.csv')

# Load the dataset for the video game sales dashboard
df = pd.read_csv('vgsales.csv')

st.set_page_config(page_title="Video Games Sales Dashboard", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="expanded")


def display_current_page():
    custom_css = """
    <style>
    .stApp {
        background: linear-gradient(to right, #434343 0%, black 100%);
        color: black;
        h1, h2, h3 {color: white;}
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # Title of the dashboard
    st.title('Video Games Sales Dashboard')
    

    # Sidebar filters
    platform_filter = st.sidebar.selectbox('Filter by Platform', df['Platform'].unique())
    genre_filter = st.sidebar.selectbox('Filter by Genre', df['Genre'].unique())

    # Filter the data based on user input
    filtered_df = df[(df['Platform'] == platform_filter) & (df['Genre'] == genre_filter)]

    # Pie chart for sales distribution
    st.subheader('Sales Distribution Among Regions (Excluding Global Sales)')
    with st.spinner('Generating pie chart...'):
        sales_distribution = filtered_df[['NA_Sales', 'JP_Sales', 'EU_Sales', 'Other_Sales']].sum()

        # Plotting pie chart
        fig = px.pie(sales_distribution, 
                     values=sales_distribution.values, 
                     names=sales_distribution.index, 
                     color_discrete_sequence=["red" , "blue" , "magenta" , "orange"])

        # Customizing the appearance
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(color='black'))
        fig.update_layout(showlegend=False)

        # Show plot
        st.plotly_chart(fig)

    # Dropdown menu to select the type of plot
    plot_type = st.sidebar.selectbox('Select Plot Type', ['Global Sales', 'NA Sales', 'JP Sales', 'EU Sales', 'Other Sales'])

    # Plot function based on selected plot type
    st.subheader(f'{plot_type} of Video Games Over Years')
    with st.spinner(f'Generating {plot_type} plot...'):
        # Determine the column name based on the selected plot type
        if plot_type == 'Global Sales':
            sales_column = 'Global_Sales'
        elif plot_type == 'NA Sales':
            sales_column = 'NA_Sales'
        elif plot_type == 'JP Sales':
            sales_column = 'JP_Sales'
        elif plot_type == 'EU Sales':
            sales_column = 'EU_Sales'
        elif plot_type == 'Other Sales':
            sales_column = 'Other_Sales'

        # Grouping data by year and summing up sales
        sales_data = filtered_df.groupby('Year')[sales_column].sum().reset_index()

        # Create figure
        fig = go.Figure()

        # Add scatter plot (dots)
        fig.add_trace(go.Scatter(x=sales_data['Year'], y=sales_data[sales_column], mode='markers',
                                 name='Dot Plot', marker=dict(color='rgb(255, 102, 102)', size=8)))

        # Add line plot
        # Customizing the appearance
        fig.update_layout(title=f'{plot_type} of Video Games Over Years',
                          xaxis_title='Year', yaxis_title=f'{plot_type} (in millions)',
                          hovermode='x', template='plotly_dark', showlegend = False)  
        # Dark theme
        fig.add_trace(go.Scatter(x=sales_data['Year'], y=sales_data[sales_column], mode='lines',
                                 name='Line Plot', line=dict(color='rgb(102, 178, 255)', width=2)))
        
        # Show plot
        st.plotly_chart(fig)



# Function to display the updates on the second button's page
def display_second_page():
    custom_css = """
    <style>
    .stApp {
        background: linear-gradient(to right, #434343 0%, black 100%);
        color: black;
        h1, h2, h3 {color: white;}
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    
    st.title('Most Popular Genre and Publishers')

    # Sidebar filters
    y_axis_filter = st.sidebar.selectbox('Filter by Y-axis', ['Genre', 'Publisher'])
    x_axis_filter = st.sidebar.selectbox('Filter by X-axis', ['Global_Sales', 'NA_Sales', 'JP_Sales', 'EU_Sales', 'Other_Sales'])

    # Slider for number of items to display
    num_items = st.sidebar.slider('Number of Items to Display', min_value=5, max_value=30, value=15)

    # Filtered data
    if y_axis_filter == 'Genre':
        top_data = df.groupby('Genre')[x_axis_filter].sum().nlargest(num_items)
        title = f'Top {num_items} Genres based on '
    else:
        top_data = df.groupby('Publisher')[x_axis_filter].sum().nlargest(num_items)
        title = f'Top {num_items} Publishers based on '

    # Plotting horizontal bar chart
    fig = px.bar(top_data, 
                 x=x_axis_filter, 
                 y=top_data.index, 
                 orientation='h', 
                 title=title + x_axis_filter,
                 labels={x_axis_filter: x_axis_filter, y_axis_filter: y_axis_filter},
                 color=x_axis_filter,
                 color_continuous_scale=px.colors.sequential.Viridis)
    
    css_str = f"""
        <style>
            .svg-container {{
                background-color: black;
            }}
            
        </style>
        """

# Apply styles using markdown
    st.markdown(css_str, unsafe_allow_html=True)

    # Reverse the order of bars
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))

    # Show plot
    st.plotly_chart(fig)

    st.subheader('Word Cloud of Game Names based on Total Global Sales')
    sales_limit = st.sidebar.slider('Total Global Sales Limit', min_value=df['Global_Sales'].min(), max_value=df['Global_Sales'].max(), value=df['Global_Sales'].max())
    if y_axis_filter == 'Genre':
        filter_value = st.sidebar.selectbox('Select Genre for Word Cloud', df['Genre'].unique())
        wordcloud_data = df[(df['Genre'] == filter_value) & (df['Global_Sales'] >= sales_limit)]['Name'].tolist()
    else:
        filter_value = st.sidebar.selectbox('Select Publisher for Word Cloud', df['Publisher'].unique())
        wordcloud_data = df[(df['Publisher'] == filter_value) & (df['Global_Sales'] >= sales_limit)]['Name'].tolist()

    if not wordcloud_data:
        st.write('No game available as per the specified filters')
        return

    wordcloud_text = ' '.join(wordcloud_data)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(wordcloud_text)
    st.image(wordcloud.to_array())




def display_third_page():
    custom_css = """
    <style>
    .stApp {
        background: linear-gradient(to right, #434343 0%, black 100%);
        color: black;
        h1, h2, h3 {color: white;}
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    
    sales_data = pd.read_csv("sales_data.csv")
    st.title('Sales Distribution Across the Globe')

    # Create a Folium map centered at the average latitude and longitude
    center_lat, center_lon = sales_data['Latitude'].mean(), sales_data['Longitude'].mean()
    mymap = folium.Map(location=[center_lat, center_lon], zoom_start=5)

    # Create a MarkerCluster for better performance with a large number of markers
    marker_cluster = MarkerCluster().add_to(mymap)

    # Add bubbles and popups for each city
    for index, row in sales_data.iterrows():
        popup_text = f"City: {row['City']}<br>Region: {row['Region']}<br>Sales: {row['Sales']}"
        folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=10, color='blue', fill=True, fill_color='blue', popup=folium.Popup(popup_text, max_width=300)).add_to(marker_cluster)

    # Display the map as an HTML component filling the complete screen
    map_html = mymap._repr_html_()

    # Apply CSS styles to remove margins
    css_styles = """
        <style>
            .stMapboxOverlay {
                margin: 0;
                padding: 0;
            }
        </style>
    """

    # Concatenate the CSS styles with the HTML representation of the map
    map_html = css_styles + map_html

    # Display the map with CSS styles applied
    components.html(map_html, height=800, width=1200, scrolling=False)
            


nav_selection = st.sidebar.radio('Navigation', ('Sales Distribution across years', 'Popularity of Games', 'Regional Sales Distribution'))

# Display content based on button selection
if nav_selection == 'Sales Distribution across years':
    display_current_page()
elif nav_selection == 'Popularity of Games':
    display_second_page()
elif nav_selection == 'Regional Sales Distribution':
    display_third_page()