# Doxy

## Installation

```shell
pipx install git+https://git.goatpr0n.de/public/doxy.git
```

## Shell completion

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

## Configuration

Save the configuration file in `~/.config/doxy/config.yml`:
```yaml
root_directory: "/path/to/docker/services"
compose_executable: "/usr/bin/docker-compose"
```

## Usage

```
Usage: doxy [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  control
  list
```

To add parameters to an control argument use "--" to end the *Doxy* parameter evaluation and pass
them to *docker-compose*.
