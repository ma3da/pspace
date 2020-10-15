import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import Cookies from 'js-cookie';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSearch } from '@fortawesome/free-solid-svg-icons'

function load(word, process, htmlSetter, srcSetter) {
  let _word = word.trim();
  if (_word !== "") {
    axios
      .post("/api/" + _word, 
               {"process": process},
               {headers: {"X-CSRFToken": Cookies.get("csrftoken")}})
      .then(resp => {
          htmlSetter(resp.data.htmlcontent);
          srcSetter(resp.data.datasource);
      })
      .catch(err => {
          console.log(err);
          htmlSetter(err.toString());
          srcSetter("?");
      });
  } else {
    htmlSetter("what word is this: '" + word + "'?");
  }
}

function Logging() {
    return (
      <div id="logging">
        <form action="#" method="post">
          <input type="password" name="pwd" />
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

function App() {
  const [word, setWord] = useState("");
  const [definitionHtml, setDefHtml] = useState("");
  const [dataSource, setDataSrc] = useState("");
  const [process, setProcess] = useState(false); // == checkbox state at start?
	const [popQueue, setPopQueue] = useState([]);

  return (
  <div id="definition-main">
    <div className="definition-center">
      <div className="definition-content centering">
        <div dangerouslySetInnerHTML={{__html: definitionHtml}} />
      </div>
    </div>

    <div className="searchbar">
      <div className="searchbar-info">
				<button onClick={pusher(<Logging />, setPopQueue)}>login</button>
				<span>source: {dataSource}</span>
			</div>
      <div className="searchbar-tools">
				<form action="#">
					<label>
					<input type="checkbox" onChange={e => setProcess(e.target.checked)} />slim</label>
					<input onChange={e => setWord(e.target.value)} />
					<button onClick={() => load(word, process, setDefHtml, setDataSrc)}><FontAwesomeIcon icon={faSearch} color="black" /></button>
				</form>
      </div>
    </div>

	<Pop queue={popQueue}
		   close={() => setPopQueue((prev) => {return prev.slice(1);})}
	/>
  </div>
  );
}

export default App;
