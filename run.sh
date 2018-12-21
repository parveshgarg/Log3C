#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
DIR="$( cd "$( dirname "${SOURCE}" )" >/dev/null && pwd )"


usage() {
  echo "
Builds and runs Log3C in a docker container

Usage: $0 [-?|-h]
       $0 -m shell [-s SEQ_FOLDER] [-k KPI_PATH] [-o OUTPUT_PATH] [-r REP_PATH]
       $0 -m run {-s SEQ_FOLDER} {-k KPI_PATH} {-o OUTPUT_PATH} {-r REP_PATH}

Options:
  -? | -h         Prints this help message

  -m shell        Runs the container in the shell mode, log3c can be then manually triggered
                  as python3 run.py [options]. This is the default mode.

  -m run          Will run log3c inside docker container. All other options are required for this.

  -s SEQ_FOLDER   Folder of log sequence matrix files on your local. Will be mounted inside docker.

  -k KPI_FILE     Path of KPIs file on your local. Will be mounted inside docker.

  -o OUTPUT_PATH  Folder for saving output clusters of data on you local. Will be mounted inside docker.

  -r REP_PATH     Folder for saving all representatives on your local. Will be mounted inside docker.
"
  exit 0
}

unset MODE SEQ_FOLDER KPI_FILE OUTPUT_PATH REP_PATH

# defaults
MODE='shell'
APP='/bin/bash'
REQUIRED=false

DOCKER_FLAGS='-it '

while getopts 'm:s:k:o:r:?h' opt
do
  case ${opt} in
    m) MODE=$OPTARG ;;
    s) SEQ_FOLDER=$OPTARG ;;
    k) KPI_FILE=$OPTARG ;;
    o) OUTPUT_PATH=$OPTARG ;;
    r) REP_PATH=$OPTARG ;;
    h|?|:) usage ;; esac
done

# if mode is run - all other parameters become required
if [[ ${MODE} == 'run' ]]; then
  APP='/usr/bin/python3 /log3c/run.py'
  REQUIRED=true
  DOCKER_FLAGS='-d '
fi

test_required() {
  if [[ -z $1 ]]; then
    echo "One or more of required parameters is missing"
    usage
  fi
}

add_volume_to_docker_flags() {
  DOCKER_FLAGS="$DOCKER_FLAGS -v $1:$2 "
}

get_absolute_path() {
  if [[ -d "$1" ]]; then
    local DIR=$1
    ABSOLUTE_PATH="$( cd ${DIR} >/dev/null && pwd )"
  elif [[ -f "$1" ]]; then
    local DIR=$(dirname $1)
    local FILE=$(basename $1)
    ABSOLUTE_PATH="$( cd ${DIR} >/dev/null && pwd)/$FILE"
  fi
}

if [[ ${REQUIRED} = true ]]; then
  test_required ${SEQ_FOLDER}
  test_required ${KPI_FILE}
  test_required ${OUTPUT_PATH}
  test_required ${REP_PATH}
fi

# mount volumes
if [[ -n ${SEQ_FOLDER} ]]; then
  get_absolute_path ${SEQ_FOLDER}
  add_volume_to_docker_flags ${ABSOLUTE_PATH} "/seq_folder"
fi

if [[ -n ${OUTPUT_PATH} ]]; then
  get_absolute_path ${OUTPUT_PATH}
  add_volume_to_docker_flags ${ABSOLUTE_PATH} "/output"
fi

if [[ -n ${REP_PATH} ]]; then
  get_absolute_path ${REP_PATH}
  add_volume_to_docker_flags ${ABSOLUTE_PATH} "/reps"
fi

if [[ -n ${KPI_FILE} ]]; then
  get_absolute_path $KPI_FILE
  KPI_FILE_DIR="$(dirname $ABSOLUTE_PATH)"
  add_volume_to_docker_flags ${KPI_FILE_DIR}/ "/kpis"
fi

echo "Building docker image"
docker build -t log3c ${DIR}

COMMAND="docker run ${DOCKER_FLAGS} log3c ${APP}"

echo $COMMAND

eval ${COMMAND}
