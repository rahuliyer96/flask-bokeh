import random
from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d, TapTool,CrosshairTool)
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
from bokeh.charts import Bar
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.models.callbacks import CustomJS
from flask import Flask, render_template, send_file
from bokeh import events
import pandas as pd


app = Flask(__name__)


@app.route("/<int:bars_count>/")
def chart(bars_count):
    if bars_count <= 0:
        bars_count = 1

    data = {"days": [], "bugs": [], "costs": []}
    for i in range(1, bars_count + 1):
        data['days'].append(i)
        data['bugs'].append(random.randint(1,100))
        data['costs'].append(random.uniform(1.00, 1000.00))

    hover = create_hover_tool()
    plot = create_bar_chart(data, "Bugs found per day", "days",
                            "bugs", hover)
    script, div = components(plot)

    return render_template("chart.html", bars_count=bars_count,
                           the_div=div, the_script=script)
@app.route("/data/")
def get_data():
    df = pd.DataFrame({"A":[1,2,3],"B":[5,6,7]})
    return df.to_json()

@app.route("/datafile/")
def get_datafile():
    df = pd.DataFrame({"A":[1,2,3],"B":[5,6,7]})
    df.to_csv("data.csv")
    return send_file('data.csv')

@app.route("/dataascsv/")
def get_datacsv():
    df = pd.DataFrame({"A":[1,2,3],"B":[5,6,7]})
    return df.to_csv()

def create_hover_tool():
    """Generates the HTML for the Bokeh's hover data tool on our graph."""
    hover_html = """
      <div>
        <span class="hover-tooltip">$x</span>
      </div>
      <div>
        <span class="hover-tooltip">$y</span>
      </div>
      <div>
        <span class="hover-tooltip">@bugs bugs</span>
      </div>
      <div>
        <span class="hover-tooltip">$@costs{0.00}</span>
      </div>
    """
    return HoverTool(tooltips=hover_html)




def create_bar_chart(data, title, x_name, y_name, hover_tool=None,
                     width=1200, height=300):
    """Creates a bar chart plot with the exact styling for the centcom
       dashboard. Pass in data as a dictionary, desired plot title,
       name of x axis, y axis and the hover tool HTML.
    """
    source = ColumnDataSource(data)
    xdr = FactorRange(factors=data[x_name])
    ydr = Range1d(start=0,end=max(data[y_name])*1.5)
    
    callback = CustomJS(args=dict(source=source), code="""
    var data = source.data;
    
    console.log("data[bugs] : " +data['bugs']);
    console.log("source data : " + data);

    var geometry = cb_data['geometries'];
        /// calculate x and y
        var x = geometry[0].x
        var y = geometry[0].y

    console.log("geometry : " + geometry[0]);
    console.log("x : " + x);
    console.log("y : " + y);
    var b = cb_obj.data;
    console.log("cb_obj-data : "+ b);
    console.log("cb_obj selected : " + cb_obj.selected);
    console.log("cb_obj selected indices : " + cb_obj.selected.indices);
    
    //This one works to give indices from 0-last
    console.log(cb_obj.selected['1d'].indices)
    if ($(".hover_bkgr_fricc").length){
    document.getElementById('id_index').value= parseInt(cb_obj.selected['1d'].indices) + 1 ; 
    $('.hover_bkgr_fricc').show();
    }

    """)
    tap_tool = TapTool(callback=callback)
    

    plot = figure(title=title, x_range=xdr, y_range=ydr, plot_width=width,plot_height=height, h_symmetry=False, v_symmetry=False,min_border=0, toolbar_location="above", tools=[hover_tool,tap_tool,CrosshairTool()],responsive=True, outline_line_color="#666666")

    glyph = VBar(x=x_name, top=y_name, bottom=0, width=.8,fill_color="#e12127")
    plot.add_glyph(source, glyph)

    xaxis = LinearAxis()
    yaxis = LinearAxis()

    plot.add_layout(Grid(dimension=0, ticker=xaxis.ticker))
    plot.add_layout(Grid(dimension=1, ticker=yaxis.ticker))
    plot.toolbar.logo = None
    plot.min_border_top = 0
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = "#999999"
    plot.yaxis.axis_label = "Bugs found"
    plot.ygrid.grid_line_alpha = 0.1
    plot.xaxis.axis_label = "Days after app deployment"
    plot.xaxis.major_label_orientation = 1
    return plot


if __name__ == "__main__":
    app.run(debug=True)