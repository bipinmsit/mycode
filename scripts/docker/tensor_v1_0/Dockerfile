FROM ubuntu:latest




# KEEP UBUNTU OR DEBIAN UP TO DATE

RUN apt-get install -y build-essential cmake apt-utils autoconf software-properties-common wget
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y dist-upgrade
RUN apt-get -y autoremove


# INSTALL THE DEPENDENCIES

# Build tools:
RUN add-apt-repository ppa:graphics-drivers/ppa && apt-get update



# GUI (if you want to use GTK instead of Qt, replace 'qt5-default' with 'libgtkglext1-dev' and remove '-DWITH_QT=ON' option in CMake):
RUN apt-get install -y qt5-default libvtk6-dev 
# Media I/O:
RUN apt-get install -y zlib1g-dev libjpeg-dev libwebp-dev libpng-dev libtiff5-dev libjasper-dev libopenexr-dev libgdal-dev

# Video I/O:
RUN apt-get install -y libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libv4l-dev libxine2-dev libxine2 xvfb

# Parallelism and linear algebra libraries:
RUN apt-get install -y libtbb-dev libeigen3-dev 

# Python:
RUN apt-get install -y python-dev python-tk python3-dev python3-tk ipython ipython3 python-pip wget
RUN mkdir /opt/py3/ && cd /opt/py3/ && wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py
RUN pip3 install tensorflow numpy pillow scipy matplotlib scikit-learn
RUN pip install tensorflow numpy pillow scipy matplotlib scikit-learn


# Documentation and Debugging:
RUN apt-get install -y doxygen vim gdb valgrind

#GIT, FFMPEG
RUN apt-get install -y git ffmpeg 



# INSTALL THE LIBRARY (YOU CAN CHANGE '3.2.0' FOR THE LAST STABLE VERSION)

#RUN apt-get install -y unzip wget
#RUN mkdir /opt/Cinema/OpenCV/
#RUN cd /opt/Cinema/OpenCV/
#RUN wget https://github.com/opencv/opencv/archive/3.2.0.zip --directory-prefix=/opt/Cinema/OpenCV/
#RUN unzip /opt/Cinema/OpenCV/3.2.0.zip -d /opt/Cinema/OpenCV/
#RUN rm /opt/Cinema/OpenCV/3.2.0.zip
#RUN mv /opt/Cinema/OpenCV/opencv-3.2.0 /opt/Cinema/OpenCV/opencv_main
#RUN cd /opt/Cinema/OpenCV/opencv_main

#Extra Modules 
#RUN git clone https://github.com/opencv/opencv_contrib.git /opt/Cinema/OpenCV/opencv_contrib
#RUN wget https://github.com/opencv/opencv_contrib/archive/3.2.0.zip --directory-prefix=/opt/Cinema/OpenCV/extra && unzip /opt/Cinema/OpenCV/extra/3.2.0.zip -d /opt/Cinema/OpenCV/opencv_contrib

#RUN mkdir /opt/Cinema/OpenCV/opencv_main/build
#RUN cd /opt/Cinema/OpenCV/opencv_main/build && cmake -DWITH_QT=ON -DOPENCV_EXTRA_MODULES_PATH=/opt/Cinema/OpenCV/opencv_contrib/modules -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON -DWITH_CUDA=ON -D ENABLE_FAST_MATH=1 -D CUDA_FAST_MATH=1 -D WITH_CUBLAS=1 -B /opt/Cinema/OpenCV/opencv_main/build /opt/Cinema/OpenCV/opencv_main/ && make -j4 -C /opt/Cinema/OpenCV/opencv_main/build && make install -C /opt/Cinema/OpenCV/opencv_main/build
#RUN ldconfig


# EXECUTE SOME OPENCV EXAMPLES AND COMPILE A DEMONSTRATION




#VideoStabilize Malloc Fix

#Use ONLY if needed.
#RUN apt-get install -y libtcmalloc-minimal4


#Get latest version of backend repo
#CMD export CPLUS_INCLUDE_PATH="$CPLUS_INCLUDE_PATH:/usr/include/python2.7/"
#CMD export PATH=.:$PATH
#CMD export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.

#VideoStabilize Malloc fix
#CMD export LD_PRELOAD="/usr/lib//libtcmalloc_minimal.so.4"

#required for MESA
#CMD export MESA_GL_VERSION_OVERRIDE=4.10
#CMD export MESA_GLSL_VERSION_OVERRIDE=410
#CMD git clone https://MadhavM@bitbucket.org/duneapp/backend.git /opt/Cinema/backend
#CMD ulimit -s 50000
# to make ulimit changes permanent /etc/security/limits.conf must be edited