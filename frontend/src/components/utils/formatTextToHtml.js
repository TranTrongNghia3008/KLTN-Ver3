// const formatTextToHtml = (text) => {
//     if (text.includes("<li><strong>")) text = `<ol>${text}</ol>`;
//     text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
//     text = text.replace(/:\s*-\s*/g, ":<br> - ");
//     text = text.replace(/\.\s*-\s*/g, ".<br> - ");
//     text = `<p>${text.replace(/\n\n/g, "</p><p>")}</p>`;
//     return text.trim();
//   };
export function formatTextToHtml(text) {
  if (text.includes("<li><strong>")) text = `<ol>${text}</ol>`;
  text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/:\s*-\s*/g, ":<br> - ");
  text = text.replace(/\.\s*-\s*/g, ".<br> - ");
  text = `<p>${text.replace(/\n\n/g, "</p><p>")}</p>`;
  return text.trim();
}