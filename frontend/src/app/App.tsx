import { ControllersInfo } from 'widgets/controllers-info';

function App() {

  return (
    <div className="App">
      <ControllersInfo />
      {/* {
        info.controllers?.map(info => (
          <ControllerData changeSetPoint={changeSetPointLevel} info={info} key={info.controller_name} />
        ))
      } */}
    </div>
  );
}

export default App;
