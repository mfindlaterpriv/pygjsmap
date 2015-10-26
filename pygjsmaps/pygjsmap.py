'''
Created on 2015/09/29

pygjsmaps by Michael Findlater
    Simple Python->Javascript+HTML Interface to Google Maps
    
Usage example:
    map = pygjsmap(34.5167, 135.8000, api_key='YOUR_API_KEY', map_filename='my_map.html')
    map.add_coord(34.5167, 135.8000, title='hey')
    map.write_map()
'''
import codecs

class pygjsmap():
    coords = []
    def __init__(self, center_lat, center_lon, api_key=None, map_filename='map.html', zoom_level=12):
        if not api_key:
            print('Warning, no Google Maps Web API key specified. Your map will not work.')
        else:
            self.api_key = str(api_key)
        self.map_filename = map_filename
        self.center_lat = str(center_lat)
        self.center_lon = str(center_lon)
        self.zoom_level = zoom_level
        self.line_data = []
    def add_coord(self, lat, lon, title=None, info=None, color=None, media=None):
        'Adds a dictionary to a list of self.coords[]:'
        self.coords.append({ 'lat': str(lat), 
                            'lon': str(lon),
                            'title': str(title),
                            'info': str(info),
                            'color': color,
                            'media': media})
    def add_line(self, latlon_a, latlon_b, color, identifier):
        '''Generates code to add a line between latlon_a (lat, lon) and latlon_b
        identifier should be a numeric value that uniquely identifies the line
        N.B. to improve this code, could generate it automatically...'''
        return """
        var line{0} = [
            {{lat: {1}, lng: {2}}},
            {{lat: {3}, lng: {4}}},
        ];
        var line_data{0} = new google.maps.Polyline({{
            path: line{0},
            geodesic: true,
            strokeColor: '#{5}',
            strokeOpacity: 1.0,
            strokeWeight: 2
        }});

        line_data{0}.setMap(map);""".format(identifier,
                                            latlon_a[0], latlon_a[1],
                                            latlon_b[0], latlon_b[1],
                                            color)

    def write_map(self):
        self.map_file = codecs.open(self.map_filename, 'w', encoding='utf-8')
        self.map_file.write('''<!DOCTYPE html>
            <html>
                <head>
                    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
                    <meta charset="utf-8">
                    <title>pygjsmaps</title>
                    <style>
                        html, body {{
                            height: 100%;
                            margin: 0;
                            padding: 0;
                        }}
                        #map {{
                            height: 100%;
                        }}
                    </style>
                </head>
            <body>
                <div id="map"></div>
                <script>
        
                function initMap() {{
                    var CenterLatLng = {{lat: {0}, lng: {1}}};
        
                    var map = new google.maps.Map(document.getElementById("map"), {{
                        zoom: {2},
                        center: CenterLatLng
                    }});'''.format(self.center_lat, self.center_lon, self.zoom_level))
                            
        # Add markers
        counter = 0
        for marker in self.coords:
            # Default width and height of marker icon we're using (0.5x size for retina disp.)
            width = '18'
            height = '33'
            if marker['color']:
                if marker['media']:
                    # Set images WxH pixels square
                    width = '45'
                    height = '45'
                    self.map_file.write('                var pinImage{0} = new google.maps.MarkerImage("{1}",\n'.format(str(counter), marker['media'][0]))
                else:
                    self.map_file.write('\n                var pinColor{0} = "{1}";\n'.format(str(counter), marker['color']))
                    self.map_file.write('                var pinImage{0} = new google.maps.MarkerImage("https://chart.googleapis.com/chart?chst=d_map_spin&chld=1.0|0|"+pinColor{0}+"|18||@",\n'.format(str(counter), marker['color']))
                self.map_file.write('null, null, null, new google.maps.Size({0},{1}));\n'.format(width, height))
            self.map_file.write('''
            var marker{0} = new google.maps.Marker({{
            position: {{lat: {1}, lng: {2}}},
            map: map,
            title: "{3}"'''.format(str(counter),
                                   marker['lat'],
                                   marker['lon'],
                                   marker['title']))
            if marker['color']:
                self.map_file.write(',\n    icon: pinImage{0}'.format(str(counter)))
            
            self.map_file.write('  });\n\n')
            
            # If HTML info exists, write it into the Javascript
            if marker['info']:
                # Create Javascript string
                self.map_file.write('var contentString{0} = '.format(str(counter)))
                counter_info = 0
                for line in marker['info'].split('\n'):
                    if counter_info == len(marker['info'].split('\n'))-1:
                        self.map_file.write("'"+line+"';\n")
                    else:
                        self.map_file.write("'"+line+"'+\n")
                    counter_info +=1
                # Create InfoWindowN
                self.map_file.write('''
                var infowindow{0} = new google.maps.InfoWindow({{
                  content: contentString{0}
                }});
                
                marker{0}.addListener('click', function() {{
                  infowindow{0}.open(map, marker{0});
                }});'''.format( str(counter) ) )
                    
            counter += 1

        # Draw lines
        if self.line_data:
            for entry in self.line_data:
                self.map_file.write(self.add_line(entry['loc_a'], entry['loc_b'], entry['color'], self.line_data.index(entry)))

        # Write the rest
        self.map_file.write('}\n'+
        '    </script>\n'+
        '    <script async defer\n'+
        '        src="https://maps.googleapis.com/maps/api/js?key='+self.api_key+'&signed_in=true&callback=initMap"></script>\n'+
        '  </body>\n'+
        '</html>\n')