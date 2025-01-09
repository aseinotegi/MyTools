import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

# Carga los datos desde el archivo CSV
df = pd.read_csv('datos.csv')

# Obtén una lista de las variables en el archivo CSV
variables = [col for col in df.columns if ':' in col]

# Inicializa la aplicación Dash
app = dash.Dash(__name__)

# Define el diseño de la aplicación
app.layout = html.Div([
    html.H1("Dashboard de Variables de Máquina"),
    
    # Dropdown para seleccionar la variable
    dcc.Dropdown(
        id='variable-selector',
        options=[{'label': var, 'value': var} for var in variables],
        value=variables[0] if variables else None  # Valor predeterminado
    ),
    
    # Espacio para mostrar el valor actual de la variable seleccionada
    html.Div(id='variable-value')
])

# Callback para mostrar el valor actual de la variable seleccionada
@app.callback(
    Output('variable-value', 'children'),
    [Input('variable-selector', 'value')]
)
def update_variable_value(selected_variable):
    if selected_variable is None:
        return "Seleccione una variable"
    
    # Obtiene el valor más reciente de la variable seleccionada
    latest_value = df[selected_variable].iloc[-1]
    
    return f'Valor actual de {selected_variable}: {latest_value}'

if __name__ == '__main__':
    app.run_server(debug=True)
