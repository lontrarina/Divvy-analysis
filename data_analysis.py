import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from matplotlib.colors import Normalize
from matplotlib.colors import LinearSegmentedColormap
import folium
from folium import plugins
import random


engine = create_engine('mysql+pymysql://root:@localhost/divvy_db')


def usage_of_rideable_types_by_membership_status():
    query = """
        SELECT 
            rideable_type, 
            member_casual, 
            COUNT(*) AS usage_count
        FROM trip_data
        GROUP BY rideable_type, member_casual;
        """
    data = pd.read_sql(query, engine)

    pivot_table = data.pivot(index='rideable_type', columns='member_casual', values='usage_count')
    pivot_table.plot(kind='bar', figsize=(10, 5))
    plt.title('Usage of Rideable Types by Membership Status')
    plt.ylabel('Usage Count')
    plt.xlabel('Rideable Type')
    plt.xticks(rotation=0)
    plt.legend(title='Member Status')
    plt.show()
    plt.close()


def popular_stations(station_name, IS_start_or_end):
    query = f"""
        SELECT 
            {station_name},
            COUNT(*) AS usage_count
        FROM trip_data
        WHERE {station_name} IS NOT NULL
        GROUP BY {station_name}
        ORDER BY usage_count DESC
        LIMIT 10;
        """
    data = pd.read_sql(query, engine)
    create_gradient_plot(data,'', IS_start_or_end)



def plot_top_stations(member_status, station_name, IS_start_or_end):
    query = f"""
        SELECT 
            {station_name},
            COUNT(*) AS usage_count
        FROM trip_data
        WHERE member_casual = '{member_status}' and {station_name} IS NOT NULL
        GROUP BY {station_name}
        ORDER BY usage_count DESC
        LIMIT 10;
        """
    data = pd.read_sql(query, engine)
    create_gradient_plot(data, member_status, IS_start_or_end)


def create_gradient_plot(data, member_status, IS_start_or_end):
    if IS_start_or_end=='start':
        colors = ["#f1948a", "#cb4335", "#943126"]  #red colors
    else:
        colors = ["#add8e6", "#6495ed", "#4169e1", "#0000ff"] #blue colors

    cmap = LinearSegmentedColormap.from_list("custom_red", colors, N=256)

    norm = Normalize(vmin=data['usage_count'].min(), vmax=data['usage_count'].max())
    colors = [cmap(norm(value)) for value in data['usage_count']]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(data[f'{IS_start_or_end}_station_name'], data['usage_count'], color=colors)
    plt.title(f'Top 10 {IS_start_or_end} Stations for {member_status.title()} Users')
    plt.xlabel('Station Name')

    plt.xticks(rotation=45, ha="right")
    plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
    plt.tight_layout()
    plt.show()
    plt.close()


def popular_stations_on_map(member_status, station_name, latitude, longitude):
    query = f"""
        SELECT 
           {station_name},
           {latitude} as latitude, 
           {longitude} as longitude,   
            COUNT(*) AS usage_count
        FROM trip_data
        WHERE member_casual = '{member_status}' and {station_name} IS NOT NULL
        GROUP BY {station_name}
        ORDER BY usage_count DESC
        LIMIT 10;
        """
    data = pd.read_sql(query, engine)

    m = folium.Map(location=[41.8781, -87.6298], zoom_start=13) #Chicago coordinates

    for _, row in data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=row['usage_count'] / data['usage_count'].max() * 20,
            popup=f"{row[f'{station_name}']}: {row['usage_count']}",
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(m)

    return m

def plot_rides_by_weekday(start_date, end_date):
    query = """
        SELECT 
            DAYOFWEEK(started_at) as day_of_week,
            member_casual,
            COUNT(*) as trip_count
        FROM trip_data
        WHERE started_at BETWEEN %s AND %s
        GROUP BY DAYOFWEEK(started_at), member_casual
        ORDER BY DAYOFWEEK(started_at);
        """
    data = pd.read_sql(query, engine, params=(start_date, end_date))

    days = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
    data['day_of_week'] = data['day_of_week'].map(days)

    member_data = data[data['member_casual'] == 'member']
    casual_data = data[data['member_casual'] == 'casual']

    plt.figure(figsize=(10, 5))
    plt.plot(member_data['day_of_week'], member_data['trip_count'], label='Member')
    plt.plot(casual_data['day_of_week'], casual_data['trip_count'], label='Casual')
    plt.title('Number of Trips by Day of Week')
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.close()


def plot_rides_by_hour_of_day(start_date, end_date):
    query = """
        SELECT 
            HOUR(started_at) as hour_of_day,
            member_casual,
            COUNT(*) as trip_count
        FROM trip_data
        WHERE started_at BETWEEN %s AND %s
        GROUP BY HOUR(started_at), member_casual
        ORDER BY HOUR(started_at);
        """
    data = pd.read_sql(query, engine, params=(start_date, end_date))

    member_data = data[data['member_casual'] == 'member']
    casual_data = data[data['member_casual'] == 'casual']

    plt.figure(figsize=(10, 5))
    plt.plot(member_data['hour_of_day'], member_data['trip_count'], label='Member')
    plt.plot(casual_data['hour_of_day'], casual_data['trip_count'], label='Casual')
    plt.title('Number of Trips by Hour of Day')
    plt.xticks(range(0, 25))
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.close()


def random_color():
    return '#%06X' % random.randint(0, 0xFFFFFF)


def most_popular_routes(member_casual):
    query = f"""
    SELECT
        start_station_name,
        start_lat as start_latitude,
        start_lng as start_longitude,
        end_station_name,
        end_lat as end_latitude,
        end_lng as end_longitude,
        COUNT(*) AS trip_count
    FROM trip_data
    WHERE
        member_casual = '{member_casual}' AND
        end_station_name IS NOT NULL AND
        start_lat IS NOT NULL AND
        start_lng IS NOT NULL AND
        end_lat IS NOT NULL AND
        end_lng IS NOT NULL AND
        start_station_name != end_station_name 
    GROUP BY
        start_station_name, start_latitude, start_longitude,
        end_station_name, end_latitude, end_longitude
    ORDER BY
        trip_count DESC
    LIMIT 10;
    """
    data = pd.read_sql(query, engine)

    m = folium.Map(location=[41.8781, -87.6298], zoom_start=12)  # Chicago coordinates

    # adding arrows on map to show direction
    for index, row in data.iterrows():
        start_coords = (row['start_latitude'], row['start_longitude'])
        end_coords = (row['end_latitude'], row['end_longitude'])
        color = '#%06X' % random.randint(0, 0xFFFFFF)

        line = folium.PolyLine(locations=[start_coords, end_coords], weight=5, color=color)
        line.add_to(m)

        plugins.PolyLineTextPath(
            line,
            '\u25BA',
            repeat=True,
            offset=10,
            attributes={'fill': color, 'font-weight': 'bold', 'font-size': '24'}
        ).add_to(m)

    m.save(f'Popular_Routes_Map_{member_casual}.html')




usage_of_rideable_types_by_membership_status()
popular_stations('start_station_name', 'start')
popular_stations('end_station_name', 'end')


plot_top_stations('member', 'end_station_name', 'end')
plot_top_stations('casual', 'end_station_name', 'end')

plot_top_stations('member', 'start_station_name', 'start')
plot_top_stations('casual', 'start_station_name', 'start')


plot_rides_by_hour_of_day('2023-09-30', '2023-11-01')
plot_rides_by_weekday('2023-09-30', '2023-11-01')



#------------
map_display = popular_stations_on_map('member', 'start_station_name', 'start_lat', 'start_lng')
map_display.save('member_top_start_stations_map.html')

map_display = popular_stations_on_map('casual', 'start_station_name', 'start_lat', 'start_lng')
map_display.save('casual_top_start_stations_map.html')


map_display = popular_stations_on_map('member', 'end_station_name', 'end_lat', 'end_lng')
map_display.save('member_top_end_stations_map.html')

map_display = popular_stations_on_map('casual', 'end_station_name', 'end_lat', 'end_lng')
map_display.save('casual_top_end_stations_map.html')


#------------
most_popular_routes('member')
most_popular_routes('casual')
