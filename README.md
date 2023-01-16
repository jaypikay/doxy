# Doxy

## Installation

```shell
pipx install git+https://github.com/jaypikay/doxy.git
```

## Shell completion

### Service name completion

By enabling shell completion the service names are *TAB-Completted* when using the `control`
command.

## Configuration

Save the configuration file in `~/.config/doxy/config.yml`:
```yaml
root_directory: "/path/to/docker/services"
compose_executable: "/usr/bin/docker-compose"
```

If you use `docker compose` instead of `docker-compose` you can use a wrapper script for
**docker-compose**
```shell
#!/bin/bash

/usr/bin/docker compose $@

exit 0
```

## Usage

```
Usage: doxy [OPTIONS] COMMAND [ARGS]...

Options:
  -f, --format [fancy|simple]  output formatting  [default: fancy]
  --help  Show this message and exit.

Commands:
  control  run docker-compose commands
  edit     edit the compose file
  list     list available services
  update   pull the latest service images and restart
```

## Examples

### List available services
```shell
$ doxy list
Available Services
├── service-1
├── service-2
├── other-service
└── my-service-demo
```

When `doxy -f simple` is used the output is easier to process by pipes.

### Start a service and detach
```shell
$ doxy control other-service up -d
```

### Edit a service
```shell
$ doxy edit service-2
```

### Bash

#### Alternative 1
Add this to ~/.bashrc:
```
eval "$(_DOXY_COMPLETE=bash_source doxy)"
```

#### Alternative 2
Save the script:
```shell
_DOXY_COMPLETE=bash_source doxy > ~/.doxy-complete.bash
```

Add this to ~/.bashrc:
```
. ~/.foo-bar-complete.bash
````

### Zsh

#### Alternative 1
Add this to ~/.zshrc:
```
eval "$(_DOXY_COMPLETE=zsh_source doxy)"
```

#### Alternative 2
Save the script:
```shell
_DOXY_COMPLETE=zsh_source doxy > ~/.doxy-complete.zsh
```

Add this to ~/.zshrc:
```
. ~/.foo-bar-complete.zsh
```
