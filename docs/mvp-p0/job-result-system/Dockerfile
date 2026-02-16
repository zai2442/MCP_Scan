FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Create exports directory
RUN mkdir -p /exports && chmod 777 /exports

EXPOSE 3000

CMD ["node", "src/app.js"]
