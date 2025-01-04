import React, { useState } from "react";
import Loading from '../components/interactives/loading';
import { writeData, readData } from '../firebase/firebaseUtils';

export default function Checker() {
    const [isProcessing, setIsProcessing] = useState(false);
    const [files, setFiles] = useState<File[]>([]);
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
                return ['pdf', 'doc', 'docx', 'txt', 'zip'].includes(extension || '');
            });

            if (validFiles.length !== uploadedFiles.length) {
                alert('Some files were rejected. Only PDF, DOC, DOCX, TXT, and ZIP files are supported.');
            }

            setFiles(validFiles);
        }
    };

    const handleProcess = async () => {
        setIsProcessing(true);
        await new Promise(resolve => setTimeout(resolve, 2000));
        setIsProcessing(false);
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
                        accept=".pdf,.doc,.docx,.txt,.zip"
                        className="hidden"
                        id="file-upload"
                        onChange={handleFileUpload}
                    />
                    <label
                        htmlFor="file-upload"
                        className="cursor-pointer text-blue-500 hover:text-blue-600"
                    >
                        <span className="text-4xl mb-2 block">📁</span>
                        <span className="text-gray-800 dark:text-white">
                            Click to upload files or drag and drop
                        </span>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                            Supported formats: PDF, DOC, DOCX, TXT, ZIP
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

                {/* <div className="mt-8 text-center">
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
                </div> */}

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
