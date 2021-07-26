# ABM
This project was my first big Agent Based Computational Economic Model 
## Usage
Run `python main.py`
## Details
This is a model built mostly from New Keynesian foundations as specified in Jordi Galí's **Monetary Policy, Inflation and the Business Cycle**,
although I've taken liberty to extend and modify it in places and fill in gaps to adapt it for an ABCE type model. Agents perform intertemporal optimisation based on utility functions.
In the future I'd like to extend the horizon over which they plan, I received issues when doing this earlier.

I built this mostly to have fun and learn at the same time, and I was able to test friedman's k-rule for inflation targeting, it was inefective in the model and
the QTM theory of inflation was inaccuarate for predicting inflation.

In the future, I'd like to remake the model, carefully document my steps and amend features I'd like to change so I can make analyses like the above but with
more confidence in what the model is saying.
## Images
### Income distribution 
![](images/1.%20variable-income/incomes.png)
### Effect of lasting (but repeatedly unexpected) 50% income tax
![](images/2.%20variable%20prices/effect%20of%20lasting%20(but%20repeatedly%20unexpected)%2050%25%20income%20tax%20from%20t%3D50%20.png)
### Effect of one-off 50% wealth tax
![](images/2.%20variable%20prices/effect%20of%20one-off%2050%25%20wealth%20tax%20at%20t%3D50.png)
### Monetary aggregate targeting
![](images/3.%20monetary%20aggregate%20targering/monetary%20aggregate%20targeting%201.png)
![](images/3.%20monetary%20aggregate%20targering/monetary%20aggregate%20targeting%202.png)
