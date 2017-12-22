This folder contains Dockerfile to build environment to run everything contained in the repository.
After installing docker, this can be done by 
`sudo docker build -t cinema .	`
And this can be run by 
`sudo docker run -it cinema bash`


You can map directories in your system to directories in the running docker image by 
`sudo docker run -it -v <sys_dir>:<docker_dir> cinema bash`

Here, 'cinema' is the name of the docker image.
/Users/Y13/Cinema/opencv
