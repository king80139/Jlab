def draw_static_3d_plot_space(username,prname):
    import pandas as pd
    import os
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.io as pio
    pio.renderers.default = "browser"
    from .utils import Read_Arg_, import_dataframe

    input_directory = "/".join([username,prname])
    _, input_, output_ = Read_Arg_("Draw_Static_3D_Plot_Space")
    input_name = os.path.join(input_directory, input_)
    table_for_3dplot = import_dataframe(input_name)
    Axes = table_for_3dplot.columns[1:4]
    trace = table_for_3dplot.columns[0]

    fig = px.scatter_3d(table_for_3dplot,
                        x=Axes[0],
                        y=Axes[1],
                        z=Axes[2],
                        labels=Axes,
                        color=trace,
                        text=trace,
                        opacity=1.0,
                        title="HUE CUBE",
                        range_x=[min(table_for_3dplot[Axes[0]] - 0.1), max(table_for_3dplot[Axes[0]] + 0.1)],
                        range_y=[min(table_for_3dplot[Axes[1]] - 0.1), max(table_for_3dplot[Axes[1]] + 0.1)],
                        range_z=[min(table_for_3dplot[Axes[2]] - 0.1), max(table_for_3dplot[Axes[2]] + 0.1)],
                        width=1200,  # 픽셀값이므로 상당히 크게 줘야합니다.
                        height=1028  # 픽셀값이므로 상당히 크게 줘야합니다.
                        )

    fig.update_layout(scene_aspectmode="cube",
                      legend=dict(yanchor="top",
                                  y=0.99,
                                  xanchor="right",
                                  x=0.99,
                                  bgcolor="ivory",
                                  bordercolor="black",
                                  borderwidth=2,
                                  itemsizing="constant",
                                  tracegroupgap=5),
                      scene=dict(
                          xaxis=dict(
                              title=dict(text="Economy",
                                         font=dict(size=15),
                                         ),
                              tickfont=dict(color="rgb(204, 051, 051)",
                                            size=14),
                              backgroundcolor="rgb(255, 204, 204)",
                              gridcolor="white",
                              showbackground=True,
                              zerolinecolor="white",
                              ticks="outside",
                              # range = [min(table_for_3dplot[Axes[0]])-0.1, max(table_for_3dplot[Axes[0]])+0.1]
                          ),
                          yaxis=dict(
                              title=dict(text="utilitarian",
                                         font=dict(size=15),
                                         ),
                              tickfont=dict(color="rgb(204, 153, 051)",
                                            size=14),
                              backgroundcolor="rgb(204, 204, 153)",
                              gridcolor="white",
                              showbackground=True,
                              zerolinecolor="white",
                              ticks="outside",
                              # range = [min(table_for_3dplot[Axes[1]])-0.1, max(table_for_3dplot[Axes[1]])+0.1]
                          ),
                          zaxis=dict(
                              title=dict(text="Hedonic",
                                         font=dict(size=15),
                                         ),
                              tickfont=dict(color="rgb(051, 051, 153)",
                                            size=14),
                              backgroundcolor="rgb(204, 204, 255)",
                              gridcolor="white",
                              showbackground=True,
                              zerolinecolor="white",
                              ticks="outside",
                              # range = [min(table_for_3dplot[Axes[2]])-0.1, max(table_for_3dplot[Axes[2]])+0.1]
                          )
                      )
                      )

    xaxis_min = fig.layout.scene.xaxis.range[0]
    xaxis_max = fig.layout.scene.xaxis.range[1]
    yaxis_min = fig.layout.scene.yaxis.range[0]
    yaxis_max = fig.layout.scene.yaxis.range[1]
    zaxis_min = fig.layout.scene.zaxis.range[0]
    zaxis_max = fig.layout.scene.zaxis.range[1]

    df_x = pd.DataFrame({"x": [1] * 8,
                         "y": [yaxis_min, yaxis_max, yaxis_max, yaxis_max, yaxis_max, yaxis_min, yaxis_min, yaxis_min],
                         "z": [zaxis_min, zaxis_min, zaxis_min, zaxis_max, zaxis_max, zaxis_max, zaxis_max, zaxis_min]})

    df_y = pd.DataFrame({"x": [xaxis_min, xaxis_max, xaxis_max, xaxis_max, xaxis_max, xaxis_min, xaxis_min, xaxis_min],
                         "y": [1] * 8,
                         "z": [zaxis_min, zaxis_min, zaxis_min, zaxis_max, zaxis_max, zaxis_max, zaxis_max, zaxis_min]})

    df_z = pd.DataFrame({"x": [xaxis_min, xaxis_max, xaxis_max, xaxis_max, xaxis_max, xaxis_min, xaxis_min, xaxis_min],
                         "y": [yaxis_min, yaxis_min, yaxis_min, yaxis_max, yaxis_max, yaxis_max, yaxis_max, yaxis_min],
                         "z": [1] * 8})

    fig.add_trace(go.Scatter3d(x=df_x["x"],
                               y=df_x["y"],
                               z=df_x["z"],
                               mode="lines",
                               line=dict(width=10,
                                         color="rgb(000, 000, 000)"),
                               surfaceaxis=0,
                               surfacecolor="rgb(255, 204, 204)",
                               opacity=.5))
    
    fig.add_trace(go.Scatter3d(x=df_y["x"],
                               y=df_y["y"],
                               z=df_y["z"],
                               mode="lines",
                               line=dict(width=10,
                                         color="rgb(000, 000, 000)"),
                               surfaceaxis=1,
                               surfacecolor="rgb(204, 204, 153)",
                               opacity=.5))

    fig.add_trace(go.Scatter3d(x=df_z["x"],
                               y=df_z["y"],
                               z=df_z["z"],
                               mode="lines",
                               line=dict(width=10,
                                         color="rgb(000, 000, 000)"),
                               surfaceaxis=2,
                               surfacecolor="rgb(204, 204, 255)",
                               opacity=.5))

    fig.add_trace(go.Scatter3d(x=[1, 1],
                               y=[yaxis_min, yaxis_max],
                               z=[1, 1],
                               mode="lines",
                               line=dict(width=10,
                                         color="rgb(000, 000, 000)"),
                               opacity=.3))

    fig.add_trace(go.Scatter3d(x=[1, 1],
                               y=[1, 1],
                               z=[zaxis_min, zaxis_max],
                               mode="lines",
                               line=dict(width=10,
                                         color="rgb(000, 000, 000)"),
                               opacity=.3))

    fig.add_trace(go.Scatter3d(x=[xaxis_min, xaxis_max],
                               y=[1, 1],
                               z=[1, 1],
                               mode="lines",
                               line=dict(width=10,
                                         color="rgb(000, 000, 000)"),
                               opacity=.3))

    fig.write_html(os.path.join(input_directory, output_))
    fig.show()
