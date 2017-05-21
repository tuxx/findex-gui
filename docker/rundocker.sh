docker rm findex postgres elasticsearch
docker run -d --name postgres -e POSTGRES_PASSWORD="findex" zombopg:0.1
docker run -d --name elasticsearch zomboes:0.1
docker run -d --name findex --link postgres --link elasticsearch -p 80:80 findexgui:latest /usr/bin/findex web runserver
docker ps
