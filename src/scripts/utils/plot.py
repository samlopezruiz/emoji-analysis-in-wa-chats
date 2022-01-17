from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px


custom_colors = [
    '#1f77b4',  # muted blue
    '#2ca02c',  # cooked asparagus green
    '#ff7f0e',  # safety orange
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'  # blue-teal
]


def stacked_histogram(df, feature, groupby, end=1, bin_size=0.05):
    fig = go.Figure()
    for i, (emoji_key, df_ss) in enumerate(df.groupby(by=groupby)):
        fig.add_trace(go.Histogram(x=df_ss[feature],
                                   histnorm='probability',
                                   xbins=dict(
                                       start=0,
                                       end=end,
                                       size=bin_size),
                                   autobinx=False,
                                   name=emoji_key))

    fig.update_layout(barmode='stack',
                      title='Distribution for top emojis of: {}'.format(feature),
                      legend=dict(font=dict(size=15)))
    fig.update_traces(opacity=1)
    fig.show()

def plot_position_histogram(positions, title=None):
    fig = make_subplots(rows=2,
                        cols=2,
                        subplot_titles=("Position in words", "Relative position in words",
                                        "Position in letters", "Relative position in letters"))

    fig.add_trace(
        go.Histogram(x=positions['pos_in_words'],
                     xbins=dict(
                         size=1),
                     name='pos_in_words'),
        row=1, col=1
    )

    fig.add_trace(
        go.Histogram(x=positions['rel_pos_in_words'],
                     xbins=dict(
                         start=0,
                         end=1,
                         size=0.05),
                     autobinx=False,
                     name='rel_pos_in_words'),
        row=1, col=2
    )

    fig.add_trace(
        go.Histogram(x=positions['pos_in_letters'],
                     xbins=dict(
                         size=1),
                     name='pos_in_letters'),
        row=2, col=1
    )

    fig.add_trace(
        go.Histogram(x=positions['rel_pos_in_letters'],
                     xbins=dict(
                         start=0,
                         end=1,
                         size=0.05),
                     name='rel_pos_in_letters'),
        row=2, col=2
    )

    fig.update_layout(title_text=title,
                      showlegend=False)
    fig.show()


def descending_bar_plot(df, x, y, color=None, plot_top=None):

    fig = px.bar(df,
                 x=x,
                 y=y,
                 color=color,
                 title='Emojis count'.format(),
                 text_auto=True).update_xaxes(categoryorder="total descending")

    if plot_top is not None:
        fig.update_layout(xaxis=dict(range=[-0.5, plot_top+0.5]))
        # df = df.iloc[:plot_top, :]

    fig.update_layout(xaxis=dict(tickfont=dict(size=20)))
    fig.show()