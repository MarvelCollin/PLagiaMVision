export interface IDebugComparison {
    originalCode1: string;
    originalCode2: string;
    normalizedCode1: string;
    normalizedCode2: string;
    fileName1: string;
    fileName2: string;
    similarity: number;
    matchDetails: {
        lineMatches: number;
        totalLines: number;
        matchingSegments: Array<{
            start1: number;
            start2: number;
            length: number;
            code: string;
        }>;
    };
}