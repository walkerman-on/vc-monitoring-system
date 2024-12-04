import { Button } from 'shared/ui/button';
import { Space } from 'antd';
import type { TableProps } from 'antd';
import { PoweroffOutlined } from '@ant-design/icons';
import { ControllersTable } from 'entities/controllers-table';
import { APIRequest } from 'shared/api/APIRequest';
import { useEffect, useRef, useState } from 'react';
import { IControllerInfo } from 'features/controller';
import { ENDPOINTS } from 'shared/api/api';

interface DataType {
	key: string;
	controller_name: string;
	status: any;
}

export const ControllersInfo = () => {
	const columns: TableProps<DataType>['columns'] = [
		{
			title: 'Название контроллера',
			dataIndex: 'controller_name',
			key: 'controller_name',
		},
		{
			title: 'Статус',
			dataIndex: 'status',
			key: 'status',
		},
		{
			title: 'Действия',
			key: 'action',
			render: (_, record) => (
				<Space size="middle">
					<Button icon={<PoweroffOutlined />} type='primary' />
				</Space>
			),
		},
	];
	interface IStatus {
		controllers: IControllerInfo[] | null
	}

	const [info, setInfo] = useState<IStatus>({ controllers: null })
	const [connected, setConnected] = useState(false)
	const socket = useRef<WebSocket | null>(null);

	useEffect(() => {
		socket.current = new WebSocket("ws://localhost:8000/status")

		socket.current.onopen = () => {
			setConnected(true)
			console.log("Соединение установлено")
		}

		socket.current.onmessage = (e) => {
			setConnected(true)
			const message = JSON.parse(e.data)
			// if (message.status !== serverResponse.controller) {
			setInfo(message)

			// }
		}

		socket.current.onclose = () => {
			setConnected(true)
			console.log("Соединение закрыто")
		}

		socket.current.onerror = () => {
			setConnected(true)
			console.log("Произошла ошибка")
		}
	}, [])

	const restartController = async () => {
		await APIRequest({ url: ENDPOINTS.controller_restart, method: "POST" })

	};

	const changeSetPointLevel = async () => {
		await APIRequest({ url: ENDPOINTS.change_setpoint, method: "POST" })
	}

	return (
		<ControllersTable
			columns={columns}
			data={info.controllers}
		/>
	);
};
