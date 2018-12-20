#!/bin/bash

docker build -t log3c .

docker run -it log3c /bin/bash