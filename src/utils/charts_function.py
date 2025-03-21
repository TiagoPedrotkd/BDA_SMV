import plotly.graph_objects as go
from IPython.display import clear_output


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
            width=2160,
            plot_bgcolor="#1e272e",
            paper_bgcolor="#1e272e",
            showlegend=True
        )

        fig.show()