import React, { useState } from 'react';
import './App.css';
import axios from 'axios';
import Cookies from 'js-cookie';

function load(word, setter) {
  let _word = word.trim();
  if (_word !== "") {
    axios
      .post("/api/" + _word, 
               {"no_process": true},
               {headers: {"X-CSRFToken": Cookies.get("csrftoken")}})
      .then(resp => {setter(resp.data.htmldefinition)})
      .catch(err => {console.log(err); setter(err.toString())});
  } else {
    setter("what word is this: '" + word + "'?");
  }
}

function App() {
  const [word, setWord] = useState("");
  const [definitionHtml, setDefinitionHtml] = useState("empty");
  const dataSource = "datasource";
  return (
  <div>
    <div className="definition-content centering">
      <p> source: { dataSource } </p>
      <div>
        {definitionHtml}
      </div>
    </div>
    <div className="searchbar">
      <div className="centering">
        <label>
        <input type="checkbox" />full</label>
        <input onChange={e => setWord(e.target.value)} />
        <button onClick={() => load(word, setDefinitionHtml)}>search</button>
      </div>
    </div>
  </div>
  );
}

export default App;
