FROM ubuntu:latest

RUN mkdir /opt/Cinema/
RUN cd /opt/Cinema/



# KEEP UBUNTU OR DEBIAN UP TO DATE

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y dist-upgrade
RUN apt-get -y autoremove


# INSTALL THE DEPENDENCIES

# Build tools:
RUN apt-get install -y build-essential cmake apt-utils autoconf software-properties-common 
RUN add-apt-repository ppa:graphics-drivers/ppa && apt-get update


#For MESA
RUN apt-get install -y libgl1-mesa-dev mesa-common-dev mesa-utils-extra llvm

# GUI (if you want to use GTK instead of Qt, replace 'qt5-default' with 'libgtkglext1-dev' and remove '-DWITH_QT=ON' option in CMake):
RUN apt-get install -y qt5-default libvtk6-dev 
# Media I/O:
RUN apt-get install -y zlib1g-dev libjpeg-dev libwebp-dev libpng-dev libtiff5-dev libjasper-dev libopenexr-dev libgdal-dev

# Video I/O:
RUN apt-get install -y libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libv4l-dev libxine2-dev libxine2 xvfb

# Parallelism and linear algebra libraries:
RUN apt-get install -y libtbb-dev libeigen3-dev 

# Python:
RUN apt-get install -y python-dev python-tk python-numpy python3-dev python3-tk python3-numpy 

# Java:
RUN apt-get install -y ant default-jdk

# Documentation:
RUN apt-get install -y doxygen

#GIT, FFMPEG
RUN apt-get install -y git ffmpeg vim gdb valgrind

#glfw dependencies
RUN apt-get install -y xorg-dev libglm-dev graphviz libxcb-dri3-0 libxcb-present0 libpciaccess0 libxcb-dri3-dev libx11-dev libmirclient-dev libwayland-dev libxrandr-dev 
#wget https://vulkan.lunarg.com/sdk/download/1.0.39.1/linux/vulkansdk-linux-x86_64-1.0.39.1.run

# INSTALL THE LIBRARY (YOU CAN CHANGE '3.1.0' FOR THE LAST STABLE VERSION)

RUN apt-get install -y unzip wget
RUN mkdir /opt/Cinema/OpenCV/
RUN cd /opt/Cinema/OpenCV/
RUN wget https://github.com/opencv/opencv/archive/3.2.0.zip --directory-prefix=/opt/Cinema/OpenCV/
RUN unzip /opt/Cinema/OpenCV/3.2.0.zip -d /opt/Cinema/OpenCV/
RUN rm /opt/Cinema/OpenCV/3.2.0.zip
RUN mv /opt/Cinema/OpenCV/opencv-3.2.0 /opt/Cinema/OpenCV/opencv_main
RUN cd /opt/Cinema/OpenCV/opencv_main

#Extra Modules 
#RUN git clone https://github.com/opencv/opencv_contrib.git /opt/Cinema/OpenCV/opencv_contrib
RUN wget https://github.com/opencv/opencv_contrib/archive/3.2.0.zip --directory-prefix=/opt/Cinema/OpenCV/extra && unzip /opt/Cinema/OpenCV/extra/3.2.0.zip -d /opt/Cinema/OpenCV/opencv_contrib

RUN mkdir /opt/Cinema/OpenCV/opencv_main/build
RUN cd /opt/Cinema/OpenCV/opencv_main/build && cmake -DWITH_QT=ON -DOPENCV_EXTRA_MODULES_PATH=/opt/Cinema/OpenCV/opencv_contrib/modules -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON -DWITH_CUDA=ON -D ENABLE_FAST_MATH=1 -D CUDA_FAST_MATH=1 -D WITH_CUBLAS=1 -B /opt/Cinema/OpenCV/opencv_main/build /opt/Cinema/OpenCV/opencv_main/ && make -j4 -C /opt/Cinema/OpenCV/opencv_main/build && make install -C /opt/Cinema/OpenCV/opencv_main/build
RUN ldconfig


# EXECUTE SOME OPENCV EXAMPLES AND COMPILE A DEMONSTRATION


#Boost installation
RUN cd ../..
RUN mkdir /opt/Cinema/boost
RUN cd /opt/Cinema/boost/
RUN wget https://sourceforge.net/projects/boost/files/boost/1.63.0/boost_1_63_0.zip --directory-prefix=/opt/Cinema/boost/
RUN unzip /opt/Cinema/boost/boost_1_63_0.zip -d /opt/Cinema/boost
RUN cd /opt/Cinema/boost/boost_1_63_0/ && /opt/Cinema/boost/boost_1_63_0/bootstrap.sh && /opt/Cinema/boost/boost_1_63_0/b2 cxxflags="-fPIC" cflags="-fPIC" -a install
#Is step required? Uncomment if YES
#RUN /bin/bash -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/boost.conf'

#OpenGL Installation

#MESA install
RUN mkdir /opt/Cinema/OpenGL/ &&\
	mkdir /opt/Cinema/OpenGL/Mesa &&\
	cd /opt/Cinema/OpenGL/Mesa &&\
	wget https://mesa.freedesktop.org/archive/mesa-17.0.0.tar.gz &&\
	tar -xvzf mesa-17.0.0.tar.gz &&\
	cd mesa-17.0.0/ &&\
	apt-get build-dep -y mesa &&\
	./configure --disable-osmesa --enable-gallium-osmesa --enable-gallium-llvm=yes --disable-llvm-shared-libs --with-gallium-drivers=swrast --with-osmesa-bits=32 &&\
	make install

#GLEW Installation
RUN apt-get install -y libxmu-dev libxi-dev libgl-dev dos2unix git wget
RUN 	cd /opt/Cinema/OpenGL/ &&\
	wget https://excellmedia.dl.sourceforge.net/project/glew/glew/2.0.0/glew-2.0.0.tgz && \
	tar -zxvf glew-2.0.0.tgz && \
	cd glew-2.0.0/build/ && \
	cmake -D BUILD_UTILS=ON -DGLEW_OSMESA=ON ./cmake &&\
	make -j4 all &&\
	make install all

	




RUN ldconfig

#VideoStabilize Malloc Fix
RUN apt-get install -y libtcmalloc-minimal4


#Get latest version of backend repo
CMD export CPLUS_INCLUDE_PATH="$CPLUS_INCLUDE_PATH:/usr/include/python2.7/"
CMD export PATH=.:$PATH
CMD export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.
#VideoStabilize Malloc fix
CMD export LD_PRELOAD="/usr/lib//libtcmalloc_minimal.so.4"
#required for MESA
CMD export MESA_GL_VERSION_OVERRIDE=4.10
CMD export MESA_GLSL_VERSION_OVERRIDE=410
CMD git clone https://MadhavM@bitbucket.org/duneapp/backend.git /opt/Cinema/backend
CMD ulimit -s 50000
# to make ulimit changes permanent /etc/security/limits.conf must be edited