import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { IDebugComparison } from '../../interfaces/IDebugComparison';

export const DebugComparisonView: React.FC<IDebugComparison> = ({
    originalCode1,
    originalCode2,
    normalizedCode1,
    normalizedCode2,
    fileName1,
    fileName2,
    similarity,
    matchDetails
}) => {
    return (
        <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <h4 className="font-semibold mb-2">Original Code from {fileName1}</h4>
                    <SyntaxHighlighter 
                        language="cpp"
                        style={tomorrow}
                        showLineNumbers
                        className="text-sm"
                    >
                        {originalCode1}
                    </SyntaxHighlighter>
                    <h4 className="font-semibold mt-4 mb-2">Normalized Version</h4>
                    <SyntaxHighlighter 
                        language="cpp"
                        style={tomorrow}
                        showLineNumbers
                        className="text-sm"
                    >
                        {normalizedCode1}
                    </SyntaxHighlighter>
                </div>
                <div>
                    <h4 className="font-semibold mb-2">Original Code from {fileName2}</h4>
                    <SyntaxHighlighter 
                        language="cpp"
                        style={tomorrow}
                        showLineNumbers
                        className="text-sm"
                    >
                        {originalCode2}
                    </SyntaxHighlighter>
                    <h4 className="font-semibold mt-4 mb-2">Normalized Version</h4>
                    <SyntaxHighlighter 
                        language="cpp"
                        style={tomorrow}
                        showLineNumbers
                        className="text-sm"
                    >
                        {normalizedCode2}
                    </SyntaxHighlighter>
                </div>
            </div>

            <div className="mt-6 p-4 bg-white dark:bg-gray-700 rounded-lg">
                <h4 className="font-semibold mb-4">Comparison Details</h4>
                <div className="space-y-2 text-sm">
                    <p>Similarity Score: <span className="font-mono">{(similarity * 100).toFixed(2)}%</span></p>
                    <p>Matching Lines: <span className="font-mono">{matchDetails.lineMatches} / {matchDetails.totalLines}</span></p>
                    <div className="mt-4">
                        <h5 className="font-semibold mb-2">Matching Segments ({matchDetails.matchingSegments.length})</h5>
                        {matchDetails.matchingSegments.map((segment, idx) => (
                            <div key={idx} className="mb-4 p-3 border-l-4 border-green-500">
                                <p className="text-xs text-gray-500 mb-2">
                                    Lines {segment.start1}-{segment.start1 + segment.length} in {fileName1} match
                                    lines {segment.start2}-{segment.start2 + segment.length} in {fileName2}
                                </p>
                                <SyntaxHighlighter 
                                    language="cpp"
                                    style={tomorrow}
                                    className="text-xs"
                                >
                                    {segment.code}
                                </SyntaxHighlighter>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
