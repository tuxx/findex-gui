Docker containers for Findex GUI
====

*Use at your own risk*


Running
===
- Run `build.sh` to build the containers
- Run `rundocker.sh` to run the containers - findex still exits at the moment.
- Tearing down the containers is still done manually, check `docker ps` and `docker stop <containerid>`


TODO
===
- Get the findexgui container running
- Make it in docker-compose?
- Upload containers to registry so you can quickly deploy it instead of building