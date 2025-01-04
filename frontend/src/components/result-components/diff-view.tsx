import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface DiffViewProps {
    code1: string;
    code2: string;
    fileName1: string;
    fileName2: string;
}

export const DiffView: React.FC<DiffViewProps> = ({ code1, code2, fileName1, fileName2 }) => {
    const lines1 = code1.split('\n');
    const lines2 = code2.split('\n');

    return (
        <div className="border rounded-lg overflow-hidden">
            <div className="grid grid-cols-2 bg-gray-100 dark:bg-gray-700">
                <div className="p-2 border-r">
                    <span className="text-sm font-mono text-gray-600 dark:text-gray-300">{fileName1}</span>
                </div>
                <div className="p-2">
                    <span className="text-sm font-mono text-gray-600 dark:text-gray-300">{fileName2}</span>
                </div>
            </div>
            <div className="grid grid-cols-2">
                <div className="border-r">
                    <SyntaxHighlighter 
                        language="cpp"
                        style={tomorrow}
                        showLineNumbers
                        customStyle={{ margin: 0, background: 'transparent' }}
                        className="text-sm"
                    >
                        {code1}
                    </SyntaxHighlighter>
                </div>
                <div>
                    <SyntaxHighlighter 
                        language="cpp"
                        style={tomorrow}
                        showLineNumbers
                        customStyle={{ margin: 0, background: 'transparent' }}
                        className="text-sm"
                    >
                        {code2}
                    </SyntaxHighlighter>
                </div>
            </div>
        </div>
    );
};
