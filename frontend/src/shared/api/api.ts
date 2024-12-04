import axios from 'axios';

const __API__ = 'http://localhost:8000';

export const $api = axios.create({
	baseURL: __API__,
});

enum IENDPOINTS {

}
export const ENDPOINTS = {
	controller_status: "/status",
	controller_restart: "/restart/backend-main-controller-1-1",
	change_setpoint: "setpoint/backend-main-controller-1-1/level?value=4.8",
}