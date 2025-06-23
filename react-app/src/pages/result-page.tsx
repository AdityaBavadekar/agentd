import { useParams } from "react-router-dom";

export default function ResultPage() {
  const { requestId } = useParams();

  const downloadReport = () => {
    window.location.href = `/api/report/${requestId}`;
  };

  return (
    <div>
      <h1>Analysis Complete</h1>
      <button onClick={downloadReport}>Download Report PDF</button>
    </div>
  );
}
