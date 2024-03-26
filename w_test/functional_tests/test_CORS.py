from flask import Flask, render_template_string, Response
import requests



#0v1# JC  Dec  2, 2023  Setup

"""
    RAW CORES TESTS
"""



app = Flask(__name__)


@app.route('/call_from_local')
def index():
    # Perform the request to the FastAPI server
    url = "http://127.0.0.1:8008/api/v1/case/case_chart_data_v1/square_data"
    url="https://core.epventures.co/api/v1/case/MarnerHoldingsB/butterfly_data"
    response = requests.get(url)
    response_text = response.text

    # HTML template with the response embedded
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Test CORS</title>
    </head>
    <body>
        <h1>Response from FastAPI server:</h1>
        <p>{response_text}</p>
    </body>
    </html>
    """

    # Render the HTML template with the response
    return render_template_string(html_template)

@app.route('/NORMAL')
def indexrootNORMAL():
    # HTML template with embedded JavaScript for AJAX request
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Test CORS</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
            $(document).ready(function() {
                // Make an AJAX GET request to the FastAPI server
                $.get("https://core.epventures.co/api/v1/case/MarnerHoldingsB/butterfly_data", function(data) {
                    // Display the response in 'response-div'
                    document.getElementById('response-div').innerText = JSON.stringify(data);
                }).fail(function() {
                    // Handle error
                    document.getElementById('response-div').innerText = 'Failed to get response';
                });
            });
        </script>
    </head>
    <body>
        <h1>Response from FastAPI server:</h1>
        <div id="response-div">Loading...</div>
    </body>
    </html>
    """

    # Render the HTML template
    return render_template_string(html_template)


@app.route('/')
def indexroot():
    # HTML template with embedded JavaScript for AJAX request
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="referrer" content="strict-origin-when-cross-origin">
        <title>Test CORS</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
            $(document).ready(function() {
                // Make an AJAX GET request to the FastAPI server with custom headers
                $.ajax({
                    url: "https://core.epventures.co/api/v1/case/MarnerHoldingsB/butterfly_data",
                    type: "GET",
                    headers: {
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Encoding": "gzip, deflate, br",  // Note: Browsers may not allow setting this header
                        "Accept-Language": "en-US,en;q=0.9",
                        "Connection": "keep-alive",
                        "Host": "core.epventures.co",  // Note: Browsers may not allow setting this header
                        "Origin": "http://127.0.0.1:3000",  // Note: Origin header is controlled by the browser
                        "Referer": "http://127.0.0.1:3000/",  // Note: Browsers may not allow setting this header
                        "User-Agent": "Your User Agent",  // Note: Browsers may not allow setting this header
                        // Add other headers as necessary
                    },
                    success: function(data) {
                        // Display the response in 'response-div'
                        document.getElementById('response-div').innerText = JSON.stringify(data, null, 2);
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        // Handle error
                        document.getElementById('response-div').innerText = 'Failed to get response: ' + errorThrown;
                    }
                });
            });
        </script>
    </head>
    <body>
        <h1>Response from FastAPI server:</h1>
        <div id="response-div">Loading...</div>
    </body>
    </html>
    """

    # Render the HTML template with additional headers
    response = Response(render_template_string(html_template))
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


@app.route('/')
def indexroot_axios():
    # HTML template with embedded JavaScript for AJAX request
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="referrer" content="strict-origin-when-cross-origin">
        <title>Test CORS</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
            $(document).ready(function() {
                // Make an AJAX GET request to the FastAPI server with custom headers
                $.ajax({
                    url: "https://core.epventures.co/api/v1/case/MarnerHoldingsB/butterfly_data",
                    type: "GET",
                    headers: {
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Encoding": "gzip, deflate, br",  // Note: Browsers may not allow setting this header
                        "Accept-Language": "en-US,en;q=0.9",
                        "Connection": "keep-alive",
                        "Host": "core.epventures.co",  // Note: Browsers may not allow setting this header
                        "Origin": "http://127.0.0.1:3000",  // Note: Origin header is controlled by the browser
                        "Referer": "http://127.0.0.1:3000/",  // Note: Browsers may not allow setting this header
                        "User-Agent": "Your User Agent",  // Note: Browsers may not allow setting this header
                        // Add other headers as necessary
                    },
                    success: function(data) {
                        // Display the response in 'response-div'
                        document.getElementById('response-div').innerText = JSON.stringify(data, null, 2);
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        // Handle error
                        document.getElementById('response-div').innerText = 'Failed to get response: ' + errorThrown;
                    }
                });
            });
        </script>
    </head>
    <body>
        <h1>Response from FastAPI server:</h1>
        <div id="response-div">Loading...</div>
    </body>
    </html>
    """

    # Render the HTML template with additional headers
    response = Response(render_template_string(html_template))
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


if __name__ == '__main__':
    app.run(debug=True)