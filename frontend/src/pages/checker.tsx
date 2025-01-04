import React, { useState } from "react";
import Loading from '../components/interactives/loading';
import { writeData, readData } from '../firebase/firebaseUtils';
import { DiffView } from '../components/result-components/diff-view';

interface PlagiarismResult {
    file1: string;
    file2: string;
    user1: string;
    user2: string;
    similarity: number;
    similar_segments: string[];
    originalCode1?: string;
    originalCode2?: string;
}

export default function Checker() {
    const [isProcessing, setIsProcessing] = useState(false);
    const [files, setFiles] = useState<File[]>([]);
    const [results, setResults] = useState<PlagiarismResult[]>([]);
    const [showResults, setShowResults] = useState(false);
    const features = [
        {
            title: "Single File Analysis",
            description: "Upload and analyze individual files for plagiarism detection",
            icon: "📄",
            highlight: "Detailed similarity analysis"
        },
        {
            title: "Multiple File Support",
            description: "Compare multiple files simultaneously to detect similarities",
            icon: "📚",
            highlight: "Batch processing capability"
        },
        {
            title: "ZIP Archive Support",
            description: "Upload ZIP files containing multiple documents for bulk analysis",
            icon: "🗂️",
            highlight: "Process entire project folders"
        },
        {
            title: "Various File Formats",
            description: "Support for PDF, DOC, DOCX, TXT, and ZIP files",
            icon: "📎",
            highlight: "Universal compatibility"
        }
    ];

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const uploadedFiles = Array.from(e.target.files);
            
            const validFiles = uploadedFiles.filter(file => {
                const extension = file.name.split('.').pop()?.toLowerCase();
                return ['zip'].includes(extension || '');
            });

            if (validFiles.length !== uploadedFiles.length) {
                alert('Only ZIP files are supported for user submissions.');
            }

            setFiles(validFiles);
        }
    };

    const handleProcess = async () => {
        setIsProcessing(true);
        setShowResults(false);
        
        try {
            const formData = new FormData();
            files.forEach((file) => {
                formData.append('files', file);
            });

            const response = await fetch('http://localhost:5000/check-plagiarism', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Failed to process files');
            }

            const result = await response.json();
            setResults(result.results);
            setShowResults(true);
            
            // Store results in Firebase
            const timestamp = new Date().toISOString();
            await writeData(`plagiarism-results/${timestamp}`, {
                timestamp,
                files: files.map(f => f.name),
                results: result.results
            });

        } catch (error) {
            console.error('Error processing files:', error);
            alert('Error processing files. Please try again.');
        } finally {
            setIsProcessing(false);
        }
    };

    const handleTestWrite = async () => {
        const testData = {
            message: "Test data",
            timestamp: new Date().toISOString(),
        };
        const result = await writeData('test/data', testData);
        if (result) {
            alert('Test data written successfully!');
        } else {
            alert('Failed to write test data');
        }
    };

    const handleTestRead = async () => {
        const data = await readData('test/data');
        if (data) {
            console.log('Read data:', data);
            alert('Data read successfully! Check console.');
        } else {
            alert('No data found or error reading data');
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="mb-16">
                <h1 className="text-4xl font-bold text-gray-800 dark:text-white text-center mb-12">
                    File Checker Features
                </h1>
                <div className="space-y-12">
                    {features.map((feature, index) => (
                        <div key={index} className="flex items-center gap-8">
                            <div className="w-1/2 pl-8 border-l border-blue-500">
                                <div className="flex items-center gap-4 mb-4">
                                    <span className="text-4xl">{feature.icon}</span>
                                    <h3 className="text-2xl font-bold text-gray-800 dark:text-white">
                                        {feature.title}
                                    </h3>
                                </div>
                                <p className="text-gray-600 dark:text-gray-300 mb-4">
                                    {feature.description}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="mt-8 bg-white dark:bg-gray-800 p-6 rounded-xl">
                <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-8 text-center">
                    Upload Files for Analysis
                </h2>
                
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 p-8 text-center rounded-lg">
                    <input
                        type="file"
                        multiple
                        accept=".zip"
                        className="hidden"
                        id="file-upload"
                        onChange={handleFileUpload}
                    />
                    <label
                        htmlFor="file-upload"
                        className="cursor-pointer text-blue-500 hover:text-blue-600 block"
                    >
                        <span className="text-4xl mb-2 block">📁</span>
                        <span className="text-gray-800 dark:text-white">
                            Upload Student Submissions (ZIP files)
                        </span>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                            Each ZIP file represents one student's submission
                        </p>
                    </label>
                </div>

                {files.length > 0 && (
                    <div className="mt-4">
                        <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-2">
                            Selected Files ({files.length}):
                        </h3>
                        <ul className="space-y-2">
                            {files.map((file, index) => (
                                <li key={index} className="text-gray-600 dark:text-gray-300">
                                    {file.name}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                <div className="mt-8 text-center">
                    {isProcessing ? (   
                        <div className="flex flex-col items-center space-y-4">
                            <Loading size="large" />
                            <p className="text-gray-600 dark:text-gray-300">
                                Analyzing files...
                            </p>
                        </div>
                    ) : (
                        <button
                            className="bg-blue-500 text-white px-8 py-3 rounded-lg hover:bg-blue-600 transition-colors"
                            onClick={handleProcess}
                            disabled={files.length === 0}
                        >
                            Start Analysis
                        </button>
                    )}
                </div>

                {showResults && (
                    <div className="mt-8 bg-white dark:bg-gray-800 p-6 rounded-xl">
                        <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
                            Analysis Results
                        </h2>
                        {results.length > 0 ? (
                            <div className="space-y-8">
                                {results.map((result, index) => (
                                    <div key={index} className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-700">
                                        <div className="flex justify-between items-center mb-4">
                                            <div>
                                                <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
                                                    Match #{index + 1}
                                                </h3>
                                                <p className="text-gray-600 dark:text-gray-300">
                                                    Student: {result.user1} ⟷ Student: {result.user2}
                                                </p>
                                                <p className="text-sm text-gray-500">
                                                    Files: {result.file1} ⟷ {result.file2}
                                                </p>
                                            </div>
                                            <div className="text-right">
                                                <span className={`text-lg font-bold ${
                                                    result.similarity > 0.8 ? 'text-red-500' : 
                                                    result.similarity > 0.6 ? 'text-yellow-500' : 'text-green-500'
                                                }`}>
                                                    {(result.similarity * 100).toFixed(1)}% Similar
                                                </span>
                                            </div>
                                        </div>
                                        {result.similar_segments.map((segment, idx) => (
                                            <div key={idx} className="mt-4">
                                                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                                    Similar Segment #{idx + 1}:
                                                </h4>
                                                <DiffView
                                                    code1={segment}
                                                    code2={segment}
                                                    fileName1={result.file1}
                                                    fileName2={result.file2}
                                                />
                                            </div>
                                        ))}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-center text-gray-600 dark:text-gray-300">
                                No significant similarities found between the files.
                            </p>
                        )}
                    </div>
                )}

                <div className="mt-8 flex justify-center gap-4">
                    <button
                        className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 transition-colors"
                        onClick={handleTestWrite}
                    >
                        Test Write to Firebase
                    </button>
                    <button
                        className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                        onClick={handleTestRead}
                    >
                        Test Read from Firebase
                    </button>
                </div>
            </div>
        </div>
    );
}
