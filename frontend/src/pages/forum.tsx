import React, { useState } from "react";

export default function Forum() {
    const [selectedInputType, setSelectedInputType] = useState<string | null>(null);

    const inputTypes = [
        {
            id: 'api',
            title: 'Using API',
            description: 'Connect directly to source using API',
            icon: '🔌'
        },
        {
            id: 'manual',
            title: 'Manual Input',
            description: 'Input URLs or links one by one',
            icon: '🔗'
        },
        {
            id: 'excel',
            title: 'Excel Upload',
            description: 'Upload Excel file containing multiple links',
            icon: '📊'
        }
    ];

    const renderInputForm = () => {
        switch (selectedInputType) {
            case 'api':
                return (
                    <div className="mt-8 bg-white text-white dark:bg-gray-800 p-6 rounded-xl">
                        <h3 className="text-xl font-bold mb-4">API Configuration</h3>
                        <input
                            type="text"
                            placeholder="API Endpoint"
                            className="w-full mb-4 p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                        />
                        <input
                            type="text"
                            placeholder="API Key"
                            className="w-full mb-4 p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                        />
                    </div>
                );
            case 'manual':
                return (
                    <div className="mt-8 bg-white text-white dark:bg-gray-800 p-6 rounded-xl">
                        <h3 className="text-xl font-bold mb-4">Enter URLs</h3>
                        <textarea
                            placeholder="Enter URLs (one per line)"
                            className="w-full h-32 mb-4 p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
                        />
                    </div>
                );
            case 'excel':
                return (
                    <div className="mt-8 bg-white text-white dark:bg-gray-800 p-6 rounded-xl">
                        <h3 className="text-xl font-bold mb-4">Upload Excel File</h3>
                        <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 p-8 text-center rounded-lg">
                            <input
                                type="file"
                                accept=".xlsx,.xls"
                                className="hidden"
                                id="excel-upload"
                            />
                            <label
                                htmlFor="excel-upload"
                                className="cursor-pointer text-blue-500 hover:text-blue-600"
                            >
                                <span className="text-4xl mb-2 block">📁</span>
                                <span>Click to upload Excel file</span>
                            </label>
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-8 text-center">
                Select Input Method
            </h1>
            <div className="grid md:grid-cols-3 gap-6">
                {inputTypes.map((type) => (
                    <div
                        key={type.id}
                        className={`
                            p-6 rounded-xl cursor-pointer transition-all duration-200
                            ${selectedInputType === type.id
                                ? 'bg-blue-500 text-white shadow-xl transform -translate-y-1'
                                : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-white hover:shadow-lg'
                            }
                        `}
                        onClick={() => setSelectedInputType(type.id)}
                    >
                        <div className="text-4xl mb-4">{type.icon}</div>
                        <h3 className="text-xl font-bold mb-2">{type.title}</h3>
                        <p className={`
                            ${selectedInputType === type.id
                                ? 'text-gray-100'
                                : 'text-gray-600 dark:text-gray-300'
                            }
                        `}>
                            {type.description}
                        </p>
                    </div>
                ))}
            </div>
            {renderInputForm()}
            {selectedInputType && (
                <div className="mt-8 text-center">
                    <button
                        className="bg-blue-500 text-white px-8 py-3 rounded-lg hover:bg-blue-600 transition-colors"
                        onClick={() => console.log(`Processing with: ${selectedInputType}`)}
                    >
                        Process
                    </button>
                </div>
            )}
        </div>
    );
}