import { api } from './api'

export const getProducts = ({ }) => {
    return api
        .get(`/products/`)
        .then((res) => res.data);
};