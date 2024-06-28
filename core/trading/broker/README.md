# Broker
A Broker is an integration to an API that allows placing/modifying/cancelling orders, managing positions, and equity.

## MetaTraderBroker ([./metatrader/](./metatrader/))
A very common broker called `MetaTrader5` has already been implemented that opens up the possibilities to use multiple brokers through one integration. 

## SimulationBroker ([./simulation](./simulation/))
A backtesting broker called `SimulationBroker` has also been implemented that allows for testing your strategies using a simulated feed of data with no hindsight emulating the feed of real-time data baked in. See [here](./simulation/).

**Note:** Should you choose to implement your own broker you can inherit the base `Broker` class found [here](./__init__.py) and implement the necessary functionality needed from your specific broker's API.

**Note:** The reason for the differentiation between brokers and data providers is that although many actual brokers provide financial data there are data providers that do not provide any trading services hence. Broker class instances will have a reference to a Repository which adds the data "read" functionalities in addition to the trade execution functionality that they provide.