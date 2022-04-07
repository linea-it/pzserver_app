# PZ Server

The Photo-z (PZ) Server is one of the Brazilian in-kind contributions offered by the Laboratório Interinstitucional de e-Astronomia (LIneA) to the PZ Coordination Group from Vera C. Rubin Observatory's Data Management (DM) Team. Inspired by features of the DES Science Portal (Gschwend et al., 2018; Fausti Neto et al., 2018), the PZ Server is being planned to be an online service, complementary to the Rubin Science Platform (RSP), to host PZ-related lightweight data products and to offer data management tools that allow sharing data products among RSP users, attach and share relevant metadata, and help on provenance tracking.

---

## Development
### Dependencies
  - [NodeJS](https://nodejs.org/en/download/)
  - [Yarn](https://classic.yarnpkg.com/lang/en/docs/install/#debian-stable)

First, install the dependencies:
```bash
yarn install
```

After, run the development server:
```bash
yarn dev
```

Finally, open [http://localhost:3000](http://localhost:3000) with your browser.

---

## Production
### Dependencies
  - [Docker](https://docs.docker.com/engine/install/)
  - [Docker Compose](https://docs.docker.com/compose/install/)

Build the application's image:
```bash
docker-compose build
```

In case you want to use an already built image, change the name in [docker-compose.yml](docker-compose.yml):
```
...
services:
  frontend:
    image: CHANGE_IMAGE_NAME
    ...
```

Run the application:
```bash
docker-compose up
```
