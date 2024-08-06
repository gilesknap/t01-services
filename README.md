# Beamline t01 IOC Instances and Services

This repository holds the a definition of example beamline t01 IOC Instances and services. It is a example of how to deploy epics-containers IOCs using docker compose for those facilities that are not using Kubernetes. It can also deploy it's set of IOCs to a developer workstation for testing / experimentation.

The top level compose.yml file represents a set of IOCs and other services that would be deployed to a single IOC server.

For this example we have a single compose file. However, if you wanted to keep all IOCs for a beamline in a single repo but deploy to multiple servers, then each server could have its own named compose file, or possibly you could use a single compose file with a profile for each server.

## Initial Setup

First install Docker and Docker Compose. See https://docs.docker.com/compose/install/.

At DLS you need only run `module load docker-compose` to enable `docker compose` backed by the podman container engine. (see end of this page if you get errors)

Setup command line completion for docker compose (optional):
```bash
# these steps will make cli completion work for zsh
mkdir -p ~/.oh-my-zsh/completions
podman completion zsh > ~/.oh-my-zsh/completions/_podman

# these steps will make cli completion work for bash
mkdir -p ~/.local/share/bash-completion/completions
podman completion bash > ~/.local/share/bash-completion/completions/podman
```

## Local Developer Testing Environment

To launch a development environment on a workstation, including phoebus perform the following steps:

```bash
git clone git@github.com:gilesknap/t01-services.git
cd t01-services
source ./environment.sh
ec up -d
```

NOTE: -d detaches from the containers. You may omit this if you would prefer to follow the logs of all the containers - these combinded logs include a colour coded prefix to make them more legible.


## Experimenting
You can now use:

```bash
# use caget/put locally
export EPICS_CA_ADDR_LIST=127.0.0.1
caget -EA-TST-01:DET:MaxSizeX_RBV
# attach to logs of a service
ec logs -di-cam-01 -f
# stop a service
ec stop -di-cam-01
# attach to a service stdio
ec attach -di-cam-01
# exec a process in a service
ec exec -di-cam-01 bash
# delete a service (deletes the container)
ec down -di-cam-01
# create and launch a single service (plus its dependencies)
ec up -di-cam-01 -d
# close down and delete all the containers
# volumes are not deleted to preserve the data
ec down
```

# Deploy To Beamline Servers
To deploy IOCs to a server, clone this repo and run the following command from the repo root:

```bash
docker compose --profile deploy up -d
```

or for a multiple server repo:
```bash
docker compose --profile deploy -f my_server_01.yml up -d
```

IMPORTANT: if you are using docker then IOCs deployed this way will automatically be brought up again on server reboot. podman will not do this by default because it is running in user space - there are workarounds for this but podman is not recommended for this purpose.

The gold standard for orchestrating these containers in production is Kubernetes. See https://epics-containers.github.io/main/tutorials/setup_k8s.html. Although compose is really useful for development and testing, Kubernetes is far superior for managing services across a cluster of hosts.

# Compose goals

These goals for switching to compose (from bespoke code in the `ec` tool) have all been met:

- be as DRY as possible
- work with docker-compose controlling either docker or podman
- enable isolated testing where PVs are not availble to the whole subnet
- include separate profiles for:
  - local testing - including phoebus OPI
  - deployment to a beamline server - this would need either:
    - network host on the IOCs
    - a ca-gateway
- structure so that there is a compose file per server
- remove need for custom code/scripts to deploy/manage the IOCs
- also allow PV isolation on servers with a ca-gateway to enable access

# DLS Troubleshooting for docker compose module

Some users who have set up podman sockets in the past may get errors with `module load docker-compose`. If you do then do the following and then re-run it.
```bash
/dls_sw/apps/setup-podman/setup.sh
sed -i ~/.config/containers/containers.conf -e '/label=false/d' -e '/^\[containers\]$/a label=false'
```