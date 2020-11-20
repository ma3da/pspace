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
          setSource(resp.data.datasource ? resp.data.datasource : "unk");
      })
      .catch(err => {
        console.log(err);
        setRaw(null);
        setProcessed(null);
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

function logIn(uid, pwd, setLogged) {
  axios
    .post("/login",
          {uid: uid, pwd: pwd},
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
  const [uid, setUid] = useState("");
  const [pwd, setPwd] = useState("");
  const uidRef = useRef(null);
  useEffect(() => {if (!uid && !pwd) uidRef.current.focus();});
  return (
    <form action="javascript:void(0);" autocomplete="off">
      <div id="logging">
        <input name="uid" onChange={e => setUid(e.target.value)} ref={uidRef} />
        <input type="password" name="pwd" onChange={e => setPwd(e.target.value)} />
        <button onClick={() => {logIn(uid, pwd, props.setLogged); props.popclose();}}>log in</button>
      </div>
    </form>
  );
}

function Pop(props) {
  if (props.queue.length > 0) {
    return (
      <div className="pop-container">
        <div className="pop-center">
          <div className="pop-content">
          {props.queue[0]}
          </div>
          <div><button onClick={props.close}>close</button></div>
        </div>
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

function WordList(props){
    const words = props.wordlist.map((word) => <div className="wordlist-item" onClick={() => props.load(word)}>{word}</div>);
    return words ? <div className="wordlist"> {words} </div> : null;
}

function parseWordBody(wb, load) {
    if (!wb) return null;
    return wb.map(token => token.link
                  ? <span className="token link" onClick={() => load(token.text)}>{token.text}</span>
                  : <span className="token">{token.text}</span>
                 );
}

function parseSubDef(o, load, d=0) {
    if (Array.isArray(o)) {
        const classname = d === 0 ? "definition-group" : "definition-subgroup";
        return (
            <div className={classname}>
                {o.map(x => parseSubDef(x, load, d+1))}
            </div>
        );
    }
    if (o.type === "def") {
        return <div className="definition-line">{parseWordBody(o.body, load)}</div>;
    } else if (o.type === "synt") {
        return (<div className="definition-line">
                  <span className="definition-synt">{o.synt}</span>
                {parseWordBody(o.body, load)}
                </div>);
    } else {
        return null;
    }
}

function SubDefinition(props){
    const wo = props.wordObj;
    const version = wo.version ? <sup>{wo.version}</sup>: null;
    return (
        <div className="definition">
            <div className="definition-word">
            <span>{wo.word}{version}</span>
            <span>{wo.code}</span>
            </div>
            <div>{parseSubDef(wo.defs, props.load)}</div>
        </div>
    );
}

function processDefinition(def, load) {
    if (!def) return <div className="definition">Could not fetch slim definition.</div>;

    const groups = def.map((wo) => <SubDefinition wordObj={wo} load={load} />);
    return <div>{groups}</div>;
}

function Definition(props){
    if (props.process) return processDefinition(props.processed, props.load);

    return props.raw ? <div className="definition" dangerouslySetInnerHTML={{__html: props.raw}} />
                     : <div className="definition">Could not fetch raw definition.</div>;
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
  const [defProcessed, setDefProcessed] = useState("");
  const [wordList, setWordList] = useState([]);
  const [dataSource, setDataSrc] = useState("");
  const [process, setProcess] = useState(false); // == checkbox state at start?
  const [popQueue, setPopQueue] = useState([]);
  const [logged, setLogged] = useState(null); // {logged, username}

  const close = () => setPopQueue((prev) => {return prev.slice(1);});
  const _load = () => load(word, setDefRawHtml, setDefProcessed, setDataSrc, setLogged);
  const _load2 = (word) => load(word, setDefRawHtml, setDefProcessed, setDataSrc, setLogged);
  const _loadWords = () => loadWords(setWordList, setLogged);

  if (logged === null) updateLogged(setLogged);
  const spanUserInfo = logged && logged.logged ? <span className="info-item">[{logged.username}]</span> : null;

  return (
  <div id="definition-main">
    <div className="definition-center">
      <div className="definition-content centering">
          <WordList wordlist={wordList} load={_load2} />
          <Definition process={process} processed={defProcessed} raw={defRawHtml} load={_load2}/>
      </div>
    </div>

    <div className="searchbar">
      <div className="searchbar-info">
        <span>
        <LogToggle setQueue={setPopQueue} logged={logged} setLogged={setLogged} close={close} />
        </span>
        {spanUserInfo}
      </div>
          <ShowToggle load={_loadWords} unload={() => setWordList([])} />
      <div className="searchbar-tools">
        <form action="javascript:void(0);">
          <label>
          <input type="checkbox" onChange={e => setProcess(e.target.checked)} /></label>
          <input onChange={e => setWord(e.target.value)} />
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
