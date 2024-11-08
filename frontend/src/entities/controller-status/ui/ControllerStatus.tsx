import React, { FC } from 'react';
import { Badge } from 'antd';
import { IStatus, IControllerStatus } from "./types"

const controller_status: IStatus = {
	running: {
		text: "в сети", color: "success"
	},
	stopped: {
		text: "не в сети", color: "error"
	},
	unknown: {
		text: "неизвестно", color: "warning"
	}
}

export const ControllerStatus: FC<IControllerStatus> = ({ status }) => {
	const statusKey: keyof IStatus = (status ?? "unknown") as keyof IStatus;

	return (
		<Badge
			status={controller_status[statusKey].color}
			text={controller_status[statusKey].text}
		/>
	)
};
