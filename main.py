from twelvedata import TDClient
import dash
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from twelvedata import TDClient
import dash
from dash import dcc, html, callback, Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots

td = TDClient(apikey="???????????????")

# Create the Dash app
app = dash.Dash(__name__, title='Stock Price Analyzer')

def create_figure(symbol):
    """Create the figure for the given stock symbol"""
    ts = td.time_series(
        symbol=symbol,
        outputsize=75,
        interval="1day",
    )

    # Get the data as a dataframe
    df = ts.as_pandas()

    # Sort by date (oldest first) to ensure proper moving average calculation
    df = df.sort_index()

    # Calculate moving averages
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()

    # Create figure with secondary y-axis for volume
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]],
        row_heights=[0.7, 0.3]
    )

    # Add price traces on top subplot
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['open'],
            mode='lines',
            name='Open',
            line=dict(color='green', width=1),
            hovertemplate='%{x|%Y-%m-%d}<br>Open: $%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['close'],
            mode='lines',
            name='Close',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='%{x|%Y-%m-%d}<br>Close: $%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['high'],
            mode='lines',
            name='High',
            line=dict(color='orange', width=1, dash='dot'),
            hovertemplate='%{x|%Y-%m-%d}<br>High: $%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['low'],
            mode='lines',
            name='Low',
            line=dict(color='red', width=1, dash='dot'),
            hovertemplate='%{x|%Y-%m-%d}<br>Low: $%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    # Add moving averages
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MA20'],
            mode='lines',
            name='MA 20',
            line=dict(color='purple', width=2),
            hovertemplate='%{x|%Y-%m-%d}<br>MA20: $%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MA50'],
            mode='lines',
            name='MA 50',
            line=dict(color='brown', width=2),
            hovertemplate='%{x|%Y-%m-%d}<br>MA50: $%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    # Add volume on bottom subplot
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['volume'],
            name='Volume',
            marker=dict(color='lightblue', line=dict(color='blue', width=0.5)),
            hovertemplate='%{x|%Y-%m-%d}<br>Volume: %{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_yaxes(title_text='Price ($)', row=1, col=1)
    fig.update_yaxes(title_text='Volume', row=2, col=1)
    fig.update_xaxes(title_text='Date', row=2, col=1)

    fig.update_layout(
        title=f'{symbol} Stock Price Analysis',
        hovermode='x unified',
        template='plotly_white',
        height=700,
        showlegend=True
    )
    
    return fig

# Define the app layout
app.layout = html.Div([
    html.H1('Stock Price Analyzer'),
    html.Div([
        html.Label('Stock Symbol:'),
        dcc.Input(
            id='symbol-input',
            type='text',
            placeholder='Enter stock symbol (e.g., MSFT)',
            value='MSFT',
            style={'marginRight': '10px', 'padding': '5px', 'fontSize': '16px'}
        )
    ], style={'marginBottom': '20px'}),
    dcc.Graph(id='price-chart')
])

@callback(
    Output('price-chart', 'figure'),
    Input('symbol-input', 'n_submit'),
    State('symbol-input', 'value')
)
def update_chart(n_submit, symbol):
    if not symbol:
        symbol = 'MSFT'
    return create_figure(symbol.upper())

if __name__ == '__main__':
    app.run(debug=True)

