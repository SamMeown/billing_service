# Billing MVP using Stripe - server

## How to run

1. Configure .env file with *Stripe* keys


### For Flask Server

2. Install dependencies

```
pip install -r requirements.txt
```

3. Export and run the application

```
export FLASK_APP=server.py
python3 -m flask run --port=4242
```


### For fastAPI Server

2. Install dependencies

```
pip install -r requirements_fastapi.txt
```

3. Run the application

```
python server_fastapi.py
```
