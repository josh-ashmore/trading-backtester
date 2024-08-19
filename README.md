# Trading Backtester
A repository for backtesting trades.

## Description
I aimed to create a backtester which is modular, generic but highly customisable by the user. It should be well defined and fully serialisable both on the input and output so as to be scheduled and clean outputs returned through whatever API or lambda is designed for the process.

## Backtester Design
The backtester's main module is an orchestrator, which takes a Pydantic user input model containing information for different categories of data and outputs a backtester output model.

## Backtester Input

### Market Data
data
    A model defining the market data required to run the orchestrator.
signal_data
    Additional data which can be applied to the market data model which is supplied and calculated manually.
market_data_settings <- is this needed?>
    High level market data settings including spot_date, underlying and currencies to run.

### Trade Data
trade_data_settings
    A definition of a base trade object which we will use to fill in the trade object.
trade_rule_settings (list)
    A list of trade rule settings: each setting object contains a further list of both trade rules (when the trade should be executed) and execution rules (how the trade should be executed)

### Initialised/Overlay Settings
account
    A model for the starting account (defining currency and initial balance to be traded)
configs
    A list of configurations which act as layers on top of the orchestrator, allowing for highly customisable backtesting. This will be discussed more below.

## Configurations and Managers

A selection of configurations are allowed as input (described below) which when passed into the orchestrator become managers with respective methods for being called through the process.

Market Data Configuration
    This config can manage how market data is sourced, transformed, and used within the backtester.
Execution Configuration
    This config specifies execution strategies such as limit orders, market orders, or algorithms like VWAP.
Portfolio Configuration
    This config controls the portfolio's overall strategy, asset allocation, and rebalancing rules.
Risk Management Configuration
    This config handles risk parameters like position sizing, stop-loss levels, and risk limits.
Optimisation Configuration
    This config controls how the backtester should optimise the strategy, it will find the most optimal set of inputs given parameter ranges and a desired metric condition.
Stream Configuration
    This config controls how streams of trades can be placed and rolled automatically without the requirement for duplicating trade and execution rules.

## Trade Rules and Execution Rules

### Trade Rules
We allow the user to provide two comparison fields with a logic operator between them. The comparison field allows the user to define where the data for comparison comes from (i.e. a trade field, market data, date value, portfolio field, a static value, etc.).

### Execution Rules
Allows the user to define how provided trades for execution are handled, with logic for basic buying and selling (positive and negative directions for the portfolio) and spread (defining a desired total cost if the strategy contains writing options and initial margin is not required). Alongside this a list of trade objects which are requested to be traded are defined (e.g. BUY a Call and SELL a Put). Rules and logic for how the notional amount for executed trades on each day are calculated exist here also.

## Backtester Orchestrator

The orchestrator takes the provided input, creates managers for provided configurations and utilises each at the necessary levels (optimiser immediately, risk manager at trade execution, etc.). At the high level, we iterate over each provided date, check the requirements to manage existing trades and open new trades (all managed within a trade schedule) at each day and update the account if neccessary.

## Backtester Output

The trade schedule and account are both used together to evaluate a series of metrics (drawdown, sharpe ratio, returns, etc.)
