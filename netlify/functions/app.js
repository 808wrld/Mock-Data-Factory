// app.js - Netlify Function
const { spawn } = require('child_process');
const path = require('path');

// Handler for Netlify Functions
exports.handler = async function(event, context) {
  // We'll use a simple approach for this demo
  // In a production environment, you'd want to use a more robust solution
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'text/html',
    },
    body: `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mock Data Factory</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
          body { padding-top: 20px; }
          .container { max-width: 960px; }
          .field-row { margin-bottom: 15px; border: 1px solid #e9ecef; padding: 15px; border-radius: 5px; }
          .preview-container { margin-top: 20px; }
          .custom-values { display: none; }
          .blank-percentage { display: none; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1 class="mb-4">Mock Data Factory</h1>
          <p class="lead">This is a serverless version of the Mock Data Factory application.</p>
          
          <div class="alert alert-info">
            <h4>Important Note</h4>
            <p>This application is deployed as a static site on Netlify. For full functionality, please run the application locally following these steps:</p>
            <ol>
              <li>Clone the repository</li>
              <li>Create a virtual environment: <code>python -m venv venv</code></li>
              <li>Activate the environment: <code>venv\\Scripts\\activate</code> (Windows) or <code>source venv/bin/activate</code> (Unix)</li>
              <li>Install dependencies: <code>pip install -r requirements.txt</code></li>
              <li>Run the application: <code>python app.py</code></li>
              <li>Open your browser and navigate to <code>http://localhost:5000</code></li>
            </ol>
          </div>
          
          <h3>Features</h3>
          <ul>
            <li>Generate realistic mock data for testing and development</li>
            <li>Support for various data types (names, emails, addresses, etc.)</li>
            <li>Export to CSV, JSON, XML, SQL, and Excel formats</li>
            <li>Customizable field types and data generation options</li>
            <li>Preview data before generating full datasets</li>
          </ul>
          
          <div class="mt-4">
            <a href="https://github.com/808wrld/Mock-Data-Factory.git" class="btn btn-primary">View on GitHub</a>
          </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
      </body>
      </html>
    `
  };
};
