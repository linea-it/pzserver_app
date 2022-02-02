# FROM node:12

# ENV PORT 3000

# # Create app directory
# RUN mkdir -p /usr/src/app
# WORKDIR /usr/src/app

# # Installing dependencies
# COPY package*.json /usr/src/app/
# RUN npm install

# # Copying source files
# COPY . /usr/src/app

# # Building app
# RUN npm run build
# EXPOSE 3000

# # Running the app
# CMD ["yarn", "start"]


FROM node:lts as dependencies
WORKDIR /pz-server
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

FROM node:lts as builder
WORKDIR /pz-server
COPY . .
COPY --from=dependencies /pz-server/node_modules ./node_modules
RUN yarn build

FROM node:lts as runner
WORKDIR /pz-server
ENV NODE_ENV production
# If you are using a custom next.config.js file, uncomment this line.
# COPY --from=builder /pz-server/next.config.js ./
COPY --from=builder /pz-server/public ./public
COPY --from=builder /pz-server/.next ./.next
COPY --from=builder /pz-server/node_modules ./node_modules
COPY --from=builder /pz-server/package.json ./package.json

EXPOSE 3000
CMD ["yarn", "start"]
