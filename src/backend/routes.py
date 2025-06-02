from flask import Flask, render_template
import pandas
import plotly.express

app = Flask(__name__)

@app.route('/')
def notdash():
   df = pandas.DataFrame({
      'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges', 'Bananas'],
      'Amount': [4, 1, 2, 2, 4, 5],
      'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
   })
   fig = plotly.express.bar(df, x='Fruit', y='Amount', color='City',    barmode='group')
   #graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
   graphJSON = fig.to_json()
   return render_template('notdash.html', graphJSON=graphJSON)