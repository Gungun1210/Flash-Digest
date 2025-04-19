import { useState } from "react";
import axios from "axios";
import History from "./components/History";
import SummaryTranscription from "./components/SummaryTranscription";
import "./App.css";

function App() {
  const [newsUrl, setNewsUrl] = useState("");
  const [action, setAction] = useState("Summarize");
  const [output, setOutput] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);  // Added loading state

  const processRequest = async () => {
    if (!newsUrl) {
      setOutput("Please enter a news URL.");
      return;
    }

    setLoading(true);  // Indicate processing starts

    try {
      const response = await axios.post("http://localhost:8002/process", {
        url: newsUrl,
        mode: action.toLowerCase(),
      });

      setOutput(response.data.result);
      setHistory([...history, response.data.result]);  // Store history
    } catch (error) {
      console.error("Error calling backend:", error);
      setOutput("Failed to connect to backend. Ensure the server is running.");
    }

    setLoading(false);  // Indicate processing ends
  };

  return (
    <div className="container">
      <img
        src="/flashdigest.png"
        alt="Logo"
        style={{
          display: "block",
          margin: "auto",
          width: "350px",
          height: "auto",
        }}
      />
      <h1>Flash Digest</h1>

      {/* News URL Input */}
      <div className="form-floating mb-2">
        <input
          type="text"
          className="form-control"
          id="floatingInput"
          value={newsUrl}
          onChange={(e) => setNewsUrl(e.target.value)}
          placeholder="Enter news URL"
        />
        <label htmlFor="floatingInput">Enter news URL...</label>
      </div>

      {/* Bootstrap Dropdown */}
      <div className="dropdown mb-2">
        <button
          className="btn btn-outline-secondary dropdown-toggle"
          type="button"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          {action}
        </button>
        <ul className="dropdown-menu">
          <li>
            <button className="dropdown-item" onClick={() => setAction("Summarize")}>
              Summarize
            </button>
          </li>
          <li>
            <button className="dropdown-item" onClick={() => setAction("Transcribe")}>
              Transcribe
            </button>
          </li>
        </ul>
      </div>

      {/* Process Button */}
      <button onClick={processRequest} type="submit" className="btn btn-primary">
        {loading ? "Processing..." : "Process"}
      </button>

      {/* Summary / Transcription Component */}
      <SummaryTranscription output={output} />

      {/* History Component */}
      <History history={history} />
    </div>
  );
}

export default App;
