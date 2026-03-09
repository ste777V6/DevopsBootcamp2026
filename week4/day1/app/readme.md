# Docker
Tis week will be about docker and how to run a container in ECS with ECR

1) copied the app from week3/day1
2) Created the Dockerfile
3) Built the image from dockerfile

docker build -t app .

docker images ls


4)Run the image in a container

docker run -td --name app -p 5000:5000 app

5) Check the container logs - 

$ docker ps
 
$ docker logs 168bdc717978

$ docker exec 

5) Tag the app and push to Github

docker tag app dockprojects123/app:1.0

docker login -u dockprojects123

docker push dockprojects123/app:1.0