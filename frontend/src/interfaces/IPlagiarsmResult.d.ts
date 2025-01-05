import { IMatchDetail } from "./IMatchDetail";

export interface IPlagiarsmResult {
  file1: string;
  file2: string;
  user1: string;
  user2: string;
  similarity: number;
  similar_segments: string[];
  originalCode1?: string;
  originalCode2?: string;
  is_exact_match?: boolean;
  match_details?: IMatchDetail[];
  normalizedCode1?: string;
  normalizedCode2?: string;
  comparisonDetails?: {
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