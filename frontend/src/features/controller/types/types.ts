export interface IControllerInfo {
	controller_name: string,
	status: string,
	data: IControllerData
}

export interface IControllerData {
	pressure: boolean,
	level: boolean,
	setpoints: {
		pressure: boolean,
		level: boolean
	},
	control: {
		uprav1: boolean,
		uprav2: boolean
	}
}

