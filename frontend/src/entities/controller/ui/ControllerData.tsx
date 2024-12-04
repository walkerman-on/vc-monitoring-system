import React, { FC } from 'react';
import { IControllerInfo } from 'features/controller';
import { Button } from "shared/ui/button"

interface IControllerData {
	info: IControllerInfo,
	changeSetPoint: () => void
}

export const ControllerData: FC<IControllerData> = ({ info, changeSetPoint }) => {
	return (
		<div key={info.controller_name}>
			<p>Имя контроллера - {info?.controller_name}</p>
			<p>Статус контроллера - {info?.status}</p>
			<div>
				<span>Уровень - {info.data?.level} </span>
				<span>Уставка - {info.data.setpoints?.level} </span>
				<span>Управляющее воздействие - {info.data.control?.uprav2} % </span>
			</div>
			<Button onClick={changeSetPoint}>Изменить уставку</Button>
		</div>
	);
};
