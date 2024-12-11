from flask import Flask, render_template, request, jsonify
from src.agent.retrievers.retriever_baseline import retrieve_subsidies

app = Flask(__name__)

# Create templates directory at src/ui/templates/
# Create static directory at src/ui/static/

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        user_input = request.form.get('query', '')
        if not user_input:
            return jsonify({'error': 'Voer eerst een zoekopdracht in.'}), 400

        # Retrieve results
        results = retrieve_subsidies(user_input)
        
        # Process results for display
        processed_results = []
        for node in results:
            metadata = node.node.metadata
            processed_results.append({
                'title': metadata.get('title', 'Untitled'),
                'score': round(node.score, 3),
                'status': metadata.get('Status', 'N/A'),
                'bereik': metadata.get('Bereik', 'N/A'),
                'deadline': metadata.get('Deadline', 'N/A'),
                'min_bijdrage': metadata.get('Minimale bijdrage', 'N/A'),
                'max_bijdrage': metadata.get('Maximale bijdrage', 'N/A'),
                'budget': metadata.get('Budget', 'N/A'),
                'text': node.node.text,
                'laatste_wijziging': metadata.get('Laatste wijziging', 'N/A'),
                'aanvraagtermijn': metadata.get('Aanvraagtermijn', 'N/A'),
                'indienprocedure': metadata.get('Indienprocedure', 'N/A')
            })
        
        return jsonify({
            'results': processed_results,
            'count': len(processed_results)
        })

    except Exception as e:
        return jsonify({'error': f'Er is een fout opgetreden: {str(e)}'}), 500

if __name__ == '__main__':
    # Create the templates directory
    import os
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    
    # Create the HTML template
    template_content = '''
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subsidie Zoeker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">🔍 Subsidie Zoeker</h1>
        
        <div class="row justify-content-center mb-4">
            <div class="col-md-8">
                <p class="text-center">
                    Zoek naar beschikbare subsidies door uw zoekopdracht hieronder in te voeren.<br>
                    <em>Bijvoorbeeld: "Ik zoek naar subsidies voor duurzame energie in Gelderland"</em>
                </p>
            </div>
        </div>

        <div class="row justify-content-center mb-4">
            <div class="col-md-8">
                <form id="searchForm">
                    <div class="mb-3">
                        <textarea 
                            class="form-control" 
                            id="queryInput" 
                            rows="4" 
                            placeholder="Bijvoorbeeld: Ik zoek naar innovatie subsidies voor het MKB in de provincie Overijssel..."
                        ></textarea>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary">Zoeken</button>
                    </div>
                </form>
            </div>
        </div>

        <div id="results" class="row justify-content-center">
            <div class="col-md-8">
                <div id="loading" class="text-center d-none">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Laden...</span>
                    </div>
                    <p>Bezig met zoeken...</p>
                </div>
                <div id="resultsCount" class="mb-4"></div>
                <div id="resultsList"></div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const query = document.getElementById('queryInput').value;
            const loading = document.getElementById('loading');
            const resultsCount = document.getElementById('resultsCount');
            const resultsList = document.getElementById('resultsList');
            
            loading.classList.remove('d-none');
            resultsCount.innerHTML = '';
            resultsList.innerHTML = '';
            
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `query=${encodeURIComponent(query)}`
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultsCount.innerHTML = `<h3>🎯 Gevonden resultaten: ${data.count}</h3>`;
                    
                    data.results.forEach(result => {
                        const resultHtml = `
                            <div class="card mb-3">
                                <div class="card-header">
                                    📋 ${result.title} - Score: ${result.score}
                                </div>
                                <div class="card-body">
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <p><strong>Status:</strong> ${result.status}</p>
                                            <p><strong>Bereik:</strong> ${result.bereik}</p>
                                            <p><strong>Deadline:</strong> ${result.deadline}</p>
                                        </div>
                                        <div class="col-md-6">
                                            <p><strong>Min. bijdrage:</strong> ${result.min_bijdrage}</p>
                                            <p><strong>Max. bijdrage:</strong> ${result.max_bijdrage}</p>
                                            <p><strong>Budget:</strong> ${result.budget}</p>
                                        </div>
                                    </div>
                                    
                                    <h5>Relevante informatie:</h5>
                                    <p>${result.text}</p>
                                    
                                    <hr>
                                    <h5>Extra details:</h5>
                                    <p><strong>Laatste wijziging:</strong> ${result.laatste_wijziging}</p>
                                    <p><strong>Aanvraagtermijn:</strong> ${result.aanvraagtermijn}</p>
                                    <p><strong>Indienprocedure:</strong> ${result.indienprocedure}</p>
                                </div>
                            </div>
                        `;
                        resultsList.innerHTML += resultHtml;
                    });
                } else {
                    resultsList.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                }
            } catch (error) {
                resultsList.innerHTML = `<div class="alert alert-danger">Er is een fout opgetreden: ${error}</div>`;
            } finally {
                loading.classList.add('d-none');
            }
        });
    </script>
</body>
</html>
    '''
    
    # Write the template file
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(template_content)
    
    # Create CSS file
    css_content = '''
        .card {
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card-header {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        #loading {
            margin: 2rem 0;
        }
    '''
    
    # Write the CSS file
    with open(os.path.join(static_dir, 'style.css'), 'w') as f:
        f.write(css_content)
    
    app.run(debug=True, port=5000)
