import { FiX } from 'react-icons/fi';
import { formatTextToHtml } from './utils/formatTextToHtml';

export default function EditedHistory({ message, setShowEditedHistory }) {
  function extractPhrases(phraseString) {
    const matches = phraseString.match(/''(.*?)''/g);
    return matches ? matches.map(match => match.replace(/''/g, '').trim()) : [];
  }

  function highlightPhrases(content, phrases, links, color) {
    phrases.forEach((phrase, index) => {
      const escapedPhrase = escapeRegExp(phrase);
      const url = links[index] || '#';
      const linkTag = `<a href="${url}" target="_blank" style="color: ${color}; font-weight: bold; text-decoration: underline;">${phrase}</a>`;
      const regex = new RegExp(escapedPhrase, 'g');
      content = content.replace(regex, linkTag);
    });
    return content;
  }

  function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function extractOldContent() {
    const oldMatch = message.match(/OldMessage:(.*?)HighlightNotCorrect:/s);
    const notCorrectHighlights = message.match(/HighlightNotCorrect:\s*(.*?)LinkNotCorrect:/s);
    const notCorrectLinks = message.match(/LinkNotCorrect:\s*(.*?)HighlightCorrect:/s);
    const correctHighlights = message.match(/HighlightCorrect:\s*(.*?)LinkCorrect:/s);
    const correctLinks = message.match(/LinkCorrect:\s*(.*?)NewMessage:/s);

    if (oldMatch) {
      let oldContent = oldMatch[1].trim();

      const incorrectPhrases = extractPhrases(notCorrectHighlights ? notCorrectHighlights[1] : '');
      const incorrectLinks = extractPhrases(notCorrectLinks ? notCorrectLinks[1] : '');
      oldContent = highlightPhrases(oldContent, incorrectPhrases, incorrectLinks, 'red');

      const correctPhrases = extractPhrases(correctHighlights ? correctHighlights[1] : '');
      const correctLinksList = extractPhrases(correctLinks ? correctLinks[1] : '');
      oldContent = highlightPhrases(oldContent, correctPhrases, correctLinksList, 'green');

      return formatTextToHtml(oldContent);
    }

    return 'No old content available.';
  }

  function extractNewContent() {
    const matchResult = message.match(/NewMessage:(.*)/s);
    if (matchResult && matchResult[1]) {
      return formatTextToHtml(matchResult[1].trim());
    } else {
      return 'No new content available.';
    }
  }

  return (
    <div className="p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold">Edit History</h3>
        <button
          onClick={() => setShowEditedHistory(false)}
          className="text-gray-600 hover:text-red-500 transition"
          title="Close"
        >
          <FiX size={24} />
        </button>
      </div>

      {/* Content Box */}
      <div className="bg-white shadow rounded overflow-hidden border">
        <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x">
          {/* Old Content */}
          <div className="p-4 max-h-[calc(100vh-150px)] overflow-y-auto">
            <div className="bg-gray-100 px-3 py-2 rounded-t">
              <h6 className="text-sm font-medium text-gray-700">Old Content</h6>
            </div>
            <div
              className="pt-3 text-sm"
              dangerouslySetInnerHTML={{ __html: extractOldContent() }}
            />
          </div>

          {/* New Content */}
          <div className="p-4 max-h-[calc(100vh-150px)] overflow-y-auto">
            <div className="bg-gray-100 px-3 py-2 rounded-t">
              <h6 className="text-sm font-medium text-gray-700">New Content</h6>
            </div>
            <div
              className="pt-3 text-sm"
              dangerouslySetInnerHTML={{ __html: extractNewContent() }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
