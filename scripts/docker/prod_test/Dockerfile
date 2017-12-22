FROM ubuntu:latest

#Keeping ubuntu up to date
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y dist-upgrade
RUN apt-get -y autoremove

#Install dependenceis



#Build Tools
RUN apt-get install -y build-essential cmake apt-utils autoconf software-properties-common curl nano

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs
RUN apt-get install -y git wget 
RUN mkdir -p /home/prod/mini-conda && cd /home/prod/mini-conda && wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh &&	bash Miniconda3-latest-Linux-x86_64.sh -bf && echo "export PATH=/root/miniconda3/bin:$PATH" >> ~/.bashrc && export PATH=/root/miniconda3/bin:$PATH && conda update -y conda

#Conda OpenCV dependency
RUN apt-get install -y python-qt4 libgtk2.0-0

#Here, either add options to create conda environment according to requirements, or create conda environment from .yml file
#which is present in scripts repo, at scripts/python/aspec_env.yml
#RUN conda env create -f /home/prod/scripts/python/aspec_env.yml &&
#	echo "source activate aspecenv" >> ~/.bashrc
#RUN source activate aspecenv


#YARN Install
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg |  apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update

#GRASS and SAGA Install. QGIS can be added, if necessary
#GRASS
RUN add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable

#SAGA
RUN add-apt-repository -y ppa:johanvdw/saga-gis

RUN apt-get update
RUN apt-get install -y grass saga yarn

#QGIS
#Add QGIS install here

#Orfeo
RUN cd /home/prod/  \
&&  wget https://www.orfeo-toolbox.org/packages/OTB-contrib-6.0.0-Linux64.run \
&& chmod +x OTB-contrib-6.0.0-Linux64.run \
&& OTB_PYTHON_EXE=/usr/bin/python2.7 ./OTB-contrib-6.0.0-Linux64.run \
&& echo 'export PYTHONPATH=/home/prod/orfeo/OTB-contrib-6.0.0-Linux64/lib/python:$PYTHONPATH' >> ~/.bashrc \
&&	export PYTHONPATH=/home/prod/orfeo/OTB-contrib-6.0.0-Linux64/lib/python:$PYTHONPATH
RUN mkdir /home/prod/scripts
COPY scripts /home/prod/scripts


	






	
