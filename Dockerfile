# We're using Ubuntu 20.10
FROM kakashi3/docker:groovy

#
# Clone repo and prepare working directory
#
RUN git clone -b sql-extended https://github.com/ashwinstr/ux-exp /root/userbot
RUN mkdir /root/userbot/.bin
WORKDIR /root/userbot

#Install python requirements
RUN pip3 install -r https://raw.githubusercontent.com/ashwinstr/ux-exp/sql-extended/requirements.txt

CMD ["python3","-m","userbot"]
