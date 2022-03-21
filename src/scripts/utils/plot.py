import os
from datetime import datetime

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


def stacked_histogram(df,
                      feature,
                      groupby=None,
                      end=1,
                      bin_size=0.05,
                      opacity=1,
                      barmode='stack',
                      title='Distribution',
                      colors=None,
                      reorder=None,
                      use_custom_colors=False,
                      save=False,
                      file_path=None,
                      save_png=False,
                      size=(1980, 1080),
                      label_scale=1.5,
                      legend_name=None,
                      return_fig=False):
    fig = go.Figure()

    if groupby is None:
        fig.add_trace(go.Histogram(x=df[feature],
                                   histnorm='probability',
                                   xbins=dict(
                                       start=0,
                                       end=end,
                                       size=bin_size),
                                   name=feature if legend_name is None else legend_name,
                                   autobinx=False))
    else:
        for i, (emoji_key, df_ss) in enumerate(df.groupby(by=groupby)):
            fig.add_trace(go.Histogram(x=df_ss[feature],
                                       histnorm='probability',
                                       xbins=dict(
                                           start=0,
                                           end=end,
                                           size=bin_size),
                                       marker=dict(color=custom_colors[
                                           i if colors is None else colors[i]]) if use_custom_colors else None,
                                       autobinx=False,
                                       name=emoji_key))

    if reorder is not None:
        fig.data = [fig.data[r] for r in reorder]

    fig.update_layout(barmode=barmode,
                      title=title + ' of: {}'.format(feature),
                      legend=dict(font=dict(size=15)))

    fig.update_traces(opacity=opacity)

    fig.update_layout(legend=dict(font=dict(size=18 * label_scale)))
    fig.update_xaxes(tickfont=dict(size=14 * label_scale), title_font=dict(size=18 * label_scale))
    fig.update_yaxes(tickfont=dict(size=14 * label_scale), title_font=dict(size=18 * label_scale))

    if return_fig:
        return fig

    fig.show()

    if file_path is not None and save is True:
        plotly_save(fig, file_path, size, save_png=save_png)


def plot_position_histogram(positions, title=None,
                            save=False,
                            file_path=None,
                            save_png=False,
                            size=(1980, 1080),
                            label_scale=1.5):
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

    fig.update_layout(title_text=title, showlegend=False, legend=dict(font=dict(size=18 * label_scale)))
    fig.update_xaxes(tickfont=dict(size=14 * label_scale), title_font=dict(size=18 * label_scale))
    fig.update_yaxes(tickfont=dict(size=14 * label_scale), title_font=dict(size=18 * label_scale))

    fig.show()

    if file_path is not None and save is True:
        plotly_save(fig, file_path, size, save_png=save_png)


def descending_bar_plot(df, x, y, color=None, plot_top=None,
                        file_path=None,
                        save=False,
                        save_png=False,
                        size=(1980, 1080),
                        label_scale=1.5,
                        ):

    fig = px.bar(df,
                 x=x,
                 y=y,
                 color=color,
                 title='Emojis count'.format(),
                 barmode='group',
                 ).update_xaxes(categoryorder="total descending")

    if plot_top is not None:
        fig.update_layout(xaxis=dict(range=[-0.5, plot_top + 0.5]))
        # df = df.iloc[:plot_top, :]

    fig.update_layout(legend=dict(font=dict(size=18 * label_scale)))
    fig.update_xaxes(tickfont=dict(size=14 * label_scale), title_font=dict(size=18 * label_scale))
    fig.update_yaxes(tickfont=dict(size=14 * label_scale), title_font=dict(size=18 * label_scale))
    fig.show()

    if file_path is not None and save is True:
        plotly_save(fig, file_path, size, save_png=save_png)


def create_dir(file_path, filename_included=True):
    if not isinstance(file_path, list):
        path = os.path.dirname(file_path) if filename_included else file_path
        if not os.path.exists(path):
            os.makedirs(path)
    else:
        for i in range(1, len(file_path)):
            path = os.path.join(*file_path[:i])
            if not os.path.exists(path):
                os.makedirs(path)


def get_new_file_path(file_path, extension, use_date_suffix):
    if not isinstance(file_path, list):
        path = os.path.dirname(file_path)
        filename = file_path.split('\\')[-1]
    else:
        path = os.path.join(*file_path[:-1])
        filename = file_path[-1]

    ex = len(extension)
    if use_date_suffix:
        filename = filename + '_' + datetime.now().strftime("%d_%m_%Y %H-%M") + extension
    else:
        filename = filename + extension
        if os.path.exists(os.path.join(path, filename)):
            counter = 1
            filename = '{}_1{}'.format(filename[:-ex], extension)
            while True:
                filename = '{}{}{}'.format(filename[:-(ex + 1)],
                                           str(counter),
                                           extension)
                if not os.path.exists(os.path.join(path, filename)):
                    return os.path.join(path, filename)
                else:
                    counter += 1
        else:
            return os.path.join(path, filename)
    return os.path.normpath(os.path.join(path, filename))


def plotly_save(fig, file_path, size, save_png=False, use_date_suffix=False):
    print("Saving image:")
    create_dir(file_path)
    image_path = get_new_file_path(file_path, '.png', use_date_suffix)
    html_path = get_new_file_path(file_path, '.html', use_date_suffix)
    if size is None:
        size = (1980, 1080)

    if save_png:
        print(image_path)
        fig.write_image(image_path, width=size[0], height=size[1], engine='orca')

    print(html_path)
    fig.write_html(html_path)
