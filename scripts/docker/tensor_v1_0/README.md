This folder contains Dockerfile to build environment to run *TensorFlow*
After installing docker, this can be done by 
`sudo docker build -t tensor_v1_0 .	`
And this can be run by 
`sudo docker run -it tensor_v1_0 bash`


You can map directories in your system to directories in the running docker image by 
`sudo docker run -it -v <sys_dir>:<docker_dir> tensor_v1_0 bash`

Here, 'tensor_v1_0' is the name of the docker image.
