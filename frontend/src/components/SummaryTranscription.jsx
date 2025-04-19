import "../styles/SummaryTranscription.css"

const SummaryTranscription = ({ output }) => {
  return (
    <div className="result-container">
      <h3>Result</h3>
      {output ? (
        <p className="result-text">{output}</p>
      ) : (
        <p className="empty-result">No summary or transcription yet.</p>
      )}
    </div>
  );
};

export default SummaryTranscription;
