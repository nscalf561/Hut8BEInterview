To start, create a python3 venv, pip install -r requirements.txt.

`python3 -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`
In the root of the folder run:
`python main.py`

Now your fastAPI server should be up and running at localhost:8000.  There is one api endpoint, localhost:8000/calculate, which takes:
    hash_rate: Union[float, int] # in TH/s
    power_consumption: Union[float, int] # in W
    electricity_cost: Union[float, int] # in USD/kWh
    initial_investment: Union[float, int] # in USD
The return payload is modeled off the exepectations of the frontend.  


## Further Work:
Changes that should be made to this api before being production ready:
* Sourcing data: in some instances we are hardcoding information that should either be in a maintained config, or pulled from a reliable source of truth.  For instance, bitcoin block rewards, etc.  Many of these things likely already have a Hut8 internal source of truth we could pull from.
* I set up some api calls to handle things like network difficulty and btc price because those are very dynamic, but I'm not familiar with what the industry standard is for those data sources
* API Versioning, it's best practice to add versions onto api's so you can gracefully migrate big changes in an endpoint.



## ASSUMPTIONS:
There are a few assumptions used for this api's calculations, which would be easy to clear up in a conversation with a product owner.
* Rounding months is valid --- the average days/month has been rounded to 30, and years to 365, this was done for simplicity, but is naive to the current point in time, and the actually averages being slightly above those values
* If you never breakeven, we return 0 for the time to breakeven
* We only allow positive input values, I'm not sure if it ever makes sense for a value to be negative there
* Some types are pulled from the frontend, such as TH/s, W, USD/kWh, and USD
