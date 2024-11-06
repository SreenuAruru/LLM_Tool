# Use the latest Node.js LTS version as the base image
FROM node:18

# Create the application directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to install dependencies
COPY package.json package-lock.json /usr/src/app/

# Install app dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port React app runs on
EXPOSE 3000

# Start the React application
CMD ["npm", "start"]
