# Configuration

Settings in Selva are handled through YAML files.
Internally it uses [strictyaml](https://pypi.org/project/strictyaml/) to parse the
yaml files in order to do the parsing in a safe and predictable way.

Settings files are located by default in the `configuration` directory with the
base name `settings.yaml`:

```
project/
├── application/
│   └── ...
└── configuration/
    ├── settings.yaml
    ├── settings_dev.yaml
    └── settings_prod.yaml
```

## Accessing the configuration

The configuration values can be accessed by injecting `selva.configuration.Settings`.


```python
from typing import Annotated
from selva.configuration import Settings
from selva.di import Inject, service


@service
class MyService:
    settings: Annotated[Settings, Inject]
```

The `selva.configuration.Settings` is a dict like object that can also be accessed
using property syntax:

```python
from selva.configuration import Settings

settings = Settings({"config": "value"})
assert settings["config"] == "value"
assert settings.config == "value"
```

### Typed settings

Since `strictyaml` is used to parse the yaml files, all values `str`s. However, we
can use `pydantic` and Selva dependency injection system to provide access to the
settings in a typed manner:

=== "application.py"

    ```python
    from pydantic import BaseModel
    from selva.configuration import Settings
    from selva.di import service
    
    
    class MySettings(BaseModel):
        int_property: int
        bool_property: bool
    
    
    @service
    def my_settings(settings: Settings) -> MySettings:
        return MySettings.model_validate(settings.my_settings)
    ```

=== "configuration/settings.yaml"

    ```yaml
    my_settings:
      int_property: 1
      bool_property: true
    ```

## Environment substitution

The settings files can include references to environment variables that takes the
format `${ENV_VAR:default_value}`. The default value is optional and an error will
be raised if neither the environment variable nor the default value are defined.

```yaml
required: ${ENV_VAR}         # required environment variable
optional: ${OPT_VAR:default} # optional environment variable
```

## Profiles

Optional profiles can be activated by settings the environment variable `SELVA_PROFILE`.
The framework will look for a file named `settings_${SELVA_PROFILE}.yaml` and merge
the values with the main `settings.yaml`. Values from the profile settings take
precedence over the values from the main settings.

As an example, if we define `SELVA_PROFILE=dev`, the file `settings_dev.yaml` will
be loaded. If instead we define `SELVA_PROFILE=prod`, then the file `settings_prod.yaml`
will be loaded.

## Environment variables

Settings can also be defined with environment variables whose names start with `SELVA__`,
where subsequent double undercores (`__`) indicates nesting (variable is a mapping).
Also, variable names will be lowercased.

For example, consider the following environment variables:

```dotenv
SELVA__PROPERTY=1
SELVA__MAPPING__PROPERTY=2
SELVA__MAPPING__ANOTHER_PROPERTY=3
```

Those variables will be collected as the following:

```python
{
    "property": "1",
    "mapping": {
        "property": "2",
        "another_property": "3",
    },
}
```