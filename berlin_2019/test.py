from flask import Flask, request
app = Flask(__name__)

import collections

@app.route('/')
def hello_world():
    return f'''
<html><body>
<h2>DNA analyser</h2>
<form action="/analyse">
  DNA sequence:<br>
  <input type="text" name="dna" value="ATGC"><br>
  <input type="submit" value="Analyse">
</form> 

<p>Type a DNA sequence and press the button!</p>
</body>
</html>
'''

@app.route('/analyse', methods=['GET', 'POST'])
def analyse():
	dna = request.args['dna']
	counter = collections.Counter(dna)
	
	return f'''
	DNA base composition analysis:<br>
	{'<br/>'.join([str(b) + ' : ' + str(c) for b,c in counter.most_common()])} 

'''
