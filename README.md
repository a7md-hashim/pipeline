# Bokeh Data Visualization App

![Main plot](/assets/defect_plot.png)

## About

This app visualizes ILI data of pipeline defects using the Python Bokeh library. It allows filtering and viewing the data in an interactive way.
## Demo

![App Demo](/assets/app-demo.gif)

## Features

- Interactive defect visualization technique that overlays transparent defect arcs
- Map showing location of defects 
- Charts displaying analysis like max depth, average depth etc.
- Data table listing the individual defects
- Options to filter by:
  - Distance along pipe
  - Defect depth 
  - Pipe wall (internal or external)
  - Defect type
- Mobile friendly responsive layout

## Usage

The app is a single self-contained HTML file called `bokeh_data_app.html`. To run it, simply open this file in a modern web browser.

Filters can be adjusted using the sidebar widgets when on larger screens. On small screens like mobile, tap the menu button to access the filters.

## Customizing

The main code for this project is main.py. Running it assembles the data, Bokeh models and HTML template into the final `bokeh_data_app.html` app.

To customize:

- Update pipeline data by editing `df1.csv`.

- Change Bokeh plots and widgets by editing `main.py`.

- Revise the HTML layout and styles in `index.html`.

## Built With

- Bokeh - Interactive web plot generation (~40%)
- Pandas - Data processing (~5%)
- Jinja - Template rendering (~1%)
- NumPy - Numeric processing (~2%)
- HTML/Bootstrap - Markup and styling (~40%)
- JavaScript - Custom interactivity (~12%)

## Deployment

As a standalone HTML/JS application, this can be deployed to any basic web server or host. Some good simple options are:

- GitHub Pages
- Amazon S3 
- Azure Blob Storage

The app can also be embedded into an existing web framework like Django.

## License

MIT
