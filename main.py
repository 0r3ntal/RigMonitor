# -*- coding: utf-8 -*-
# Author: Oren Sternberg
# Date: 3/22/2023
# Description: RigMonitor
# GitHub: https://github.com/0r3ntal

""" starting point for an Oil rig sensor monitoring station 3.25.2023 """

import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import pandas as pd
import datetime
import random
from dash.dependencies import Input, Output
import numpy as np

app = dash.Dash(__name__)


def generate_sensor_data(sensor_type, hours=24, interval_minutes=10, sensor_id=None):
    """
      Generate simulated sensor data for a given sensor type, time range, and sensor ID.

      Args:
          sensor_type (str): The type of sensor for which to generate data. Must be one of
              'corrosion', 'pressure', 'temperature', 'acoustic', or 'flow_rate'.
          hours (int): The number of hours of data to generate. Defaults to 24.
          interval_minutes (int): The number of minutes between each time point. Defaults to 10.
          sensor_id (int or None): The ID of the sensor for which to generate data. If None, a random ID will be used.

      Returns:
          pandas.DataFrame: A DataFrame containing simulated sensor data, with columns for time, sensor ID, value,
          status, and (for corrosion sensors only) type.

      Raises:
          ValueError: If an invalid sensor type is provided.
      """

    now = datetime.datetime.now()
    time_range = pd.date_range(now - datetime.timedelta(hours=hours), now, freq=f'{interval_minutes}min')

    if sensor_type == "corrosion":
        values = np.random.uniform(0, 1, len(time_range))  # Corrosion rate in mm/year
        status = np.where(values < 0.1, "Good", np.where(values < 0.4, "Concern", "Malfunction"))
        corrosion_types = np.random.choice(['Uniform', 'Pitting', 'Galvanic', 'Crevice'], len(time_range))
        sensor_data = pd.DataFrame({
            'Time': time_range,
            'Sensor ID': [sensor_id] * len(time_range),
            'Value': values,
            'Status': status,
            'Type': corrosion_types
        })

    elif sensor_type == "pressure":
        values = np.random.uniform(0, 100, len(time_range))  # Pressure value in psi
        status = np.where(values < 80, "Good", np.where(values < 95, "Concern", "Malfunction"))
        sensor_data = pd.DataFrame({
            'Time': time_range,
            'Sensor ID': [sensor_id] * len(time_range),
            'Value': values,
            'Status': status
        })

    elif sensor_type == "temperature":
        values = np.random.uniform(-50, 150, len(time_range))  # Temperature value in Celsius
        status = np.where((-20 < values) & (values < 120), "Good", np.where((-40 < values) & (values < 140), "Concern", "Malfunction"))
        sensor_data = pd.DataFrame({
            'Time': time_range,
            'Sensor ID': [sensor_id] * len(time_range),
            'Value': values,
            'Status': status
        })

    elif sensor_type == "acoustic":
        min_value, max_value = 40, 120  # dB
        good_min, good_max = 60, 90
        concern_min, concern_max = 50, 100
        values = np.random.uniform(min_value, max_value, len(time_range))
        status = np.where((good_min <= values) & (values <= good_max), "Good", np.where((concern_min <= values) & (values <= concern_max), "Concern", "Malfunction"))
        sensor_data = pd.DataFrame({
            'Time': time_range,
            'Sensor ID': [sensor_id] * len(time_range),
            'Value': values,
            'Status': status
        })

    elif sensor_type == "flow_rate":
        value = random.uniform(0, 1000)  # Flow rate in liters per minute
        status = "Good" if 100 < value < 900 else "Concern" if 50 < value < 950 else "Malfunction"
        sensor_data.append({"Time": t, "Sensor ID": sensor_id, "Value": value, "Status": status
                            })

    return sensor_data








app.layout = html.Div([
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
    html.H1("Oil Rig Sensor Dashboard", style={'text-align': 'center'}),
    html.Div([
        html.H2("Corrosion Sensors"),
        dcc.Graph(id='corrosion-sensor-bar-chart', ),
        html.Div(id='corrosion-sensor-details'),
    ]),
    html.Div([
        html.H2("Pressure Sensors"),
        dcc.Graph(id='pressure-sensor-bar-chart', ),
        html.Div(id='pressure-sensor-details'),
    ]),
    html.Div([
        html.H2("Temperature Sensors"),
        dcc.Graph(id='temperature-sensor-bar-chart', ),
        html.Div(id='temperature-sensor-details'),
    ]),
    html.Div([
        html.H2("Acoustic Sensors"),
        dcc.Graph(id='acoustic-sensor-bar-chart'),
        html.Div(id='acoustic-sensor-details'),
    ]),

    html.Div([
        html.H2("Flow Rate Sensors"),
        dcc.Graph(id='flow-rate-sensor-bar-chart'),
        html.Div(id='flow-rate-sensor-details'),
    ]),
])

@app.callback(
    Output("corrosion-sensor-bar-chart", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_corrosion_bar_chart(n):
    df = pd.concat([generate_sensor_data("corrosion", hours=1, interval_minutes=10, sensor_id=i) for i in range(10)])
    current_values = df.groupby('Sensor ID').last().reset_index()



    fig = go.Figure(go.Bar(x=current_values['Sensor ID'], y=current_values['Value'],
                           marker_color=current_values['Status'].apply(
                               lambda x: 'green' if x == "Good" else 'orange' if x == "Concern" else 'red')))
    fig.update_layout(title='Current Corrosion Sensor Values',
                      xaxis_title='Sensor ID',
                      yaxis_title='Corrosion Rate (mm/year)',
                      yaxis_range=[0, 1])

    return fig

@app.callback(Output('corrosion-sensor-details', 'children'),
              Input('corrosion-sensor-bar-chart', 'clickData'))
def display_corrosion_sensor_details(clickData):
    """
       Display detailed sensor data for a corrosion sensor based on the user's click on the corresponding bar in the
       corrosion sensor bar chart.

       Args:
           clickData (dict): The click data from the corrosion sensor bar chart, including the ID of the clicked sensor.

       Returns:
           dash.html.Div: A div containing a line chart of the selected sensor's data over the past 24 hours, along with
           details of the sensor's ID and corrosion types.
    """


    if clickData:
        sensor_id = clickData['points'][0]['x']
        detailed_data = generate_sensor_data("corrosion", hours=24, interval_minutes=10, sensor_id=sensor_id)

        # Print the detailed_data DataFrame


        line_chart = dcc.Graph(
            figure=go.Figure(
                data=go.Scatter(x=detailed_data['Time'], y=detailed_data['Value'],
                                mode='lines+markers',
                                marker_color=detailed_data['Status'].apply(
                                    lambda x: 'green' if x == "Good" else 'orange' if x == "Concern" else 'red')),
                layout=dict(title=f'Corrosion Sensor {sensor_id} - 24 Hours Data',
                            xaxis_title='Time',
                            yaxis_title='Corrosion Rate (mm/year)',
                            yaxis_range=[0, 1],
                            xaxis=dict(range=[detailed_data['Time'].min(), detailed_data['Time'].max()]),
                            yaxis=dict(range=[0, 1])
                            )
            )
        )

        corrosion_types = ", ".join(detailed_data['Type'].unique())
        details = html.Div([
            html.H3(f'Sensor ID: {sensor_id}'),
            html.P(f'Corrosion Types: {corrosion_types}')
        ])

        return html.Div([line_chart, details])


# Pressure sensor bar chart and details
@app.callback(Output('pressure-sensor-bar-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_pressure_bar_chart(n):
    df = pd.concat([generate_sensor_data("pressure", hours=1, interval_minutes=10, sensor_id=i) for i in range(10)])
    current_values = df.groupby('Sensor ID').last().reset_index()

    fig = go.Figure()

    for status, color in zip(["Good", "Concern", "Malfunction"], ["green", "orange", "red"]):
        filtered_values = current_values[current_values["Status"] == status]
        fig.add_trace(go.Bar(x=filtered_values['Sensor ID'], y=filtered_values['Value'],
                             name=status,
                             marker_color=color,
                             marker_line=dict(color=color, width=1),
                             legendgroup=status,
                             showlegend=True))

    fig.update_layout(title='Current Pressure Sensor Values',
                      xaxis_title='Sensor ID',
                      yaxis_title='Pressure (psi)',
                      yaxis_range=[0, 100],
                      legend_title="Status")

    return fig

@app.callback(Output('pressure-sensor-details', 'children'),
              Input('pressure-sensor-bar-chart', 'clickData'))
def display_pressure_sensor_details(clickData):
    """
        Display detailed sensor data for a pressure sensor based on the user's click on the corresponding bar in the
        pressure sensor bar chart.

        Args:
            clickData (dict): The click data from the pressure sensor bar chart, including the ID of the clicked sensor.

        Returns:
            dash.html.Div: A div containing a line chart of the selected sensor's data over the past 24 hours.
        """

    if clickData:
        sensor_id = clickData['points'][0]['x']
        detailed_data = generate_sensor_data("pressure", hours=24, interval_minutes=10, sensor_id=sensor_id)

        line_chart = dcc.Graph(
            figure=go.Figure(
                data=go.Scatter(x=detailed_data['Time'], y=detailed_data['Value'],
                                mode='lines+markers',
                                marker_color=detailed_data['Status'].apply(lambda x: 'green' if x == "Good" else 'orange' if x == "Concern" else 'red')),
                layout=dict(title=f'Pressure Sensor {sensor_id} - 24 Hours Data',
                            xaxis_title='Time',
                            yaxis_title='Pressure (psi)',
                            yaxis_range=[0, 100]
                )
            )
        )

        return line_chart

# Temperature sensor bar chart and details
@app.callback(Output('temperature-sensor-bar-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_temperature_bar_chart(n):
    """
        Updates the temperature sensor bar chart in the dashboard.

        Args:
            n (int): The number of intervals that have elapsed since the app started running.

        Returns:
            A Plotly Figure object representing the updated temperature sensor bar chart.
    """

    df = pd.concat([generate_sensor_data("temperature", hours=1, interval_minutes=10, sensor_id=i) for i in range(10)])
    current_values = df.groupby('Sensor ID').last().reset_index()

    fig = go.Figure(go.Bar(x=current_values['Sensor ID'], y=current_values['Value'],
                           marker_color=current_values['Status'].apply(lambda x: 'green' if x == "Good" else 'orange' if x == "Concern" else 'red')))
    fig.update_layout(title='Current Temperature Sensor Values',
                      xaxis_title='Sensor ID',
                      yaxis_title='Temperature (°C)',
                      yaxis_range=[-50, 150])

    return fig

@app.callback(Output('temperature-sensor-details', 'children'),
              Input('temperature-sensor-bar-chart', 'clickData'))

def display_temperature_sensor_details(clickData):
    """
        Displays detailed data for a selected temperature sensor when the user clicks on the corresponding bar in the bar chart.

        Args:
            clickData (dict): A dictionary containing information about the click event on the bar chart.

        Returns:
            A Dash HTML div containing the detailed data for the selected temperature sensor.
    """

    if clickData:
        sensor_id = clickData['points'][0]['x']
        detailed_data = generate_sensor_data("temperature", hours=24, interval_minutes=10, sensor_id=sensor_id)

        line_chart = dcc.Graph(
            figure=go.Figure(
                data=go.Scatter(x=detailed_data['Time'], y=detailed_data['Value'],
                                mode='lines+markers',
                                marker_color=detailed_data['Status'].apply(lambda x: 'green' if x == "Good" else 'orange' if x == "Concern" else 'red')),
                layout=dict(title=f'Temperature Sensor {sensor_id} - 24 Hours Data',
                            xaxis_title='Time',
                            yaxis_title='Temperature (°C)',
                            yaxis_range=[-50, 150]
                )
            )
        )

        return line_chart

@app.callback(Output('acoustic-sensor-bar-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_acoustic_bar_chart(n):
    """
        Updates the acoustic sensor bar chart.

        Args:
            n (int): The number of intervals that have elapsed since the app started.

        Returns:
            fig (plotly.graph_objs._figure.Figure): A plotly bar chart figure containing the updated sensor data.
    """
    df = pd.concat([generate_sensor_data("acoustic", hours=1, interval_minutes=10, sensor_id=i) for i in range(10)])
    current_values = df.groupby('Sensor ID').last().reset_index()

    fig = go.Figure(go.Bar(x=current_values['Sensor ID'], y=current_values['Value'],
                           marker_color=current_values['Status'].apply(lambda x: 'green' if x == "Good" else 'orange' if x == "Concern" else 'red')))
    fig.update_layout(title='Current Acoustic Sensor Values',
                      xaxis_title='Sensor ID',
                      yaxis_title='Acoustic Level (dB)',
                      yaxis_range=[40, 120])

    return fig

@app.callback(Output('acoustic-sensor-details', 'children'),
              Input('acoustic-sensor-bar-chart', 'clickData'))
def display_acoustic_sensor_details(clickData):
    """
        Displays detailed information about a clicked acoustic sensor.

        Args:
            clickData (dict): A dictionary containing information about the clicked point in the acoustic sensor bar chart.

        Returns:
            dcc.Graph: A plotly line chart containing the 24-hour data for the clicked sensor.
    """
    if clickData:
        sensor_id = clickData['points'][0]['x']
        # detailed_data = generate_sensor_data("acoustic", hours=24, interval_minutes=10, sensor_id=sensor_id)
        detailed_data = generate_sensor_data("acoustic", hours=24, interval_minutes=10, sensor_id=int(sensor_id))

        line_chart = dcc.Graph(
            figure=go.Figure(
                data=go.Scatter(x=detailed_data['Time'], y=detailed_data['Value'],
                                mode='lines+markers',
                                marker_color=detailed_data['Status'].apply(lambda x: 'green' if x == "Good" else 'orange' if x == "Concern" else 'red')),
                layout=dict(title=f'Acoustic Sensor {sensor_id} - 24 Hours Data',
                            xaxis_title='Time',
                            yaxis_title='Acoustic Level (dB)',
                            yaxis_range=[40, 120]
                )
            )
        )

        return line_chart


if __name__ == '__main__':
    app.run_server(debug=True)