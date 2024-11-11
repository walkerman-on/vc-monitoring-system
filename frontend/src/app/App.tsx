import React, { useEffect, useRef, useState } from 'react';
import { Button } from 'shared/ui/button';
import { APIRequest } from 'shared/api/APIRequest';
import { Badge } from 'antd';
import { ENDPOINTS } from "shared/api/api"
import { ControllerStatus } from 'entities/controller-status';
import { Switch } from "antd"
interface IStatus {
  status: string | null
}

function App() {
  const [serverResponse, setServerResponse] = useState<IStatus>({ status: "unknown" })
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
      if (message.status !== serverResponse.status) {
        setServerResponse(message)

      }
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
  return (
    <div className="App">
      <span>Контроллер 1</span>
      <Switch disabled={serverResponse.status === "running" ? true : false} defaultChecked={serverResponse.status === "running" ? true : false} onChange={onChange} />
      <ControllerStatus status={serverResponse.status} />
    </div>
  );
}

export default App;
