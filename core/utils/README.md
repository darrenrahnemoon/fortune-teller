# Utilities

Utility functions and classes are grouped based on concern i.e. anything related to the concern of collections (list of dicts) is encapsulated in the `collection` directory. 

If collections require an implementation of a special feature for example for command line interfaces (say pretty printing, etc.) they will contain a `command.py` file implementing the functionality in command sessions.

Some useful utilities are:

# Command Sessions ([command.py](./command.py))
Used extensively around this framework to simplify writing CLI args and options, command sessions allow reusing args and options across multiple commands by mixing in different command sessions together. 

Managing logging and environment/stage is already baked into the `CommandSession` class.
See [LoggingCommandSessionMixin](./logging/command.py) for available args.
See [EnvironmentCommandSession](./environment/command.py) for available args.

```python
class CookLasagnaCommandSession(CommandSession):
	def setup(self):
		super().setup()
		self.parser.add_argument('--for', default = 'Garfield')
		self.parser.add_argument('--abort', action = BooleanOptionalAction)

	def run(self):
		super().run()

		if self.args.abort:
			print("Abort! Abort!")
			return

		print(f"Cooking for {self.args.for}")
```

# Test Management ([test/](./test/README.md))
Adds a functional pattern for writing tests similar to mocha, chai libraries. Read more [here](./test/README.md).

# Serializers ([serializer.py](./serializer.py))
Standardizes the flow of serializing data and deserializing data in the entire framework by implementing a base `Serializer` class that has a `serialize` and `deserialize` method. You can extend this class to implement your own serializers as well.

```python
from fortune_teller.core.utils.serializer import Serializer
from dataclasses import dataclass

@dataclass
class MySerializer(Serializer):
	def serialize(self, deserialized_value):
		# Serialize the value

	def deserialize(self, serialized_value):
		# Deserialize the value
```

# Timestamps ([time.py](./time.py))
Standardizes timestamp management by normalizing any timestamp-like data into a `pandas.Timestamp`.

# Dictionary ([dict.py](./dict.py))
Adds support for recursive (nested) dictionaries.

# DataFrame Containers ([dataframe_container.py](./dataframe_container.py))
Wrapper around `pandas.DataFrame` that DRYs out common logic between `Charts` and `Indicators`. Read more about them [here](../trading/chart/README.md).
