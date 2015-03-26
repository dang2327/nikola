FROM python
MAINTAINER Danh Nguyen <dnguyen@drexel.edu>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y build-essential libxml2-dev libxslt-dev zlib1g-dev locales

ENV LANG en_US.UTF-8 

RUN wget https://github.com/jgm/pandoc/releases/download/1.13.2/pandoc-1.13.2-1-amd64.deb 
RUN dpkg -i /pandoc-1.13.2-1-amd64.deb

COPY requirements-extras.txt /
COPY requirements.txt /

RUN pip install -r /requirements-extras.txt

COPY . /nikola
WORKDIR /nikola
RUN python setup.py install

VOLUME ["/workdir"]

WORKDIR /workdir

ENTRYPOINT ["nikola"]
