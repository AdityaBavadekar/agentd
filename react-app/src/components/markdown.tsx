import ReactMarkdown from "react-markdown";

const MarkdownBlock = (
    { text }: { text: string }
) => {
  return (
<div className="text-gray-200 bg-gray-800 p-4 rounded-lg shadow-md mt-4 break-words overflow-auto">      <ReactMarkdown>{text}</ReactMarkdown>
    </div>
  );
};

export default MarkdownBlock;
