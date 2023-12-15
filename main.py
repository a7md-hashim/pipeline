#Import libraries
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.layouts import row, column
from bokeh.plotting import figure
from bokeh.models import CustomJS, ColumnDataSource, CDSView, RangeSlider, MultiSelect, Slider, DataTable, TableColumn,GroupFilter, Div, Range1d
import pandas as pd
import numpy as np
from jinja2 import Template

# ... (where the data is loaded): This data was anonymized by changing the coordinates
#.. and randomizing the depth between the minimum and maximum values in the original real data.
#.. This is only a small part of the data.
df=pd.read_csv('df1.csv')
# Rename columns
df = df.rename(columns={"Distance (m)": "Distance", "Int/Ext": "IntExt", "Depth (%wt)": "Depth",
                        "Longitude (°)": "lon", "Latitude (°)" : "lat", "Dim.Class" : "Class"})
# Convert all data in the column "Depth" to integers
df["Depth"] = df["Depth"].astype(int)
#Duplicate Depth column to manipulate the value in visualization
df["Depth1"] = df["Depth"]
# function to convert the coordinates from WGS84 to Web Mercator
def wgs84_to_web_mercator(df, lon="lon", lat="lat"):
    k = 6378137
    df[lon] = df[lon] * (k * np.pi/180.0)
    df[lat] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df
df = wgs84_to_web_mercator(df)
# Create a Bokeh ColumnDataSource
source = ColumnDataSource(df)
original_source = ColumnDataSource(df.copy())
# Create a RangeSlider widget to filter the DataFrame by "Distance (m)" (0, ~12750)
max_distance = np.ceil(df['Distance'].max())
distance_slider = RangeSlider(start=1, end=max_distance, value=(0, max_distance), title="Distance",styles={'font-size': '120%'})
# Create a RangeSlider widget to filter the DataFrame by depth
max_depth = df['Depth1'].max()
depth_slider = RangeSlider(start=0, end=max_depth, value=(0, max_depth), title="Depth%",styles={'font-size': '120%'})

# Create a RangeSlider widget to manipulate the opacity of the figure
opc_slider = Slider(start=0, end=0.5, value=0.1, step=.02, title="Opacity")

# Create a MultiSelect widgets to filter the DataFrame by pipe wall & corrosion type
OPTIONS = [("Int", "Int"), ("Ext", "Ext")]
int_ext_multiselect = MultiSelect(value=["Int", "Ext"], options=OPTIONS, title="Pipe Wall",styles={'font-size': '120%'})
type_options = [("Circumferential Grooving","Circumferential Grooving"),("Pitting","Pitting"),("General","General")]
type_multiselect = MultiSelect(value=["Pitting", "General", "Circumferential Grooving"], options=type_options,
                                title="Corrosion Type", sizing_mode="scale_width",styles={'font-size': '120%'})


# Create an IntegerSlider widget to multiply the "Depth (%wt)" column to exaggerate the difference visually if needed
mult_slider = Slider(start=1, end=10, value=3, title="Amplifier")

# Create the main Bokeh figure

# Create CDSView for Exteral pipe wall
E_view = CDSView(filter=GroupFilter(column_name='IntExt', group='Ext'))
# Create CDSView for Interal pipe wall
I_view = CDSView(filter=GroupFilter(column_name='IntExt', group='Int'))
# Multiply the "Depth (%wt)" column by the slider value to exaggerate the difference visually
# without changing the underlying data
source.data['Depth']=source.data['Depth1']*mult_slider.value
# initiate the plot
fig = figure()
fig.xaxis.visible = False
fig.xgrid.visible = False
fig.yaxis.visible = False
fig.ygrid.visible = False
# Add the arcs for the external pipe wall's defects
ext_arc= fig.arc(source=source, view=E_view, x = .3, y = .3, radius = .85,  start_angle = "start", end_angle="end",
          line_color = 'black',start_angle_units = 'deg',end_angle_units = 'deg',
    line_width  = "Depth",line_alpha = opc_slider.value,direction = 'clock'
    )
# Add the arcs for the internal pipe wall's defects
int_arc= fig.arc(source=source, view=I_view,x = .3, y = .3, radius = .35,  start_angle = "start", end_angle="end",
          line_color = 'crimson',start_angle_units = 'deg',end_angle_units = 'deg',
    line_width  = "Depth",line_alpha = opc_slider.value,direction = 'clock'
    )

# Link the slider to the glyph's alpha property
opc_slider.js_link('value', ext_arc.glyph, 'line_alpha')
opc_slider.js_link('value', int_arc.glyph, 'line_alpha')

# Create a CustomJS callback to filter the data frame.
# JS code is used to enable converting the whole data app into static HTML ()
callback = CustomJS(
  args=dict(source=source,original_source=original_source, distance_slider=distance_slider,fig=fig,
            int_ext_multiselect=int_ext_multiselect,mult_slider=mult_slider,type_multiselect=type_multiselect,
            depth_slider=depth_slider),
  code="""
// Assuming original_source is a ColumnDataSource that contains the original data
var distance_min = distance_slider.value[0];
var distance_max = distance_slider.value[1];
var int_ext_values = int_ext_multiselect.value;
var mult = mult_slider.value;
var typ = type_multiselect.value;
var dep_min = depth_slider.value[0];
var dep_max = depth_slider.value[1];

// Create a new object to hold the filtered data
var new_data = {};
for (var key in original_source.data) {
    new_data[key] = [];
}
// Apply the filters and update 'Depth' column
for (var i = 0; i < original_source.data['Distance'].length; ++i) {
    if (original_source.data['Distance'][i] >= distance_min && original_source.data['Distance'][i] <= distance_max &&
    original_source.data['Depth1'][i] >= dep_min && original_source.data['Depth1'][i] <= dep_max &&
     int_ext_values.includes(original_source.data['IntExt'][i]) && typ.includes(original_source.data['Class'][i]))  {
        for (var key in original_source.data) {
            if (key === 'Depth') {
                new_data[key].push(original_source.data[key][i] * mult);
            } else {
                new_data[key].push(original_source.data[key][i]);
            }
        }
    }
}
// Update the data source
source.data = new_data;

// Request redraw
source.change.emit();
fig.change.emit();
  """
)


# Create a DataTable to display the data (complementary to the figure)
columns = [
        TableColumn(field="IntExt", title="Pipe Wall"),
        TableColumn(field="Girth Weld No.", title="Girth Weld No."),
        TableColumn(field="Depth1", title="Depth (%wt)"),
        TableColumn(field="Class", title="Corrosion Class"),
    ]
data_table = DataTable(source=source, columns=columns)

# Create small intro text description for the visual 
intro = Div(text="""
<p>This technique overlays all the defects found in cross-sectional scans of the pipeline as arcs with low opacity. 
The thickness of the arcs corresponds to the depth of the defects. This allows easy visual identification of areas 
with a higher density of defects along the circumference of the pipe. By stacking the transparent defect maps,
regions with more overlapping defects become visibly darker. This provides a clear visual indicator of the circumferential 
regions most prone to defect formation without losing information on the individual defects, unlike a heatmap..</p>
""",styles={'font-size': '110%'})

#Create a map to display the defects' locations
# set to roughly extent of points
x_range = Range1d(start=df['lon'].min() - 100, end=df['lon'].max() + 100, bounds=None)
y_range = Range1d(start=df['lat'].min() - 100, end=df['lat'].max() + 100, bounds=None)
# create figure for the map
p = figure(tools='wheel_zoom,pan,hover,zoom_in, zoom_out,reset', x_range=x_range, y_range=y_range,
           tooltips=[("Depth", "@Depth1"), ("Class", "@Class"),("Pipe wall", "@IntExt")],
           width=1000, height=300,x_axis_type="mercator", y_axis_type="mercator",title="A Map of Pipeline Defects: Circle Sizes Correspond to Depth")
p.axis.visible = False
fig.xaxis.visible = False
fig.xgrid.visible = False
fig.yaxis.visible = False
fig.ygrid.visible = False
p.add_tile("CARTODBPOSITRON", retina=True)

# create point glyphs which their size is based on the depth of the defect
p.circle(x='lon', y='lat', size="Depth1", fill_color="#F7DEA7", line_color="black", line_width=0.5, source=source)

#Create info cards to display statistics
# Calculate the percentage of the filtered data from the original
total_defects= len(original_source.data["Depth1"])
no_defects= len(source.data["Depth1"])
percentage = round(no_defects / len(original_source.data["Depth1"]) * 100)
# Calculate the max, min, and avg values of the filtered data
maxd = max(source.data["Depth1"]) # the depth column is named "Depth1"
mind = min(source.data["Depth1"])
avgd = round(sum(source.data["Depth1"]) / len(source.data["Depth1"]))
# Create Div widgets to display the statistics
td_wgt = Div(text=f'<b>{total_defects}</b>',styles={'font-size': '100%'})
d_wgt = Div(text=f'<b>{no_defects}</b>',styles={'font-size': '100%'})
prct_wgt = Div(text=f'<b>{percentage}</b> %',styles={'font-size': '300%'})

max_wgt = Div(text=f"<b>{maxd}</b> %",styles={'font-size': '300%'})
min_wgt = Div(text=f"<b>{mind}</b> %",styles={'font-size': '300%'})
avg_wgt = Div(text=f"<b>{avgd}</b> %",styles={'font-size': '300%'})

# Define a CustomJS callback to recalculate the statistics based on the source data
callback1 = CustomJS(args=dict(source=source, original_source=original_source, prct_wgt=prct_wgt, max_wgt=max_wgt, 
                                d_wgt=d_wgt, td_wgt=td_wgt,min_wgt=min_wgt, avg_wgt=avg_wgt), code='''
    // Get the source data as an array
    const data = source.data;

    // Get the original data as an array
    const original_data = original_source.data;

    // Calculate the percentage of the filtered data from the original
    let total_defects = original_data['Depth1'].length;
    let no_defects = data['Depth1'].length;
    let percentage = Math.round(no_defects / total_defects * 100, 0);

    // Calculate the max, min, and avg values of the filtered data
    let maxd = Math.max(...data['Depth1']);
    let mind = Math.min(...data['Depth1']);
    let avgd = data['Depth1'].reduce((a, b) => a + b, 0) / no_defects;
    // Convert the average value to a string with 0 decimals
    avgd = avgd.toFixed(0);
    // Update the text of the Div widgets
    td_wgt.text = `<b>${total_defects}</b>`;
    d_wgt.text = `<b>${no_defects}</b>`;
    prct_wgt.text = `<b>${percentage}</b> %`;
    max_wgt.text = `<b>${maxd}</b> %`;
    min_wgt.text = `<b>${mind}</b> %`;
    avg_wgt.text = `<b>${avgd}</b> %`;
''')

# Attach the callback to the data property of the source
source.js_on_change('data', callback1)




# Set the callback on the widgets
distance_slider.js_on_change('value', callback)
depth_slider.js_on_change('value', callback)
int_ext_multiselect.js_on_change('value', callback)
mult_slider.js_on_change('value', callback)
type_multiselect.js_on_change('value', callback)
opc_slider.js_on_change('value', callback)

# Add the widgets into two columns to display them in the UI separately

widget_col = column(
    distance_slider,
    depth_slider,
    row(int_ext_multiselect,type_multiselect) ,
    mult_slider,
    opc_slider)

widget_col1 = column(
    distance_slider,
    depth_slider,
    row(int_ext_multiselect,type_multiselect) ,
    mult_slider,
    opc_slider)

#cobmine all the models into one and get the script & divs to embed them in the UI
bokeh_models= dict(wc=widget_col1, widgets=widget_col, pre = intro, clock= fig, tbl= data_table, locations= p
                   , d_wgt=d_wgt, td_wgt=td_wgt,prct_wgt=prct_wgt, max_wgt=max_wgt, min_wgt=min_wgt, avg_wgt=avg_wgt)
script, div = components(bokeh_models)

# Get the HTML template from the file as a string
with open('E:\Projects\corrosion\index.html') as f:
    template_string = f.read()

# Define the HTML template (bootstrap 5 was used to give responsiveness)
template = Template(template_string)

# Generate the necessary HTML and JavaScript code for embedding Bokeh plots in an HTML file.
resources = INLINE.render()

filename = 'bokeh_data_app.html'
# render the plot using the template
html = template.render(resources=resources,
                       script=script,
                       div=div)

with open(filename, mode="w", encoding="utf-8") as f:
    f.write(html)
