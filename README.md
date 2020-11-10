# github2gitlab

### Installation/Setup

It is recommended to install the python3 requirements in a virtual environment:

`pip install -r requirements.txt`

Copy the `example_config.py` to `config.py` and change the fields to match your configuration.

You will need an API token from GitHub with the ability to read repositories.

### Usage

The main script has an argparser for specifying the user.

`python3 github2gitlab.py --help`

#### Example

`python3 github2gitlab.py --user cloudy`

### TODO

- Code cleanup
- Add backwards support
- make sure readme is the filename, not repo name, also add that as optional
- input sanitization/check if users are valid
- Add support for private github repositories
- Flag to preserve last commit date if appending source repository URL (optional)
- Git credential management (prevent conflicts if using an archival account/auth)
- add batch users/multi-threading support
- ...
