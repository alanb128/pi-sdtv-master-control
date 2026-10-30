FROM node:22-bullseye

RUN apt-get update && apt-get install -y git nano usbutils

# Defines our working directory in container
WORKDIR /usr/src/app

# Copies the package.json first for better cache on later pushes
COPY package*.json ./

COPY . ./

# This install npm dependencies on the balena build server,
# making sure to clean up the artifacts it creates in order to reduce the image size.
RUN JOBS=MAX npm install --production --unsafe-perm && npm cache verify && rm -rf /tmp/*

# This will copy all files in our root to the working directory in the container
COPY . ./

# server.js will run when container starts up on the device
CMD ["npm", "start"]
