import "../styles/History.css";

const History = ({ history }) => {
  return (
    <div className="history-container">
      <h3>History</h3>
      {history.length === 0 ? (
        <p className="empty-history">No past summaries yet.</p>
      ) : (
        <ul className="history-list">
          {history.map((entry, index) => (
            <li key={index} className="history-item">
              {entry}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default History;
