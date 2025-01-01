import React from 'react';
import HoverInformation from '../interactives/hover-information';

interface MatchedSource {
  type: string;
  source: string;
  similarity: number;
  sourceAnswer?: string;
  possiblePrompt?: string;  // Add this line
}

interface SimilarityResults {
  submission: number;
  browser: number;
  ai: number;
}

interface Submission {
  traineeNumber: string;
  forumQuestion: string;
  forumAnswer: string;
  similarityResults: SimilarityResults;
  overallPlagiarismScore: number;
  matchedSources: MatchedSource[];
}

const SubmissionResult: React.FC<{ submission: Submission }> = ({ submission }) => {

  const getSeverityColor = (score: number) => {
    if (score >= 75) return 'text-red-500';
    if (score >= 50) return 'text-yellow-500';
    return 'text-green-500';
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-800 dark:text-white mb-2">
            {submission.traineeNumber}
          </h3>
          <p className="text-gray-600 dark:text-gray-300 text-sm">
            Question: {submission.forumQuestion}
          </p>
        </div>
        <div className={`text-2xl font-bold ${getSeverityColor(submission.overallPlagiarismScore)}`}>
          {submission.overallPlagiarismScore}%
        </div>
      </div>

      {/* Modified Answer Section - Always visible */}
      <div className="mb-6">
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h4 className="font-bold text-gray-700 dark:text-gray-300 mb-2">Forum Answer:</h4>
          <p className="text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
            {submission.forumAnswer}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <HoverInformation text="Shows the percentage match with other student submissions in the system. High percentages may indicate collaboration or copying between students.">
          <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
            <div className="text-sm text-gray-600 dark:text-gray-400">Submission Match</div>
            <div className={`text-lg font-bold ${getSeverityColor(submission.similarityResults.submission)}`}>
              {submission.similarityResults.submission}%
            </div>
          </div>
        </HoverInformation>

        <HoverInformation text="Indicates similarity with publicly available content from websites, documentation, and other online sources. High matches suggest content may be copied from the internet.">
          <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
            <div className="text-sm text-gray-600 dark:text-gray-400">Browser Match</div>
            <div className={`text-lg font-bold ${getSeverityColor(submission.similarityResults.browser)}`}>
              {submission.similarityResults.browser}%
            </div>
          </div>
        </HoverInformation>

        <HoverInformation text="Shows likelihood that the content was generated using AI tools like ChatGPT. High percentages suggest the answer may have been created using AI assistance.">
          <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
            <div className="text-sm text-gray-600 dark:text-gray-400">AI Match</div>
            <div className={`text-lg font-bold ${getSeverityColor(submission.similarityResults.ai)}`}>
              {submission.similarityResults.ai}%
            </div>
          </div>
        </HoverInformation>
      </div>

      <div className="mt-4">
        <h4 className="font-bold text-gray-700 dark:text-gray-300 mb-2">Matched Sources:</h4>
        <div className="space-y-2">
          {submission.matchedSources.map((source, index) => (
            <div key={index} className="text-sm">
              <div className="text-gray-600 dark:text-gray-400 flex justify-between">
                <span>{source.source}</span>
                <span className={`font-medium ${getSeverityColor(source.similarity)}`}>
                  {source.similarity}%
                </span>
              </div>
              {source.type === 'submission' && source.sourceAnswer && (
                <div className="mt-2 ml-4 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    Original Answer:
                  </p>
                  <p className="text-gray-800 dark:text-gray-200 mt-1">
                    {source.sourceAnswer}
                  </p>
                </div>
              )}
              {source.type === 'ai' && source.possiblePrompt && (
                <div className="mt-2 ml-4 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    Possible AI Prompt:
                  </p>
                  <p className="text-gray-800 dark:text-gray-200 mt-1">
                    {source.possiblePrompt}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SubmissionResult;
