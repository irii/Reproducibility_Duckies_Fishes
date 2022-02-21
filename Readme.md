[![DOI](https://zenodo.org/badge/461684112.svg)](https://zenodo.org/badge/latestdoi/461684112)

# Duckies vs. Fish
Cheat-sheet for reproducing duckies vs. fish

## Docker Desktop
`````commandline
docker build -t re-duckies-fishes .
docker run --rm -e -v C:\OUTPUT_RM:/home/repro/output re-duckies-fishes

docker cp <Container-Id>:/home/repro/output/ .
`````

## Docker Engine only
`````commandline
docker build -t re-duckies-fishes .

docker run --env PREDICTION_COUNT=3 re-duckies-fishes

# Find Docker Container-Id
docker ps -aqf "name="

docker cp <Container-Id>:/home/repro/output/ .
`````

## OSX
````commandline
./osx_build.sh "/OUTPUT_FOLDER_PATH"
````

## Linux / Ubuntu
````commandline
./linux_build.sh "/OUTPUT_FOLDER_PATH"
````

## Windows Powershell
_Docker Desktop is required!_
````commandline
powershell -ExecutionPolicy Bypass -File .\win_build.ps1 "C:\OUTPUT_FOLDER_PATH"
````
