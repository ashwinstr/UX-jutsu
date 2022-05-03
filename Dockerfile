FROM ghcr.io/ashwinstr/ux-venom-docker:latest

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# adding email and username to the bot
RUN git config --global user.email "ashwinstr@gmail.com"
RUN git config --global user.name "ashwinstr"

# command to run on container start
CMD [ "bash", "./run" ]
