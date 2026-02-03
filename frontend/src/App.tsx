import Upload from "./components/Upload";
import Query from "./components/Query";
import "./App.css";

function App() {
  return (
    <div className="App">
      <h1>RAG Knowledge Assistant</h1>
      <Upload />
      <hr />
      <Query />
    </div>
  );
}

export default App;
