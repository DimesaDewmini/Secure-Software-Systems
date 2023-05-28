import requests

headers = {
    'accept': 'application/json',
    'X-API-Key': 'a07051ed1a9bd160a369a026bb5b6731'
}

def predict_sqlinjection(input_val):
    # Set the base URL of your FastAPI application
    url = f'http://127.0.0.1:8000/predict/?input={input_val}' # Replace with your actual base URL
    
    # Send the POST request to the /predict/{input} endpoint
    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        # Process the JSON response
        return response.json()
    else:
        return f'Request failed with status code {response.status_code}'