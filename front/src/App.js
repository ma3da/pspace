import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faSignInAlt, faSignOutAlt } from '@fortawesome/free-solid-svg-icons';

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

function loadWords(setWordList, setLogged){
    axios
        .get("/api/words")
        .then(resp => {
            setWordList(resp.data);
        })
        .catch(err => {
            console.log(err);
            updateLogged(setLogged);
        });
}

function updateLogged(setLogged) {
  axios.get("/logged")
       .then(resp => {setLogged(resp.data);})
       .catch(console.log);
}

function logIn(pwd, setLogged) {
  axios
    .post("/login",
        {"pwd": pwd},
        {headers: {"X-CSRFToken": Cookies.get("csrftoken")}})
    .then(resp => {
      setLogged(resp.data);
    })
    .catch(console.log);
}

function logOut(setLogged) {
  axios
    .post("/logout",
        {},
        {headers: {"X-CSRFToken": Cookies.get("csrftoken")}})
    .then(resp => {
      setLogged(resp.data);
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
  const logged = props.logged ? props.logged.logged : false;
  let value = logged ? <FontAwesomeIcon icon={faSignOutAlt} /> : <FontAwesomeIcon icon={faSignInAlt} />;
  let func = logged ? (() => logOut(props.setLogged)) : pusher(<Logging popclose={props.close} setLogged={props.setLogged} />, props.setQueue);
  return <button onClick={func}>{value}</button>;
}

function processDefinition(def) {
    console.log(def);
    return <div dangerouslySetInnerHTML={{__html: def}} />;
}

function WordList(props){
    const words = props.wordlist.map((word) => <div className="wordlist-item" onClick={() => props.load(word)}>{word}</div>);
    return words ? <div className="wordlist"> {words} </div> : null;
}

function Definition(props){
    return props.process ? processDefinition(props.processed)
        : <div className="definition" dangerouslySetInnerHTML={{__html: props.raw}} />;
}

function ShowToggle(props){
    const [show, setShow] = useState(true);
    const _show = () => {props.load(); setShow(false);};
    const _hide = () => {props.unload(); setShow(true);};
    return show ? <button onClick={_show}>show</button>
                : <button onClick={_hide}>hide</button>;
}

function App() {
  const [word, setWord] = useState("");
  const [defRawHtml, setDefRawHtml] = useState("");
  const [defProcessed, setDefProcessed] = useState({});
  const [wordList, setWordList] = useState([]);
  const [dataSource, setDataSrc] = useState("");
  const [process, setProcess] = useState(false); // == checkbox state at start?
  const [popQueue, setPopQueue] = useState([]);
  const [logged, setLogged] = useState(null); // {logged, username}
  const searchRef = useRef(null);

  const close = () => setPopQueue((prev) => {return prev.slice(1);});
  const _load = () => load(word, setDefRawHtml, setDefProcessed, setDataSrc, setLogged);
  const _load2 = (word) => load(word, setDefRawHtml, setDefProcessed, setDataSrc, setLogged);
  const _loadWords = () => loadWords(setWordList, setLogged);

  if (logged === null) updateLogged(setLogged);
  useEffect(() => {if (popQueue.length === 0) searchRef.current.focus();});
  const spanUserInfo = logged && logged.logged ? <span className="info-item">logged as: {logged.username}</span> : null;

  return (
  <div id="definition-main">
    <div className="definition-center">
      <div className="definition-content centering">
          <WordList wordlist={wordList} load={_load2} />
          <Definition process={process} processed={defProcessed} raw={defRawHtml} />
      </div>
    </div>

    <div className="searchbar">
      <div className="searchbar-info">
        <span>
        <LogToggle setQueue={setPopQueue} logged={logged} setLogged={setLogged} close={close} />
        </span>
        {spanUserInfo}
        <span className="info-item">source: {dataSource}</span>
      </div>
          <ShowToggle load={_loadWords} unload={() => setWordList([])} />
      <div className="searchbar-tools">
        <form action="javascript:void(0);">
          <label>
          <input type="checkbox" onChange={e => setProcess(e.target.checked)} />slim</label>
          <input onChange={e => setWord(e.target.value)} ref={searchRef} />
          <button onClick={_load}><FontAwesomeIcon icon={faSearch} /></button>
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
