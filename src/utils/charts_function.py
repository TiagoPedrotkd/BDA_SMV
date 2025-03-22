import plotly.graph_objects as go
from IPython.display import clear_output
import pandas as pd


def update_pie_chart(selected_column, missing_values, df, output_widget):
    with output_widget:
        clear_output(wait=True)

        filtered_data = missing_values[missing_values["Column"] == selected_column]
        if filtered_data.empty:
            print(f"⚠️ No missing values found for '{selected_column}'")
            return

        missing_count = filtered_data["Missing Values"].values[0]
        total_count = len(df)
        present_count = total_count - missing_count

        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=["Present", "Missing"],
            values=[present_count, missing_count],
            marker=dict(colors=["#27ae60", "#e74c3c"]),
            textinfo="percent+label",
            showlegend=True
        ))

        fig.update_layout(
            title=dict(text=f"📌 Missing vs Present Data in {selected_column}", x=0.5, font=dict(size=18, color="white")),
            font=dict(color="white"),
            height=500,
            plot_bgcolor="#1e272e",
            paper_bgcolor="#1e272e",
            showlegend=True
        )

        fig.show()

def time_series_analysis(df_daily, df):
    fig = go.Figure()

    # Linha diária
    fig.add_trace(go.Scatter(
        x=df_daily['Date'],
        y=df_daily['Close_NVDA'],
        mode='lines',
        name='Daily',
        line=dict(color='#3498db', width=2.2, shape='spline', smoothing=1.2),
        visible=True
    ))

    # Botões de período (1Y, 5Y, etc.)
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0,
                xanchor="left",
                y=1.15,
                yanchor="top",
                bgcolor="#34495e",
                bordercolor="#7f8c8d",
                borderwidth=1,
                font=dict(color="white", size=13),
                buttons=[
                    dict(method="relayout", label="1Y",
                         args=[{"xaxis.range": [df['Date'].max() - pd.DateOffset(years=1), df['Date'].max()],
                                "title": "📈 NVIDIA Closing Prices - Last 1 Year"}]),
                    dict(method="relayout", label="5Y",
                         args=[{"xaxis.range": [df['Date'].max() - pd.DateOffset(years=5), df['Date'].max()],
                                "title": "📈 NVIDIA Closing Prices - Last 5 Years"}]),
                    dict(method="relayout", label="10Y",
                         args=[{"xaxis.range": [df['Date'].max() - pd.DateOffset(years=10), df['Date'].max()],
                                "title": "📈 NVIDIA Closing Prices - Last 10 Years"}]),
                    dict(method="relayout", label="All",
                         args=[{"xaxis.autorange": True,
                                "title": "📈 NVIDIA Closing Prices Over Time"}])
                ]
            )
        ]
    )

    # Layout e eixo X
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True, thickness=0.04),
            type="date",
            showline=True,
            linecolor="#7f8c8d"
        ),
        title=dict(
            text="📈 NVIDIA Closing Prices Over Time",
            font=dict(size=20, color="white"),
            x=0.5
        ),
        yaxis_title="Closing Price (USD)",
        plot_bgcolor="#1e272e",
        paper_bgcolor="#1e272e",
        font=dict(color="white"),
        hovermode="x unified",
        margin=dict(t=110, b=60, l=60, r=60),
        height=700
    )

    fig.show()



def daily_change_analysis(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Daily_Change_%'],
        mode='lines',
        name='Daily % Change',
        line=dict(color='#f39c12', width=2.2, shape='spline', smoothing=1.2),
        hovertemplate='📅 %{x}<br>📈 Change: %{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0,
                xanchor="left",
                y=1.18,
                yanchor="top",
                bgcolor="#34495e",
                bordercolor="#7f8c8d",
                borderwidth=1,
                font=dict(color="white", size=13),
                active=3,
                buttons=[
                    dict(method="relayout", label="1Y",
                         args=[{"xaxis.range": [df['Date'].max() - pd.DateOffset(years=1), df['Date'].max()],
                                "title": "📊 NVIDIA – Daily % Change - Last 1 Year"}]),
                    dict(method="relayout", label="5Y",
                         args=[{"xaxis.range": [df['Date'].max() - pd.DateOffset(years=5), df['Date'].max()],
                                "title": "📊 NVIDIA – Daily % Change - Last 5 Years"}]),
                    dict(method="relayout", label="10Y",
                         args=[{"xaxis.range": [df['Date'].max() - pd.DateOffset(years=10), df['Date'].max()],
                                "title": "📊 NVIDIA – Daily % Change - Last 10 Years"}]),
                    dict(method="relayout", label="All",
                         args=[{"xaxis.autorange": True,
                                "title": "📊 NVIDIA – Daily % Change Over Time"}])
                ]
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="📊 NVIDIA – Daily Percentage Change in Closing Price",
            font=dict(size=20, color="white"),
            x=0.5
        ),
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor="#34495e",
            showline=True,
            linecolor="#7f8c8d",
            rangeslider=dict(visible=True, thickness=0.05),
            type="date"
        ),
        yaxis=dict(
            title="Daily % Change",
            showgrid=True,
            gridcolor="#34495e",
            zeroline=True,
            zerolinewidth=1.5,
            zerolinecolor="#95a5a6"
        ),
        plot_bgcolor="#1e272e",
        paper_bgcolor="#1e272e",
        font=dict(color="white"),
        hovermode="x unified",
        margin=dict(t=110, b=60, l=60, r=60),
        height=650
    )

    fig.show()

def volume_act_analysis(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Volume_NVDA'],
        mode='lines',
        name='Volume',
        line=dict(color='#1abc9c', width=2.2),
        hovertemplate='📅 %{x}<br>📦 Volume: %{y}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df[df['Unusual_Activity']]['Date'],
        y=df[df['Unusual_Activity']]['Volume_NVDA'],
        mode='markers',
        name='Unusual Activity',
        marker=dict(color='#e74c3c', size=8, symbol='circle'),
        hovertemplate='📅 %{x}<br>🚨 Unusual Volume: %{y}<extra></extra>'
    ))

    fig.update_layout(
        updatemenus=[dict(
            type="buttons",
            direction="right",
            x=0,
            xanchor="left",
            y=1.15,
            yanchor="top",
            bgcolor="#34495e",
            bordercolor="#7f8c8d",
            borderwidth=1,
            font=dict(color="white", size=13),
            buttons=[
                dict(method="relayout", label="1Y",
                     args=[{"xaxis.range": [df['Date'].max() - pd.DateOffset(years=1), df['Date'].max()],
                            "title": "📊 NVIDIA – Volume Activity (1 Year)"}]),
                dict(method="relayout", label="5Y",
                     args=[{"xaxis.range": [df['Date'].max() - pd.DateOffset(years=5), df['Date'].max()],
                            "title": "📊 NVIDIA – Volume Activity (5 Years)"}]),
                dict(method="relayout", label="10Y",
                     args=[{"xaxis.range": [df['Date'].max() - pd.DateOffset(years=10), df['Date'].max()],
                            "title": "📊 NVIDIA – Volume Activity (10 Years)"}]),
                dict(method="relayout", label="All",
                     args=[{"xaxis.autorange": True,
                            "title": "📊 NVIDIA – Volume and Market Activity"}])
            ]
        )]
    )

    fig.update_layout(
        title=dict(
            text="📊 NVIDIA – Volume and Market Activity",
            font=dict(size=20, color="white"),
            x=0.5
        ),
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor="#34495e",
            linecolor="#7f8c8d",
            rangeslider=dict(visible=True, thickness=0.04),
            type="date"
        ),
        yaxis=dict(
            title="Trading Volume",
            showgrid=True,
            gridcolor="#34495e"
        ),
        plot_bgcolor="#1e272e",
        paper_bgcolor="#1e272e",
        font=dict(color="white"),
        hovermode="x unified",
        height=650,
        margin=dict(t=90, b=60, l=60, r=60)
    )

    fig.show()


