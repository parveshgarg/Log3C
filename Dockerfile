FROM ubuntu:18.04

RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    curl \
    wget

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt


COPY lib/cascading_clustering.py /log3c/lib/cascading_clustering.py
COPY run.py /log3c/run.py
COPY lib/util.py /log3c/lib/util.py
COPY lib/__init__.py /log3c/lib/__init__.py


WORKDIR /log3c

CMD [ "/bin/bash" ]