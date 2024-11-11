import axios from 'axios';

const __API__ = 'http://localhost:8000';

export const $api = axios.create({
	baseURL: __API__,
});

enum IENDPOINTS {

}
export const ENDPOINTS = {
	controller_status: "/status",
	controller_restart: "/restart"
}