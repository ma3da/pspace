import React, { useState } from 'react';
import './App.css';
import axios from 'axios';
import Cookies from 'js-cookie';

function load(word, htmlSetter, srcSetter) {
  let _word = word.trim();
  if (_word !== "") {
    axios
      .post("/api/" + _word, 
               {"no_process": true},
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
  return (
  <div>
    <div className="definition-content centering">
      <p> source: { dataSource } </p>
      <div dangerouslySetInnerHTML={{__html: definitionHtml}} />
    </div>
    <div className="searchbar">
      <div className="centering">
        <label>
        <input type="checkbox" />full</label>
        <input onChange={e => setWord(e.target.value)} />
        <button onClick={() => load(word, setDefHtml, setDataSrc)}>search</button>
      </div>
    </div>
  </div>
  );
}

export default App;
