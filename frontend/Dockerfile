FROM node:16.14.2-slim AS dependencies
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

FROM node:16.14.2-slim AS builder
WORKDIR /app
COPY . .
COPY --from=dependencies /app/node_modules ./node_modules
RUN yarn build

FROM node:16.14.2-slim AS runner

WORKDIR /app

ARG USERID=1000
ARG GROUPID=1000

# RUN apt-get update \
#   && apt-get install -y --no-install-recommends build-essential \
#   && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
#   && apt-get clean 

RUN echo "Creating user with UID ${USERID} and GID ${GROUPID}"

RUN groupmod -g "${GROUPID}" node && usermod -u "${USERID}" -g "${GROUPID}" node

ENV NODE_ENV production

# If you are using a custom next.config.js file, uncomment this line.
# COPY --from=builder /pz-server/next.config.js ./
COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/.next ./.next
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
COPY --from=builder --chown=node:node /app/package.json ./package.json

USER node

EXPOSE 3000
CMD ["yarn", "start"]
