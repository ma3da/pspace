import React, { useState } from 'react';
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

function App() {
  const [word, setWord] = useState("");
  const [definitionHtml, setDefHtml] = useState("");
  const [dataSource, setDataSrc] = useState("");
  const [process, setProcess] = useState(false); // == checkbox state at start?
  return (
  <div id="definition-main">
    <div className="definition-center">
      <div className="definition-content centering">
        <div dangerouslySetInnerHTML={{__html: definitionHtml}} />
      </div>
    </div>

    <div className="searchbar">
      <div classname="searchbar-info">source: { dataSource }</div>
      <div className="searchbar-tools">
      <form action="#">
        <label>
        <input type="checkbox" onChange={e => setProcess(e.target.checked)} />slim</label>
        <input onChange={e => setWord(e.target.value)} />
        <button onClick={() => load(word, process, setDefHtml, setDataSrc)}><FontAwesomeIcon icon={faSearch} color="black" /></button>
      </form>
      </div>
    </div>

  </div>
  );
}

export default App;
