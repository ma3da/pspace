import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';

function load(word, setRaw, setProcessed, setSource, setLogged) {
  let _word = word.trim();
  if (_word !== "") {
    axios
      .get("/api/" + _word)
      .then(resp => {
          setRaw(resp.data.htmlcontent);
          setProcessed(resp.data.processed);
          setSource(resp.data.datasource);
      })
      .catch(err => {
				console.log(err);
				setRaw("Could not fetch raw definition.");
				setProcessed("Could not fetch slim definition.");
				setSource("?");
				updateLogged(setLogged);
      });
  } else {
    setRaw("what word is this: '" + word + "'?");
    setProcessed("what word is this: '" + word + "'?");
  }
}

function updateLogged(setLogged) {
	axios.get("/logged")
			 .then(resp => {setLogged(resp.data.logged);})
			 .catch(console.log);
}

function logIn(pwd, setLogged) {
	axios
		.post("/login",
        {"pwd": pwd},
        {headers: {"X-CSRFToken": Cookies.get("csrftoken")}})
		.then(resp => {
      setLogged(resp.data.logged);
		})
		.catch(console.log);
}

function logOut(setLogged) {
	axios
		.post("/logout",
        {},
        {headers: {"X-CSRFToken": Cookies.get("csrftoken")}})
		.then(resp => {
			setLogged(resp.data.logged);
		})
		.catch(console.log);
}

function Logging(props) {
	const [pwd, setPwd] = useState("");
	const pwdRef = useRef(null);
	useEffect(() => {pwdRef.current.focus();});
	return (
		<div id="logging">
			<form action="javascript:void(0);">
				<input type="password" name="pwd" onChange={e => setPwd(e.target.value)} ref={pwdRef} />
				<button onClick={() => {logIn(pwd, props.setLogged); props.popclose();}}>log in</button>
			</form>
		</div>
	);
}

function Pop(props) {
	if (props.queue.length > 0) {
		return (
			<div className="pop-container">
				<div className="pop-content">
					{props.queue[0]}
				</div>
			<div><button onClick={props.close}>close</button></div>
			</div>
		);
	}
	return null;
}

function pusher(elem, setter) {
	return () => setter((queue) => {return setter(queue.concat([elem]));});
}

function LogToggle(props) {
  let value = props.logged ? "log out" : "log in";
  let func = props.logged ? (() => logOut(props.setLogged)) : pusher(<Logging popclose={props.close} setLogged={props.setLogged} />, props.setQueue);
  return <button onClick={func}>{value}</button>;
}

function processDefinition(def) {
    console.log(def);
    return <div dangerouslySetInnerHTML={{__html: def}} />;
}

function Definition(props){
    return props.process ? processDefinition(props.processed)
        : <div dangerouslySetInnerHTML={{__html: props.raw}} />;
}

function App() {
  const [word, setWord] = useState("");
  const [defRawHtml, setDefRawHtml] = useState("");
  const [defProcessed, setDefProcessed] = useState({});
  const [dataSource, setDataSrc] = useState("");
  const [process, setProcess] = useState(false); // == checkbox state at start?
	const [popQueue, setPopQueue] = useState([]);
  const close = () => setPopQueue((prev) => {return prev.slice(1);});
	const [logged, setLogged] = useState(null);
	if (logged === null) updateLogged(setLogged);
	const searchRef = useRef(null);
	useEffect(() => {if (popQueue.length === 0) searchRef.current.focus();});
  return (
  <div id="definition-main">
    <div className="definition-center">
      <div className="definition-content centering">
          <Definition process={process} processed={defProcessed} raw={defRawHtml}/>
      </div>
    </div>

    <div className="searchbar">
      <div className="searchbar-info">
        <LogToggle setQueue={setPopQueue} logged={logged} setLogged={setLogged} close={close}/>
				<span>source: {dataSource}</span>
			</div>
      <div className="searchbar-tools">
				<form action="javascript:void(0);">
					<label>
					<input type="checkbox" onChange={e => setProcess(e.target.checked)} />slim</label>
					<input onChange={e => setWord(e.target.value)} ref={searchRef} />
					<button onClick={() => load(word, setDefRawHtml, setDefProcessed, setDataSrc, setLogged)}><FontAwesomeIcon icon={faSearch} color="black" /></button>
				</form>
      </div>
    </div>

	<Pop queue={popQueue}
		   close={close}
	/>
  </div>
  );
}

export default App;
