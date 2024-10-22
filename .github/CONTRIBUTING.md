# Program Structure

If a new module be added into FBCB_Basic, you must change the `config.py`, append a new class variable named with your module name to control if your module is enabled in **Config** class like `name: bool = False`.
After that, you need to create a new class inheriting `baseConfig`, which provide two functions `load()` and `save()` to communicate with configuration file. Then, build your own class (usually named "nameConfig") follow MCDR guide for class `Serializable`.

All submodule will be construct as a python class, which will be import into `__init__.py` and register into the plugin, and MUST has below **Class Variables**, **Instance Variables**, and **Instance Functions**:

## Class Variables

1. MODULE_NAME \
    A unique name in FBCB_Basic, also used in `Config`.

2. CONFIG_FILENAME \
    The filename which this module will storage all of it's configurations into it. And it will be saved in `config/fbcb_basic/{CONFIG_FILENAME}`

3. COMMAND_PREFIX \
    The root command you will use to control your module in MCDR and in game. It will be registered into plugin and used as `!!fbcb {COMMAND_PREFIX}`

4. ROOT_ACTION \
    A simple sentence to describe what action will be executed while receive command: `!!fbcb {COMMAND_PREFIX}`

5. ROOT_HELP \
    A simple sentence will be show to prompt users how to check the help message of your module (mostly is `!!fbcb {COMMAND_PREFIX} help`), and will be shown while receive command: `!!fbcb help` with other modules.

## Instance Variables

1. helpNode \
    FBCB_Basic will redirect a command `!!fbcb help {COMMAND_PREFIX}` to this command Node, which will widely used to show the help message for the module.

## Instance Functions

1. on_player_joined(self, server: ServerInterface, player, info: Info) \
    If module is enabled, this function will be called as it register this event listener into MCDR.

2. register_command(self, commandRoot) \
    FBCB_Basic will call this function and pass the commandRoot `!!fbcb` , let module register it's own command Nodes to the root.
