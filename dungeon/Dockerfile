FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y telnet

COPY run-app.sh /run-app.sh

WORKDIR /app

COPY . .

RUN chmod +x add-ttyd.sh
RUN ./add-ttyd.sh 

RUN rm add-ttyd.sh
RUN rm -rf ttyd

RUN chmod +x /run-app.sh

EXPOSE 8989

ENTRYPOINT [ "/run-app.sh" ]
