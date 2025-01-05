import React, { useState } from "react";
import Loading from '../components/interactives/loading';
import { writeData, readData } from '../firebase/firebaseUtils';
import { DiffView } from '../components/result-components/diff-view';
import { DebugComparisonView } from '../components/result-components/debug-comparison-view';
import { IPlagiarsmResult } from "../interfaces/IPlagiarsmResult";
interface AnalysisSummary {
    total_submissions: number;
    total_files: number;
    total_comparisons: number;
    significant_matches: number;
}

interface ProgressState {
    status: 'processing' | 'complete' | 'error';
    stage?: string;
    progress?: number;
    currentComparison?: {
        user1: string;
        user2: string;
        file1: string;
        file2: string;
    };
    summary?: AnalysisSummary;
}

interface DebugInfo {
    normalizedCode1?: string;
    normalizedCode2?: string;
    similarityDetails?: {
        totalLines: number;
        matchingLines: number;
        variableChanges: boolean;
    };
}

interface AnalysisDetail {
    type: 'info' | 'warning' | 'detection' | 'skip' | 'error' | 'summary';
    message: string;
    files?: string[];
    similarity?: number;
    segmentCount?: number;
    reason?: string;
    matches?: number;
    details?: string[];
    totalMatches?: number;
    highestSimilarity?: number;
}

interface ProcessHistory {
    timestamp: string;
    action: string;
    details: {
        analysisDetail?: AnalysisDetail;
        file1?: string;
        file2?: string;
        similarity?: number;
        reason?: string;
        normalizedCode1?: string;
        normalizedCode2?: string;
    };
}

export default function Checker() {
    const [isProcessing, setIsProcessing] = useState(false);
    const [files, setFiles] = useState<File[]>([]);
    const [results, setResults] = useState<IPlagiarsmResult[]>([]);
    const [showResults, setShowResults] = useState(false);
    const [progress, setProgress] = useState<ProgressState | null>(null);
    const [similarityThreshold, setSimilarityThreshold] = useState(0.7);
    const [selectedResult, setSelectedResult] = useState<number | null>(null);
    const [debugInfo, setDebugInfo] = useState<DebugInfo | null>(null);
    const [processHistory, setProcessHistory] = useState<ProcessHistory[]>([]);
    const [showHistory, setShowHistory] = useState(false);
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

    const addToHistory = (action: string, details: any) => {
        setProcessHistory(prev => [...prev, {
            timestamp: new Date().toISOString(),
            action,
            details
        }]);
    };

    const listenToProgress = (sessionId: string) => {
        const eventSource = new EventSource(`http://localhost:5000/progress/${sessionId}`);
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setProgress(data);
            
            if (data.currentComparison) {
                addToHistory("Comparing Files", {
                    file1: `${data.currentComparison.user1}/${data.currentComparison.file1}`,
                    file2: `${data.currentComparison.user2}/${data.currentComparison.file2}`,
                    reason: data.stage
                });
            }
            
            if (data.status === 'complete') {
                setResults(data.results.results);
                setShowResults(true);
                eventSource.close();
                setIsProcessing(false);
            } else if (data.status === 'error') {
                alert('Error processing files: ' + data.message);
                eventSource.close();
                setIsProcessing(false);
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
            setIsProcessing(false);
            alert('Lost connection to server');
        };
    };

    const handleProcess = async () => {
        setIsProcessing(true);
        setShowResults(false);
        setProgress(null);
        
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

            const { session_id } = await response.json();
            listenToProgress(session_id);

        } catch (error) {
            console.error('Error processing files:', error);
            alert('Error processing files. Please try again.');
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

    const getSensitivityLabel = (threshold: number) => {
        if (threshold <= 0.2) return "Very Low - Will detect most similarities";
        if (threshold <= 0.4) return "Low - May include coincidental matches";
        if (threshold <= 0.6) return "Medium - Balanced detection";
        if (threshold <= 0.8) return "High - Only significant matches";
        return "Very High - Only nearly identical code";
    };

    const showDetailedAnalysis = (result: IPlagiarsmResult, index: number) => {
        setSelectedResult(index);
        setDebugInfo({
            normalizedCode1: result.originalCode1,
            normalizedCode2: result.originalCode2,
            similarityDetails: {
                totalLines: result.originalCode1?.split('\n').length || 0,
                matchingLines: result.similar_segments.reduce((acc, segment) => 
                    acc + segment.split('\n').length, 0),
                variableChanges: result.match_details?.some(m => m.has_variable_changes) || false
            }
        });
    };

    const renderAnalysisButtons = () => (
        <div className="mt-8">
            {results.map((result, index) => (
                <div key={index} className="mb-6 p-4 border rounded-lg bg-white dark:bg-gray-800">
                    <div className="flex justify-between items-center mb-4">
                        <button
                            onClick={() => showDetailedAnalysis(result, index)}
                            className="text-blue-500 hover:text-blue-600"
                        >
                            Show Detailed Analysis for Match #{index + 1}
                        </button>
                        <span className={`px-3 py-1 rounded-full text-sm ${
                            result.is_exact_match ? 'bg-red-100 text-red-800' :
                            result.similarity > 0.8 ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                        }`}>
                            {result.similarity * 100}% Match
                        </span>
                    </div>

                    {selectedResult === index && debugInfo && (
                        <div className="mt-4 space-y-4">
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">
                                    <h4 className="font-semibold mb-2">Match Statistics</h4>
                                    <ul className="space-y-2">
                                        <li>Total Lines: {debugInfo.similarityDetails?.totalLines}</li>
                                        <li>Matching Lines: {debugInfo.similarityDetails?.matchingLines}</li>
                                        <li>Match Percentage: {result.similarity * 100}%</li>
                                        <li>Variable Names Changed: {debugInfo.similarityDetails?.variableChanges ? 'Yes' : 'No'}</li>
                                    </ul>
                                </div>
                                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">
                                    <h4 className="font-semibold mb-2">Match Locations</h4>
                                    <ul className="space-y-2">
                                        {result.match_details?.map((match, idx) => (
                                            <li key={idx}>
                                                Segment {idx + 1}: Lines {match.line_number1} - {match.line_number1 + match.line_count} in File 1
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>

                            {result.match_details?.map((match, idx) => (
                                <div key={idx} className="border-t pt-4">
                                    <h4 className="font-semibold mb-2">
                                        Matching Segment {idx + 1} 
                                        {match.has_variable_changes && (
                                            <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                                                Variables Changed
                                            </span>
                                        )}
                                    </h4>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-sm text-gray-500 mb-1">Original Code</p>
                                            <pre className="text-xs bg-gray-50 dark:bg-gray-700 p-2 rounded overflow-x-auto">
                                                {match.segment}
                                            </pre>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500 mb-1">Normalized Code</p>
                                            <pre className="text-xs bg-gray-50 dark:bg-gray-700 p-2 rounded overflow-x-auto">
                                                {match.normalized_segment}
                                            </pre>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );

    const renderHistory = () => (
        <div className="mt-8 p-4 bg-white dark:bg-gray-800 rounded-xl shadow">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-gray-800 dark:text-white">Analysis History</h3>
                <button 
                    onClick={() => setShowHistory(false)}
                    className="text-gray-500 hover:text-gray-700"
                >
                    ✕
                </button>
            </div>
            <div className="max-h-[70vh] overflow-y-auto">
                {processHistory.map((entry, index) => (
                    <div key={index} className={`mb-4 p-3 border-l-4 ${
                        entry.details.analysisDetail?.type === 'warning' ? 'border-red-500 bg-red-50 dark:bg-red-900/20' :
                        entry.details.analysisDetail?.type === 'detection' ? 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20' :
                        'border-blue-500 bg-gray-50 dark:bg-gray-700'
                    }`}>
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-500">{new Date(entry.timestamp).toLocaleTimeString()}</span>
                            <span className={`font-semibold ${
                                entry.details.analysisDetail?.type === 'warning' ? 'text-red-600' :
                                entry.details.analysisDetail?.type === 'detection' ? 'text-yellow-600' :
                                'text-blue-600'
                            }`}>
                                {entry.details.analysisDetail?.type?.toUpperCase() || entry.action}
                            </span>
                        </div>
                        <div className="mt-2 space-y-2">
                            <p className="text-gray-700 dark:text-gray-300">
                                {entry.details.analysisDetail?.message}
                            </p>
                            {entry.details.analysisDetail?.files && (
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Files: {entry.details.analysisDetail.files.join(' ⟷ ')}
                                </p>
                            )}
                            {entry.details.analysisDetail?.similarity && (
                                <p className={`text-sm font-mono ${
                                    entry.details.analysisDetail.similarity > 0.8 ? 'text-red-500' :
                                    entry.details.analysisDetail.similarity > 0.6 ? 'text-yellow-500' :
                                    'text-green-500'
                                }`}>
                                    Similarity: {(entry.details.analysisDetail.similarity * 100).toFixed(1)}%
                                </p>
                            )}
                            {entry.details.analysisDetail?.reason && (
                                <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                                    Reason: {entry.details.analysisDetail.reason}
                                </p>
                            )}
                            {entry.details.analysisDetail?.details && (
                                <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                                    <p className="font-semibold">Matching Sections:</p>
                                    <ul className="list-disc list-inside space-y-1">
                                        {entry.details.analysisDetail.details.map((detail, idx) => (
                                            <li key={idx}>{detail}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );

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

                <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Similarity Threshold: {(similarityThreshold * 100).toFixed(0)}%
                    </label>
                    <div className="mt-2">
                        <input
                            type="range"
                            min="0"
                            max="100"
                            value={similarityThreshold * 100}
                            onChange={(e) => setSimilarityThreshold(Number(e.target.value) / 100)}
                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                        />
                    </div>
                    <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        Sensitivity: {getSensitivityLabel(similarityThreshold)}
                    </p>
                    <div className="mt-2 grid grid-cols-5 text-xs text-gray-400">
                        <div>Very Low</div>
                        <div>Low</div>
                        <div className="text-center">Medium</div>
                        <div className="text-right">High</div>
                        <div className="text-right">Very High</div>
                    </div>
                </div>

                <div className="mt-8 text-center">
                    {isProcessing ? (   
                        <div className="flex flex-col items-center space-y-4">
                            <Loading size="large" />
                            <div className="w-full max-w-md">
                                {progress && (
                                    <>
                                        <p className="text-gray-600 dark:text-gray-300 mb-2">
                                            {progress.stage}
                                        </p>
                                        {progress.progress !== undefined && (
                                            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mb-4">
                                                <div 
                                                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-500" 
                                                    style={{ width: `${progress.progress}%` }}
                                                ></div>
                                            </div>
                                        )}
                                        {progress.currentComparison && (
                                            <p className="text-sm text-gray-500 dark:text-gray-400">
                                                Comparing {progress.currentComparison.user1}'s {progress.currentComparison.file1} with<br/>
                                                {progress.currentComparison.user2}'s {progress.currentComparison.file2}
                                            </p>
                                        )}
                                    </>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="space-x-4">
                            <button
                                className="bg-blue-500 text-white px-8 py-3 rounded-lg hover:bg-blue-600 transition-colors"
                                onClick={handleProcess}
                                disabled={files.length === 0}
                            >
                                Start Analysis
                            </button>
                            <button
                                className="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors"
                                onClick={() => setShowHistory(true)}
                                disabled={processHistory.length === 0}
                            >
                                Show Process History
                            </button>
                        </div>
                    )}
                </div>

                {progress?.summary && (
                    <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-2">
                            Analysis Summary
                        </h3>
                        <div className="grid grid-cols-4 gap-4 text-sm">
                            <div>
                                <p className="text-gray-500 dark:text-gray-400">Total Submissions</p>
                                <p className="text-lg font-semibold">{progress.summary.total_submissions}</p>
                            </div>
                            <div>
                                <p className="text-gray-500 dark:text-gray-400">Total Files</p>
                                <p className="text-lg font-semibold">{progress.summary.total_files}</p>
                            </div>
                            <div>
                                <p className="text-gray-500 dark:text-gray-400">Files Compared</p>
                                <p className="text-lg font-semibold">{progress.summary.total_comparisons}</p>
                            </div>
                            <div>
                                <p className="text-gray-500 dark:text-gray-400">Matches Found</p>
                                <p className="text-lg font-semibold">{progress.summary.significant_matches}</p>
                            </div>
                        </div>
                    </div>
                )}

                {showResults && (
                    <div className="mt-8 bg-white dark:bg-gray-800 p-6 rounded-xl">
                        <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
                            Analysis Results
                        </h2>
                        {results.length > 0 ? (
                            <>
                                {results.map((result, index) => (
                                    <div key={index} className={`border rounded-lg p-4 ${
                                        result.is_exact_match 
                                            ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' 
                                            : 'bg-gray-50 dark:bg-gray-700'
                                    }`}>
                                        <div className="flex justify-between items-center mb-4">
                                            <div>
                                                <h3 className="text-lg font-semibold text-gray-800 dark:text-white flex items-center gap-2">
                                                    Match #{index + 1}
                                                    {result.is_exact_match && (
                                                        <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded dark:bg-red-900 dark:text-red-200">
                                                            Exact Match Detected
                                                        </span>
                                                    )}
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
                                                    result.is_exact_match ? 'text-red-500' :
                                                    result.similarity > 0.8 ? 'text-red-500' : 
                                                    result.similarity > 0.6 ? 'text-yellow-500' : 'text-green-500'
                                                }`}>
                                                    {result.is_exact_match ? 'Exact Match' : `${(result.similarity * 100).toFixed(1)}% Similar`}
                                                </span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => setSelectedResult(selectedResult === index ? null : index)}
                                            className="w-full text-left mt-4 text-blue-500 hover:text-blue-600"
                                        >
                                            {selectedResult === index ? 'Hide' : 'Show'} Detailed Debug Information
                                        </button>
                                        
                                        {selectedResult === index && (
                                            <DebugComparisonView
                                                originalCode1={result.originalCode1 || ''}
                                                originalCode2={result.originalCode2 || ''}
                                                normalizedCode1={result.normalizedCode1 || ''}
                                                normalizedCode2={result.normalizedCode2 || ''}
                                                fileName1={result.file1}
                                                fileName2={result.file2}
                                                similarity={result.similarity}
                                                matchDetails={result.comparisonDetails || {
                                                    lineMatches: 0,
                                                    totalLines: 0,
                                                    matchingSegments: []
                                                }}
                                            />
                                        )}
                                        {result.match_details ? (
                                            <div className="space-y-4">
                                                {result.match_details.map((match, idx) => (
                                                    <div key={idx} className="mt-4">
                                                        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                                                            Match #{idx + 1} ({match.line_count} lines)
                                                            {match.has_variable_changes && (
                                                                <span className="ml-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                                                                    Variable Names Changed
                                                                </span>
                                                            )}
                                                        </h4>
                                                        <p className="text-xs text-gray-500 mb-2">
                                                            Found at lines {match.line_number1} and {match.line_number2}
                                                        </p>
                                                        <DiffView
                                                            code1={match.segment}
                                                            code2={match.segment2}
                                                            fileName1={result.file1}
                                                            fileName2={result.file2}
                                                        />
                                                        {match.has_variable_changes && (
                                                            <div className="mt-2 p-2 bg-gray-100 dark:bg-gray-800 rounded">
                                                                <p className="text-xs text-gray-500 mb-1">Normalized version (ignoring variable names):</p>
                                                                <pre className="text-xs text-gray-600 dark:text-gray-400">
                                                                    {match.normalized_segment}
                                                                </pre>
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            result.similar_segments.map((segment, idx) => (
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
                                            ))
                                        )}
                                    </div>
                                ))}
                                
                                {renderAnalysisButtons()}
                            </>
                        ) : (
                            <p className="text-center text-gray-600 dark:text-gray-300">
                                No significant similarities found between the files.
                            </p>
                        )}
                    </div>
                )}

                {showHistory && renderHistory()}

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
