import folium
import json
import pandas as pd
import matplotlib
from matplotlib.colors import LinearSegmentedColormap

class SeoulMap:
    def __init__(self):
        self.map_obj = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

    def make_layer(self, map_name, geodata=None):
        if geodata:
            layer = folium.GeoJson(geodata, name=map_name)
        else:
            layer = folium.FeatureGroup(name=map_name)
        return layer

    def add_layer(self, layer):
        layer.add_to(self.map_obj)

    def get_color(self, value, values, num_colors=10):
        min_val, max_val = min(values), max(values)
        normalized_value = (value - min_val) / (max_val - min_val)
        green_colormap = LinearSegmentedColormap.from_list(
            "green_shades", ["#e6f4e6", "#004d00"], N=num_colors
        )
        color_code = green_colormap(normalized_value)
        return matplotlib.colors.rgb2hex(color_code[:3])

    def display_population(self, layer, geodata, data, cols, map_col):
        for feature in geodata['features']:
            district_name = feature['properties'][map_col]
            value = data.loc[data[cols[0]] == district_name, cols[1]].values
            feature['properties']['value'] = value[0] if len(value) != 0 else 0

        folium.GeoJson(
            geodata,
            name="인구 데이터",
            style_function=lambda feature: {
                'fillColor': self.get_color(
                    data.loc[data[cols[0]] == feature['properties'][map_col], cols[1]].values[0]
                    if feature['properties'][map_col] in data[cols[0]].values else 0,
                    list(data[cols[1]])
                ),
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=[map_col, 'value'],
                aliases=['자치구:', '1인가구비중(%):']
            )
        ).add_to(layer)
        return layer

    def show(self):
        folium.LayerControl().add_to(self.map_obj)
        return self.map_obj

    def save(self, file_name):
        self.map_obj.save(file_name)

if __name__ == '__main__':
    test = SeoulMap()
    with open('../data/geoData/서울_자치구_경계_2017.geojson', encoding='utf-8') as f:
        gu_geojson = json.load(f)

    t1 = test.make_layer('서울시 자치구 경계', gu_geojson)
    test.add_layer(t1)

    t2 = test.make_layer('서울시 행정동 경계')
    test.add_layer(t2)

    test.save('Test.html')
