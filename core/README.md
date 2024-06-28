# Core
Fortune Teller is primarily comprised of three main submodules.

## Trading Management
Contains many trading features such as:

* Standardized chart management
* Technical indicator management
* Order placement
* Position management
* Repository management (financial data providers)
* Broker management (third party that allows order placement and position management)

Read more in [./trading/](./trading).

## Tensorflow Integration
Contains a service-based pattern for tensorflow that adds modularization to your implementations. 
Also includes other awesome features such as:

* Parallel preprocessing of data and training with multiprocessing on one machine
* Seamless integration with the standardized command line pattern in the Utils section for quick alterations of the training process
* Tuning and training based on different hyperparameter selections seamlessly through the command line without changing a single line of code

Read more in [./tensorflow/](./tensorflow).

## Utilities
Many quality of life utilities are available via the utilities module. From standardizing environment management, commands line, database management, etc.

Read more in [./utils/](./utils).