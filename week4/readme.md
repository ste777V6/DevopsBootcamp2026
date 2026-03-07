# Docker
Tis week will be about docker and how to run a container in ECS with ECR

1) copied the app from week3/day1
2) Created the Dockerfile
3) Built the image from dockerfile

@ste777V6 ➜ .../DevopsBootcamp2026/week4/day1/app (main)
docker build -t app .

@ste777V6 ➜ .../DevopsBootcamp2026/week4/day1/app (main) $ docker images
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
app          latest    900fbab4dbca   28 minutes ago   1.15GB

4)Run the image in a container

@ste777V6 ➜ .../DevopsBootcamp2026/week4/day1/app (main)
docker run -td --name app -p 5000:5000 app

5) Check the container logs - 

@ste777V6 ➜ .../DevopsBootcamp2026/week4/day1/app (main) $ docker ps
CONTAINER ID   IMAGE     COMMAND           CREATED          STATUS          PORTS                                                   NAMES
168bdc717978   app       "python app.py"   6 minutes ago    Up 6 minutes    0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp, 8000/tcp   app
42d35e3b1f39   python    "python3"         38 minutes ago   Up 38 minutes                                                           affectionate_ramanujan
@ste777V6 ➜ .../DevopsBootcamp2026/week4/day1/app (main) 
$ docker logs 168bdc717978
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.17.0.3:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 360-783-733
172.17.0.1 - - [07/Mar/2026 16:15:07] "GET / HTTP/1.1" 200 -
172.17.0.1 - - [07/Mar/2026 16:15:08] "GET /favicon.ico HTTP/1.1" 404 -
@ste777V6 ➜ .../DevopsBootcamp2026/week4/day1/app (main) $ 