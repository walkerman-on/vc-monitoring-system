import React, { useEffect, useRef, useState } from 'react';
import { Button } from 'shared/ui/button';
import { APIRequest } from 'shared/api/APIRequest';
import { Badge } from 'antd';
import { ENDPOINTS } from "shared/api/api"
import { ControllerStatus } from 'entities/controller-status';
import { Switch } from "antd"
import { ControllerData } from 'entities/controller';
import { IController } from 'features/controller';
import { Space, Tag } from 'antd';
import type { TableProps } from 'antd';
import { ControllersTable } from 'entities/controllers-table';
import { PoweroffOutlined } from '@ant-design/icons';

interface DataType {
  key: string;
  controller_name: string;
  status: any;
}

const columns: TableProps<DataType>['columns'] = [
  {
    title: 'Название контроллера',
    dataIndex: 'controller_name',
    key: 'controller_name',
    render: (text) => <a>{text}</a>,
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

const data: DataType[] = [
  {
    key: '1',
    controller_name: "controller_1",
    status: <Badge status='success' text="работает" />
  },
  {
    key: '2',
    controller_name: "controller_2",
    status: <Badge status='error' text="не работает" />
  },
  {
    key: '3',
    controller_name: "controller_3",
    status: <Badge status='warning' text="ожидание" />
  },
];

interface IStatus {
  controllers: IController[] | null
}

function App() {
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

  const onChange = async () => {
    await APIRequest({ url: ENDPOINTS.controller_restart, method: "POST" })

  };

  const changeSetPointLevel = async () => {
    await APIRequest({ url: ENDPOINTS.change_setpoint, method: "POST" })
  }

  return (
    <div className="App">
      {
        info.controllers?.map(info => (
          <ControllerData changeSetPoint={changeSetPointLevel} info={info} key={info.controller_name} />
        ))
      }
      {/* 
      <Switch disabled={serverResponse.status === "running" ? true : false} defaultChecked={serverResponse.status === "running" ? true : false} onChange={onChange} />
      <ControllerStatus status={serverResponse.status} />
      */}
      <ControllersTable columns={columns} data={data} />
    </div>
  );
}

export default App;
