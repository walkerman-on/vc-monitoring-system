export type IStatusValues = {
	text: string,
	color: "success" | "processing" | "error" | "warning" | "default",
}

export type IStatus = {
	running: IStatusValues,
	stopped: IStatusValues,
	unknown: IStatusValues,
}

export type IControllerStatus = {
	status?: string | null
}