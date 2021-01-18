# We're using Ubuntu 20.10
FROM varietyjames1/userge_x:latest

#
# Clone repo and prepare working directory
#
RUN git clone -b sql-extended https://github.com/ashwinstr/ux-exp /root/userbot
RUN mkdir /root/userbot/.bin
WORKDIR /root/userbot

#Install python requirements
RUN pip3 install -r https://raw.githubusercontent.com/ashwinstr/ux-exp/alpha/requirements.txt

CMD ["python3","-m","userbot"]
